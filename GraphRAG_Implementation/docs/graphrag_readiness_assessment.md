# Structural GraphRAG Readiness Assessment — v0.1

**STATUS: REVIEW-PENDING; capability analysis only, not a performance claim.**

| Question | Capability from structural BPMN | Additional need / limitation |
|---|---|---|
| What activities belong to a process? | Direct via `HAS_ELEMENT`, filtered to Activity nodes | Needs approved complete BPMN and process identity |
| What follows a given activity? | Traversal via `FLOWS_TO` | Sequence topology is not a guarantee of runtime execution |
| Which branches originate at a gateway? | Direct outgoing flow traversal | Gateway semantics and each condition must be interpreted; absent conditions stay absent |
| Under what recorded condition does a branch occur? | Direct if condition expression exists | Natural-language explanation may require rule interpretation; expression may be opaque |
| Which lane contains an activity? | Direct via `IN_LANE` | Does not identify a real-world actor/role without separate evidence |
| Which data elements are associated with an activity? | Association traversal through `DataAssociation` | Association is not proof of mandatory input or produced business document |
| Where did a process fact originate? | Source SOP/model/element IDs and content hash | Need a source-location mapping to SOP page/section for user-facing citations |
| What document is required, who approves, or what deadline applies? | Not reliably answerable from this structural layer alone | Requires reviewed semantic layer grounded in SOP text/flowchart |
| What happens in an undocumented exception? | Cannot be answered | Must abstain or report source gap |

The current mapper is not a Text-to-Cypher or answer-generation system. Trustworthy procedural QA additionally needs approved BPMN fidelity mapping, authoritative SOP section provenance, reviewed semantic assertions, question/ground-truth approval, read-only execution controls, and evidence-grounded abstention. No empirical readiness or performance is claimed.
