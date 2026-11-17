# 4. BAB III — METODOLOGI PENELITIAN

> [!note] Fungsi bab
> Bab III adalah **kontrak sebelum eksekusi**: pembaca lain semestinya dapat memahami dan mengulang rancangan penelitian. Judul di bawah mengikuti *alur studi contoh*, sedangkan kotak `ASAG` mengingatkan padanan yang lebih cocok untuk penelitianmu.

## 3.1. Perolehan 7 Dokumen SOP

- [ ] **Pahami pola pengumpulan data sumber**. Lakukan: identifikasi asal, otorisasi, format, dan fungsi tujuh SOP pada contoh.
- [ ] **Adaptasikan ke datasetmu**. Lakukan: jelaskan sumber 9 soal, jawaban referensi, jawaban siswa, skor guru, feedback guru, periode/perizinan, dan unit data. **Output:** tabel inventaris dan bagan hubungan data.
- [ ] **Handoff ke agent**. Berikan skema nyata dan metadata sah; jangan meminta agent menebak jumlah peserta atau distribusi skor.

## 3.2. Wawancara dengan Pihak FSM

- [ ] **Pahami fungsi validasi pihak domain**. Lakukan: pada contoh, wawancara mengumpulkan FAQ dan jawaban acuan; identifikasi perannya untuk ground truth.
- [ ] **Adaptasikan ke ASAG**. Lakukan: jika guru membuat skor/feedback, dokumentasikan proses penilaian, rubrik, kualitas anotasi, dan bila ada, proses konfirmasi dengan guru. Jangan menulis “wawancara” jika tidak dilakukan.
- [ ] **Handoff ke agent**. Berikan protokol pengumpulan dan dokumen pendukung; agent menyajikan kegiatan faktual saja.

## 3.3. Pengembangan Chatbot

- [ ] **Tulis blueprint penelitian tingkat sistem**. Lakukan: gambar data → preprocessing → fixed test → calibration → fitur/segmentasi → rule mining → scoring/feedback → evaluasi. **Output:** `architecture.md` dan diagram yang telah disetujui.
- [ ] **Definisikan kontrak setiap modul**. Lakukan: catat masukan, keluaran, parameter, keputusan, serta dependensi.
- [ ] **Handoff ke agent**. Agent menjelaskan arsitektur dari gambar dan kontrak fungsi; tidak boleh menambah modul yang tidak ada.

### 3.3.1. Pengembangan Chatbot RAG

- [ ] **Pahami logika pipeline A dalam sumber**. Lakukan: pada studi contoh, jalurnya persiapan → pemodelan → knowledge store → retrieval → generation → evaluasi. **Untuk ASAG:** gunakan ini sebagai contoh penyajian pipeline bertahap, bukan sebagai kewajiban membuat RAG.

#### 3.3.1.1. Data Preparation

- [ ] **Tetapkan preprocessing**. Lakukan: buat langkah validasi ID, pembersihan teks, normalisasi seperlunya, dan perlakuan bahasa Inggris/Jawa secara eksplisit.
- [ ] **Tetapkan split per soal**. Lakukan: simpan manifest train/dev/calibration/test serta jumlah dan sebaran skor setiap soal.
- [ ] **Buat pemeriksaan leakage dan duplikasi**. Lakukan: cek ID identik, teks duplikat lintas split, informasi referensi yang boleh digunakan, dan operasi yang belajar dari target.
- [ ] **Handoff ke agent**. Berikan kode, konfigurasi, contoh sebelum-sesudah, tabel jumlah; bedakan rancangan Bab III dari angka hasil Bab IV.

#### 3.3.1.2. Data Modeling

- [ ] **Rumuskan setiap algoritma**. Lakukan: untuk Jaccard, definisikan tokenisasi, himpunan/perbandingan, jendela kandidat, kriteria batas potong, tie-breaking, dan penanganan teks pendek.
- [ ] **Definisikan sampel kalibrasi 10%**. Lakukan: jelaskan 10% dari populasi apa (per soal atau global), pemilihan, perlakuan band relevance/autotune, dan data mana yang dilarang disentuh.
- [ ] **Uraikan fitur dan band**. Lakukan: definisikan input → fitur → kategori/rentang band, serta hubungan ke pembentukan aturan.
- [ ] **Handoff ke agent**. Berikan notasi, rumus, pseudocode, contoh perhitungan, dan kode yang cocok. Agent tidak boleh merekayasa formula.

#### 3.3.1.3. Knowledge Store

- [ ] **Definisikan representasi yang disimpan**. Lakukan: simpan segmen, fitur, band, rule, provenance, serta relasi ID jawaban/soal. **Output:** skema artefak terstruktur.
- [ ] **Jelaskan versi pengetahuan**. Lakukan: siapa membuatnya, dengan data split apa, dan cara penyimpanannya agar audit/test dapat diulang.
- [ ] **Handoff ke agent**. Minta deskripsi struktur penyimpanan aktual; jangan menyatakan memakai vector DB bila hanya menggunakan CSV/JSON.

#### 3.3.1.4. Data Retrieval

- [ ] **Jelaskan cara mencari aturan relevan**. Lakukan: tentukan apakah sistem mengakses daftar rule, mencocokkan band, mengambil exemplar, atau melakukan retrieval semantik.
- [ ] **Tetapkan fallback dan konflik rule**. Lakukan: apa yang terjadi jika tidak ada rule, dua rule bertentangan, atau confidence rendah.
- [ ] **Handoff ke agent**. Berikan tabel contoh input → matched rule → keputusan; jangan mengganti logika dengan retrieval RAG jika tidak digunakan.

#### 3.3.1.5. LLM Generation

- [ ] **Definisikan generator feedback sebenarnya**. Lakukan: jika feedback berbasis rule/template, jelaskan mapping skor/band/rule → saran; jika memakai LLM, jelaskan prompt, konteks, pembatasan, model, dan versinya.
- [ ] **Pastikan bahasa target**. Lakukan: periksa bagaimana jawaban Inggris/Jawa menghasilkan feedback bahasa Indonesia dan bagaimana kesesuaian maknanya diuji.
- [ ] **Handoff ke agent**. Berikan contoh aktual input → keputusan → feedback dan kontrol halusinasi/ketidaksesuaian.

#### 3.3.1.6. Evaluation Process

- [ ] **Rancang evaluasi skor**. Lakukan: definisikan perhitungan QWK, Spearman, metrik tambahan, skala skor dan agregasi per soal.
- [ ] **Rancang evaluasi feedback**. Lakukan: tentukan metrik otomatis dan/atau penilaian manusia, rubrik, blind review jika relevan.
- [ ] **Rancang analisis kegagalan**. Lakukan: identifikasi kesalahan pada jawaban pendek, parafrasa, bahasa, band yang ambigu, dan rule yang tidak cocok.
- [ ] **Handoff ke agent**. Berikan protokol evaluasi final dan formula; belum boleh menulis hasil.

### 3.3.2. Pengembangan Chatbot RASA

- [ ] **Pahami pipeline pembanding dari contoh**. Lakukan: persiapan data → pelatihan → prediksi → generation → evaluasi. **Untuk ASAG:** jadikan contoh cara menjabarkan baseline atau pendekatan kedua yang benar-benar kamu uji.

#### 3.3.2.1. Data Preparation

- [ ] **Pastikan dataset pembanding adil**. Lakukan: tetapkan akses data yang sama atau jelaskan perbedaan perlakuan; semua pendekatan harus diuji pada test ID yang sama jika ingin dibandingkan langsung.
- [ ] **Handoff ke agent**. Berikan manifest split per eksperimen dan alasan bila konfigurasi data berbeda.

#### 3.3.2.2. Data Training

- [ ] **Jabarkan pelatihan/kalibrasi per pendekatan**. Lakukan: tetapkan algoritma, input, loss/objektif jika ada, fitur, parameter, seed, stopping, dan keluaran.
- [ ] **Handoff ke agent**. Berikan konfigurasi final; hindari narasi bahwa semua model dilatih jika sebagian berbasis rule.

#### 3.3.2.3. Prediction Stage

- [ ] **Tulis alur inferensi satu sampel**. Lakukan: masukan baru → preprocessing identik → segmentasi/fitur → rule/model → skor atau label. **Output:** contoh terverifikasi.
- [ ] **Handoff ke agent**. Gunakan satu trace nyata, bukan contoh numerik fiktif yang tersamar sebagai hasil.

#### 3.3.2.4. Result Generation

- [ ] **Definisikan output dan constraints**. Lakukan: format skor/feedback, pembulatan, batas skala, penjelasan rule, fallback dan bahasa.
- [ ] **Handoff ke agent**. Berikan spesifikasi JSON/tabel hasil dan contoh valid.

#### 3.3.2.5. Evaluation Process

- [ ] **Tetapkan fairness perbandingan**. Lakukan: satu fixed test, metrik identik, prosedur inferensi stabil, dan identitas soal konsisten.
- [ ] **Catat variasi eksperimen**. Lakukan: registrasikan seluruh eksperimen yang benar-benar dilakukan dan alasan perbedaan konfigurasi.
- [ ] **Handoff ke agent**. Berikan tabel design-of-experiments; jangan menyimpulkan metode unggul sebelum melihat hasil.

## 3.4. Perbandingan Performa Kedua Model

- [ ] **Tentukan uji perbandingan**. Lakukan: jelaskan membandingkan apa dengan apa, pada unit observasi yang mana, serta apakah agregasi per soal atau lintas soal sah dilakukan.
- [ ] **Rancang tabel dan visualisasi sebelum run**. Lakukan: siapkan template baris per soal × eksperimen × metrik, sebaran kesalahan, dan confidence interval bila memadai.
- [ ] **Tetapkan aturan interpretasi**. Lakukan: perbedaan angka tidak otomatis signifikan; tetapkan analisis statistik sesuai desain dan ukuran sampel bila diperlukan.
- [ ] **Handoff ke agent**. Berikan desain analisis; agent hanya boleh membantu menjalankan analisis yang telah disetujui.

> [!important] Pembatas sumber
> Subbab 3.1–3.4 di atas mempertahankan hierarki contoh, tetapi contoh ASAG adalah **adaptasi usulan**. Pada daftar isi skripsimu, sebaiknya **nama subbab mengikuti pipeline ASAG yang sesungguhnya**, bukan mempertahankan nama *Pengembangan Chatbot RAG/RASA*.

---
