import json
from types import SimpleNamespace

import pytest
from neo4j import GraphDatabase, Record, RoutingControl
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.llm.types import LLMResponse, LLMUsage

from fsm_graphrag.config import Settings
from fsm_graphrag.graphrag_pipeline import (
    GraphRAGService,
    create_neo4j_driver,
    format_evidence_record,
)
from fsm_graphrag.text_to_cypher import PipelineError, QuestionRequest

SOP_ID = "FSM-SOP-CUTI-AKADEMIK"
MODEL_ID = "FSM-SOP-CUTI-AKADEMIK-BPMN-v1"
QUERY = (
    "MATCH (p:Process {sop_id: $sop_id, model_id: $model_id})-[:HAS_ELEMENT]->(a:Activity) "
    "RETURN p.sop_id AS sop_id, p.model_id AS model_id, a.bpmn_id AS bpmn_id, "
    "a.name AS nama, a.source_file_id AS source_file_id, "
    "a.source_sha256 AS source_sha256 LIMIT $maks_hasil"
)
ROW = {
    "sop_id": SOP_ID,
    "model_id": MODEL_ID,
    "bpmn_id": "Task_1",
    "nama": "Pemeriksaan berkas",
    "source_file_id": "pilot_sop_a.bpmn",
    "source_sha256": "a" * 64,
}


def make_settings(*, api_key: str | None = "test-key") -> Settings:
    return Settings(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="unused-secret",
        neo4j_database="neo4j",
        neo4j_query_timeout_seconds=5,
        log_level="INFO",
        llm_api_key=api_key,
        llm_base_url="https://llm.example/v1",
        llm_model="model-uji",
        llm_temperature=0,
        llm_timeout_seconds=30,
    )


class FakeDriverResult:
    def __init__(self, rows, query_type="r"):
        self.rows = [Record(row.items()) for row in rows]
        self.query_type = query_type
        self.calls = []

    def execute_query(self, *, query_, parameters_, database_, routing_):
        self.calls.append((query_, parameters_, database_, routing_))
        if query_.text.startswith("EXPLAIN "):
            return [], SimpleNamespace(query_type=self.query_type), None
        return self.rows, SimpleNamespace(query_type="r"), None


class FakeOpenAILLM(OpenAILLM):
    instances = []
    answer_content = None
    generated_query = QUERY
    generated_parameters = {"sop_id": SOP_ID, "model_id": MODEL_ID}

    def __init__(self, *, stage, trace, **kwargs):
        self.stage = stage
        self.trace = trace
        self.options = kwargs
        self.calls = []
        self.instances.append(self)

    def invoke(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        self.trace.latensi_ms[self.stage] = 1.0
        self.trace.token_usage[f"{self.stage}_input"] = 11
        self.trace.token_usage[f"{self.stage}_output"] = 5
        self.trace.estimated_cost[self.stage] = None
        if self.stage == "text_to_cypher":
            content = json.dumps(
                {"cypher": self.generated_query, "parameters": self.generated_parameters}
            )
        elif self.answer_content is not None:
            content = self.answer_content
        else:
            evidence_id = format_evidence_record(ROW).metadata["evidence_id"]
            content = json.dumps(
                {
                    "answer": "Berkas diperiksa pada aktivitas yang tercatat.",
                    "evidence_ids": [evidence_id],
                    "abstain": False,
                }
            )
        return LLMResponse(content=content, usage=LLMUsage(request_tokens=11, response_tokens=5))


@pytest.fixture
def driver_with_rows(monkeypatch):
    stub = FakeDriverResult([ROW])
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "unused-secret"))
    monkeypatch.setattr(driver, "execute_query", stub.execute_query)
    yield driver, stub
    driver.close()


def make_service(driver, monkeypatch, *, api_key="test-key"):
    FakeOpenAILLM.instances = []
    FakeOpenAILLM.answer_content = None
    FakeOpenAILLM.generated_query = QUERY
    FakeOpenAILLM.generated_parameters = {"sop_id": SOP_ID, "model_id": MODEL_ID}
    monkeypatch.setattr("fsm_graphrag.graphrag_pipeline.TracedOpenAILLM", FakeOpenAILLM)
    return GraphRAGService(driver=driver, settings=make_settings(api_key=api_key))


def test_graphrag_returns_grounded_answer_and_executes_bounded_read_query(
    driver_with_rows, monkeypatch
):
    driver, stub = driver_with_rows
    service = make_service(driver, monkeypatch)

    response = service.answer(
        QuestionRequest("Apa yang diperiksa?", sop_id=SOP_ID, model_id=MODEL_ID),
        request_id="uji-graphrag-1",
    )

    assert response.abstain is False
    assert response.evidence[0].data["bpmn_id"] == "Task_1"
    assert response.trace.query_validation == "LOLOS_ALLOWLIST_DAN_PARAMETER"
    assert response.trace.query_execution == "BERHASIL"
    assert response.trace.token_usage["jawaban_input"] == 11
    assert len(stub.calls) == 2
    assert stub.calls[0][0].text == f"EXPLAIN {QUERY}"
    assert stub.calls[1][0].text == QUERY
    assert all(call[0].timeout == 5 for call in stub.calls)
    assert all(call[2] == "neo4j" and call[3] == RoutingControl.READ for call in stub.calls)
    assert stub.calls[1][1]["maks_hasil"] == 50


def test_unsafe_query_is_rejected_before_database_execution(driver_with_rows, monkeypatch):
    driver, stub = driver_with_rows
    service = make_service(driver, monkeypatch)
    FakeOpenAILLM.generated_query = "MATCH (n:Process) DETACH DELETE n RETURN n LIMIT $maks_hasil"
    FakeOpenAILLM.generated_parameters = {}

    with pytest.raises(PipelineError, match="terlarang"):
        service.answer(QuestionRequest("Hapus proses"), request_id="uji-graphrag-2")
    assert stub.calls == []


def test_non_read_only_explain_result_is_never_executed(driver_with_rows, monkeypatch):
    driver, stub = driver_with_rows
    stub.query_type = "w"
    service = make_service(driver, monkeypatch)

    with pytest.raises(PipelineError, match="read-only"):
        service.answer(QuestionRequest("Tampilkan proses"), request_id="uji-graphrag-3")
    assert len(stub.calls) == 1
    assert stub.calls[0][0].text.startswith("EXPLAIN ")


def test_empty_result_abstains_without_calling_answer_llm(driver_with_rows, monkeypatch):
    driver, stub = driver_with_rows
    stub.rows = []
    service = make_service(driver, monkeypatch)

    response = service.answer(QuestionRequest("Di luar SOP"), request_id="uji-graphrag-4")

    answer_llm = next(item for item in FakeOpenAILLM.instances if item.stage == "jawaban")
    assert response.abstain is True
    assert response.evidence == ()
    assert response.trace.error_category == "ABSTAIN_EMPTY_EVIDENCE"
    assert answer_llm.calls == []


def test_incomplete_provenance_abstains_before_answer_generation(driver_with_rows, monkeypatch):
    driver, stub = driver_with_rows
    row = {"bpmn_id": "Task_1", "sop_id": SOP_ID, "model_id": MODEL_ID}
    stub.rows = [Record(row.items())]
    service = make_service(driver, monkeypatch)

    response = service.answer(QuestionRequest("Apa aktivitasnya?"), request_id="uji-graphrag-5")

    answer_llm = next(item for item in FakeOpenAILLM.instances if item.stage == "jawaban")
    assert response.abstain is True
    assert response.trace.error_category == "EVIDENCE_PROVENANCE_INCOMPLETE"
    assert answer_llm.calls == []


def test_invalid_evidence_citation_is_rejected(driver_with_rows, monkeypatch):
    driver, _ = driver_with_rows
    service = make_service(driver, monkeypatch)
    FakeOpenAILLM.answer_content = json.dumps(
        {"answer": "Tidak berdasar.", "evidence_ids": ["E-salah"], "abstain": False}
    )

    with pytest.raises(PipelineError, match="referensi evidence"):
        service.answer(QuestionRequest("Apa aktivitasnya?"), request_id="uji-graphrag-6")


def test_missing_api_key_fails_before_provider_client_creation(driver_with_rows, monkeypatch):
    driver, _ = driver_with_rows
    service = make_service(driver, monkeypatch, api_key=None)

    with pytest.raises(PipelineError, match="LLM_API_KEY"):
        service.answer(QuestionRequest("Apa aktivitasnya?"), request_id="uji-graphrag-7")
    assert FakeOpenAILLM.instances == []


def test_neo4j_driver_uses_compose_credentials(monkeypatch):
    settings = make_settings()
    captured = {}

    def fake_driver(uri, *, auth):
        captured["uri"] = uri
        captured["auth"] = auth
        return object()

    monkeypatch.setattr("fsm_graphrag.graphrag_pipeline.GraphDatabase.driver", fake_driver)

    driver = create_neo4j_driver(settings)

    assert driver is not None
    assert captured == {
        "uri": settings.neo4j_uri,
        "auth": (settings.neo4j_user, settings.neo4j_password),
    }


def test_evidence_formatter_keeps_provenance_and_stable_id():
    first = format_evidence_record(ROW)
    second = format_evidence_record(ROW)

    assert first.metadata["evidence_id"] == second.metadata["evidence_id"]
    assert json.loads(first.content)["data"]["source_sha256"] == "a" * 64
