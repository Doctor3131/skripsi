# 3. BAB II — TINJAUAN PUSTAKA

> [!note] Fungsi bab
> Menyediakan **landasan untuk pilihan metode dan evaluasi**. Tiap teori harus mempunyai alasan kemunculan dan hubungan eksplisit dengan pipeline penelitian.

## 2.1. Penelitian Terkait

- [ ] **Bangun strategi pencarian literatur**. Lakukan: tentukan kata kunci, sumber, periode, kriteria relevansi; simpan log pencarian.
- [ ] **Baca dan verifikasi sumber primer**. Lakukan: ekstraksi tujuan, dataset, desain, metrik, hasil, keterbatasan; jangan menyamakan metrik yang tidak kompatibel.
- [ ] **Buat matriks perbandingan**. Output: penulis/tahun, persoalan, metode, data, evaluasi, temuan, gap.
- [ ] **Lakukan sintesis tematik**. Lakukan: kelompokkan studi menurut masalah atau pendekatan, bahas kecenderungan/kontradiksi, lalu simpulkan celah penelitianmu.
- [ ] **Handoff ke agent**. Berikan matriks dan PDF/sitasi valid; minta sintesis lintas paper, bukan daftar abstrak berurutan.
- [ ] **Review klaim novelty**. Setiap kata “pertama”, “terbaik”, “belum ada” harus diperiksa secara ketat atau dihapus.

## 2.2. Chatbot Model

- [ ] **Pahami konsep dalam skripsi contoh**. Lakukan: bedakan jenis chatbot berbasis aturan, retrieval, dan generatif. **Untuk skripsimu:** cek apakah konsep ini memang relevan; jangan menyalinnya hanya karena ada di PDF contoh.
- [ ] **Handoff ke agent**. Jika tidak relevan, minta proposal padanan teori sesuai arsitektur ASAG, bukan paragraf chatbot.

## 2.3. Natural Language Processing

- [ ] **Tentukan tugas NLP yang benar-benar dijalankan**. Lakukan: sebutkan input teks, normalisasi, representasi, model, serta tahap penilaian/feedback. **Output:** diagram input → transformasi → output.
- [ ] **Handoff ke agent**. Berikan diagram pipeline dan referensi primer; minta teori yang menunjang operasi tersebut.

## 2.4. Deep Learning

- [ ] **Uji relevansi teori**. Lakukan: jelaskan apakah ada deep learning pada scoring/embedding/feedback, dan perannya. Jika tidak ada, ringkas atau hilangkan sesuai ketentuan pembimbing.
- [ ] **Handoff ke agent**. Jangan menambah teori deep learning yang tidak dipakai.

## 2.5. Transformer Model

- [ ] **Jelaskan kebutuhan komponen**. Lakukan: jika memakai transformer, tetapkan model, operasi, alasan, dan hubungan dengan data multibahasa. **Output:** ringkasan arsitektur dengan referensi.
- [ ] **Handoff ke agent**. Minta penjelasan mekanisme relevan, bukan sejarah panjang tanpa hubungan penelitian.

## 2.6. Large Language Model

- [ ] **Pastikan posisi LLM dalam arsitektur**. Lakukan: klasifikasikan apakah LLM melakukan penilaian, menghasilkan feedback, membantu anotasi, atau hanya dipakai agent drafting. **Penting:** AI untuk menulis skripsi **bukan** otomatis metode penelitian.
- [ ] **Catat batas model dan risiko**. Lakukan: model/version, prompt, ketidakpastian, evaluasi, biaya, dan reproduksibilitas jika LLM bagian metode.
- [ ] **Handoff ke agent**. Minta teori sesuai peran LLM yang benar-benar digunakan.

## 2.7. Chunking Process

- [ ] **Bedakan istilah**. Lakukan: periksa apakah “chunking dokumen” pada contoh RAG sepadan atau berbeda dengan **segmentasi jawaban siswa** dalam ASAG.
- [ ] **Definisikan segmentasi milikmu**. Lakukan: rumuskan unit potong, batas token/kalimat, Jaccard untuk menentukan batas potong, output segmen. **Output:** definisi, pseudocode, contoh input-output.
- [ ] **Handoff ke agent**. Wajib menyerahkan algoritma dan contoh nyata; larang agent menyebut segmentasi sebagai chunking RAG tanpa penjelasan.

## 2.8. Embedding Process

- [ ] **Identifikasi kebutuhan embedding**. Lakukan: apakah ada representasi semantik pada scoring atau feedback? Sebutkan fungsi, model, dimensi, kesamaan, dan cara mengevaluasinya jika digunakan.
- [ ] **Handoff ke agent**. Tulis hanya parameter/model yang benar-benar dipakai dan diverifikasi.

## 2.9. Vector Database

- [ ] **Periksa penggunaan nyata**. Lakukan: jika tidak memakai basis data vektor, jangan mempertahankan sebagai teori inti hanya demi mengikuti contoh.
- [ ] **Handoff ke agent**. Jika komponen ada, jelaskan penyimpanan, query, indeks, dan relasinya dengan arsitektur.

## 2.10. Retrieval-Augmented Generation

- [ ] **Putuskan relevansi RAG**. Lakukan: tentukan apakah RAG metode penelitian, pembanding, komponen feedback, atau hanya bagian dari skripsi contoh.
- [ ] **Handoff ke agent**. Jika tidak digunakan, jangan ditulis sebagai landasan metode skripsimu.

## 2.11. RASA Framework

- [ ] **Putuskan relevansi RASA**. Lakukan: konfirmasi apakah ada komponen RASA pada penelitianmu; bila tidak, perlakukan hanya sebagai studi contoh.
- [ ] **Handoff ke agent**. Arahkan teori padanan ke algoritma scoring, band relevance, autotune, atau rule mining yang benar-benar digunakan.

## 2.12. Evaluation Metrices

- [ ] **Rancang taksonomi evaluasi**. Lakukan: bedakan kualitas skor, kualitas feedback, efisiensi sistem, dan validitas eksperimen. **Output:** matriks metrik → variabel → interpretasi → batasan.
- [ ] **Jelaskan rumus dan contoh numerik**. Lakukan: pastikan tiap formula sesuai library/implementasi aktual dan jenis nilai.
- [ ] **Handoff ke agent**. Berikan definisi matematis resmi dan hasil hitung contoh; minta uraian dalam bahasa yang konsisten.

### 2.12.1. ROUGE Metric

- [ ] **Tentukan apakah dipakai**. Lakukan: jika menilai kemiripan feedback teks, tentukan ROUGE sebagai metrik leksikal, bukan otomatis ukuran kualitas pedagogis.
- [ ] **Periksa perhitungan**. Lakukan: pilih ROUGE-N/L, precision/recall/F1, preprocessing, contoh dan library.
- [ ] **Handoff ke agent**. Jangan mengklaim ROUGE membuktikan jawaban atau feedback “benar secara semantik”.

### 2.12.2. BERTScore Metric

- [ ] **Tentukan apakah dipakai**. Lakukan: definisikan model contextual embedding, bahasa, dan pengaruh parafrasa pada hasil.
- [ ] **Uji kecocokan lintas bahasa**. Lakukan: jika referensi dan output Indonesia sedangkan masukan Inggris/Jawa, jelaskan pasangan teks apa yang benar-benar dibandingkan.
- [ ] **Handoff ke agent**. Minta membedakan kesamaan semantik dengan evaluasi ketepatan dan kebermanfaatan feedback.

> [!tip] Adaptasi struktur Bab II
> Judul 2.2–2.12 di atas dipertahankan **agar terbaca sebagai jejak struktur PDF contoh**, bukan rekomendasi daftar isi final ASAG. Setelah audit relevansi, buat struktur Bab II versi penelitianmu dengan teori **ASAG, automatic feedback, cross-lingual processing, Jaccard segmentation, band relevance, autotune, rule mining, QWK, Spearman**, dan metode lain **hanya jika memang dipakai**.

---
