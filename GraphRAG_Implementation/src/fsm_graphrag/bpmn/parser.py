"""Small, deterministic BPMN 2.0 XML parser using only the Python standard library."""

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

from .model import (
    BpmnAssociation,
    BpmnDocument,
    BpmnLane,
    BpmnMessageFlow,
    BpmnNode,
    BpmnParticipant,
    BpmnProcess,
    BpmnTextAnnotation,
    DataArtifact,
    DataAssociation,
    SequenceFlow,
)


class BpmnParseError(ValueError):
    """Raised when input is not a well-formed BPMN 2.0 definitions document."""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def _text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    value = " ".join("".join(element.itertext()).split())
    return value or None


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if _local_name(child.tag) == name]


def _category(kind: str) -> str | None:
    if kind.endswith("Gateway"):
        return "gateway"
    if kind.endswith("Event"):
        return "event"
    if (
        kind == "task"
        or kind.endswith(("Task", "Activity"))
        or kind
        in {
            "subProcess",
            "transaction",
            "callActivity",
        }
    ):
        return "activity"
    return None


def parse_bpmn_xml(xml: str | bytes, source_name: str = "<memory>") -> BpmnDocument:
    """Parse BPMN flow nodes, sequence flows, lanes, participants, and data refs.

    Parsing preserves source IDs and text verbatim after XML whitespace
    normalization. Structural/reference checks are delegated to validate_bpmn.
    """
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise BpmnParseError(f"Invalid XML in {source_name}: {exc}") from exc

    namespace = root.tag[1:].split("}", maxsplit=1)[0] if root.tag.startswith("{") else ""
    if _local_name(root.tag) != "definitions" or not namespace.endswith("/MODEL"):
        raise BpmnParseError(f"{source_name} is not a BPMN 2.0 definitions document")

    process_elements = _children(root, "process")
    processes: list[BpmnProcess] = []
    nodes: list[BpmnNode] = []
    flows: list[SequenceFlow] = []
    lanes: list[BpmnLane] = []
    artifacts: list[DataArtifact] = []
    associations: list[DataAssociation] = []

    for process in process_elements:
        process_id = process.get("id", "")
        executable = process.get("isExecutable")
        processes.append(
            BpmnProcess(
                id=process_id,
                name=process.get("name"),
                is_executable=None if executable is None else executable.lower() == "true",
            )
        )

        process_lanes: list[tuple[str, str | None, tuple[str, ...], str | None]] = []
        for lane_set in (item for item in process.iter() if _local_name(item.tag) == "laneSet"):
            for lane in _children(lane_set, "lane"):
                lane_id = lane.get("id", "")
                refs = tuple(
                    ref
                    for ref in (_text(item) for item in _children(lane, "flowNodeRef"))
                    if ref is not None
                )
                parent = next((p for p in process.iter() if lane in list(p)), None)
                parent_lane_id = (
                    parent.get("id")
                    if parent is not None and _local_name(parent.tag) == "lane"
                    else None
                )
                process_lanes.append((lane_id, lane.get("name"), refs, parent_lane_id))
                lanes.append(BpmnLane(lane_id, lane.get("name"), process_id, refs, parent_lane_id))

        parent_by_element = {child: parent for parent in process.iter() for child in parent}
        for item in process.iter():
            kind = _local_name(item.tag)
            category = _category(kind)
            item_id = item.get("id")
            if category and item_id:
                assigned_lanes = tuple(
                    lane_id for lane_id, _, refs, _ in process_lanes if item_id in refs
                )
                documentation = _text(next(iter(_children(item, "documentation")), None))
                nodes.append(
                    BpmnNode(
                        id=item_id,
                        kind=kind,
                        category=category,
                        name=item.get("name"),
                        process_id=process_id,
                        lane_ids=assigned_lanes,
                        default_flow_id=item.get("default"),
                        documentation=documentation,
                        attached_to_ref=item.get("attachedToRef"),
                    )
                )
            elif (
                kind
                in {
                    "dataObject",
                    "dataObjectReference",
                    "dataInput",
                    "dataOutput",
                    "dataStoreReference",
                }
                and item_id
            ):
                artifacts.append(DataArtifact(item_id, kind, item.get("name")))

            if kind in {"dataInputAssociation", "dataOutputAssociation"}:
                source_refs = tuple(
                    ref
                    for ref in (_text(child) for child in _children(item, "sourceRef"))
                    if ref is not None
                )
                target_ref = _text(next(iter(_children(item, "targetRef")), None))
                associations.append(
                    DataAssociation(
                        id=item.get("id"),
                        source_refs=source_refs,
                        target_ref=target_ref,
                        direction="input" if kind == "dataInputAssociation" else "output",
                        activity_id=parent_by_element[item].get("id", "")
                        if item in parent_by_element
                        else "",
                        transformation=_text(next(iter(_children(item, "transformation")), None)),
                    )
                )

            if kind == "sequenceFlow" and item_id:
                condition_element = next(iter(_children(item, "conditionExpression")), None)
                condition = _text(condition_element)
                flows.append(
                    SequenceFlow(
                        id=item_id,
                        source_ref=item.get("sourceRef", ""),
                        target_ref=item.get("targetRef", ""),
                        process_id=process_id,
                        name=item.get("name"),
                        condition=condition,
                        expression_language=(
                            condition_element.get("language")
                            if condition_element is not None
                            else None
                        ),
                    )
                )

    default_flow_ids = {node.default_flow_id for node in nodes if node.default_flow_id}
    flows = [
        SequenceFlow(
            id=flow.id,
            source_ref=flow.source_ref,
            target_ref=flow.target_ref,
            process_id=flow.process_id,
            name=flow.name,
            condition=flow.condition,
            is_default=flow.id in default_flow_ids,
            expression_language=flow.expression_language,
        )
        for flow in flows
    ]

    participants = tuple(
        BpmnParticipant(
            id=item.get("id", ""), name=item.get("name"), process_ref=item.get("processRef")
        )
        for collaboration in (
            item for item in root.iter() if _local_name(item.tag) == "collaboration"
        )
        for item in _children(collaboration, "participant")
    )
    collaborations = [item for item in root.iter() if _local_name(item.tag) == "collaboration"]
    message_flows = tuple(
        BpmnMessageFlow(
            item.get("id", ""),
            item.get("sourceRef", ""),
            item.get("targetRef", ""),
            item.get("name"),
        )
        for collaboration in collaborations
        for item in _children(collaboration, "messageFlow")
    )
    annotations = tuple(
        BpmnTextAnnotation(item.get("id", ""), _text(next(iter(_children(item, "text")), None)))
        for item in root.iter()
        if _local_name(item.tag) == "textAnnotation"
    )
    structural_associations = tuple(
        BpmnAssociation(
            item.get("id", ""),
            _text(next(iter(_children(item, "sourceRef")), None)) or "",
            _text(next(iter(_children(item, "targetRef")), None)) or "",
            item.get("associationDirection"),
        )
        for item in root.iter()
        if _local_name(item.tag) == "association"
    )

    recognized = {
        "definitions",
        "process",
        "laneSet",
        "lane",
        "flowNodeRef",
        "documentation",
        "incoming",
        "outgoing",
        "startEvent",
        "endEvent",
        "intermediateCatchEvent",
        "intermediateThrowEvent",
        "boundaryEvent",
        "sequenceFlow",
        "messageFlow",
        "attachedToRef",
        "conditionExpression",
        "exclusiveGateway",
        "inclusiveGateway",
        "parallelGateway",
        "eventBasedGateway",
        "complexGateway",
        "task",
        "userTask",
        "serviceTask",
        "manualTask",
        "scriptTask",
        "businessRuleTask",
        "sendTask",
        "receiveTask",
        "subProcess",
        "transaction",
        "callActivity",
        "dataObject",
        "dataObjectReference",
        "dataInput",
        "dataOutput",
        "dataStoreReference",
        "dataInputAssociation",
        "dataOutputAssociation",
        "sourceRef",
        "targetRef",
        "transformation",
        "collaboration",
        "participant",
        "textAnnotation",
        "text",
        "association",
        "extensionElements",
        # BPMN DI supplies layout only; it is intentionally not a graph node.
        "BPMNDiagram",
        "BPMNPlane",
        "BPMNShape",
        "BPMNEdge",
        "BPMNLabel",
        "Bounds",
        "waypoint",
        # IO specification wrappers are represented by DataAssociation records.
        "ioSpecification",
        "dataInputs",
        "dataOutputs",
        "inputSet",
        "inputSets",
        "outputSet",
        "outputSets",
        "dataInputRefs",
        "dataOutputRefs",
    }
    unsupported = tuple(
        sorted(
            {
                _local_name(item.tag)
                for item in root.iter()
                if _local_name(item.tag) not in recognized
            }
        )
    )

    return BpmnDocument(
        source_name=source_name,
        target_namespace=root.get("targetNamespace"),
        processes=tuple(processes),
        nodes=tuple(nodes),
        sequence_flows=tuple(flows),
        lanes=tuple(lanes),
        participants=participants,
        message_flows=message_flows,
        text_annotations=annotations,
        associations=structural_associations,
        data_artifacts=tuple(artifacts),
        data_associations=tuple(associations),
        source_sha256=hashlib.sha256(xml.encode() if isinstance(xml, str) else xml).hexdigest(),
        unsupported_elements=unsupported,
    )


def parse_bpmn_file(path: str | Path) -> BpmnDocument:
    """Read and parse a BPMN XML file, retaining its path as provenance."""
    source = Path(path)
    try:
        content = source.read_bytes()
    except OSError as exc:
        raise BpmnParseError(f"Could not read BPMN file {source}: {exc}") from exc
    return parse_bpmn_xml(content, source_name=source.as_posix())
