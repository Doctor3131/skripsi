"""Reference and identifier validation for parsed BPMN documents."""

from dataclasses import dataclass

from .model import BpmnDocument


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    source_id: str | None = None


def validate_bpmn(document: BpmnDocument) -> tuple[ValidationIssue, ...]:
    """Return deterministic structural/reference issues without repairing input."""
    issues: list[ValidationIssue] = []
    entities = [
        *document.processes,
        *document.nodes,
        *document.sequence_flows,
        *document.lanes,
        *document.participants,
        *document.data_artifacts,
    ]
    ids: set[str] = set()
    for entity in entities:
        if not entity.id:
            issues.append(ValidationIssue("missing_id", "BPMN element has no id"))
        elif entity.id in ids:
            issues.append(
                ValidationIssue(
                    "duplicate_id", f"Duplicate BPMN id: {entity.id}", source_id=entity.id
                )
            )
        ids.add(entity.id)

    for association in document.data_associations:
        if association.id:
            if association.id in ids:
                issues.append(
                    ValidationIssue(
                        "duplicate_id",
                        f"Duplicate BPMN id: {association.id}",
                        source_id=association.id,
                    )
                )
            ids.add(association.id)

    process_ids = {process.id for process in document.processes}
    node_by_id = {node.id: node for node in document.nodes}
    flow_by_id = {flow.id: flow for flow in document.sequence_flows}
    artifact_ids = {artifact.id for artifact in document.data_artifacts}

    if not document.processes:
        issues.append(ValidationIssue("no_process", "BPMN document contains no process"))

    for node in document.nodes:
        if node.process_id not in process_ids:
            issues.append(
                ValidationIssue(
                    "unknown_process",
                    f"Unknown process reference: {node.process_id}",
                    source_id=node.id,
                )
            )
        if node.default_flow_id:
            default_flow = flow_by_id.get(node.default_flow_id)
            if default_flow is None:
                issues.append(
                    ValidationIssue(
                        "unknown_default_flow",
                        f"Default flow {node.default_flow_id} does not exist",
                        source_id=node.id,
                    )
                )
            elif default_flow.source_ref != node.id:
                issues.append(
                    ValidationIssue(
                        "invalid_default_flow",
                        f"Default flow {node.default_flow_id} does not leave {node.id}",
                        source_id=node.id,
                    )
                )

    for flow in document.sequence_flows:
        for ref_name, ref in (("source", flow.source_ref), ("target", flow.target_ref)):
            if ref not in node_by_id:
                issues.append(
                    ValidationIssue(
                        "unknown_flow_node",
                        f"Sequence flow {flow.id} has unknown {ref_name} reference: {ref}",
                        source_id=flow.id,
                    )
                )
        if flow.process_id not in process_ids:
            issues.append(
                ValidationIssue(
                    "unknown_process",
                    f"Sequence flow {flow.id} belongs to unknown process {flow.process_id}",
                    source_id=flow.id,
                )
            )

    lane_ids = {lane.id for lane in document.lanes}
    for lane in document.lanes:
        for ref in lane.flow_node_refs:
            if ref not in node_by_id:
                issues.append(
                    ValidationIssue(
                        "unknown_lane_node",
                        f"Lane {lane.id} references unknown flow node {ref}",
                        source_id=lane.id,
                    )
                )
    for node in document.nodes:
        for lane_id in node.lane_ids:
            if lane_id not in lane_ids:
                issues.append(
                    ValidationIssue(
                        "unknown_lane",
                        f"Node {node.id} references unknown lane {lane_id}",
                        source_id=node.id,
                    )
                )

    for participant in document.participants:
        if participant.process_ref and participant.process_ref not in process_ids:
            issues.append(
                ValidationIssue(
                    "unknown_participant_process",
                    f"Participant {participant.id} references unknown process "
                    f"{participant.process_ref}",
                    source_id=participant.id,
                )
            )

    known_data_ids = artifact_ids | set(node_by_id)
    for association in document.data_associations:
        if not association.source_refs:
            issues.append(
                ValidationIssue(
                    "missing_data_source",
                    "Data association has no sourceRef",
                    source_id=association.id,
                )
            )
        if not association.target_ref:
            issues.append(
                ValidationIssue(
                    "missing_data_target",
                    "Data association has no targetRef",
                    source_id=association.id,
                )
            )
        refs = (
            *association.source_refs,
            *((association.target_ref,) if association.target_ref else ()),
            association.activity_id,
        )
        for ref in refs:
            if ref not in known_data_ids:
                issues.append(
                    ValidationIssue(
                        "unknown_data_reference",
                        f"Data association references unknown element {ref}",
                        source_id=ref,
                    )
                )

    return tuple(issues)
