# Schema v0.1 revision — pre-change inspection

**Status:** implementation note; review pending.

- Git already contained user changes in `.gitignore`, root `AGENTS.md`, architecture files, Obsidian theme files, and `data/flowchart/`. These were preserved and are outside this revision.
- M0 is recorded complete in `docs/implementation_task_tracker.md`.
- Existing M1 code includes immutable dataclasses, a standard-library parser, reference validator, deterministic proposal mapper, one synthetic gateway fixture, and five BPMN tests (plus two config tests noted in the tracker).
- Existing proposal v0 maps lanes to `Actor`, data to `Document`, and associations to `REQUIRES`/`PRODUCES`; these are the requested revision targets.
- `data/bpmn/` contains only `.gitkeep`; no two-SOP BPMN files are available for source-grounded validation.
- Existing parser does not retain source content hash, expression language, nested lane parentage, data association transformation expressions, or deterministic unsupported-element findings. Existing mapper uses raw BPMN IDs and source paths as graph identity/provenance.
- Following PI direction, v0.1 identity policy now requires explicit, nonempty `sop_id` from the approved source inventory and explicit versioned `model_id`; no mapper fallback is allowed. No actual SOP/model identifiers have been assigned because the approved inventory and BPMN files are absent.
- Existing validator checks several references but does not report unsupported BPMN constructs or all missing/duplicate association references. No Neo4j data was inspected or modified.

This inventory records the baseline before v0.1 edits. The synthetic fixture remains synthetic and is not treated as FSM SOP evidence.
