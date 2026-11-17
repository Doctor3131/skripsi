"""Proyeksi deterministik tanpa ingest menggunakan skema v0.1 yang disetujui."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import PurePath

from .model import BpmnDocument
from .validator import validate_bpmn


@dataclass(frozen=True)
class ProposedGraphNode:
    label: str
    properties: dict[str, object]


@dataclass(frozen=True)
class ProposedGraphRelationship:
    type: str
    source_id: str
    target_id: str
    properties: dict[str, object]


@dataclass(frozen=True)
class GraphMappingDraft:
    schema_status: str
    nodes: tuple[ProposedGraphNode, ...]
    relationships: tuple[ProposedGraphRelationship, ...]
    unsupported_elements: tuple[str, ...] = ()


def _key(sop_id: str, model_id: str, element_id: str) -> str:
    raw = json.dumps([sop_id, model_id, element_id], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def map_bpmn_to_graph(document: BpmnDocument, *, sop_id: str, model_id: str) -> GraphMappingDraft:
    """Project into a draft graph; identity inputs are mandatory."""
    if not sop_id.strip() or not model_id.strip():
        raise ValueError("sop_id and model_id must be non-empty explicit identifiers")
    errors = [issue for issue in validate_bpmn(document) if issue.severity == "error"]
    if errors:
        raise ValueError(
            "Cannot map invalid BPMN document: " + "; ".join(i.message for i in errors)
        )
    provenance = {
        "sop_id": sop_id,
        "model_id": model_id,
        "source_file_id": PurePath(document.source_name).name,
        "source_sha256": document.source_sha256,
    }

    def keys(raw_id: str) -> str:
        return _key(sop_id, model_id, raw_id)

    nodes: list[ProposedGraphNode] = []
    rels: list[ProposedGraphRelationship] = []
    flow_nodes = {n.id: n for n in document.nodes}
    artifacts = {a.id: a for a in document.data_artifacts}

    for process in document.processes:
        nodes.append(
            ProposedGraphNode(
                "Process",
                {
                    "graph_id": keys(process.id),
                    "bpmn_id": process.id,
                    "name": process.name,
                    "is_executable": process.is_executable,
                    "bpmn_kind": "process",
                    **provenance,
                },
            )
        )
    for node in document.nodes:
        label = {"activity": "Activity", "event": "Event", "gateway": "Gateway"}[node.category]
        nodes.append(
            ProposedGraphNode(
                label,
                {
                    "graph_id": keys(node.id),
                    "bpmn_id": node.id,
                    "name": node.name,
                    "bpmn_kind": node.kind,
                    "documentation": node.documentation,
                    "process_bpmn_id": node.process_id,
                    "default_flow_bpmn_id": node.default_flow_id,
                    **provenance,
                },
            )
        )
        rels.append(
            ProposedGraphRelationship(
                "HAS_ELEMENT",
                keys(node.process_id),
                keys(node.id),
                {"bpmn_id": node.id, **provenance},
            )
        )
        for lane_id in node.lane_ids:
            rels.append(
                ProposedGraphRelationship(
                    "IN_LANE", keys(node.id), keys(lane_id), {"lane_bpmn_id": lane_id, **provenance}
                )
            )
        if node.attached_to_ref:
            rels.append(
                ProposedGraphRelationship(
                    "ATTACHED_TO", keys(node.id), keys(node.attached_to_ref), provenance
                )
            )
    for lane in document.lanes:
        nodes.append(
            ProposedGraphNode(
                "Lane",
                {
                    "graph_id": keys(lane.id),
                    "bpmn_id": lane.id,
                    "name": lane.name,
                    "process_bpmn_id": lane.process_id,
                    "parent_lane_bpmn_id": lane.parent_lane_id,
                    **provenance,
                },
            )
        )
        if lane.parent_lane_id:
            rels.append(
                ProposedGraphRelationship(
                    "CONTAINS_LANE", keys(lane.parent_lane_id), keys(lane.id), provenance
                )
            )
        else:
            rels.append(
                ProposedGraphRelationship(
                    "HAS_LANE", keys(lane.process_id), keys(lane.id), provenance
                )
            )
    for artifact in document.data_artifacts:
        nodes.append(
            ProposedGraphNode(
                "DataElement",
                {
                    "graph_id": keys(artifact.id),
                    "bpmn_id": artifact.id,
                    "name": artifact.name,
                    "bpmn_kind": artifact.kind,
                    **provenance,
                },
            )
        )
    for participant in document.participants:
        nodes.append(
            ProposedGraphNode(
                "Participant",
                {
                    "graph_id": keys(participant.id),
                    "bpmn_id": participant.id,
                    "name": participant.name,
                    "process_bpmn_id": participant.process_ref,
                    **provenance,
                },
            )
        )
        if participant.process_ref:
            rels.append(
                ProposedGraphRelationship(
                    "REPRESENTS_PROCESS",
                    keys(participant.id),
                    keys(participant.process_ref),
                    provenance,
                )
            )
    for flow in document.message_flows:
        rels.append(
            ProposedGraphRelationship(
                "MESSAGE_FLOWS_TO",
                keys(flow.source_ref),
                keys(flow.target_ref),
                {
                    "graph_id": keys(flow.id),
                    "bpmn_id": flow.id,
                    "source_bpmn_id": flow.source_ref,
                    "target_bpmn_id": flow.target_ref,
                    "name": flow.name,
                    **provenance,
                },
            )
        )
    for annotation in document.text_annotations:
        nodes.append(
            ProposedGraphNode(
                "TextAnnotation",
                {
                    "graph_id": keys(annotation.id),
                    "bpmn_id": annotation.id,
                    "text": annotation.text,
                    **provenance,
                },
            )
        )
    for association in document.associations:
        rels.append(
            ProposedGraphRelationship(
                "ANNOTATES",
                keys(association.source_ref),
                keys(association.target_ref),
                {
                    "graph_id": keys(association.id),
                    "bpmn_id": association.id,
                    "association_direction": association.direction,
                    **provenance,
                },
            )
        )
    for flow in document.sequence_flows:
        rels.append(
            ProposedGraphRelationship(
                "FLOWS_TO",
                keys(flow.source_ref),
                keys(flow.target_ref),
                {
                    "graph_id": keys(flow.id),
                    "bpmn_id": flow.id,
                    "source_bpmn_id": flow.source_ref,
                    "target_bpmn_id": flow.target_ref,
                    "name": flow.name,
                    "condition": flow.condition,
                    "expression_language": flow.expression_language,
                    "is_default": flow.is_default,
                    **provenance,
                },
            )
        )
    for association in document.data_associations:
        association_key = keys(
            association.id or f"association:{association.activity_id}:{association.direction}"
        )
        nodes.append(
            ProposedGraphNode(
                "DataAssociation",
                {
                    "graph_id": association_key,
                    "bpmn_id": association.id,
                    "direction": association.direction,
                    "owner_bpmn_id": association.activity_id,
                    "transformation": association.transformation,
                    **provenance,
                },
            )
        )
        owner_key = keys(association.activity_id)
        rels.append(
            ProposedGraphRelationship(
                "HAS_DATA_ASSOCIATION", owner_key, association_key, provenance
            )
        )
        for ref in association.source_refs:
            if ref in artifacts or ref in flow_nodes:
                rels.append(
                    ProposedGraphRelationship(
                        "HAS_SOURCE",
                        association_key,
                        keys(ref),
                        {"source_bpmn_id": ref, **provenance},
                    )
                )
        if association.target_ref and (
            association.target_ref in artifacts or association.target_ref in flow_nodes
        ):
            rels.append(
                ProposedGraphRelationship(
                    "HAS_TARGET",
                    association_key,
                    keys(association.target_ref),
                    {"target_bpmn_id": association.target_ref, **provenance},
                )
            )
    return GraphMappingDraft(
        "approved_v0.1_draft_projection",
        tuple(nodes),
        tuple(rels),
        document.unsupported_elements,
    )
