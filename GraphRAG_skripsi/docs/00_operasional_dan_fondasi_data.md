# 0. Aturan operasional dan definisi selesai

## 0.1. Makna setiap checklist

- [ ] **Paham** — dapat menjelaskan *mengapa* tahap diperlukan, masukan, transformasi, keluaran, dan dampaknya terhadap tahap sesudahnya.
- [ ] **Kerjakan** — menjalankan kegiatan nyata, bukan hanya membuat teks yang mendeskripsikan kegiatan.
- [ ] **Buktikan** — menyimpan data, log, tabel, cuplikan kode, sumber pustaka, atau keputusan yang relevan.
- [ ] **Draft dengan agent** — menyerahkan konteks + bukti + batasan dan menerima draf yang bisa diverifikasi.
- [ ] **Review sendiri** — mencocokkan setiap klaim dengan artefak; barulah checklist dianggap selesai.

> [!warning] Aturan status
> **Jangan centang** jika hanya sudah mempunyai paragraf dari AI. Sebuah bagian baru selesai apabila pekerjaan penelitiannya benar, bukti tersedia, dan teksnya sesuai bukti.

## 0.2. Standar bahan yang diterima agent

- [ ] Siapkan `research_brief.md`: topik, tujuan, rumusan masalah, unit analisis, klaim kontribusi, batasan penelitian.
- [ ] Siapkan `architecture.md`: diagram pipeline, fungsi setiap komponen, input-output, versi kode/model, konfigurasi eksperimen.
- [ ] Siapkan `data_dictionary.md`: nama kolom, tipe, arti, asal, aturan missing value, data sensitif, contoh yang aman.
- [ ] Siapkan `experiment_registry.csv`: ID eksperimen, hipotesis, dataset/split, konfigurasi, seed, waktu eksekusi, artefak, status.
- [ ] Siapkan `evidence_index.md`: daftar klaim → file bukti → lokasi baris/tabel/gambar → status verifikasi.
- [ ] Siapkan `literature_matrix.md`: studi, masalah, metode, dataset, metrik, temuan, keterbatasan, DOI/URL yang diperiksa.
- [ ] Siapkan `writing_style.md`: bahasa, istilah baku, format sitasi, ketentuan kampus, gaya penulisan akademik.
- [ ] Tetapkan folder `drafts/`, `approved/`, `results/`, `figures/`, `references/`, `decisions/`.

**Alur:** data/arsitektur milik peneliti → validasi → arsip bukti → brief terbatas ke agent → draf dengan penanda bukti → review → versi disetujui.

## 0.3. Kebijakan integritas penelitian

- [ ] Tidak ada klaim empiris tanpa file atau tabel pendukung.
- [ ] Sitasi harus dapat ditelusuri ke sumber asli; agent dilarang mengarang DOI, halaman, atau kutipan.
- [ ] Hasil eksperimen yang belum dijalankan ditulis sebagai **rencana**, bukan **hasil**.
- [ ] Perubahan split, sampel, threshold, parameter, maupun prompt dicatat dengan tanggal dan alasan.
- [ ] Test set final diperlakukan sebagai data evaluasi terkunci, bukan bahan tuning atau pemilihan strategi.
- [ ] Bedakan *temuan faktual*, *interpretasi*, dan *dugaan* di setiap bab.
- [ ] Periksa ketentuan universitas tentang pemakaian AI dan pelaporan penggunaan AI.

---
# 1. Persiapan penelitian dan fondasi data

## 1.1. Dari ide ke pertanyaan penelitian

- [ ] **Definisikan masalah nyata**. Lakukan: tulis siapa terdampak, apa kegagalannya, mengapa penting, dan bukti masalah. **Output:** problem statement 3–5 kalimat. **Agent:** minta kritik kejelasan, bukan membuat masalah fiktif.
- [ ] **Tetapkan unit analisis**. Lakukan: putuskan satu baris data mewakili apa (misalnya satu jawaban siswa untuk satu soal). **Output:** definisi unit dan ID unik. **Agent:** gunakan unit ini konsisten di seluruh draf.
- [ ] **Bedakan gap praktik dan gap penelitian**. Lakukan: bandingkan kondisi nyata dengan keterbatasan metode/studi yang ada. **Output:** matriks gap dengan dukungan sumber. **Agent:** jangan menyatakan *belum pernah diteliti* tanpa bukti penelusuran.
- [ ] **Turunkan tujuan menjadi pertanyaan terukur**. Lakukan: tautkan tiap tujuan dengan metrik/bukti yang dapat dihasilkan. **Output:** tabel RQ → metode → metrik → hasil → kesimpulan.
- [ ] **Definisikan kontribusi**. Lakukan: pisahkan kontribusi metode, data, evaluasi, dan penerapan; jangan menganggap semua komponen pasti baru.

## 1.2. Audit data mentah

- [ ] **Inventaris sumber**. Lakukan: catat pemilik data, izin penggunaan, periode, jumlah, bahasa, format, kondisi, keterbatasan. **Output:** `data_inventory.csv`.
- [ ] **Buat skema kolom**. Lakukan: deklarasikan field wajib, key, aturan validasi dan hubungan antar tabel. **Output:** `data_dictionary.md`.
- [ ] **Audit kualitas**. Lakukan: hitung missing, duplikat, label inkonsisten, data tak terbaca, perbedaan skala nilai, sebaran per soal/bahasa. **Output:** `data_audit.ipynb` + tabel ringkasan.
- [ ] **Pisahkan data asli dari hasil olahan**. Lakukan: `raw/` dibuat read-only; pipeline menghasilkan `processed/` dengan versi dan transformasi tercatat.
- [ ] **Tentukan kebijakan privasi**. Lakukan: hilangkan identitas siswa, batasi akses dataset, anonimisasi contoh jawaban, jangan mengirim PII ke agent tanpa kebutuhan dan izin.
- [ ] **Susun dokumentasi provenance**. Lakukan: tetapkan asal setiap nilai ground truth dan cara memeriksanya. **Output:** file manifest + contoh rekonstruksi satu record.

> [!example] ASAG — cek skema minimum
> `question_id`, `language`, `question_text`, `reference_answer`, `student_answer`, `teacher_score`, `teacher_feedback`, `answer_id`. Jika sebuah field tidak tersedia atau tidak sah digunakan, dokumentasikan; jangan mengisinya dengan hasil rekaan AI. Penelitianmu memiliki 4 soal Inggris dan 5 soal Jawa; **pelaporan dan pemisahan data perlu menjaga identitas soal**.

## 1.3. Desain pengujian sebelum implementasi

- [ ] **Tentukan target prediksi dan keluaran**. Lakukan: jelaskan skor, skala, feedback, format keluaran, serta kriteria keberhasilan.
- [ ] **Tetapkan baseline yang masuk akal**. Lakukan: pilih pembanding yang menjawab RQ dan realistis dijalankan; jelaskan alasan pemilihan.
- [ ] **Definisikan split independen**. Lakukan: tentukan train/dev/calibration/test sesuai tujuan; simpan daftar ID tiap split dan seed sebelum melihat hasil akhir.
- [ ] **Pastikan independensi per soal**. Lakukan: bila evaluasi **per soal**, buat dan audit pembagian pada masing-masing `question_id`; jangan hanya melihat distribusi gabungan.
- [ ] **Dokumentasikan stratifikasi**. Lakukan: tentukan apakah strata berdasarkan skor guru/band yang telah sah tersedia, dan tangani strata terlalu kecil.
- [ ] **Identifikasi risiko leakage**. Lakukan: periksa apakah aturan, band, fitur, autotune, threshold, atau pemilihan sampel memanfaatkan data test atau statistik yang berasal dari test.
- [ ] **Kunci aturan pemilihan test**. Lakukan: bila sampel test dipilih melalui prosedur berbasis data, jelaskan apakah seleksi menggunakan target/fitur; evaluasi potensi bias dan hindari penggunaan hasil test untuk memilih metode.
- [ ] **Pisahkan eksperimen pengembangan dan evaluasi final**. Lakukan: seluruh tuning memakai train/dev yang sah; jalankan test final setelah konfigurasi diputuskan.
- [ ] **Pilih metrik sesuai jenis skor**. Lakukan: pertimbangkan QWK untuk kesepakatan ordinal dan Spearman untuk asosiasi peringkat; tambahkan metrik error jika relevan. Jelaskan makna, keterbatasan, dan skala masing-masing.
- [ ] **Definisikan metrik feedback**. Lakukan: terangkan apa yang dinilai (ketepatan konsep, kesesuaian guru, kebermanfaatan, bahasa), penilai, rubrik dan prosedur evaluasi.

> [!danger] Khusus workflow sampel 10% + band relevance/autotune
> Jangan menyamakan **pemilihan fixed test set**, **pemilihan sampel kalibrasi**, dan **pembuatan rule**. Ketiganya memiliki peran berbeda. Jika prosedur autotune/band relevance dijalankan dua kali, simpan konfigurasi, cakupan data, serta hasil terpisah; jangan biarkan informasi dari *fixed test* mengarahkan kalibrasi/pembentukan rule. Pemilihan stratified random untuk test umumnya lebih mudah diaudit, tetapi keputusan final tetap harus sesuai tujuan eksperimen dan disetujui pembimbing.

## 1.4. Siapkan jalur reproduksibilitas

- [ ] Catat versi lingkungan, dependency, hardware, model eksternal, prompt, dan random seed.
- [ ] Buat script/notebook yang dapat dijalankan ulang mulai dari data yang diizinkan hingga tabel hasil.
- [ ] Simpan output mentah per `answer_id`/`question_id` sebelum membuat agregasi.
- [ ] Buat aturan nama artefak (`EXP01_q03_seed42_metrics.csv` dsb.).
- [ ] Uji rekonstruksi minimal satu hasil tabel dari artefak mentah.

---
