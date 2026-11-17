# GraphRAG SOP FSM

Proyek eksplorasi tanya jawab berbasis proses untuk SOP layanan akademik FSM Undip. Dua BPMN pilot telah disetujui PI, dibekukan, dan di-ingest ke Neo4j lokal menggunakan skema graph v0.1. Proyek masih berada pada fase eksplorasi; belum ada penulisan skripsi atau klaim hasil penelitian.

## Kebutuhan

- Python 3.11
- `uv`
- Docker Engine dengan Docker Compose

Direktori ini adalah root aplikasi. Data riset bersama berada di `../data/` pada root vault.

## Menjalankan lingkungan lokal

```sh
cd GraphRAG_Implementation
uv lock --python 3.11
uv sync --locked
cp -n .env.example .env  # hanya jika .env belum ada
# Isi .env dengan kredensial lokal yang kuat.
docker compose up -d
uv run python -m fsm_graphrag.neo4j_smoke
```

Neo4j Browser tersedia di `http://localhost:7474`; koneksi Bolt menggunakan `bolt://localhost:7687`. Perintah `docker compose down` menghentikan layanan tanpa menghapus volume. Jangan gunakan `docker compose down -v` kecuali penghapusan data memang diminta.

## Artefak pilot

- BPMN cuti: `../data/bpmn/pilot_sop_a.bpmn`
- BPMN aktif setelah cuti: `../data/bpmn/pilot_sop_b.bpmn`
- Manifest approval dan checksum: `results/m2/pilot_manifest.json`
- Traceability SOP–BPMN: `results/m2/sop_bpmn_traceability.csv`
- Laporan ingest dan validasi graph: `results/m2/ingestion_report.json`

Ingest ulang secara idempoten dengan `uv run python scripts/ingest_pilot_graph.py`. Skrip memeriksa konflik hash versi dan ID ganda sebelum menulis, memakai `MERGE`, dan memverifikasi statistik, kondisi, jalur, serta provenance setelah transaksi.

## Persiapan Text-to-Cypher

Pipeline ada di `src/fsm_graphrag/graphrag_pipeline.py`: `Text2CypherRetriever` dan `GraphRAG` menangani retrieval serta jawaban; wrapper memvalidasi Cypher, memeriksa `EXPLAIN`, membatasi hasil/timeout, memeriksa provenance dan citation, serta abstain bila bukti tidak cukup. Tes pada Neo4j lokal tanpa memanggil LLM: `uv run python scripts/graphrag_local_smoke.py`.

`OpenAILLM` library memakai OpenAI SDK Chat Completions. Atur `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TEMPERATURE`, dan `LLM_TIMEOUT_SECONDS` di `.env`. Endpoint harus kompatibel dengan `/v1/chat/completions`. Inisialisasi tidak mengirim request. Belum ada model dipilih atau panggilan API; PI perlu menyetujui model, izin penggunaan data, dan biaya sebelum request eksternal.

`NEO4J_READ_USER` dan `NEO4J_READ_PASSWORD` disediakan untuk kredensial database khusus baca saja. Compose saat ini memakai Neo4j Community Edition, yang tidak mendukung role terpisah. Karena itu driver produksi menolak fallback ke akun admin sampai PI memilih lingkungan yang dapat menyediakan hak read-only. Smoke lokal hanya memverifikasi query melalui `EXPLAIN` dan routing `READ`, bukan role kredensial.

## Verifikasi pengembangan

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/validate_pilot_bpmn.py
uv run python scripts/preflight_pilot_mapping.py
```

Parser dan mapper deterministik. Verifikasi lokal: `uv run pytest`, `uv run ruff check .`, dan `uv run ruff format --check .`. Status pekerjaan, batas interpretasi, dan keputusan PI tercatat di `docs/implementation_task_tracker.md`, `docs/text_to_cypher_contract.md`, dan `docs/decision_log.md`.
