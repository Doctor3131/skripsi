# BPMN Schema v0.1 Validation Report

**STATUS: REVIEW-PENDING**

## Synthetic fixture

Sources: `tests/fixtures/synthetic_gateway.bpmn` plus an inline synthetic BPMN case in `tests/unit/test_bpmn.py` (synthetic only). Together they cover process, events/tasks, exclusive gateway, conditional/default sequence flow, lane, participants, message flow, boundary attachment, text annotation and association, data store reference, data inputs/outputs, and data associations.

| Check | Expected | Result |
|---|---|---|
| Deterministic repeat projection | equal output | PASS — equality assertion |
| Stable IDs/reprocessing | same tuple gives same key | PASS — repeated projection assertion |
| Cross-model collision separation | distinct model identity gives distinct IDs | PASS — synthetic fixture with two model/SOP tuples |
| Original subtypes | exact BPMN local tag retained | PASS — gateway subtype and parser fixture checks |
| Sequence topology / condition / default | source IDs, refs, condition, explicit language and default retained | PASS for fixture topology/condition/default; explicit-language positive case not present |
| Lane membership | `IN_LANE`, no actor interpretation | PASS — lane link exists and no Actor label |
| Data association direction | association node + source/target links | PASS — source and target references asserted |
| Invalid/unresolved refs | validation error, mapper rejects | PASS — unknown sequence-flow endpoints |
| Additional structural constructs | participant, message flow, annotation link, boundary attachment, data-store reference | PASS — inline synthetic case asserts these draft projections |
| Provenance | hash and logical identity retained | PASS — source hash asserted, composite key tested |
| Unsupported semantic inference | no REQUIRES/PRODUCES or Actor/Document labels | PASS — forbidden labels and relationship types asserted |

Commands from `GraphRAG_Implementation/`: `UV_CACHE_DIR=/tmp/uv-cache-graphrag uv run pytest`, `... uv run ruff check .`, and `... uv run ruff format --check .`. Result after additional-construct support: 10 tests passed; Ruff lint and formatting passed. The cache override was needed because the default user cache was read-only in this environment.

## Two-SOP source-grounded results

Not assessable: `data/bpmn/` contains only `.gitkeep`; no two BPMN models were present. This is a source availability blocker, not a failed validation. No SOP claims or synthetic-to-SOP extrapolation are made.

## Limits

Parser coverage is partial, not BPMN XSD conformance. Participant/pool and collaboration relations, message flow, boundary attachment, annotations, and data stores require explicit modeling decisions. Multiple sources are retained; multiple targets are not represented by the current IR. Expression language is preserved only when directly present as the condition expression's `language` attribute.
