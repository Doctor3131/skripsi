# Application Directory Architecture

`GraphRAG_Implementation/` is the Python application project root. Run `uv`,
pytest, Ruff, and Docker Compose commands from this directory. The separate
`../data/` directory is shared with the thesis-writing workspace; use paths
relative to this directory, such as `../data/flowchart/` or `../data/bpmn/`.

## Directory tree

```text
GraphRAG_Implementation/
├── .env                    # Local credentials; ignored by Git
├── .env.example            # Safe configuration template
├── .gitignore              # Project-local secrets, caches, and results rules
├── .python-version         # Python version used by uv
├── AGENTS_IMPLEMENT.md     # Application engineering instructions
├── ARCHITECTURE.md         # This directory guide
├── README.md               # Setup, run, and verification commands
├── docker-compose.yml      # Local Neo4j service and persistent volumes
├── pyproject.toml          # Package metadata, dependencies, and tool config
├── uv.lock                 # Resolved dependency versions
├── docs/
│   ├── bpmn_graph_schema_proposal.md  # Unapproved graph schema proposal
│   ├── decision_log.md               # Recorded project decisions/evidence
│   └── implementation_task_tracker.md # Milestones and status
├── results/                # Generated run outputs; currently placeholder only
├── src/fsm_graphrag/
│   ├── bpmn/               # BPMN model, parser, validation, draft mapping
│   ├── config.py           # Environment settings and validation
│   ├── logging_config.py   # Structured JSON logging setup
│   └── neo4j_smoke.py      # Read-only Neo4j connectivity check
└── tests/
    ├── fixtures/           # Synthetic BPMN inputs for tests
    └── unit/               # Parser, mapping, and config tests

../data/                    # Shared research data, outside this project folder
├── raw/                    # Original source documents; keep unchanged
├── flowchart/              # SOP flowcharts; original source files
├── bpmn/                   # BPMN source models
├── processed/              # Derived data and intermediate artifacts
├── evaluation/             # Candidate and approved evaluation material
└── references/             # Shared research reference files
```

## Data and safety boundaries

- `tests/fixtures/` contains synthetic examples for repeatable unit tests; it is
  not empirical SOP data.
- `../data/raw/` stores SOP text originals and `../data/flowchart/` stores
  corresponding SOP flowcharts. Use both when creating or revising BPMN in
  `../data/bpmn/`; record disagreements for researcher review instead of
  resolving them automatically.
- Keep raw and derived research datasets out of version control unless their
  inclusion is explicitly approved. The workspace-root `.gitignore` protects
  the shared data directories while retaining `.gitkeep` placeholders.
- The proposed BPMN graph mapping is a draft. Do not use it for Neo4j ingestion
  until the researcher approves the schema.
