---
title: Checklist Penyusunan Skripsi — Research to Writing
type: research-workflow
status: active
created: 2026-11-15
tags:
  - skripsi
  - penelitian
  - checklist
  - obsidian
  - agentic-writing
aliases:
  - Thesis Master Checklist
---

# Checklist Penyusunan Skripsi — dari Riset sampai Naskah Final

Instruksi dan workflow penulisan ini berada di `GraphRAG_skripsi/AGENTS_SKRIPSI.md`.
Workflow penelitian bersama ada di root `../AGENTS.md`; data sumber bersama ada di `../data/`.

> [!abstract] Tujuan vault note ini
> Ini adalah **checklist eksekusi**, bukan hanya daftar isi. Setiap tugas mempunyai **apa yang dilakukan → bagaimana melakukannya → bukti/output → cara menyerahkannya kepada agent penulis → kondisi selesai**. Struktur Bab I–V mengikuti contoh skripsi *Perbandingan Kinerja Framework RASA dan RAG pada Chatbot Layanan Kemahasiswaan*; **metode RAG/RASA bukan metode wajib skripsimu**. Contoh penerapan khusus ASAG diberi tanda `ASAG`.

> [!important] Pembagian tanggung jawab
> **Peneliti (kamu)** menetapkan masalah, desain, sumber data, aturan eksperimen, memverifikasi hasil, dan menyetujui klaim. **Agent coding/analisis** membantu mengimplementasikan pipeline serta menghasilkan artefak yang bisa diaudit. **Agent penulis** mengubah artefak yang telah disetujui menjadi narasi akademik, bukan membuat fakta, angka, pustaka, atau keputusan penelitian baru.

## Fungsi AGENTS_SKRIPSI.md

File ini menjadi indeks dan katalog referensi untuk panduan rinci di folder `docs/`. Gunakan dokumen sesuai topik; perubahan isi checklist dilakukan pada dokumen topiknya, lalu tautan dan statusnya dirawat di indeks ini.

| Dokumen | Isi |
|---|---|
| [`docs/00_operasional_dan_fondasi_data.md`](docs/00_operasional_dan_fondasi_data.md) | Aturan operasional dan fondasi data |
| [`docs/01_bab_i_pendahuluan.md`](docs/01_bab_i_pendahuluan.md) | Bab I — Pendahuluan |
| [`docs/02_bab_ii_tinjauan_pustaka.md`](docs/02_bab_ii_tinjauan_pustaka.md) | Bab II — Tinjauan Pustaka |
| [`docs/03_bab_iii_metodologi.md`](docs/03_bab_iii_metodologi.md) | Bab III — Metodologi Penelitian |
| [`docs/04_bab_iv_hasil_pembahasan.md`](docs/04_bab_iv_hasil_pembahasan.md) | Bab IV — Hasil dan Pembahasan |
| [`docs/05_bab_v_penutup.md`](docs/05_bab_v_penutup.md) | Bab V — Penutup |
| [`docs/06_bagian_awal_pustaka_lampiran.md`](docs/06_bagian_awal_pustaka_lampiran.md) | Bagian awal, daftar pustaka, dan lampiran |
| [`docs/07_quality_gates.md`](docs/07_quality_gates.md) | Quality gates lintas bab |
| [`docs/08_protokol_agentic_review.md`](docs/08_protokol_agentic_review.md) | Protokol agentic drafting dan review |
| [`docs/09_template_tugas_dashboard.md`](docs/09_template_tugas_dashboard.md) | Template kartu tugas dan dashboard progres |

## Aturan penggunaan

- `AGENTS_SKRIPSI.md` berfungsi sebagai daftar isi dan rujukan pusat; detail checklist dan template berada di dokumen-dokumen `docs/` di atas.
- Ikuti gerbang persetujuan peneliti. Jangan menandai keputusan, bukti, atau draf sebagai disetujui hanya karena sudah ditulis.
- Instruksi riset lintas-workspace ada di root [`AGENTS.md`](../AGENTS.md); instruksi engineering ada di [`../GraphRAG_Implementation/AGENTS_IMPLEMENT.md`](../GraphRAG_Implementation/AGENTS_IMPLEMENT.md).
- Penyusunan proposal Bab I–III boleh berjalan paralel dengan implementasi. Bab I–II hanya menggunakan masalah dan pustaka yang dapat ditelusuri; Bab III boleh menjelaskan rancangan yang direncanakan. Tandai pilihan yang belum diputuskan PI sebagai sementara, dan perbarui metode agar sesuai implementasi aktual.
- Bab IV–V, abstrak final, kesimpulan, serta klaim hasil tidak boleh disusun sebagai temuan final sebelum eksperimen selesai, evidence diperiksa, dan PI menyetujui hasil.
