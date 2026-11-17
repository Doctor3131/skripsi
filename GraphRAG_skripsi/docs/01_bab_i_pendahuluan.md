# 2. BAB I — PENDAHULUAN

> [!note] Fungsi bab
> Memindahkan pembaca dari **konteks luas → masalah yang didukung bukti → gap yang spesifik → pertanyaan terukur → tujuan dan batasan**. Bab ini tidak boleh menjanjikan hasil yang tidak didukung rancangan evaluasi.

## 1.1. Latar Belakang

- [ ] **Susun peta enam langkah**. Lakukan: konteks bidang → masalah nyata → urgensi/bukti → solusi yang pernah diteliti → kekurangan/pertanyaan belum terjawab → pendekatan/kontribusimu. **Output:** outline satu kalimat per langkah.
- [ ] **Kumpulkan bukti konteks dan masalah**. Lakukan: siapkan studi primer, statistik/observasi, dan bukti kasus spesifik; cocokkan setiap klaim dengan sumber. **Output:** tabel klaim-sumber.
- [ ] **Petakan state of the art**. Lakukan: kelompokkan pendekatan sebelumnya, bukan hanya menulis rangkuman paper satu per satu. **Output:** tabel perbandingan data/metode/metrik/kelemahan.
- [ ] **Tuliskan gap yang bisa diuji**. Lakukan: rumuskan apa yang belum dijawab atau belum teruji pada kondisi penelitianmu; jangan hanya menulis “belum ada aplikasi”.
- [ ] **Tutup dengan posisi penelitian**. Lakukan: jelaskan apa yang diteliti, mengapa pendekatan dipilih, dan apa yang akan diukur tanpa mengklaim sudah berhasil.
- [ ] **Handoff ke agent**. Beri problem brief, tabel literatur terverifikasi, konteks data, rancangan metode, batas klaim. Minta draf per paragraf dengan `evidence_id`.
- [ ] **Validasi aliran paragraf**. Pastikan kalimat pertama masing-masing paragraf berhubungan dengan paragraf sebelumnya dan mengerucut ke rumusan masalah.

## 1.2. Rumusan Masalah

- [ ] **Ubah gap menjadi RQ**. Lakukan: satu pertanyaan utama + subpertanyaan jika diperlukan, masing-masing punya variabel, unit, kondisi, dan ukuran. **Output:** `rq_matrix.md`.
- [ ] **Uji keterjawaban**. Lakukan: tunjukkan prosedur eksperimen dan tabel hasil yang secara langsung menjawab setiap RQ.
- [ ] **Handoff ke agent**. Minta redaksi ringkas berbasis RQ final; jangan izinkan menambah RQ baru tanpa persetujuan.

## 1.3. Tujuan Penelitian

- [ ] **Ubah setiap RQ menjadi tujuan operasional**. Lakukan: gunakan verba yang terukur (mengembangkan, membandingkan, mengevaluasi), sertakan keluaran evaluasi. **Output:** peta RQ → tujuan.
- [ ] **Uji konsistensi**. Tidak boleh ada tujuan yang tidak dievaluasi pada Bab IV.
- [ ] **Handoff ke agent**. Tulis tujuan paralel dengan rumusan masalah, tanpa klaim hasil.

## 1.4. Manfaat Penelitian

- [ ] **Identifikasi penerima manfaat**. Lakukan: pisahkan manfaat bagi peneliti/pengembang, pengguna, dan bidang keilmuan. **Output:** matriks hasil → pihak → manfaat.
- [ ] **Bedakan manfaat potensial dan terbukti**. Lakukan: jangan menyebut peningkatan efisiensi pengguna jika tidak ada pengujian yang mengukurnya.
- [ ] **Handoff ke agent**. Nyatakan manfaat sebagai potensi yang wajar dan sesuai ruang lingkup.

## 1.5. Ruang Lingkup

- [ ] **Daftarkan batas objek dan data**. Lakukan: soal, bahasa, populasi, jenis jawaban, skala skor, batas domain, dan data yang tidak digunakan.
- [ ] **Daftarkan batas metode dan evaluasi**. Lakukan: strategi sampling, model/algoritma, split, metrik, batas implementasi.
- [ ] **Jelaskan konsekuensi batasan**. Lakukan: tulis risiko generalisasi atau kemampuan yang tidak diklaim.
- [ ] **Handoff ke agent**. Berikan keputusan final dari `decisions/`; minta redaksi spesifik, bukan batasan generik.

## 1.6. Sistematika Penelitian

- [ ] **Sinkronkan dengan daftar isi final**. Lakukan: tulis fungsi Bab I–V berdasarkan konten yang benar-benar ada.
- [ ] **Handoff ke agent**. Boleh dibuat pada akhir penulisan, setelah semua struktur stabil.

---
