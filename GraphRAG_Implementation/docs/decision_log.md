# Decision Log

## 2026-11-17 — Revisi BPMN v2 berbasis template dan reset graph penuh

- **Arahan PI:** gunakan `data/bpmn/template_contoh.bpmn` sebagai basis struktur XML dan tampilan kedua BPMN pilot; ganti isi database proyek dengan graph baru.
- **Perubahan model:** file `pilot_sop_a.bpmn` dan `pilot_sop_b.bpmn` tetap pada nama yang sama; ID model menjadi v2. Pool, lane horizontal, ukuran shape, label BPMN DI, dan jalur ortogonal mengikuti pola template. ID elemen, alur, kondisi, lane, objek data, dan provenance SOP dipertahankan.
- **Pemulihan struktur:** revisi lokal sebelumnya pada BPMN cuti kehilangan beberapa child `dataInput`/`dataOutput` dan `targetRef`. Generator v2 memulihkan referensi tersebut dari model deklaratif yang disetujui; semantik data kembali lengkap.
- **Validasi:** 40 unit test lulus; Ruff lint/format dan validasi BPMN lokal lulus; pra-ingest tidak menemukan unsupported element, ID duplikat, atau endpoint hilang. Proyeksi tetap 43 node/70 relasi.
- **Reset database:** atas arahan eksplisit PI, seluruh graph data pada database proyek `neo4j` dihapus: 43 node/70 relasi menjadi 0/0. Indeks, konstrain, volume, autentikasi, dan konfigurasi dipertahankan. Bukti: `results/m2/database_reset_report.json`.
- **Ingest ulang:** v2 berhasil di-ingest (43 node/70 relasi), provenance cocok dengan checksum baru, lalu rerun idempoten tidak menggandakan data. Run tercatat di `results/m2/ingestion_report.json`.
- **Smoke:** retrieval baca-saja lokal untuk kedua SOP lulus tanpa panggilan LLM; `results/m4/graphrag_local_smoke.json`.
- **Status review:** manifest v2 masih `PENDING_REVIEW`; PI perlu meninjau tampilan/diagram v2 sebelum freeze. Persetujuan semantik v1 tetap menjadi landasan konten v2, bukan approval final visual v2.

## 2026-11-17 — Penutupan tindak lanjut M2 atas keputusan PI

- **Keputusan PI:** Untuk lingkup eksplorasi pilot, status pemeriksaan sumber/izin/otoritas versi diterima dan tindak lanjut validasi BPMN XSD serta review modeler khusus ditutup.
- **Batas klaim:** Keputusan ini adalah penerimaan PI untuk melanjutkan lingkup eksplorasi; bukan bukti verifikasi independen atas pemilik/hak publikasi dan tidak menyatakan XSD atau modeler BPMN telah diperiksa.
- **Keputusan PI:** Dokumentasi backup/restore Neo4j dikeluarkan dari lingkup tugas saat ini.
- **Bukti pencatatan:** `docs/implementation_task_tracker.md` dan checklist root `AGENTS.md`.

## 2026-11-17 — Koneksi GraphRAG menggunakan kredensial Neo4j Community

- **Keputusan PI:** Tetap menggunakan Neo4j Community self-hosted dengan autentikasi aktif; pipeline memakai `NEO4J_USER/PASSWORD` yang sama dengan Compose.
- **Perubahan:** Menghapus konfigurasi dan factory driver yang mewajibkan akun khusus ber-role reader. Driver GraphRAG memakai kredensial umum proyek.
- **Batas keamanan:** Community tidak menyediakan role read-only. Akun tetap memiliki hak admin pada tingkat database; allowlist, `EXPLAIN`, pemeriksaan tipe query, routing `READ`, batas hasil, dan timeout hanya membatasi jalur aplikasi.
- **Status gate:** Ketiadaan role read-only bukan lagi blocker pemilihan edisi. Persetujuan provider/model, penggunaan data, biaya, prompt, dan katalog pertanyaan tetap terbuka.
- **Bukti:** `src/fsm_graphrag/config.py`, `src/fsm_graphrag/graphrag_pipeline.py`, `tests/unit/test_graphrag_pipeline.py`, dan kontrak Text-to-Cypher.

## 2026-11-16 — Pendekatan pemodelan dan bahasa pilot BPMN

- **Keputusan PI:** Flowchart visual yang rusak/tidak tersedia bukan prasyarat. PDF naratif menjadi acuan utama urutan dan kondisi; tabel DOCX menjadi pelengkap informasi pelaksana/metadata.
- **ID model disetujui:** `FSM-SOP-CUTI-AKADEMIK-BPMN-v1` dan `FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v1`.
- **Batas interpretasi:** Kondisi “persyaratan lengkap” pada SOP cuti dipertahankan tanpa mengarang hasil untuk kondisi tidak lengkap. Status aktif pada SOP aktif setelah cuti dimodelkan sebagai hasil, bukan tugas tambahan. Ketidakselarasan sumber ditandai pada traceability.
- **Bahasa:** Artefak engineering, teks BPMN, dokumentasi, dan skripsi pada fase penulisan nanti menggunakan Bahasa Indonesia. Tag/atribut standar teknis tetap mengikuti spesifikasinya.
- **Batas gate:** Keputusan ini mengizinkan draf BPMN lokal untuk ditinjau; tidak menyetujui/freeze BPMN atau mengizinkan ingest Neo4j.
- **Bukti:** `docs/bpmn_modeling_rules.md` dan berkas BPMN pilot.

## 2026-11-16 — Draf BPMN pilot dibuat

- **Pelaksanaan:** BPMN `pilot_sop_a.bpmn` dan `pilot_sop_b.bpmn`, pratinjau SVG, manifest sumber/model, pemeriksaan jalur, dan indeks traceability dibuat secara deterministik dengan skrip berbahasa Indonesia.
- **Validasi:** Parser dan pemeriksa referensi lulus untuk kedua model; ID XML unik; hash sumber cocok inventaris; seluruh elemen semantik tercakup di traceability; berkas XML/SVG well-formed. Seluruh 17 unit test, Ruff, dan pemeriksaan format lulus.
- **Batas:** Ini adalah draf untuk tinjauan PI, bukan approval fidelitas atau freeze. Validasi XSD BPMN penuh belum dilakukan dan tidak ada data yang di-ingest ke Neo4j.
- **Bukti:** `scripts/build_pilot_bpmn.py`, `scripts/validate_pilot_bpmn.py`, `results/m2/`, dan `data/bpmn/`.

## 2026-11-17 — Tafsir pilihan pengambilan surat ditandai untuk tinjauan PI

- **Temuan pemodelan:** Menempatkan “mahasiswa dapat mengambil surat” sebagai alur lurus membuat aktivitas pengambilan tampak wajib, padahal kata “dapat” dapat menunjukkan pilihan.
- **Implementasi draf:** Langkah 7 berlanjut ke gateway eksklusif; jalur bersyarat menuju pengambilan surat, sedangkan jalur bawaan mengakhiri proses setelah surat dikirim. Tidak ada jalur untuk persyaratan tidak lengkap.
- **Batas klaim:** Opsionalitas dan jalur bawaan ini adalah tafsir pemodelan, bukan fakta SOP yang telah dikonfirmasi. Keduanya ditandai pada traceability dan menunggu review PI sebelum BPMN dibekukan.
- **Bukti:** `docs/bpmn_modeling_rules.md`, `results/m2/path_check.md`, `results/m2/sop_bpmn_traceability.csv`, `results/m2/bpmn_validation.json`, serta BPMN dan SVG turunan.

## 2026-11-17 — Pemeriksaan proyeksi graf pra-ingest

- **Pelaksanaan:** Memetakan dua BPMN draf secara lokal menggunakan skema v0.1 yang telah disetujui; menambahkan properti `default_flow_bpmn_id` pada node gateway agar rujukan cabang bawaan ikut tersimpan.
- **Hasil aktual:** 43 node dan 70 relasi terproyeksi; tidak ditemukan ID node ganda atau endpoint relasi yang hilang. Kondisi `persyaratan lengkap`, kondisi pilihan pengambilan, dan cabang bawaan tercatat pada laporan.
- **Batas dan penyesuaian:** Proyeksi hanya pemeriksaan pra-ingest; tidak ada koneksi/tulisan Neo4j. Pemeriksaan awal mengklasifikasikan BPMN DI dan pembungkus IO specification sebagai tak didukung; setelah memeriksa parser, elemen DI ditetapkan sebagai tata letak, sedangkan IO specification telah direpresentasikan melalui rekaman asosiasi data. Keduanya kini dikenali sebagai metadata/struktur tanpa membuat node graf tambahan. BPMN tetap menunggu persetujuan semantik PI.
- **Bukti:** `scripts/preflight_pilot_mapping.py`, `results/m2/mapping_preflight.json`, dan uji mapping sintetis.

## 2026-11-17 — Persetujuan semantik pilot dan pemeriksaan target Neo4j

- **Persetujuan PI:** PI menyetujui tafsir draf yang dirinci untuk langkah pengambilan surat dan jalur bawaan, ketiadaan cabang persyaratan tidak lengkap, perlakuan konflik penandatangan (PDF diikuti; konflik DOCX dicatat), serta status aktif sebagai hasil akhir.
- **Pemeriksaan target:** Docker menunjukkan kontainer `neo4j-learn` aktif, tetapi kontainer tersebut tidak dikelola Compose proyek. Koneksi Bolt baca-saja menggunakan konfigurasi lokal menghasilkan kegagalan autentikasi.
- **Batas tindakan:** Belum ada query tulis atau ingest. Target Neo4j yang benar perlu dikonfirmasi/dikonfigurasi sebelum ingest agar data tidak masuk ke database yang keliru.
- **Bukti:** Persetujuan PI di percakapan 2026-11-17; log smoke check lokal tidak mencatat kredensial.

## 2026-11-17 — BPMN pilot dibekukan dan di-ingest ke Neo4j lokal

- **Persetujuan PI:** Setelah PI menyetujui empat tafsir semantik, dua BPMN v1 dibekukan dengan checksum pada `results/m2/pilot_manifest.json`.
- **Lingkungan:** Kontainer proyek `graphrag_implementation-neo4j-1` (image Neo4j 5.26.5), database `neo4j`; smoke check koneksi lulus.
- **Ingest:** Run ID `m2-ingest-20261116T174747461682Z`, transaksi `MERGE`, tanpa reset atau penghapusan. Database kosong untuk kedua SOP sebelum ingest pertama; hasil pertama 43 node dan 70 relasi.
- **Verifikasi pengulangan:** Run berikutnya menemukan 43 node/70 relasi, selesai tanpa duplikasi, dan jumlah akhir tetap 43/70.
- **Fidelity:** Semua tipe relasi cocok dengan proyeksi; kondisi persyaratan lengkap, pilihan pengambilan, dan alur bawaan cocok; dua jalur cuti mencapai kedua end event, satu jalur SOP aktif mencapai `End_Aktif`; semua node/relasi memiliki provenance.
- **Batas:** Validasi XSD BPMN penuh, migrasi constraint/index Neo4j, dan backup/restore belum dijalankan. Nomor resmi/otoritas versi SOP dan hak publikasi tetap belum dipastikan. Tidak ada layanan LLM eksternal yang digunakan.
- **Bukti:** `results/m2/ingestion_report.json`, `results/m2/bpmn_validation.json`, `results/m2/path_check.md`, dan `results/m2/pilot_manifest.json`.

## 2026-11-17 — Persiapan pipeline Text-to-Cypher tanpa provider eksternal

- **Pelaksanaan:** Membuat kontrak pipeline Bahasa Indonesia, prompt Text-to-Cypher v1 dan jawaban grounded v1, validator query fail-closed, eksekutor Neo4j `READ_ACCESS`, serialisasi evidence, abstain, kategori error, dan trace latensi/token/biaya.
- **Kontrol:** Query harus memakai skema allowlist, parameter skalar, `LIMIT $maks_hasil` (maksimum 50), `EXPLAIN`, dan timeout 5 detik. Klausa/prosedur mutasi, multi-statement, komentar, literal string, dan identifier bertanda backtick ditolak.
- **Verifikasi aktual:** 33 unit test lulus. Smoke query tetap melalui `EXPLAIN` dan transaksi baca terhadap dua SOP menemukan 8 aktivitas cuti dan 2 aktivitas aktif dengan provenance lengkap; lihat `results/m4/read_only_smoke.json`.
- **Batas:** Belum ada provider/model LLM, kredensial, panggilan eksternal, atau validasi jawaban model aktual. `READ_ACCESS` adalah pembatasan transaksi aplikasi; akun Neo4j khusus read-only belum dibuat. AST parser penuh, persistensi trace eksperimen, katalog pertanyaan, dan ground truth menunggu review PI.
- **Bukti:** `src/fsm_graphrag/text_to_cypher.py`, `prompts/`, `docs/text_to_cypher_contract.md`, `scripts/text_to_cypher_read_smoke.py`, dan `tests/unit/test_text_to_cypher.py`.

## 2026-11-17 — Migrasi pipeline ke neo4j-graphrag

- **Keputusan PI:** Ganti implementasi custom sebagai pipeline utama dengan `Text2CypherRetriever` dan `GraphRAG`; gunakan konfigurasi generik OpenAI-compatible (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`) dan pertahankan kontrol penting aplikasi.
- **Implementasi:** Pin `neo4j-graphrag[openai]==1.22.0` dan Neo4j Python driver `6.4.1`; `OpenAILLM` menggunakan Chat Completions. Retriever proyek memvalidasi JSON/query sebelum eksekusi, lalu menggunakan `EXPLAIN`, `RoutingControl.READ`, batas 50, timeout, formatter evidence/provenance, citation validation, dan abstain.
- **Verifikasi aktual:** 39 unit test lulus menggunakan mock, Ruff lint/format lulus, dan smoke lokal GraphRAG menemukan 8 evidence SOP cuti serta 2 evidence SOP aktif dengan provenance melalui `EXPLAIN`/routing READ. Tidak ada request eksternal; lihat `results/m4/graphrag_local_smoke.json`.
- **Catatan historis (digantikan keputusan Community 2026-11-17 di bagian atas):** Pada saat catatan ini dibuat, `create_read_only_driver()` menolak fallback admin dan pipeline menunggu keputusan lingkungan. Keputusan terbaru menggunakan kredensial Compose pada Neo4j Community; akun tetap admin pada tingkat database dan guardrail berlaku di aplikasi.
- **Gerbang eksternal:** `.env` key/model LLM tetap kosong; belum ada persetujuan penggunaan SOP ke endpoint, biaya/model, atau panggilan LLM. Temperature default 0 dan dapat dikonfigurasi.
- **Bukti:** `src/fsm_graphrag/graphrag_pipeline.py`, `prompts/neo4j_*_v1.md`, `docs/text_to_cypher_contract.md`, `scripts/graphrag_local_smoke.py`, `tests/unit/test_graphrag_pipeline.py`, `pyproject.toml`, dan `uv.lock`.

## 2026-11-16 — PI approval of PDF/DOCX source pairings

- **Decision (PI):** Approve the seven PDF-to-DOCX pairings listed in `docs/data_inventory.csv` as the intended source pairs for this project.
- **Scope:** This approves pairing only. It does not establish official SOP IDs, authoritative version/effective date, usage permission, or turn the DOCX activity/actor tables into missing visual flowcharts.
- **Implementation:** Inventory pairing status set to `APPROVED_BY_PI` with approval date 2026-11-16. Content hashes are unchanged and still identify the exact files reviewed.
- **Evidence:** PI approval in conversation on 2026-11-16.

## 2026-11-16 — Project SOP identifiers and source version labels

- **Decision (PI-directed):** Generate stable project-local `sop_id` values for the seven approved source pairs and record a version label from the DOCX header creation/revision dates.
- **Identifiers:** The `FSM-SOP-*` values in `docs/data_inventory.csv` are project identifiers only; they are not asserted to be official FSM/Undip SOP numbers.
- **Version boundary:** `source_version_label` records observed DOCX header metadata, not proof that a revision is authoritative or currently effective. These labels do not replace the PI-assigned BPMN `model_id` required by schema v0.1.
- **Use scope:** PI instruction authorizes local processing for this inventory task. This is not a determination of rights from the source owner. External service use remains unauthorized without explicit approval; the inventory records these scopes separately.
- **Evidence:** Updated `docs/data_inventory.csv`; source-pair hashes remain unchanged.

## 2026-11-16 — Pilot SOP selection

- **Decision (PI):** Select (1) SOP Permohonan Izin Cuti Akademik and (2) SOP Permohonan Izin Aktif Kuliah Setelah Cuti as the two pilot procedures.
- **Rationale provided:** The procedures are conceptually related and can support BPMN-to-Neo4j ingestion, sequential reasoning, conditional reasoning where the SOP documents a condition, cross-SOP retrieval, and Text-to-Cypher exploration.
- **Scope:** This approves pilot selection only. Pairings, project IDs, source hierarchy, and model IDs were approved in later decisions. It does not resolve source-owner rights/version authority, settle semantic conflicts, approve BPMN models, or authorize graph ingestion.
- **Review points remaining:** Review the cuti completeness-condition representation, its approval-metadata conflict, and the active-after-cuti outcome interpretation before BPMN freeze. Visual flowcharts are not a prerequisite by PI decision.
- **Evidence:** PI selection recorded in the conversation on 2026-11-16; source audit in `docs/sop_audit.md`.

## 2026-11-16 — Researcher approval of BPMN-to-Graph Schema v0.1

- **Decision:** The researcher approved schema v0.1, including node labels, relationship types, attributes, composite identity policy, and the agreed additional structural mappings.
- **Status:** Schema review gate M3-01 is complete. Approval does not validate the schema against real SOP BPMNs, approve specific pilot files, or authorize ingestion before the M2 source-validation gate.
- **Evidence:** `docs/bpmn_graph_schema_proposal.md` and `docs/bpmn_graph_schema_contract.md` now carry the approved status; tracker and root checklist are updated.

## 2026-11-16 — Composite identity policy for BPMN projection

- **Decision (researcher-directed):** Use an approved source-inventory `sop_id` and an explicit, PI-approved versioned `model_id` as mandatory identity components with the original BPMN element ID. A revised BPMN gets a new `model_id`; retain prior versions. Content SHA-256 is provenance, not the version identifier.
- **Implementation:** The draft mapper now requires nonempty `sop_id` and `model_id` arguments and has no placeholder/namespace fallback. Synthetic tests use clearly synthetic identifiers. Project-local SOP identifiers are now recorded in the approved source inventory; BPMN `model_id` values remain unassigned pending approved BPMN versions.
- **Status:** Identity policy applied to the approved v0.1 proposal/contract and draft mapper. No Neo4j ingestion occurred.

## 2026-11-16 — Conditional support for additional BPMN structures

- **Decision (researcher-directed):** Project participant/pool neutrally, message flow separately from sequence flow, text annotations with explicit associations, boundary-event attachment, and data-store references when present in approved pilot BPMN.
- **Implementation:** Added draft structural mapping support and IR/parser fields. These constructs do not imply roles, procedural rules, exception outcomes, or document requirements.
- **Status:** Proposal only; confirm implementation against supplied approved pilot BPMN before ingestion. No Neo4j changes.

## 2026-11-15 — Application project directory and M0 follow-up

- **Decision:** Keep application code, environment setup, Docker Compose, tests, results, and implementation docs under `GraphRAG_Implementation/`; keep thesis-writing materials under `GraphRAG_skripsi/`; keep shared research data in the workspace-root `data/`. Root `AGENTS.md` coordinates both workflows.
- **Rationale:** Separate application engineering from thesis drafting while retaining one workspace-level research workflow.
- **Implementation:** Relocated `README.md`, `pyproject.toml`, `.python-version`, `.env.example`, `.gitignore`, and `docker-compose.yml` from the vault root into this project directory. README and project instructions now state the project-root command convention. Shared data folders live at the workspace root and are protected by the root `.gitignore`.
- **Verification:** Python compilation and `docker compose config --quiet` passed. A local `.env` was generated with a unique random password, restrictive file permissions, and no secret output; `.env` is excluded from version control.
- **M0 verification update:** `uv.lock` is present and `uv lock --check` plus `uv sync --locked --offline` pass. After limiting dotenv loading to the current project directory, both config unit tests pass; Ruff lint and format checks also pass. The researcher subsequently started Neo4j and reported that the connectivity smoke check passed. M0 acceptance criteria are complete.

## 2026-11-15 — M0 project scaffold

- **Observed:** The vault contained the project prompt and the general thesis checklist, but no Python project and no SOP/BPMN source data.
- **Decision:** Initialize the engineering scaffold at the vault root using Python 3.11 and `uv`, as requested in the project prompt.
- **Rationale:** Establish a reproducible environment before process modeling or ingestion.
- **Implementation choices:** Neo4j 5.26.5 container with the 5.28.2 Python driver; `python-dotenv` 1.1.0; pytest 8.3.5; Ruff 0.11.2. Direct dependencies and tools are exactly pinned. These versions are declared but lock resolution and installation remain unverified because PyPI DNS/network access failed in this environment.
- **Verification evidence:** `python3.11 -m compileall -q src tests` passed. Compose configuration validation passed using a temporary environment value. Pytest, Ruff, dependency sync, and the live database smoke check could not be executed because dependencies are not installed and network access to PyPI is unavailable; no database image was pulled.
- **Data boundary:** No real SOP content or credentials are present; the `.env` file and research data paths are excluded from version control.
- **Review queue:** The final BPMN-to-graph schema, source SOP selection, external LLM provider/model, and evaluation design require researcher approval at their respective milestones.

## 2026-11-15 — M1 synthetic BPMN parser and schema proposal

- **Observed:** No researcher-approved BPMN/SOP sources are present in the application project. Implementation and tests therefore use only a synthetic BPMN fixture.
- **Implementation:** Added a deterministic standard-library XML parser, structural/reference validator, and draft mapper. The parser preserves BPMN IDs, process/node kinds, sequence-flow conditions and default branches, lane references, participant process references, documentation, data artifact/association IDs, and source file path. Empty data-directory placeholders were moved under this application project and the raw/derived data folders are excluded by its `.gitignore`.
- **Schema proposal:** Added `docs/bpmn_graph_schema_proposal.md`. Draft output is tagged `proposal_pending_reviewer_approval`; no Neo4j ingestion uses it.
- **Verification:** `uv run pytest` passed (7 tests); `uv run ruff check .` and `uv run ruff format --check .` passed.
- **Limits:** This is not full BPMN XSD conformance validation. Diagram interchange/layout, extension elements, message flows, and multi-document graph key policy are not implemented. Data association mapping is a draft and needs review.
- **Decision needed:** Researcher review of lane-to-actor semantics, participant/pool representation, activity labels, stable multi-SOP keys, and data association representation before schema approval.

## 2026-11-15 — Shared data and workspace instruction filenames

- **Decision:** Place shared research data in the workspace-root `data/` so implementation and thesis-writing materials can reference the same files. The root `.gitignore` protects raw and derived datasets.
- **Implementation:** Moved `GraphRAG_Implementation/data/` to root `data/`. Renamed `Promt.md` to `GraphRAG_Implementation/AGENTS_IMPLEMENT.md`, the thesis checklist to `GraphRAG_skripsi/AGENTS_SKRIPSI.md`, and the research workflow checklist to root `AGENTS.md`; updated path references.
- **Boundary:** No research data was added or transformed; only `.gitkeep` placeholders moved.
