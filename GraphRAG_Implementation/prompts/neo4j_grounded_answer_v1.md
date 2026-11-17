# Prompt Jawaban Berbasis Evidence Neo4j GraphRAG v1

Konteks berikut berisi record graph SOP dalam JSON, termasuk `evidence_id` dan provenance.

Pertanyaan: {query_text}

Evidence:
{context}

Contoh format:
{examples}

## Aturan

- Jawab dalam Bahasa Indonesia hanya berdasarkan konteks evidence.
- Setiap klaim faktual harus didukung `evidence_id` yang tersedia.
- Uraikan urutan mengikuti relasi `FLOWS_TO`; sebut kondisi dan cabang bawaan sesuai evidence.
- Jangan mengarang kondisi yang tidak ada, termasuk jalur persyaratan tidak lengkap.
- Jangan menyimpulkan bahwa dua SOP tersambung sebagai satu alur langsung.
- Jika konteks kosong, kurang, ambigu, atau bertentangan, abstain.
- Keluarkan hanya JSON valid tanpa markdown.

## Format keluaran

{{"answer":"...","evidence_ids":["E-..."],"abstain":false}}

Untuk abstain gunakan `{{"answer":"Informasi belum cukup pada evidence SOP yang tersedia.","evidence_ids":[],"abstain":true}}`.
