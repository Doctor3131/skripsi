# BPMN-to-Graph Schema Proposal — v0.1

**STATUS: APPROVED BY RESEARCHER — 2026-11-16 (schema v0.1).**

## Scope

This is the researcher-approved v0.1 contract for a deterministic structural projection of BPMN 2.0 into a property graph. It has not been ingested into Neo4j and says nothing about GraphRAG performance. The available validation sources are synthetic fixtures; `data/bpmn/` has no SOP models at this revision. BPMN itself may omit procedural details present in SOP text or flowcharts.

## Structural and semantic boundary

**Layer A, in scope:** explicitly encoded BPMN elements, attributes, and structural references. No lane is presumed to be a person or role; no data element is presumed to be an administrative document or prerequisite. Graph reachability does not establish execution guarantees.

**Layer B, future proposal only:** roles, document meaning, requirements, business rules, SOP sections, and semantic links grounded in authoritative SOP evidence. Nothing in Layer B is generated here. Future integration could link reviewed semantic entities to Layer A through provenance-bearing mappings.

## Node labels

| Label | BPMN source | Required properties | Optional properties |
|---|---|---|---|
| `Process` | process | `graph_id`, `bpmn_id`, `bpmn_kind`, `sop_id`, `model_id`, source provenance | `name`, `is_executable` |
| `Activity` | tasks, subprocesses, transactions, call activities | identity/provenance, `bpmn_kind`, `process_bpmn_id` | `name`, `documentation` |
| `Event` | start/intermediate/end/boundary events | identity/provenance, `bpmn_kind`, `process_bpmn_id` | `name`, `documentation` |
| `Gateway` | exclusive/inclusive/parallel/event-based/complex gateways | identity/provenance, `bpmn_kind`, `process_bpmn_id` | `name`, `documentation` |
| `Lane` | BPMN lane | identity/provenance, `process_bpmn_id` | `name`, `parent_lane_bpmn_id` |
| `DataElement` | data object/reference, input/output, data-store reference | identity/provenance, `bpmn_kind` | `name` |
| `DataAssociation` | input/output association | identity/provenance, `direction`, `owner_bpmn_id` | `transformation` |
| `Participant` (additional) | collaboration participant/pool | identity/provenance | `name`, `process_bpmn_id` |
| `TextAnnotation` (additional) | BPMN text annotation | identity/provenance | `text` |

Keep BPMN subtype in `bpmn_kind`; do not create labels per subtype. `Participant` is an approved additional label for neutral collaboration structure.

## Relationships

| Type and direction | Meaning/properties |
|---|---|
| `HAS_ELEMENT`: Process → FlowNode | Structural process membership; source BPMN ID and provenance. |
| `FLOWS_TO`: FlowNode → FlowNode | Sequence flow; `graph_id`, `bpmn_id`, source/target BPMN IDs, name, condition, expression language, default flag, provenance. No inferred execution semantics. |
| `HAS_LANE`: Process → Lane | Top-level lane membership. |
| `CONTAINS_LANE`: parent Lane → nested Lane | Nested lane structure. |
| `IN_LANE`: FlowNode → Lane | Explicit `flowNodeRef` membership; not actor assignment. |
| `HAS_DATA_ASSOCIATION`: owning FlowNode → DataAssociation | Association ownership and direction. |
| `HAS_SOURCE`: DataAssociation → source DataElement/FlowNode | One edge per source ref; keeps association direction explicit. |
| `HAS_TARGET`: DataAssociation → target DataElement/FlowNode | Target reference. |
| `REPRESENTS_PROCESS`: Participant → Process | Explicit participant `processRef`; participant remains semantically neutral. |
| `MESSAGE_FLOWS_TO`: Participant → Participant | Explicit collaboration message flow, separate from sequence flow. |
| `ATTACHED_TO`: boundary Event → FlowNode | Explicit `attachedToRef`; no exception behavior is inferred. |
| `ANNOTATES`: source → target | Explicit BPMN association to/from a `TextAnnotation`; direction attribute preserved. |

Do not substitute `REQUIRES` or `PRODUCES`. Multiple `HAS_SOURCE` edges and one/multiple target references preserve association structure; transformation expression remains an attribute. The current IR represents one target per association; multiple-target BPMN encodings need explicit support before projection.

## Identity and provenance

`graph_id = SHA-256(JSON([sop_id, model_id, original_bpmn_id]))`, with compact UTF-8 JSON and stable ordered fields. `sop_id` follows the approved source inventory; `model_id` is an explicit PI-approved BPMN model version. Both are mandatory mapper inputs; there is no implicit fallback. A revised BPMN model receives a new `model_id`; preserve prior versions for provenance. Preserve `bpmn_id` separately. Relationship identity uses the same key rule with the original sequence-flow or association ID.

`model_id` should be a PI-assigned stable model identifier/version, not a path or file order. `source_file_id` is a stable logical source name; `source_sha256` fingerprints the exact input bytes. A content change creates a new provenance version; it does not mutate the meaning of an existing identity. Reprocessing identical SOP/model/element tuples is deterministic. Distinct SOP or model IDs prevent ordinary cross-document BPMN ID collisions; duplicate element IDs inside one model are validation errors. File paths are diagnostic only and excluded from graph identity.

## Contract and invariants

See [`bpmn_graph_schema_contract.md`](bpmn_graph_schema_contract.md) for the normative proposal-level mapping contract. Projection rejects structural validation errors, preserves original subtype and references, emits no inferred semantic predicates, and returns a deterministic sorted unsupported-element report. It is a pure in-memory draft function, not an ingestion interface.

## Coverage and limitations

The synthetic fixture covers process, start/end events, user tasks, exclusive gateway, conditions/default branch, lane, participant, data input/output, data object references, and associations. It does not establish FSM SOP coverage. Additional structural projections now support participant/processRef, message flow, text annotations and BPMN associations, boundary-event attachment, and data-store references when encountered. These are only structural encodings; they do not infer roles, business rules, or data semantics. Nested lane parentage is retained by the IR. Unsupported tag reporting is deterministic but not equivalent to XSD validation. Multi-source data associations are represented; multi-target forms are not yet supported. The parser is not a full BPMN 2.0 conformance validator.

## Example from synthetic fixture (not SOP evidence)

`Gateway_Approved` is a `Gateway` with `bpmn_kind="exclusiveGateway"`; `Flow_Approved` preserves condition text `approved = true`; `Flow_Rejected` is flagged default because the gateway declares that flow ID. `Task_Review` is in `Lane_Office` via `IN_LANE`. `InputAssociation_Form` is a `DataAssociation` node connected to its source and target via `HAS_SOURCE`/`HAS_TARGET`. No role, mandatory-document, or outcome semantics are added.

## Approval and remaining implementation boundaries

The researcher approved the v0.1 schema, identity policy, and additional structural mappings on 2026-11-16. This approves the proposed structural contract; it does not claim full BPMN 2.0 coverage or validate the mapping against real FSM SOPs. The current single-target data-association IR limitation remains explicit. Source-grounded coverage checks and any implementation gaps found against the two approved pilot BPMNs remain prerequisites for ingestion.
