# Prompt Text-to-Cypher Neo4j GraphRAG v1

Ubah pertanyaan menjadi satu query Cypher untuk graph SOP. Jangan menjawab pertanyaan dan jangan menambah fakta proses.

## Skema graph

{schema}

## Contoh format (opsional)

{examples}

## Pertanyaan

{query_text}

## Aturan wajib

- Gunakan hanya label, relasi, dan properti pada schema.
- Query dimulai dengan `MATCH`, mengembalikan evidence dengan `RETURN`, dan diakhiri `LIMIT $maks_hasil`.
- Gunakan parameter skalar untuk nilai; jangan gabungkan teks pertanyaan menjadi literal Cypher.
- Telusuri urutan dengan `FLOWS_TO`; ambil kondisi dan cabang bawaan dari relasi tersebut.
- Kembalikan properti provenance `sop_id`, `model_id`, `source_file_id`, `source_sha256`, dan ID BPMN.
- Jangan gunakan klausa mutasi/administrasi, prosedur, `CALL`, `LOAD CSV`, subquery, `UNION`, komentar, atau lebih dari satu statement.
- Jika query tidak dapat dibuat dari schema, isi `cypher` dengan string kosong dan `parameters` dengan objek kosong.
- Keluarkan hanya JSON valid tanpa markdown atau penjelasan.

## Bentuk keluaran

{{"cypher":"MATCH ... RETURN ... LIMIT $maks_hasil","parameters":{{"sop_id":"..."}}}}
