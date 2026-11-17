"""Pipeline GraphRAG SOP memakai retriever dan generator Neo4j GraphRAG."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase, Query, RoutingControl
from neo4j.exceptions import CypherSyntaxError
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.generation.prompts import RagTemplate, Text2CypherTemplate
from neo4j_graphrag.generation.types import RagResultModel
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.types import RawSearchResult, RetrieverResultItem, Text2CypherSearchModel

from fsm_graphrag.config import Settings
from fsm_graphrag.text_to_cypher import (
    APPROVED_MODELS,
    APPROVED_SOPS,
    MAX_RESULTS,
    CypherSafetyValidator,
    Evidence,
    PipelineError,
    PipelineResponse,
    PipelineTrace,
    QuestionRequest,
    _has_provenance,
    _json_safe,
    trace_to_dict,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FALLBACK = json.dumps(
    {
        "answer": "Informasi belum cukup pada evidence SOP yang tersedia.",
        "evidence_ids": [],
        "abstain": True,
    },
    ensure_ascii=False,
)


class TracedOpenAILLM(OpenAILLM):
    """OpenAILLM yang mencatat waktu dan pemakaian token tanpa mencatat credential."""

    def __init__(self, *, stage: str, trace: PipelineTrace, **kwargs: Any) -> None:
        self.stage = stage
        self.trace = trace
        super().__init__(**kwargs)

    def invoke(self, *args: Any, **kwargs: Any):
        started = time.perf_counter()
        try:
            result = super().invoke(*args, **kwargs)
        except Exception:
            self.trace.latensi_ms[self.stage] = round((time.perf_counter() - started) * 1000, 3)
            raise
        self.trace.latensi_ms[self.stage] = round((time.perf_counter() - started) * 1000, 3)
        if result.usage is not None:
            self.trace.token_usage[f"{self.stage}_input"] = result.usage.request_tokens
            self.trace.token_usage[f"{self.stage}_output"] = result.usage.response_tokens
        else:
            self.trace.token_usage[f"{self.stage}_input"] = None
            self.trace.token_usage[f"{self.stage}_output"] = None
        self.trace.estimated_cost[self.stage] = None
        return result


class GuardedText2CypherRetriever(Text2CypherRetriever):
    """Retriever library dengan validasi proyek sebelum query dijalankan."""

    # Versi server diuji oleh smoke test proyek; hindari CALL dbms.components()
    # saat inisialisasi agar retriever tidak meminta hak prosedur tambahan.
    VERIFY_NEO4J_VERSION = False

    def __init__(
        self,
        *,
        driver,
        llm,
        schema: str,
        custom_prompt: str,
        examples: list[str],
        database: str,
        timeout_seconds: float,
        trace: PipelineTrace,
        validator: CypherSafetyValidator | None = None,
        result_formatter=None,
    ) -> None:
        super().__init__(
            driver=driver,
            llm=llm,
            neo4j_schema=schema,
            examples=examples,
            result_formatter=result_formatter or format_evidence_record,
            custom_prompt=custom_prompt,
            neo4j_database=database,
        )
        self.timeout_seconds = timeout_seconds
        self.trace = trace
        self.validator = validator or CypherSafetyValidator()
        self._prompt_template = Text2CypherTemplate(
            template=custom_prompt,
            expected_inputs=["schema", "examples", "query_text"],
        )

    def get_search_results(
        self,
        query_text: str,
        prompt_params: dict[str, Any] | None = None,
        *,
        sop_id: str | None = None,
        model_id: str | None = None,
    ) -> RawSearchResult:
        request = Text2CypherSearchModel(query_text=query_text)
        parameters = dict(prompt_params or {})
        examples = parameters.pop("examples", None) or "\n".join(self.examples)
        schema = parameters.pop("schema", None) or self.neo4j_schema
        prompt = self._prompt_template.format(
            schema=schema,
            examples=examples,
            query_text=request.query_text,
            **parameters,
        )
        started = time.perf_counter()
        try:
            model_response = self.llm.invoke(input=prompt)
            try:
                generated = json.loads(model_response.content)
            except json.JSONDecodeError as exc:
                raise PipelineError(
                    "TEXT_TO_CYPHER_FORMAT_ERROR", "Keluaran query bukan JSON valid."
                ) from exc
            query = generated.get("cypher")
            query_parameters = generated.get("parameters", {})
            if not isinstance(query, str) or not isinstance(query_parameters, dict):
                raise PipelineError(
                    "TEXT_TO_CYPHER_FORMAT_ERROR", "Field cypher/parameters tidak valid."
                )
            self.trace.latensi_ms["text_to_cypher"] = round(
                (time.perf_counter() - started) * 1000, 3
            )
            self.trace.generated_cypher = query
            if not query.strip():
                self.trace.query_validation = "ABSTAIN_TIDAK_ADA_QUERY"
                self.trace.query_execution = "TIDAK_DIJALANKAN"
                return RawSearchResult(records=[], metadata={"cypher": ""})

            safe = self.validator.validate(
                query,
                query_parameters,
                sop_id=sop_id,
                model_id=model_id,
            )
            self.trace.query_validation = "LOLOS_ALLOWLIST_DAN_PARAMETER"
            retrieval_started = time.perf_counter()
            explain = Query(
                f"EXPLAIN {safe.query}",
                timeout=self.timeout_seconds,
            )
            _, summary, _ = self.driver.execute_query(
                query_=explain,
                parameters_=safe.parameters,
                database_=self.neo4j_database,
                routing_=RoutingControl.READ,
            )
            if summary.query_type != "r":
                self.trace.query_validation = "DITOLAK_NON_READ_ONLY"
                raise PipelineError(
                    "QUERY_DITOLAK", "EXPLAIN tidak mengklasifikasikan query sebagai read-only."
                )

            bounded_query = Query(safe.query, timeout=self.timeout_seconds)
            records, _, _ = self.driver.execute_query(
                query_=bounded_query,
                parameters_=safe.parameters,
                database_=self.neo4j_database,
                routing_=RoutingControl.READ,
            )
            self.trace.query_execution = "BERHASIL"
            self.trace.latensi_ms["retrieval"] = round(
                (time.perf_counter() - retrieval_started) * 1000, 3
            )
            return RawSearchResult(
                records=records[:MAX_RESULTS],
                metadata={"cypher": safe.query},
            )
        except CypherSyntaxError as exc:
            self.trace.query_execution = "GAGAL_SYNTAX"
            raise PipelineError("CYPHER_SYNTAX_ERROR", "Neo4j menolak sintaks Cypher.") from exc
        except PipelineError:
            raise
        except Exception as exc:
            self.trace.query_execution = "GAGAL_RETRIEVAL"
            raise PipelineError("RETRIEVAL_ERROR", "Tahap retrieval GraphRAG gagal.") from exc


class GraphRAGService:
    """Mengorkestrasi Text2CypherRetriever dan grounded answer melalui GraphRAG."""

    def __init__(
        self,
        *,
        driver,
        settings: Settings,
        prompt_dir: Path | None = None,
        examples: list[str] | None = None,
    ) -> None:
        self.driver = driver
        self.settings = settings
        self.prompt_dir = prompt_dir or PROJECT_ROOT / "prompts"
        self.examples = examples or []

    @classmethod
    def from_settings(
        cls,
        *,
        settings: Settings,
        prompt_dir: Path | None = None,
        examples: list[str] | None = None,
    ) -> GraphRAGService:
        """Bangun service produksi hanya dengan kredensial database baca saja."""
        return cls(
            driver=create_read_only_driver(settings),
            settings=settings,
            prompt_dir=prompt_dir,
            examples=examples,
        )

    def close(self) -> None:
        """Tutup koneksi driver Neo4j yang dimiliki service."""
        self.driver.close()

    def _llm(self, *, stage: str, trace: PipelineTrace) -> TracedOpenAILLM:
        missing = []
        if not self.settings.llm_api_key:
            missing.append("LLM_API_KEY")
        if not self.settings.llm_model:
            missing.append("LLM_MODEL")
        if missing:
            raise PipelineError(
                "LLM_CONFIG_MISSING", "Konfigurasi belum diisi: " + ", ".join(missing)
            )
        return TracedOpenAILLM(
            stage=stage,
            trace=trace,
            model_name=self.settings.llm_model,
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            model_params={"temperature": self.settings.llm_temperature},
            timeout=self.settings.llm_timeout_seconds,
            max_retries=0,
        )

    def answer(self, request: QuestionRequest, *, request_id: str) -> PipelineResponse:
        if not request.question.strip():
            raise PipelineError("PERTANYAAN_KOSONG", "Pertanyaan tidak boleh kosong.")
        if request.sop_id is not None and request.sop_id not in APPROVED_SOPS:
            raise PipelineError("SOP_TIDAK_DIKENAL", "sop_id tidak ada dalam pilot.")
        if request.model_id is not None and (
            request.sop_id is None or APPROVED_MODELS.get(request.sop_id) != request.model_id
        ):
            raise PipelineError("MODEL_TIDAK_DIKENAL", "model_id tidak cocok dengan SOP pilot.")

        trace = PipelineTrace(request_id=request_id)
        try:
            cypher_llm = self._llm(stage="text_to_cypher", trace=trace)
            answer_llm = self._llm(stage="jawaban", trace=trace)
            retriever = GuardedText2CypherRetriever(
                driver=self.driver,
                llm=cypher_llm,
                schema=_graph_schema(),
                custom_prompt=(self.prompt_dir / "neo4j_text_to_cypher_v1.md").read_text(
                    encoding="utf-8"
                ),
                examples=self.examples,
                database=self.settings.neo4j_database,
                timeout_seconds=self.settings.neo4j_query_timeout_seconds,
                trace=trace,
            )
            rag = GraphRAG(
                retriever=retriever,
                llm=answer_llm,
                prompt_template=RagTemplate(
                    template=(self.prompt_dir / "neo4j_grounded_answer_v1.md").read_text(
                        encoding="utf-8"
                    ),
                    expected_inputs=["context", "query_text", "examples"],
                    system_instructions=(
                        "Jawab hanya dalam Bahasa Indonesia dan ikuti JSON keluaran."
                    ),
                ),
            )
            scoped_question = request.question.strip()
            if request.sop_id:
                scoped_question = f"Cakupan sop_id={request.sop_id}. {scoped_question}"
            result: RagResultModel = rag.search(
                query_text=scoped_question,
                retriever_config={"sop_id": request.sop_id, "model_id": request.model_id},
                return_context=True,
                response_fallback=_FALLBACK,
            )
            raw_items = result.retriever_result.items if result.retriever_result else []
            evidence = tuple(_item_to_evidence(item) for item in raw_items)
            trace.retrieved_evidence_ids = [item.evidence_id for item in evidence]
            if not evidence:
                trace.query_execution = "BERHASIL_TANPA_EVIDENCE"
                trace.error_category = "ABSTAIN_EMPTY_EVIDENCE"
            answer_data = _parse_answer(result.answer)
            answer_text = answer_data.get("answer")
            evidence_ids = answer_data.get("evidence_ids")
            abstain = answer_data.get("abstain")
            allowed = {item.evidence_id for item in evidence}
            if (
                not isinstance(answer_text, str)
                or not isinstance(evidence_ids, list)
                or not isinstance(abstain, bool)
                or any(not isinstance(item, str) or item not in allowed for item in evidence_ids)
                or (not abstain and not evidence_ids)
            ):
                raise PipelineError(
                    "JAWABAN_TIDAK_TER-GROUND",
                    "Jawaban tidak mematuhi format abstain atau referensi evidence.",
                )
            if any(not _has_provenance(item.data) for item in evidence):
                raise PipelineError(
                    "EVIDENCE_PROVENANCE_INCOMPLETE", "Evidence retrieval tidak lengkap provenance."
                )
            return PipelineResponse(answer_text, evidence, abstain, trace)
        except PipelineError as exc:
            trace.error_category = exc.category
            if exc.category == "EVIDENCE_PROVENANCE_INCOMPLETE":
                return PipelineResponse(
                    "Evidence graph tidak memiliki provenance sumber yang lengkap.",
                    (),
                    True,
                    trace,
                )
            exc.trace = trace_to_dict(PipelineResponse("", (), True, trace))
            raise
        except Exception as exc:
            trace.error_category = "GRAPHRAG_ERROR"
            error = PipelineError("GRAPHRAG_ERROR", "Pipeline GraphRAG gagal.")
            error.trace = trace_to_dict(PipelineResponse("", (), True, trace))
            raise error from exc


def create_read_only_driver(settings: Settings):
    """Buat driver baca saja; tidak memakai akun admin sebagai fallback."""
    if not settings.neo4j_read_user or not settings.neo4j_read_password:
        raise ValueError("Isi NEO4J_READ_USER dan NEO4J_READ_PASSWORD untuk pipeline GraphRAG.")
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_read_user, settings.neo4j_read_password),
    )


def format_evidence_record(record) -> RetrieverResultItem:
    """Ubah record Neo4j menjadi konteks JSON berprovenance dan ID evidence stabil."""
    data = {key: _json_safe(value) for key, value in record.items()}
    if not _has_provenance(data):
        raise PipelineError(
            "EVIDENCE_PROVENANCE_INCOMPLETE", "Record hasil tidak membawa provenance wajib."
        )
    fingerprint = hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:12]
    evidence_id = f"E-{fingerprint}"
    content = json.dumps(
        {"evidence_id": evidence_id, "data": data},
        ensure_ascii=False,
        sort_keys=True,
    )
    return RetrieverResultItem(
        content=content,
        metadata={"evidence_id": evidence_id, "data": data},
    )


def _item_to_evidence(item: RetrieverResultItem) -> Evidence:
    metadata = item.metadata or {}
    evidence_id = metadata.get("evidence_id")
    data = metadata.get("data")
    if not isinstance(evidence_id, str) or not isinstance(data, dict):
        raise PipelineError("EVIDENCE_FORMAT_ERROR", "Format evidence retriever tidak valid.")
    return Evidence(evidence_id=evidence_id, data=data)


def _parse_answer(content: str) -> dict[str, Any]:
    try:
        response = json.loads(content)
    except json.JSONDecodeError as exc:
        raise PipelineError("JAWABAN_FORMAT_ERROR", "Jawaban GraphRAG bukan JSON valid.") from exc
    if not isinstance(response, dict):
        raise PipelineError("JAWABAN_FORMAT_ERROR", "Jawaban GraphRAG harus berupa objek JSON.")
    return response


def _graph_schema() -> str:
    from fsm_graphrag.text_to_cypher import SCHEMA_LABELS, SCHEMA_PROPERTIES, SCHEMA_RELATIONSHIPS

    labels = ", ".join(sorted(SCHEMA_LABELS))
    properties = ", ".join(sorted(SCHEMA_PROPERTIES))
    relationships = ", ".join(sorted(SCHEMA_RELATIONSHIPS))
    return (
        f"Node labels: {labels}.\n"
        f"Node and relationship properties: {properties}.\n"
        f"Relationship types: {relationships}."
    )
