# Direktori Skripsi GraphRAG

> [!note]
> Direktori ini menyiapkan tempat kerja proposal dan penulisan skripsi. Draf proposal Bab I–III dapat dibuat paralel dengan engineering berdasarkan sumber dan literatur terverifikasi; Bab IV–V menunggu hasil eksperimen dan review PI.

## Struktur

```text
GraphRAG_skripsi/
├── AGENTS_SKRIPSI.md
├── ARCHITECTURE.md
├── README.md
├── docs/                   # Panduan yang dipecah per topik; terindeks di AGENTS_SKRIPSI.md
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
├── drafts/                 # Draf aktif, dipisah per bab
│   ├── bab-i/
│   ├── bab-ii/
│   ├── bab-iii/
│   ├── bab-iv/
│   └── bab-v/
├── approved/               # Naskah/bagian yang sudah direview peneliti
│   ├── bab-i/ ... bab-v/
├── evidence/               # Indeks dan bukti yang boleh dipakai untuk penulisan
├── results/                # Tabel, log, dan ringkasan hasil terverifikasi
├── figures/                # Gambar/diagram final untuk naskah
├── references/              # Inventaris paper/buku, verifikasi bibliografi, dan reading cards
└── decisions/               # Keputusan penelitian dan perubahan yang disetujui
```

## Alur penggunaan

1. Catat metode, keputusan, dan hasil aktual di lokasi engineering yang sesuai. Proposal Bab I–III boleh memakai rancangan sementara dengan status yang jelas.
2. Pindahkan atau tautkan hanya artefak yang sudah diverifikasi ke `evidence/`, `results/`, `figures/`, atau `references/`.
3. Buat draf per bab di `drafts/`; tandai klaim yang belum memiliki bukti.
4. Setelah review peneliti, simpan versi yang disetujui di `approved/`.

Folder kosong dipertahankan dengan `.gitkeep`. Ikuti [panduan dan checklist penyusunan skripsi](AGENTS_SKRIPSI.md) untuk gate, format handoff, dan kriteria selesai. Sumber data bersama berada di `../data/`; catatan engineering tetap berada di `../GraphRAG_Implementation/`.
