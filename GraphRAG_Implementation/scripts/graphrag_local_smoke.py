"""Uji GraphRAG retriever lokal dengan Cypher tetap; tidak memanggil layanan LLM."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from neo4j import GraphDatabase
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.llm.types import LLMResponse

from fsm_graphrag.config import load_settings
from fsm_graphrag.graphrag_pipeline import (
    GuardedText2CypherRetriever,
    _graph_schema,
)
from fsm_graphrag.text_to_cypher import (
    APPROVED_MODELS,
    APPROVED_SOPS,
    PipelineTrace,
)

ROOT = Path(__file__).resolve().parents[1]
PROMPT = (ROOT / "prompts/neo4j_text_to_cypher_v1.md").read_text(encoding="utf-8")
QUERY = (
    "MATCH (p:Process {sop_id: $sop_id, model_id: $model_id}) "
    "-[:HAS_ELEMENT]->(a:Activity) "
    "RETURN p.sop_id AS sop_id, p.model_id AS model_id, a.bpmn_id AS bpmn_id, "
    "a.name AS nama, a.source_file_id AS source_file_id, "
    "a.source_sha256 AS source_sha256 LIMIT $maks_hasil"
)


def main() -> None:
    settings = load_settings()
    llm = OpenAILLM(
        model_name="offline-smoke-placeholder",
        api_key="not-used-for-this-smoke-check",
        base_url="http://127.0.0.1:1/v1",
        max_retries=0,
    )
    llm.invoke = lambda *args, **kwargs: LLMResponse(  # noqa: E731
        content=json.dumps(
            {"cypher": QUERY, "parameters": {}},
            ensure_ascii=False,
        )
    )
    outcomes = []
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        for sop_id, title in APPROVED_SOPS.items():
            trace = PipelineTrace(request_id=f"smoke-{sop_id}")
            retriever = GuardedText2CypherRetriever(
                driver=driver,
                llm=llm,
                schema=_graph_schema(),
                custom_prompt=PROMPT,
                examples=[],
                database=settings.neo4j_database,
                timeout_seconds=settings.neo4j_query_timeout_seconds,
                trace=trace,
            )
            result = retriever.search(
                query_text=f"Tampilkan aktivitas pada {title}.",
                sop_id=sop_id,
                model_id=APPROVED_MODELS[sop_id],
            )
            if not result.items:
                raise RuntimeError(f"Graph pilot tidak menghasilkan activity untuk {sop_id}.")
            if any(
                not item.metadata or not item.metadata.get("data", {}).get("source_sha256")
                for item in result.items
            ):
                raise RuntimeError(f"Evidence/provenance tidak lengkap untuk {sop_id}.")
            outcomes.append(
                {
                    "sop_id": sop_id,
                    "model_id": APPROVED_MODELS[sop_id],
                    "jumlah_evidence": len(result.items),
                    "evidence_ids": [item.metadata["evidence_id"] for item in result.items],
                    "query_validation": trace.query_validation,
                    "query_execution": trace.query_execution,
                }
            )

    report = {
        "status": "LULUS",
        "run_id": datetime.now(UTC).strftime("graphrag-smoke-%Y%m%dT%H%M%S%fZ"),
        "llm_api_dipanggil": False,
        "llm_object": "OpenAILLM dengan invoke diganti respons tetap",
        "database_access": (
            "akun Community tetap admin; query dibatasi guardrail aplikasi, EXPLAIN, "
            "dan routing READ"
        ),
        "hasil": outcomes,
    }
    output = ROOT / "results/m4/graphrag_local_smoke.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Smoke GraphRAG lokal lulus untuk {len(outcomes)} SOP; tanpa panggilan LLM.")


if __name__ == "__main__":
    main()
