# Thesis-Writing Directory Architecture

`GraphRAG_skripsi/` is the workspace for preparing, reviewing, and storing
thesis-writing artifacts. The workflow instructions and writing checklist are
in `AGENTS_SKRIPSI.md`. Shared research data remains in `../data/`; this folder
should contain only writing materials and verified evidence selected for use.

## Directory tree

```text
GraphRAG_skripsi/
├── AGENTS_SKRIPSI.md  # Writing workflow, gates, and review checklist
├── ARCHITECTURE.md    # This directory guide
├── README.md          # Writing workspace overview and handoff flow
├── docs/              # Modular guides indexed by AGENTS_SKRIPSI.md
│   ├── 00_operasional_dan_fondasi_data.md
│   ├── 01_bab_i_pendahuluan.md
│   ├── 02_bab_ii_tinjauan_pustaka.md
│   ├── 03_bab_iii_metodologi.md
│   ├── 04_bab_iv_hasil_pembahasan.md
│   ├── 05_bab_v_penutup.md
│   ├── 06_bagian_awal_pustaka_lampiran.md
│   ├── 07_quality_gates.md
│   ├── 08_protokol_agentic_review.md
│   └── 09_template_tugas_dashboard.md
├── approved/          # Researcher-reviewed thesis text, organized by chapter
│   ├── bab-i/
│   ├── bab-ii/
│   ├── bab-iii/
│   ├── bab-iv/
│   └── bab-v/
├── decisions/         # Writing-related decisions and approved changes
├── drafts/            # Active drafts, separated by chapter
│   ├── bab-i/
│   ├── bab-ii/
│   ├── bab-iii/
│   ├── bab-iv/
│   └── bab-v/
├── evidence/          # Verified evidence pointers/material approved for writing
├── figures/           # Figures prepared or approved for thesis use
├── references/        # Curated bibliography and literature-writing materials
└── results/           # Verified result summaries for writing

../data/               # Shared source and research data, not duplicated here
├── raw/               # Original SOP/source documents
├── bpmn/              # BPMN models
├── processed/         # Derived artifacts
├── evaluation/        # Evaluation questions and related material
└── references/        # Shared reference source files
    ├── books/
    └── papers/
```

## Handoff boundaries

- Engineering implementation and reproducibility records belong in
  `../GraphRAG_Implementation/`.
- Use `../data/` as the shared source location; do not copy or edit originals
  inside this writing workspace.
- Move or link only checked evidence and results into `evidence/` and
  `results/` for drafting.
- Keep work in `drafts/` until it has been reviewed. Store approved text in
  `approved/` only after researcher approval.
- Empty chapter folders are placeholders, not evidence that thesis chapters
  have been written or approved.
