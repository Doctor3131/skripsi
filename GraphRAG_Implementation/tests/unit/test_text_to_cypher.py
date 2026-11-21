import pytest

from fsm_graphrag.text_to_cypher import (
    CypherSafetyValidator,
    PipelineError,
)

SAFE_QUERY = (
    "MATCH (p:Process {sop_id: $sop_id, model_id: $model_id})-[:HAS_ELEMENT]->(a:Activity) "
    "RETURN a.bpmn_id AS bpmn_id LIMIT $maks_hasil"
)


def test_validator_accepts_scoped_read_query_and_sets_controlled_limit() -> None:
    safe = CypherSafetyValidator().validate(
        SAFE_QUERY,
        {"sop_id": "SOP-LAIN"},
        sop_id="FSM-SOP-CUTI-AKADEMIK",
        model_id="FSM-SOP-CUTI-AKADEMIK-BPMN-v2",
    )
    assert safe.parameters == {
        "sop_id": "FSM-SOP-CUTI-AKADEMIK",
        "model_id": "FSM-SOP-CUTI-AKADEMIK-BPMN-v2",
        "maks_hasil": 50,
    }


@pytest.mark.parametrize(
    "query",
    [
        "MATCH (n:Process) DELETE n RETURN n LIMIT $maks_hasil",
        "MATCH (n:Process) RETURN n LIMIT $maks_hasil; MATCH (x:Process) RETURN x",
        "MATCH (n:Process) RETURN n LIMIT 999",
        "MATCH (n:UnknownLabel) RETURN n LIMIT $maks_hasil",
        "MATCH (n:Process) RETURN apoc.doIt(n) LIMIT $maks_hasil",
        "MATCH (n:Process) WHERE EXISTS { MATCH (x:Activity) } RETURN n LIMIT $maks_hasil",
        "MATCH (n:Process) RETURN n.source_password LIMIT $maks_hasil",
        "MATCH (n:Process:$(label)) RETURN n LIMIT $maks_hasil",
        "MATCH (n:Process) RETURN n[$field] LIMIT $maks_hasil",
        "MATCH (n:Process) RETURN n LIMIT $maks_hasil // comment",
    ],
)
def test_validator_rejects_unsafe_or_out_of_schema_queries(query: str) -> None:
    with pytest.raises(PipelineError):
        CypherSafetyValidator().validate(query, {})


def test_validator_rejects_complex_or_unused_parameters() -> None:
    with pytest.raises(PipelineError, match="skalar"):
        CypherSafetyValidator().validate(
            SAFE_QUERY,
            {
                "sop_id": ["a", "b"],
                "model_id": "FSM-SOP-CUTI-AKADEMIK-BPMN-v2",
            },
        )
    with pytest.raises(PipelineError, match="tidak dipakai"):
        CypherSafetyValidator().validate(
            SAFE_QUERY,
            {
                "sop_id": "x",
                "model_id": "FSM-SOP-CUTI-AKADEMIK-BPMN-v2",
                "other": "y",
            },
        )
