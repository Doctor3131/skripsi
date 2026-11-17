# 10. Template kartu tugas

> [!tip] Cara menggunakan
> Duplikasi blok ini ke note terpisah per aktivitas besar (contoh: `Tasks/Segmentasi Jaccard.md`). Gunakan `[[tautan]]` ke dataset, arsitektur, jurnal, dan output eksperimen.

```markdown
---
type: thesis-task
status: todo
chapter: "[bab/subbab]"
owner: peneliti
---
# [Nama aktivitas]

## Mengapa ini perlu?
[Hubungan dengan RQ dan langkah sebelum/sesudah]

## Alur implementasi
Input → Validasi → Proses → Output → Evaluasi → Interpretasi

## Checklist
- [ ] Saya memahami tujuan dan definisi keberhasilannya
- [ ] Saya memahami input dan asal datanya
- [ ] Saya memahami algoritma/rumus/parameter yang digunakan
- [ ] Saya menjalankan implementasi pada data yang sah
- [ ] Saya memeriksa edge cases dan risiko leakage
- [ ] Saya menyimpan output dan provenance
- [ ] Saya menyiapkan brief + evidence untuk agent
- [ ] Saya mereview draf dan memverifikasi semua klaim

## Bukti (wajib)
- Dataset/split: [[...]]
- Kode/notebook: [[...]]
- Config + seed: [[...]]
- Tabel/gambar: [[...]]
- Klaim yang didukung: [[...]]

## Handoff ke agent
Tujuan: ...
Input: ...
Batasan: ...
Format output: ...

## Definition of Done
[Siapa memvalidasi, bukti apa yang harus ada, dokumen mana yang diperbarui]
```

---
# 11. Dashboard progres

> [!summary] Urutan pengerjaan yang disarankan
> Jalur proposal dan engineering berjalan paralel: **proposal Bab I–II** bertumpu pada masalah/RQ dan literatur terverifikasi; **proposal Bab III** menjelaskan rancangan sambil implementasi dan evaluasi berlangsung. Setelah hasil tersedia, sinkronkan Bab III, lalu susun Bab IV–V dan abstrak final setelah review PI.

| Tahap | Status | Artefak penentu | Siap drafting jika... |
|---|---|---|---|
| Masalah & RQ | ⬜ | `research_brief.md`, `rq_matrix.md` | tujuan dapat diuji |
| Audit data | ⬜ | inventaris, dictionary, audit | sumber dan kualitas jelas |
| Protokol evaluasi | ⬜ | split manifest, metrik, anti-leakage | test final terkunci |
| Literature review | ⬜ | matriks artikel tervalidasi | gap didukung sumber |
| Arsitektur/metode | ⬜ | diagram, pseudocode, konfigurasi | input-output jelas |
| Implementasi | ⬜ | kode, log, trace contoh | bisa dijalankan ulang |
| Eksperimen | ⬜ | prediksi mentah, tabel metrik | hasil dapat diaudit |
| Analisis | ⬜ | grafik dan error analysis | RQ terjawab dengan bukti |
| Proposal Bab I–III | ⬜ | draf + peta klaim/evidence | sumber terverifikasi; asumsi dan rencana diberi label |
| Bab IV–V dan abstrak final | ⬜ | hasil/evidence approved + draf | eksperimen selesai dan hasil disetujui PI |
| Finalisasi | ⬜ | format, referensi, lampiran | konsisten dan siap review |

## Tiga pertanyaan wajib sebelum mencentang tugas apa pun

1. **Dari mana data/informasi tahap ini berasal dan apakah saya boleh menggunakannya?**
2. **Apa transformasi/keputusan yang saya lakukan, mengapa, dan dapatkah saya mengulanginya?**
3. **Bukti spesifik apa yang akan menjadi tabel/gambar/kalimat pada skripsi, dan bisakah agent menulisnya tanpa mengarang?**

---

## Catatan asal dan adaptasi

- **Struktur contoh**: judul dan hierarki Bab I–V mengikuti daftar isi PDF skripsi RASA/RAG yang diunggah, termasuk subbagian 3.3.1.1 dan 3.3.2.5. Pada Bab IV struktur mengikuti penerapan hasil di contoh.
- **Adaptasi**: workflow data, *fixed test*, kalibrasi 10%, band relevance, autotune, segmentasi Jaccard, rule mining, ASAG multibahasa, evaluasi QWK/Spearman, serta protokol agentic adalah panduan untuk kebutuhan penelitianmu, **bukan klaim bahwa semuanya tertulis di PDF contoh**.
- **Batasan**: nama dan urutan subbab final harus disesuaikan dengan ketentuan pembimbing/prodi dan metodologi penelitian yang benar-benar dipilih.
