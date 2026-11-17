# Workspace Architecture

This file documents the top-level research workspace. The two work areas are
shown only as directory entries here; see their own architecture guides for
their internal trees: [application architecture](GraphRAG_Implementation/ARCHITECTURE.md)
and [thesis-writing architecture](GraphRAG_skripsi/ARCHITECTURE.md).

## Root tree

```text
skripsi-vault/
├── .gitignore                    # Protects shared research data
├── .obsidian/                    # Obsidian vault settings
├── AGENTS.md                     # Shared research workflow and review gates
├── ARCHITECTURE.md               # This workspace-level directory guide
├── data/                         # Research data shared by both work areas
│   ├── raw/                      # Original source documents, unchanged
│   ├── flowchart/                # SOP flowcharts, unchanged source files
│   ├── bpmn/                     # BPMN models created from approved sources
│   ├── processed/                # Derived/intermediate artifacts
│   ├── evaluation/               # Evaluation questions and materials
│   └── references/               # books/ and papers/ shared references
├── GraphRAG_Implementation/      # Application engineering project
└── GraphRAG_skripsi/             # Thesis-writing workspace
```

## Workspace boundaries

- `data/` is the shared source location. Both work areas access it through
  `../data/` from their respective directories.
- Keep SOP text originals in `data/raw/` and flowchart originals in
  `data/flowchart/` unchanged. Create or revise BPMN in `data/bpmn/` using both
  related sources. Record disagreements for PI review; do not resolve them
  automatically. Store other derived artifacts in their corresponding data
  folders and follow the root `.gitignore` rules for research datasets.
- Application code and setup stay in `GraphRAG_Implementation/`; writing drafts
  and approved thesis materials stay in `GraphRAG_skripsi/`.
- The root `AGENTS.md` coordinates the two workflows. Each work area documents
  its own internal directory structure in its local `ARCHITECTURE.md`.

The raw data directory currently contains seven SOP PDF files; other data
subdirectories contain placeholders until their corresponding materials are
provided or produced.
