# Implementation Task Tracker — FSM Process-Aware GraphRAG

Status: research exploration; no thesis writing. This tracker adapts the supplied checklist's reproducibility, evidence management, provenance, and human review practices to this project. ASAG-specific techniques and metrics are out of scope.

Project root: `GraphRAG_Implementation/`. Run project setup, test, lint, and Docker Compose commands from this directory. Shared research data lives at `../data/`; root `AGENTS.md` coordinates this engineering workflow with the separate thesis-writing workflow.

Milestone crosswalk: this engineering tracker numbers implementation milestones locally. Root checklist M2 is SOP audit/modeling (tracked below as M2 source audit, then local M2 ingestion); root M3 is graph parsing/ingestion; root M4 is Text-to-Cypher; root M5 is preliminary evaluation. Root M1 literature review is independent and tracked by its literature artifacts.

## M0 — Environment Setup (complete; smoke check passed 2026-11-15)

- [x] Inspect the existing vault; no Python project or real SOP data was present.
- [x] Add Python 3.11 project metadata and pin direct dependency/tool versions.
- [x] Configure Neo4j with Docker Compose and persistent named volumes.
- [x] Add `.env.example`, secret/data exclusions in `.gitignore`, and environment validation.
- [x] Configure structured JSON logging.
- [x] Add unit test cases, lint/format config, and a read-only Neo4j smoke check.
- [x] Document setup, verification, and teardown commands.
- [x] Generate `uv.lock` and verify locked installation with `uv lock --check` and `uv sync --locked --offline`.
- [x] Validate Python source syntax with `python3.11 -m compileall -q src tests`.
- [x] Validate Compose configuration with `env NEO4J_PASSWORD=<local-validation-value> docker compose config --quiet`.
- [x] Run `uv run pytest`, `uv run ruff check .`, and `uv run ruff format --check .` (2 tests passed; lint and format checks passed).
- [x] Run the Neo4j connection smoke check (researcher reported pass on 2026-11-15 after Neo4j became healthy).

Acceptance evidence: `README.md`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, source modules, and command results in the milestone report. Verification: `uv lock --check` and offline `uv sync --locked` passed; `python3.11 -m compileall -q src tests` passed; `docker compose config --quiet` passed; pytest passed (2 tests); Ruff lint and format checks passed; researcher reported the Neo4j connection smoke check passed after the service became healthy. M0 acceptance criteria are complete.

## M1 — BPMN Parsing and Graph Mapping (schema v0.1 approved; SOP validation pending)

- [x] Researcher reviewed and approved schema labels, relationship types, attributes, identity, and rationale in `docs/bpmn_graph_schema_proposal.md` (2026-11-16).
- [x] Add synthetic BPMN fixture and deterministic parser, validator, and draft-mapping tests.
- [x] Preserve source identifiers, branch conditions, lane assignment, document references, and file provenance; do not infer missing process information.
- [x] Prepare v0.1 contract, validation report, and GraphRAG readiness assessment; schema approved by researcher on 2026-11-16.

M1 implementation evidence: `docs/schema_v01_inspection.md`, `docs/bpmn_graph_schema_proposal.md`, `docs/bpmn_graph_schema_contract.md`, `docs/bpmn_schema_validation_report.md`, `docs/graphrag_readiness_assessment.md`, `src/fsm_graphrag/bpmn/`, and synthetic BPMN cases under `tests/`. Verification passed: 8 BPMN tests and 2 config tests; Ruff lint and formatting checks passed. Schema v0.1 was approved by the researcher on 2026-11-16. Only synthetic fixture coverage was possible; no FSM SOP BPMN files were available. Source-grounded validation and Neo4j ingestion remain pending approved pilot BPMN inputs.

## M2 — Audit SOP dan ingest graph dua pilot (ingest pilot selesai)

- [x] Inventory seven PDF/DOCX source pairs, record exact-byte SHA-256, and extract available header metadata in `docs/data_inventory.csv`; PI approved the pairings on 2026-11-16.
- [x] Audit process text, actors, documents, timing, conditions, ambiguity, and cross-source differences in `docs/sop_audit.md`.
- [ ] PI confirms source-owner rights and whether the dated DOCX revisions are authoritative/current. Project-local `sop_id` values and metadata-based labels are recorded; official SOP numbers/effective dates and rights remain unverified. Visual flowcharts are not a prerequisite.
- [x] PI selected `Permohonan Izin Cuti Akademik` and `Permohonan Izin Aktif Kuliah Setelah Cuti` on 2026-11-16; rationale and scope boundary are recorded in `docs/decision_log.md`.
- [x] PI decided on 2026-11-16 that missing/broken visual flowcharts are not a prerequisite; PDF narrative controls sequence/conditions and DOCX tables supplement actors/metadata.
- [x] Generate both draft BPMNs, Indonesian SVG previews, model manifest, path check, and traceability index with the approved source hierarchy and model IDs; see `scripts/build_pilot_bpmn.py` and `results/m2/`.
- [x] Validasi parser/referensi struktur lulus untuk kedua model; ID model dan hash sumber cocok dengan inventaris, serta seluruh elemen terlacak. Lihat `scripts/validate_pilot_bpmn.py` dan `results/m2/bpmn_validation.json`.
- [x] Verification for this revision: `pytest` (17 passed), Ruff lint/format checks passed, XML/SVG well-formedness passed with `xmllint`, local parser/reference validation passed, and a second deterministic build produced identical hashes for BPMN, SVG, and traceability outputs. Full BPMN XSD validation and visual inspection in a dedicated BPMN modeler remain outstanding.
- [x] Jalankan pra-ingest lokal dengan skema v0.1; tidak ditemukan elemen semantik tak didukung, ID ganda, atau endpoint relasi hilang. Metadata BPMN DI/IO dikenali dan tidak menambah node graf. Lihat `results/m2/mapping_preflight.json`.
- [x] PI menyetujui fidelitas semantik dan konflik yang dirinci pada 2026-11-17; checksum BPMN dibekukan dalam `results/m2/pilot_manifest.json`.
- [x] Ingest kedua BPMN approved/frozen ke Neo4j Compose dengan transaksi `MERGE`; tidak ada reset/penghapusan. Run `m2-ingest-20261116T174747461682Z` dan hasil ada di `results/m2/ingestion_report.json`.
- [x] Verifikasi identitas stabil, endpoint/jenis relasi, kondisi, cabang bawaan, provenance, traversal seluruh jalur, serta statistik node dan relasi.
- [x] Ulang ingest idempoten: basis data tetap 43 node dan 70 relasi; tidak ada ID ganda.
- [ ] Lengkapi pemeriksaan sumber resmi/izin pemilik, nomor SOP resmi, tanggal efektif, dan status kewenangan versi DOCX. Persetujuan PI saat ini mencakup pemrosesan lokal pilot, bukan penetapan otoritas penerbit.
- [ ] Selesaikan validasi BPMN XSD penuh, review dalam modeler BPMN, dan dokumentasi backup/restore Neo4j.

**Status saat ini:** kedua BPMN disetujui PI dan dibekukan pada 2026-11-17; keduanya telah di-ingest ke Neo4j Compose proyek. Validasi graph lulus: 43 node, 70 relasi, semua akhir proses terjangkau, kondisi/cabang bawaan dan provenance cocok, serta rerun tidak menggandakan data. Nomor resmi/izin pemilik dan otoritas versi sumber belum dipastikan. Validasi XSD penuh, modeler BPMN khusus, serta backup/restore belum dilakukan. Flowchart visual bukan prasyarat.

## M3 — Text-to-Cypher dan Generasi Jawaban (implementasi GraphRAG; gerbang database/LLM terbuka)

- [x] Migrasikan dependency ke `neo4j-graphrag[openai]==1.22.0` dan Neo4j driver `6.4.1`; lockfile terbarui.
- [x] Implementasikan `Text2CypherRetriever` tersaring, `GraphRAG`, dan `OpenAILLM` dengan Chat Completions; dua instance memisahkan query dan jawaban.
- [x] Gunakan variabel generik `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TEMPERATURE` (default 0), dan timeout. Tidak ada nilai model/API key lokal yang di-hard-code.
- [x] Pertahankan allowlist Cypher/schema, parameter skalar, `LIMIT` aplikasi maksimum 50, `EXPLAIN`/query-type read-only, routing READ, timeout query, evidence/provenance, citation validation, abstain, latency/token trace.
- [x] Gunakan kredensial Compose (`NEO4J_USER/PASSWORD`) untuk driver GraphRAG; pada Community hak database tetap admin dan operasi baca dibatasi di lapisan aplikasi.
- [x] Tambahkan tes unit menggunakan mock; tidak ada request LLM. Jalur GraphRAG dan guardrail diuji dengan 39 tes.
- [x] Tambahkan `scripts/graphrag_local_smoke.py` untuk menjalankan query tetap lewat retriever library dan Neo4j lokal tanpa memanggil LLM.
- [x] Jalankan smoke baru pada Neo4j lokal melalui `GuardedText2CypherRetriever`; 8 evidence cuti dan 2 aktif ditemukan dengan provenance. `EXPLAIN`/routing READ lulus; tidak ada panggilan LLM. Laporan `results/m4/graphrag_local_smoke.json`.
- [ ] PI mengisi/menyetujui endpoint/model, biaya, izin data, prompt dan katalog pertanyaan sebelum request LLM eksternal.

**Status:** Implementasi memakai kredensial Compose pada Neo4j Community. Verifikasi setelah perubahan: 39 unit test lulus, Ruff lint/format lulus, dan smoke GraphRAG lokal menemukan 8 evidence cuti serta 2 evidence aktif dengan provenance melalui `EXPLAIN`/routing READ; tidak ada panggilan LLM. Guardrail aplikasi membatasi query, tetapi akun database tetap memiliki hak admin. Pipeline masih menunggu persetujuan PI untuk endpoint/model, penggunaan data/biaya, dan katalog pertanyaan. Tidak ada panggilan LLM eksternal.

## M4 — Preliminary Testing (not started)

- [ ] Draft exploratory question categories and candidate cases for researcher review.
- [ ] Do not treat questions/reference answers as authoritative until researcher approval.
- [ ] Keep synthetic fixture results separate from empirical FSM SOP results.
