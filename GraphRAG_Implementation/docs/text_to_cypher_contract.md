# Kontrak Text-to-Cypher Neo4j GraphRAG — v1

Status: **pipeline lokal memakai `neo4j-graphrag`; panggilan model menunggu konfigurasi dan izin PI**. Implementasi memakai `Text2CypherRetriever`, `GraphRAG`, dan `OpenAILLM` melalui OpenAI SDK Chat Completions. Dependensi terkunci pada `neo4j-graphrag[openai]==1.22.0` dan driver Neo4j `6.4.1`.

## Konfigurasi

- `LLM_API_KEY`, `LLM_BASE_URL`, dan `LLM_MODEL` mengatur kredensial, endpoint kompatibel Chat Completions, dan model. `LLM_TEMPERATURE` default `0`; `LLM_TIMEOUT_SECONDS` default 30.
- `NEO4J_URI`, `NEO4J_USER`, dan `NEO4J_PASSWORD` adalah konfigurasi koneksi yang sama dengan Docker Compose.
- `NEO4J_QUERY_TIMEOUT_SECONDS` default 5; `NEO4J_DATABASE` menentukan database.
- Nilai rahasia hanya berada di `.env` lokal dan tidak dicatat dalam trace.

## Alur request

1. Validasi pertanyaan, `sop_id`, dan `model_id` terhadap dua pilot yang disetujui.
2. `GuardedText2CypherRetriever` menyusun prompt Bahasa Indonesia dengan schema graph dan meminta JSON berisi query serta parameter.
3. `CypherSafetyValidator` menolak query kosong, mutasi/admin, prosedur, multi-statement, komentar, elemen schema di luar allowlist, literal, dan parameter non-skalar. `LIMIT $maks_hasil` dipasang aplikasi dengan batas 50.
4. Driver menjalankan `EXPLAIN`; hanya query dengan `query_type == "r"` yang diteruskan. Query dan `EXPLAIN` menggunakan routing `READ` serta timeout transaksi.
5. `result_formatter` mengubah record menjadi evidence JSON ber-ID stabil. Provenance SOP, model, file/hash sumber, dan ID BPMN wajib ada; jika tidak, pipeline abstain sebelum panggilan jawaban.
6. `GraphRAG` memberikan konteks evidence kepada `OpenAILLM`. Jawaban harus berupa JSON dengan citation evidence ID; aplikasi memeriksa citation terhadap hasil retrieval.
7. Hasil/trace mencakup Cypher, status validasi/eksekusi, evidence, abstain, latensi, token bila tersedia, dan kategori error.

## Guardrails dan keterbatasan

- Query divalidasi sebelum `EXPLAIN`; query yang lolos tetap dibatasi oleh pemeriksaan `query_type`, routing `READ`, allowlist, parameter, batas hasil, dan timeout aplikasi.
- Docker Compose memakai Neo4j Community. Edisi ini tidak menyediakan role terpisah, sehingga akun pipeline memakai kredensial Compose dan tetap memiliki hak admin pada tingkat database. Guardrail pipeline membatasi operasi melalui aplikasi, bukan sebagai kontrol hak akses database; jangan memberi kredensial ini ke komponen yang tidak dipercaya.
- Smoke test lokal membuktikan konektivitas serta jalur validasi/eksekusi aplikasi, bukan izin database read-only.
- Endpoint generik harus kompatibel dengan OpenAI Chat Completions. Instalasi dan inisialisasi klien tidak mengirim request. Panggilan LLM belum dilakukan.
- `VERIFY_NEO4J_VERSION` library dinonaktifkan pada subclass karena versi server proyek diverifikasi lewat smoke test dan pemeriksaan library menggunakan `CALL dbms.components()` saat inisialisasi. Neo4j server 5.26.5 memenuhi rentang yang didukung package.
