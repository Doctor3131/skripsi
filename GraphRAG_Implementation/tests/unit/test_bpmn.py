from dataclasses import replace
from pathlib import Path

import pytest

from fsm_graphrag.bpmn import (
    BpmnParseError,
    map_bpmn_to_graph,
    parse_bpmn_file,
    parse_bpmn_xml,
    validate_bpmn,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "synthetic_gateway.bpmn"


def test_parser_preserves_flow_conditions_lanes_and_data_refs() -> None:
    document = parse_bpmn_file(FIXTURE)

    assert document.source_name.endswith("synthetic_gateway.bpmn")
    assert [process.id for process in document.processes] == ["Process_Pilot"]
    assert document.nodes[1].id == "Task_Review"
    assert document.nodes[1].lane_ids == ("Lane_Office",)
    assert document.nodes[1].documentation == "Synthetic fixture only."

    approved = next(flow for flow in document.sequence_flows if flow.id == "Flow_Approved")
    rejected = next(flow for flow in document.sequence_flows if flow.id == "Flow_Rejected")
    assert approved.condition == "approved = true"
    assert not approved.is_default
    assert rejected.is_default
    assert rejected.source_ref == "Gateway_Approved"

    assert document.participants[0].process_ref == "Process_Pilot"
    assert any(
        node.label == "Participant"
        for node in map_bpmn_to_graph(
            document, sop_id="SYNTHETIC-PILOT", model_id="synthetic-v1"
        ).nodes
    )
    assert {artifact.id for artifact in document.data_artifacts} == {
        "ReviewFormInput",
        "ReceiptOutput",
        "RequestForm",
        "ApprovalReceipt",
    }
    assert document.data_associations[0].activity_id == "Task_Review"
    assert document.data_associations[0].id == "InputAssociation_Form"
    assert document.data_associations[0].source_refs == ("RequestForm",)


def test_validator_accepts_fixture_and_reports_unknown_flow_target() -> None:
    document = parse_bpmn_file(FIXTURE)
    assert validate_bpmn(document) == ()

    invalid_flow = replace(document.sequence_flows[0], target_ref="MissingTask")
    invalid_document = replace(
        document, sequence_flows=(invalid_flow, *document.sequence_flows[1:])
    )
    issues = validate_bpmn(invalid_document)

    assert any(issue.code == "unknown_flow_node" for issue in issues)
    assert any("MissingTask" in issue.message for issue in issues)


def test_mapping_is_deterministic_and_keeps_branch_provenance() -> None:
    document = parse_bpmn_file(FIXTURE)

    first = map_bpmn_to_graph(document, sop_id="SYNTHETIC-PILOT", model_id="synthetic-v1")
    second = map_bpmn_to_graph(document, sop_id="SYNTHETIC-PILOT", model_id="synthetic-v1")

    assert first == second
    assert first.schema_status == "approved_v0.1_draft_projection"
    gateway = next(node for node in first.nodes if node.properties["bpmn_id"] == "Gateway_Approved")
    assert gateway.label == "Gateway"
    assert gateway.properties["default_flow_bpmn_id"] == "Flow_Rejected"
    branch = next(
        relationship
        for relationship in first.relationships
        if relationship.properties.get("bpmn_id") == "Flow_Approved"
    )
    assert branch.type == "FLOWS_TO"
    assert branch.properties["condition"] == "approved = true"
    assert branch.properties["bpmn_id"] == "Flow_Approved"
    assert branch.properties["source_file_id"].endswith("synthetic_gateway.bpmn")
    assert any(
        relationship.type == "HAS_SOURCE"
        and relationship.target_id != ""
        and relationship.properties["source_bpmn_id"] == "RequestForm"
        for relationship in first.relationships
    )
    assert any(
        relationship.type == "HAS_TARGET"
        and relationship.properties["target_bpmn_id"] == "ApprovalReceipt"
        for relationship in first.relationships
    )
    assert {node.label for node in first.nodes}.isdisjoint({"Actor", "Document"})
    assert all(
        rel.type not in {"REQUIRES", "PRODUCES", "PERFORMED_BY"} for rel in first.relationships
    )
    assert any(rel.type == "IN_LANE" for rel in first.relationships)
    assert all(node.properties["source_sha256"] for node in first.nodes)


def test_composite_identity_is_stable_and_separates_models() -> None:
    document = parse_bpmn_file(FIXTURE)
    first = map_bpmn_to_graph(document, sop_id="SOP-A", model_id="model-v1")
    repeated = map_bpmn_to_graph(document, sop_id="SOP-A", model_id="model-v1")
    other = map_bpmn_to_graph(document, sop_id="SOP-B", model_id="model-v1")
    assert first == repeated
    assert first.nodes[0].properties["graph_id"] != other.nodes[0].properties["graph_id"]
    assert first.nodes[0].properties["bpmn_id"] == other.nodes[0].properties["bpmn_id"]


def test_mapping_requires_explicit_identity_components() -> None:
    document = parse_bpmn_file(FIXTURE)
    with pytest.raises(TypeError):
        map_bpmn_to_graph(document)  # type: ignore[call-arg]
    with pytest.raises(ValueError, match="must be non-empty"):
        map_bpmn_to_graph(document, sop_id="SOP-X", model_id=" ")


def test_additional_collaboration_annotation_boundary_and_store_mapping() -> None:
    xml = """<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
      targetNamespace="urn:test">
      <process id="P"><task id="T"><boundaryEvent id="B" attachedToRef="T"/></task>
        <dataStoreReference id="DS" name="Store"/>
        <textAnnotation id="A"><text>Note</text></textAnnotation>
        <association id="AS" sourceRef="A" targetRef="T" associationDirection="One"/>
      </process>
      <collaboration id="C"><participant id="PA" processRef="P"/><participant id="PB"/>
        <messageFlow id="MF" sourceRef="PA" targetRef="PB"/>
      </collaboration>
    </definitions>"""
    document = parse_bpmn_xml(xml)
    graph = map_bpmn_to_graph(document, sop_id="SYNTHETIC-X", model_id="model-v1")
    assert any(
        n.label == "DataElement" and n.properties["bpmn_kind"] == "dataStoreReference"
        for n in graph.nodes
    )
    assert any(n.label == "TextAnnotation" and n.properties["text"] == "Note" for n in graph.nodes)
    assert any(r.type == "ATTACHED_TO" for r in graph.relationships)
    assert any(
        r.type == "MESSAGE_FLOWS_TO" and r.properties["bpmn_id"] == "MF"
        for r in graph.relationships
    )
    assert any(
        r.type == "ANNOTATES" and r.properties["association_direction"] == "One"
        for r in graph.relationships
    )


def test_mapping_rejects_invalid_documents() -> None:
    document = parse_bpmn_file(FIXTURE)
    invalid_flow = replace(document.sequence_flows[0], source_ref="MissingEvent")
    invalid_document = replace(
        document, sequence_flows=(invalid_flow, *document.sequence_flows[1:])
    )

    with pytest.raises(ValueError, match="Cannot map invalid BPMN"):
        map_bpmn_to_graph(invalid_document, sop_id="SYNTHETIC-PILOT", model_id="synthetic-v1")


def test_parser_rejects_malformed_xml_and_non_bpmn_root() -> None:
    with pytest.raises(BpmnParseError, match="Invalid XML"):
        parse_bpmn_xml("<definitions>")

    with pytest.raises(BpmnParseError, match="not a BPMN 2.0"):
        parse_bpmn_xml('<root xmlns="urn:example" />')


def test_parser_accepts_generic_task_without_actor_lane() -> None:
    xml = """<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
      <process id="P"><startEvent id="S"/><task id="T" name="Tugas tanpa pelaksana eksplisit"/>
        <endEvent id="E"/><sequenceFlow id="F1" sourceRef="S" targetRef="T"/>
        <sequenceFlow id="F2" sourceRef="T" targetRef="E"/></process></definitions>"""
    document = parse_bpmn_xml(xml)
    task = next(node for node in document.nodes if node.id == "T")
    assert task.kind == "task"
    assert task.category == "activity"
    assert task.lane_ids == ()
    assert validate_bpmn(document) == ()
