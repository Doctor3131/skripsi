# BPMN-to-Graph Schema Contract v0.1

**STATUS: APPROVED BY RESEARCHER — 2026-11-16 (schema v0.1).**

All identities use `SHA-256(compact JSON UTF-8 [sop_id, model_id, bpmn_id])`; retain the original ID as `bpmn_id`. `sop_id` must match the PI-approved source inventory, and `model_id` must be explicitly assigned as the PI-approved BPMN version. Both are mandatory nonempty mapper inputs. A revised BPMN receives a new `model_id`; retain the prior version. Provenance on every projected node and relationship: `sop_id`, `model_id`, logical `source_file_id`, exact-byte `source_sha256`. Do not use absolute path, traversal order, random ID, namespace fallback, or inferred SOP metadata as identity.

| Source | Projection | Required checks |
|---|---|---|
| process | `Process` | nonempty unique ID; `bpmn_kind=process`; preserve name/executable flag |
| task/subprocess/transaction/callActivity | `Activity` | retain exact local BPMN tag as `bpmn_kind`; `HAS_ELEMENT` from process |
| event | `Event` | retain exact tag and process membership |
| gateway | `Gateway` | retain exact tag, default flow reference on source node/flows |
| sequenceFlow | `FLOWS_TO` | endpoints exist as FlowNodes; preserve ID, refs, name, condition text, explicit expression language, default status |
| lane | `Lane` | retain IDs, lane name, process and parent lane; project process/nested lane links |
| flowNodeRef | `IN_LANE` | referenced FlowNode and Lane exist; preserve nested membership without actor semantics |
| data object/input/output/store reference | `DataElement` | retain source subtype; no document/prerequisite classification |
| data association | `DataAssociation` | preserve ID, direction, owner, sources, target, transformation; owner/source/target references resolve; no REQUIRES/PRODUCES |
| participant | `Participant` + optional `REPRESENTS_PROCESS` | preserve ID and explicit processRef; no actor/role inference |
| messageFlow | `MESSAGE_FLOWS_TO` between participants | separate from sequence flow; preserve ID and endpoints |
| boundary event | `Event` + `ATTACHED_TO` | preserve explicit attachedToRef; infer no exception behavior |
| text annotation | `TextAnnotation` + explicit `ANNOTATES` relationship | preserve text, association ID/direction, and endpoints |

Projection is deterministic for a fixed model and identifiers. Repeated element ID within one model is an error; cross-model collisions are separated by SOP/model identity. A missing or invalid reference is reported and prevents projection; source XML is never repaired. Unsupported BPMN tags are reported in stable lexical order with no silent semantic substitution. No Neo4j operation is part of this contract.

Current implementation caveats: the IR supports one target per data association. Additional structural elements are supported only for the explicit fields listed above; this is not full BPMN collaboration, annotation, boundary-event, or data-store semantics. XML tag inventory is not XSD validation.
