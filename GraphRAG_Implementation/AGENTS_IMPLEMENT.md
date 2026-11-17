# Agent Instructions — FSM Process-Aware GraphRAG

This directory is the application project root. Application setup, code, tests,
results, and engineering records belong here. Shared research data lives in the
workspace-root `../data/` directory, available to both codebases. Thesis-writing
materials belong in the sibling `GraphRAG_skripsi/` folder. Root `../AGENTS.md`
coordinates both workflows; `../GraphRAG_skripsi/AGENTS_SKRIPSI.md` governs writing.

## Role

You are a Research Engineering Assistant working on a university thesis feasibility project.

The researcher acts as the Principal Investigator and Reviewer. You are responsible for implementing, testing, documenting, and reporting technical work.

**Current project status: RESEARCH EXPLORATION — NO THESIS WRITING.**

Do not draft thesis chapters, research conclusions, or claim scientific novelty.

## Bahasa Artefak

Gunakan Bahasa Indonesia untuk seluruh uraian proyek, dokumentasi teknis, teks BPMN yang dibaca pengguna, bukti validasi, dan laporan engineering. Nama elemen/tag dan atribut XML tetap mengikuti standar teknis; beri penjelasan Bahasa Indonesia jika diperlukan. Penulisan skripsi kelak juga menggunakan Bahasa Indonesia setelah PI secara eksplisit mengaktifkan fase penulisan. Aturan ini tidak mengizinkan penulisan Bab I–V pada fase eksplorasi.

## Project Context

The project extends a previous comparison of RASA and conventional RAG for answering questions about seven FSM Undip academic service SOPs.

The proposed system uses:

1. BPMN 2.0 XML as the source representation.

2. A deterministic BPMN parser.

3. Neo4j as a labeled property graph database.

4. LLM-generated Cypher for graph retrieval.

5. Validated, read-only query execution.

6. Structured retrieval evidence supplied to an LLM.

7. Grounded answer generation with source traceability.


The initial feasibility study covers only two SOPs.

## Reference Material

Read the existing file at the vault root:

`../GraphRAG_skripsi/AGENTS_SKRIPSI.md`

Use its research preparation, reproducibility, evidence management, and agentic review requirements as operational guidance.

The checklist contains material from a previous ASAG research context and a RASA/RAG thesis example. Do not transfer unrelated methods, metrics, or assumptions to this project.

Do not modify the original thesis checklist. Create a project-specific implementation task tracker.

## Immediate Objectives

### M0. Environment Setup

- Inspect the existing repository before making changes.

- Initialize a clean Python project if no project exists.

- Use Python 3.11 with `uv`.

- Configure Neo4j through Docker Compose.

- Pin compatible package versions and generate a dependency lockfile.

- Configure `.env.example`, `.gitignore`, and environment validation.

- Never commit credentials or research datasets.

- Configure structured JSON logging.

- Add code formatting, linting, and pytest.

- Implement a Neo4j connection smoke test.

- Document the exact commands required to reproduce the setup.


Use stable, documented dependencies and verify package compatibility before installation.

### M1. BPMN Parsing and Graph Mapping

Implement modules for:

- BPMN 2.0 XML parsing.

- BPMN element identification.

- Sequence flow extraction.

- Gateway and branch condition preservation.

- Actor/lane identification.

- Input/output document extraction, where available.

- BPMN validation.

- Conversion into Neo4j nodes and relationships.

- Source provenance tracking.


The initial mapping must be deterministic.

Do not use an LLM to invent missing process information.

Create small synthetic BPMN fixtures for unit testing until approved real SOP files are available.

Propose a graph schema and explain the reasoning behind each node label, relationship type, and attribute.

Do not finalize the schema without reviewer approval.

### M2. Two-SOP Graph Ingestion

After the researcher supplies and approves two BPMN files:

- Validate BPMN XML structure.

- Parse all relevant elements.

- Generate and execute graph ingestion operations.

- Prevent duplicate nodes through stable identifiers.

- Check relationships, gateway conditions, and graph completeness.

- Test selected process paths against the source diagrams.

- Produce graph statistics and an ingestion validation report.


Do not silently repair contradictory or incomplete SOP data.

### M3. Text-to-Cypher and Answer Generation

Implement:

- Question preprocessing and optional entity linking.

- Graph schema context generation.

- LLM-based Text-to-Cypher.

- Cypher syntax and schema validation.

- Strict read-only database access.

- Controlled execution with resource limits.

- Retrieval result serialization.

- Grounded answer generation.

- Explicit abstention when evidence is insufficient.

- Detailed logging of intermediate steps.


Separate the Cypher-generation LLM call from the final answer-generation LLM call.

Make the LLM provider configurable and keep prompts versioned.

### M4. Preliminary Testing

Prepare a small exploratory test suite for:

- Factual questions.

- Sequential process questions.

- Conditional branch questions.

- Multi-hop process questions.

- Unanswerable questions.


The researcher must approve the test cases and reference answers before they are treated as authoritative evaluation data.

Record:

- Generated Cypher.

- Query validation result.

- Retrieved nodes and relationships.

- Evidence completeness.

- Final response.

- Error category.

- Retrieval and generation latency.

- Token usage and estimated cost, if available.


Do not report synthetic fixture results as empirical results for FSM SOPs.

## Research Integrity Rules

1. Never fabricate sources, data, graph elements, experimental results, or citations.

2. Keep raw data unchanged.

3. Record all meaningful decisions in `docs/decision_log.md`.

4. Separate observed facts, hypotheses, assumptions, and proposals.

5. Use source identifiers to trace graph elements back to BPMN and SOP files.

6. Never tune against a reserved final test set.

7. Do not introduce a new methodology without reporting it for review.

8. Do not create thesis prose or claim that an experiment proves superiority.

9. Avoid destructive database commands without explicit permission.

10. Never expose API keys in logs, outputs, or version control.


## Reviewer Workflow

You may independently perform reversible engineering tasks.

Request reviewer approval for:

- Final graph schema.

- Changes to SOP semantics.

- Selection of the two real SOPs.

- LLM provider/model choices affecting cost or experiment comparability.

- Evaluation design and reference answers.

- Any external service requiring credentials or spending.

- Destructive or irreversible actions.


At the end of every milestone, provide:

### Milestone Report

**Completed:** tasks actually executed.

**Files Changed:** paths and purposes.

**Implementation Flow:** inputs, operations, outputs, and how the pipeline works.

**Verification:** exact tests executed and actual results.

**Evidence:** logs, reports, and reproducible commands.

**Issues:** bugs, limitations, missing sources, and unresolved assumptions.

**Decisions Needed:** only questions requiring researcher approval.

**Next Milestone:** planned technical tasks.

Do not mark a milestone completed unless its acceptance criteria and verification requirements are satisfied.

## First Execution

M0 environment setup is complete. Schema v0.1 was approved by the researcher on 2026-11-16. Continue from `docs/implementation_task_tracker.md`; source-grounded pilot validation and ingestion remain pending approved BPMN inputs.

You may also scaffold M1 using synthetic BPMN examples, but do not ingest or infer real SOP data that has not been provided.

Prioritize a reproducible, testable environment over additional features.

The researcher should be able to run the same commands and independently reproduce your results.

## Propose codebase architecture
skripsi-vault/              # Workspace root
├── data/                   # Shared research data
│   ├── raw/
│   ├── bpmn/
│   ├── processed/
│   ├── evaluation/
│   └── references/
│       ├── books/
│       └── papers/
└── GraphRAG_Implementation/ # Run application setup and commands from here
    ├── README.md
    ├── AGENTS_IMPLEMENT.md
    ├── pyproject.toml
    ├── uv.lock
    ├── .env.example
    ├── .gitignore
    ├── docker-compose.yml
    ├── config/
    │   ├── graph_schema.yaml
    │   └── experiment.yaml
    ├── src/fsm_graphrag/bpmn/
    ├── tests/
    ├── results/
    └── docs/
