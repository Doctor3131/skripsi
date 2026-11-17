"""Immutable intermediate data structures for parsed BPMN 2.0 XML."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BpmnProcess:
    id: str
    name: str | None
    is_executable: bool | None


@dataclass(frozen=True)
class BpmnNode:
    id: str
    kind: str
    category: str
    name: str | None
    process_id: str
    lane_ids: tuple[str, ...] = ()
    default_flow_id: str | None = None
    documentation: str | None = None
    attached_to_ref: str | None = None


@dataclass(frozen=True)
class SequenceFlow:
    id: str
    source_ref: str
    target_ref: str
    process_id: str
    name: str | None = None
    condition: str | None = None
    is_default: bool = False
    expression_language: str | None = None


@dataclass(frozen=True)
class BpmnLane:
    id: str
    name: str | None
    process_id: str
    flow_node_refs: tuple[str, ...]
    parent_lane_id: str | None = None


@dataclass(frozen=True)
class BpmnParticipant:
    id: str
    name: str | None
    process_ref: str | None


@dataclass(frozen=True)
class BpmnMessageFlow:
    id: str
    source_ref: str
    target_ref: str
    name: str | None = None


@dataclass(frozen=True)
class BpmnTextAnnotation:
    id: str
    text: str | None


@dataclass(frozen=True)
class BpmnAssociation:
    id: str
    source_ref: str
    target_ref: str
    direction: str | None = None


@dataclass(frozen=True)
class DataArtifact:
    id: str
    kind: str
    name: str | None


@dataclass(frozen=True)
class DataAssociation:
    id: str | None
    source_refs: tuple[str, ...]
    target_ref: str | None
    direction: str
    activity_id: str
    transformation: str | None = None


@dataclass(frozen=True)
class BpmnDocument:
    source_name: str
    target_namespace: str | None
    processes: tuple[BpmnProcess, ...]
    nodes: tuple[BpmnNode, ...]
    sequence_flows: tuple[SequenceFlow, ...]
    lanes: tuple[BpmnLane, ...]
    participants: tuple[BpmnParticipant, ...]
    data_artifacts: tuple[DataArtifact, ...]
    data_associations: tuple[DataAssociation, ...]
    source_sha256: str = ""
    unsupported_elements: tuple[str, ...] = ()
    message_flows: tuple[BpmnMessageFlow, ...] = ()
    text_annotations: tuple[BpmnTextAnnotation, ...] = ()
    associations: tuple[BpmnAssociation, ...] = ()
