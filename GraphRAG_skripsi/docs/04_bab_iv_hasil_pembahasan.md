# 5. BAB IV — HASIL DAN PEMBAHASAN

> [!note] Fungsi bab
> Bab III menjelaskan **apa dan bagaimana akan dilakukan**; Bab IV menunjukkan **apa yang benar-benar terjadi**, menyajikan buktinya, dan menjelaskan **mengapa hasil tersebut masuk akal**. Pola tiap subbab: **tujuan langkah → setting nyata → hasil/tabel/grafik → interpretasi → keterbatasan → kaitan ke langkah berikutnya**.

## 4.1. Pengembangan Chatbot RAG

- [ ] **Buat peta bukti untuk pipeline A**. Lakukan: cocokkan tiap tahap rancangan Bab III dengan file eksekusi dan tabel hasil. **Output:** matriks `metode → artefak → gambar/tabel → interpretasi`.

### 4.1.1. Data Preparation

- [ ] **Tampilkan karakteristik data aktual**. Lakukan: sajikan jumlah data, distribusi tiap soal/bahasa/skor, missing, duplikat, serta final split. **Output:** tabel yang dihasilkan script.
- [ ] **Perlihatkan contoh transformasi**. Lakukan: pilih contoh aman sebelum-sesudah preprocessing dan jelaskan dampaknya.
- [ ] **Bahas implikasi data**. Lakukan: apakah ada soal dengan sangat sedikit sampel, ketidakseimbangan skor, atau risiko bias?
- [ ] **Handoff ke agent**. Berikan summary CSV, tabel, dan contoh yang telah divalidasi; larang penambahan angka di luar artefak.

### 4.1.2. Data Modeling

- [ ] **Laporkan implementasi segmentasi dan fitur**. Lakukan: tampilkan contoh jawaban → batas Jaccard → segmen → band; sertakan parameter dan alasan konfigurasi.
- [ ] **Laporkan kalibrasi/rule mining**. Lakukan: catat jumlah sampel dan aturan per soal/band, kriteria dukungan aturan, konflik, dan cakupan.
- [ ] **Laporkan eksperimen parameter**. Lakukan: tampilkan konfigurasi yang benar-benar diuji; jelaskan dasar memilih konfigurasi final tanpa menggunakan test final.
- [ ] **Handoff ke agent**. Berikan log dan tabel; minta analisis deskriptif serta pertanyaan kritis, bukan hasil buatan.

### 4.1.3. Knowledge Store

- [ ] **Tunjukkan hasil penyimpanan artefak**. Lakukan: jelaskan skema rule/fitur/band yang tersimpan, jumlahnya, dan contoh record.
- [ ] **Verifikasi provenance**. Lakukan: dapatkah rule ditelusuri ke data train/calibration yang diperbolehkan?
- [ ] **Handoff ke agent**. Berikan skema aktual dan contoh anonim.

### 4.1.4. Data Retrieval

- [ ] **Tampilkan trace pencocokan aturan**. Lakukan: pilih kasus benar, keliru, dan tidak tercakup; tunjukkan aturan terpilih serta alasannya.
- [ ] **Analisis kegagalan**. Lakukan: jelaskan apakah kegagalan berasal dari preprocessing, segmentasi, band, rule, atau data.
- [ ] **Handoff ke agent**. Berikan sampel trace asli dengan klasifikasi error yang telah dicek.

### 4.1.5. LLM Generation

- [ ] **Tampilkan contoh feedback aktual**. Lakukan: bandingkan jawaban siswa, skor guru, feedback guru, skor prediksi, dan feedback sistem dalam contoh anonim.
- [ ] **Evaluasi ketepatan klaim feedback**. Lakukan: bahas apakah feedback didukung segmen/rule dan menggunakan bahasa Indonesia yang sesuai.
- [ ] **Handoff ke agent**. Berikan pasangan contoh terverifikasi dan larangan menyimpulkan kualitas hanya dari kemiripan teks.

### 4.1.6. Evaluation Process

- [ ] **Hitung metrik dari prediksi mentah**. Lakukan: jalankan fungsi QWK, Spearman, metrik error, dan/atau evaluasi feedback pada test yang sah.
- [ ] **Lakukan breakdown per soal**. Lakukan: sajikan jumlah test, metrik, dan catatan karakteristik tiap soal; jangan hanya rata-rata total.
- [ ] **Laporkan ketidakpastian**. Lakukan: jika ukuran sampel memungkinkan, tambahkan interval/variasi antar-run; jika tidak, jelaskan keterbatasannya.
- [ ] **Handoff ke agent**. Berikan tabel final yang diaudit, definisi metrik, dan visualisasi; minta interpretasi bukan re-estimasi.

## 4.2. Pengembangan Chatbot RASA

- [ ] **Buat peta bukti pipeline pembanding**. Lakukan: hubungkan konfigurasi pendekatan B, data uji, hasil prediksi, dan metrik dengan rancangan Bab III.

### 4.2.1. Data Preparation

- [ ] **Tunjukkan data yang digunakan pendekatan B**. Lakukan: verifikasi split dan preprocessing sesuai eksperimen. **Output:** jumlah dan manifest ID.

### 4.2.2. Data Training

- [ ] **Laporkan proses fit/kalibrasi aktual**. Lakukan: catat konfigurasi, jumlah data, jejak tuning, log dan aturan pemilihan model.

### 4.2.3. Prediction Stage

- [ ] **Perlihatkan prediksi pada data tetap**. Lakukan: contoh beberapa jawaban pada ID yang sama untuk semua pendekatan.

### 4.2.4. Result Generation

- [ ] **Perlihatkan keluaran akhir**. Lakukan: skor dan feedback pendekatan B, format, kekurangan, dan kasus fallback.

### 4.2.5. Evaluation Process

- [ ] **Hitung metrik pada fixed test yang sama**. Lakukan: cek jumlah/ID test identik; nyatakan bila metrik tak dapat dibandingkan karena kondisi berbeda.
- [ ] **Handoff ke agent untuk keseluruhan 4.2**. Berikan artefak pendekatan B terpisah; minta penulisan paralel dengan 4.1 tanpa menyalin pembahasan atau mengganti label metode.

## 4.3. Perbandingan Performa Kedua Model

- [ ] **Bangun tabel perbandingan berpasangan**. Lakukan: satu baris per `question_id` × ID test × eksperimen (atau agregat yang tetap terlacak). **Output:** `comparison_final.csv`.
- [ ] **Bandingkan QWK, Spearman dan metrik relevan**. Lakukan: jelaskan angka sekaligus maknanya; bedakan korelasi urutan dari kesepakatan skor.
- [ ] **Analisis per soal dan per bahasa**. Lakukan: cari pola spesifik soal Inggris/Jawa tanpa mengklaim generalisasi jika datanya terbatas.
- [ ] **Lakukan error analysis berpasangan**. Lakukan: identifikasi kasus ketika A benar–B salah, A salah–B benar, keduanya salah; periksa segmen/band/rule terkait.
- [ ] **Bahas trade-off**. Lakukan: kualitas skor, feedback, coverage, biaya komputasi, kompleksitas implementasi, stabilitas.
- [ ] **Hubungkan kembali ke RQ dan pustaka**. Lakukan: untuk setiap temuan, sebut RQ yang dijawab, bukti, interpretasi, dan keselarasan/perbedaan dari studi sebelumnya.
- [ ] **Akui batas inferensi**. Lakukan: jangan mengklaim kausalitas atau signifikansi tanpa desain/uji yang mendukung.
- [ ] **Handoff ke agent**. Berikan tabel final, grafik, matriks literatur, dan daftar pembatasan; agent menyusun narasi **temuan → bukti → analisis → implikasi**, peneliti menyetujui setiap kesimpulan.

---
