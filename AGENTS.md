---
title: GraphRAG Research Checklist — BPMN × Neo4j × Text-to-Cypher
aliases:
  - FSM GraphRAG Research Checklist
  - GraphRAG Feasibility Tracker
created: 2026-11-15
type: project-research-checklist
status: exploration
phase: pre-writing
researcher_role: principal-investigator-reviewer
agent_role: research-engineering-assistant
related:
  - "[[AGENTS_SKRIPSI|Master Research Checklist]]"
tags:
  - skripsi
  - graphrag
  - bpmn
  - neo4j
  - text-to-cypher
  - research-engineering
  - agentic
  - obsidian
---

# GraphRAG Research Checklist — FSM SOP

> [!abstract] Tujuan
> Checklist **khusus tahap pra-penulisan** untuk eksplorasi *process-aware GraphRAG*: tujuh SOP layanan akademik/kemahasiswaan FSM Undip sebagai korpus induk, **dua SOP sebagai pilot**, model proses **BPMN 2.0 XML**, **Neo4j property graph**, pertanyaan → **LLM-generated Cypher** → query graph → evidence terstruktur → LLM menjawab. Dokumen ini **melengkapi, bukan menggantikan** [[AGENTS_SKRIPSI|Master Research Checklist]].

> [!danger] Batas fase — wajib dipatuhi agent
> Engineering dan penyusunan proposal dapat berjalan paralel. Bab I–III boleh disusun sebagai proposal berdasarkan sumber, literatur terverifikasi, keputusan PI, dan rancangan yang tersedia; rincian yang belum dipastikan harus ditandai sebagai rencana/asumsi dan diperbarui ketika engineering menghasilkan bukti. **JANGAN menyusun Bab IV–V, abstrak final, kesimpulan penelitian, atau klaim hasil/novelty yang belum didukung.** Hasil exploratory ≠ hasil final. Materi khusus ASAG pada master checklist **tidak berlaku** pada proyek GraphRAG ini.

> [!important] Pembagian peran
> **Peneliti (PI/Reviewer):** menyediakan tujuh SOP sumber, memilih dua SOP pilot, memverifikasi BPMN dan informasi proses, menyetujui graph schema, kebijakan pengujian, penggunaan LLM berbiaya, serta keputusan metodologis. **Agent:** menginventarisasi, mengusulkan, mengimplementasikan, menguji, mencatat evidence, melaporkan risiko; tidak boleh mengarang informasi SOP atau menyetujui pekerjaannya sendiri.

## Navigasi

- [[#Workspace dan workflow proyek]]

- [[#1. M0 — Repository dan environment]]
- [[#2. M1 — Inventaris dan pembacaan paper]]
- [[#3. M2 — Audit SOP dan pemodelan BPMN pilot]]
- [[#4. M3 — BPMN parsing dan graph ingestion]]
- [[#5. M4 — Text-to-Cypher dan grounded answer generation]]
- [[#6. M5 — Preliminary evaluation dan error analysis]]
- [[#7. M6 — Keputusan feasibility pra-penulisan]]
- [[#8. Peta keterkaitan dengan Master Checklist]]
- [[#9. Kontrak kerja agent dan reviewer]]
- [[#10. Template kartu tugas dan review gate]]
- [[#11. Dashboard status]]

## Workspace dan workflow proyek

Workspace ini memiliki dua area kerja dengan workflow masing-masing, serta satu direktori data di root vault:

- **Application engineering:** [`GraphRAG_Implementation/`](GraphRAG_Implementation/), dengan instruksi khusus di [`AGENTS_IMPLEMENT.md`](GraphRAG_Implementation/AGENTS_IMPLEMENT.md), status milestone di [`docs/implementation_task_tracker.md`](GraphRAG_Implementation/docs/implementation_task_tracker.md), dan keputusan di [`docs/decision_log.md`](GraphRAG_Implementation/docs/decision_log.md). Jalankan setup Python dan Docker dari folder ini.
- **Thesis writing:** [`GraphRAG_skripsi/`](GraphRAG_skripsi/), mengikuti [instruksi dan checklist penulisan](GraphRAG_skripsi/AGENTS_SKRIPSI.md). Proposal Bab I–III dapat berjalan paralel dengan engineering; Bab IV–V menunggu hasil dan evidence yang disetujui.
- **Research data:** [`data/`](data/) berada di root vault agar menjadi sumber bersama bagi engineering dan penulisan. Struktur data: `raw/`, `flowchart/`, `bpmn/`, `processed/`, `evaluation/`, `references/books/`, `references/papers/`, `diagram/`.

Checklist ini adalah koordinator riset: engineering menghasilkan artefak dan evidence; checklist penulisan mengatur alur penyusunan naskah. Jangan mencampur setup aplikasi dengan draft skripsi.

## Bahasa artefak

Gunakan Bahasa Indonesia untuk artefak engineering, teks yang tampil pada BPMN, dokumentasi, evidence, dan proposal skripsi. Nama elemen teknis wajib mengikuti standar. Penulisan proposal Bab I–III telah diizinkan untuk berjalan paralel dengan eksplorasi engineering. Bab IV–V tetap menunggu hasil terverifikasi dan persetujuan PI.

Semua path kode, konfigurasi, hasil, dan dokumen engineering relatif terhadap `GraphRAG_Implementation/`. Path data merujuk ke `data/` di root vault (dari folder implementation gunakan `../data/`).

---

# 0. Protokol dan definisi selesai

Gunakan status `TODO`, `IN_PROGRESS`, `BLOCKED`, `PENDING_REVIEW`, `APPROVED`, atau `REVISE`; checkbox hanya ditandai selesai setelah evidence diperiksa. Siklus kerja: pahami → implementasikan → verifikasi → serahkan evidence → review PI. Pisahkan fakta, asumsi, usulan, dan keputusan; setiap perubahan data/model/schema/prompt/evaluasi harus terlacak versinya. Lindungi izin dan data sensitif, dan jangan mengirim SOP ke layanan eksternal tanpa izin PI.

Task governance tetap dipertahankan: `GOV-01` batas fase; `GOV-02` status tugas; `GOV-03` gerbang tugas; `GOV-04` sumber kebenaran; `GOV-05` klasifikasi klaim; `GOV-06` kontrol perubahan; `GOV-07` keamanan/izin; `GOV-08` arsitektur; `GOV-09` penjelasan implementasi; `GOV-10` inventaris/provenance; `GOV-11` registri eksperimen; `GOV-12` indeks evidence; `GOV-13` antrean review; `GOV-14` matriks literatur/verifikasi indeks. Artefak engineering rinci berada di `GraphRAG_Implementation/docs/`; literatur dan writing workflow mengikuti checklist terkait.

**Definisi selesai:** tugas dipahami, benar-benar dijalankan, diverifikasi dengan pemeriksaan relevan, memiliki evidence yang dapat direproduksi, dan memperoleh approval PI bila keputusan reviewer diperlukan.

---

# 1. M0 — Repository dan environment

**Status: COMPLETE.** M0 selesai; rincian command, bukti, dan hasil ada di [`implementation_task_tracker.md`](GraphRAG_Implementation/docs/implementation_task_tracker.md) dan README engineering.

Task IDs selesai: `M0-01` audit awal; `M0-02` struktur repo/data; `M0-03` Python/uv; `M0-04` Docker Neo4j; `M0-05` koneksi; `M0-06` akses read-only; `M0-07` tests; `M0-08` logging; `M0-09` dokumentasi; `M0-10` reproduksi bersih.

**Gate M0:** lulus berdasarkan bukti M0 dan laporan smoke test PI pada 2026-11-15. Kebijakan biaya/akses layanan eksternal tetap memerlukan persetujuan PI saat digunakan.

---

# 2. M1 — Inventaris dan pembacaan paper

**Tujuan:** memahami landasan BPMN, process knowledge graph, Text-to-Cypher, dan evaluasi retrieval sebelum menetapkan desain final. **Bukan** menulis tinjauan pustaka skripsi.

**Alur:** daftar kandidat → verifikasi metadata dan indeks → baca full text → ekstrak pertanyaan/metode/hasil/batasan → bandingkan → review PI.

## Checklist tindakan

- [ ] `M1-01` **Inventaris paper.** **Lakukan:** buat satu record per versi publikasi; catat judul, penulis, tahun, DOI, URL, venue, tipe (jurnal/prosiding/preprint), dan versi. **Bukti:** `docs/literature_matrix.csv`. **Done:** tidak ada paper yang hanya dikenal dari judul.
- [ ] `M1-02` **Verifikasi Scopus secara ketat.** **Lakukan:** periksa artikel/record lewat Scopus atau sumber bibliografi yang jelas; rekam tanggal cek, link bukti, status `CONFIRMED_ARTICLE`, `VENUE_ONLY`, `NOT_VERIFIED`, `NOT_INDEXED` bila bukti cukup. **Jangan menyamakan indeks jurnal dengan indeks artikel.** **Bukti:** `docs/scopus_verification.md`. **Done:** tiap status punya bukti atau ketidakpastian eksplisit.
- [ ] `M1-03` **Baca paper BPMN→graph.** **Fokus:** mapping BPMN XML ke labeled property graph, sequence flow/gateway, provenance, graph validation. **Bukti:** reading card dengan kutipan/parafrase lokasi halaman.
- [ ] `M1-04` **Baca paper process-aware LLM/RAG.** **Fokus:** arsitektur retrieval, representasi proses, jenis pertanyaan, evaluation dataset dan error. **Bukti:** reading card.
- [ ] `M1-05` **Baca paper Text-to-Cypher.** **Fokus:** schema prompting, syntax vs semantic correctness, execution-guided repair, database safety. **Bukti:** reading card.
- [ ] `M1-06` **Baca paper RAG vs GraphRAG.** **Fokus:** kondisi GraphRAG unggul/kalah, query types, biaya, latency, fairness baseline. **Bukti:** comparative card.
- [ ] `M1-07` **Baca paper evaluasi BPMN.** **Fokus:** syntactic validity, completeness, semantic fidelity, gateways dan jalur alternatif; identifikasi metrik yang cocok. **Bukti:** quality rubric draft.
- [ ] `M1-08` **Ekstrak desain eksperimen (bukan hanya temuan).** **Lakukan:** catat korpus, unit analisis, dataset split, jumlah pertanyaan, metrik, baseline, prosedur anotasi dan ancaman validitas. **Bukti:** kolom metode/evaluasi pada matriks.
- [ ] `M1-09` **Buat peta kesamaan/perbedaan.** **Lakukan:** kelompokkan studi menjadi BPMN ingestion, process QA, Text-to-Cypher, GraphRAG evaluation. **Bukti:** `docs/literature_landscape.md`. **Done:** ada *claim–evidence mapping*, bukan klaim “belum ada yang pernah”.
- [ ] `M1-10` **Catat pertanyaan untuk PI.** **Lakukan:** tiap paper menghasilkan 2–3 pertanyaan kritis yang relevan dengan SOP FSM. **Bukti:** `docs/reading_questions.md`. **Done:** PI memahami pilihan teknis dan batas penelitian.

### Template reading card (duplikasi per paper)

```markdown
### PAPER-ID — Judul
- Identitas/DOI/venue/versi:
- Status Scopus + bukti + tanggal cek:
- Masalah/RQ penulis:
- Representasi data dan arsitektur:
- Pipeline implementasi:
- Dataset/ukuran/unit analisis:
- Baseline/metrik/prosedur pengujian:
- Temuan (sertakan lokasi halaman/tabel):
- Keterbatasan (dari paper vs inferensi kita):
- Apa yang dapat direplikasi/dikembangkan:
- Pertanyaan untuk PI:
- Status pembacaan: TODO / READ / VERIFIED_BY_PI
```

> [!question] Pertanyaan review PI — M1
> Apakah research gap yang disarankan memang didukung studi primer? Apakah paper terbit di venue yang relevan? Apakah eksperimen paper dapat direproduksi? Mana yang *text-to-graph*, mana yang *graph-to-answer*?

**Gate M1:** daftar bacaan prioritas, verifikasi bibliografi, dan literature matrix diterima PI. **Belum menyatakan novelty final.**

---

# 3. M2 — Audit SOP dan pemodelan BPMN pilot

**Tujuan:** memperoleh dua berkas BPMN 2.0 yang benar secara teknis dan setia pada sumber SOP yang disetujui. Berdasarkan keputusan PI 2026-11-16, PDF naratif adalah acuan utama urutan/kondisi dan tabel DOCX adalah pelengkap aktor/metadata; flowchart visual bukan prasyarat.

**Alur:** audit 7 SOP → pilih 2 pilot → inventaris proses → bangun BPMN XML → cek BPMN↔SOP → approve/freeze versi.

**Keputusan PI (2026-11-16):** SOP Permohonan Izin Cuti Akademik dan SOP Permohonan Izin Aktif Kuliah Setelah Cuti dipilih sebagai pilot; lihat alasan pada `GraphRAG_Implementation/docs/decision_log.md`.

## Checklist tindakan

- [ ] `M2-01` **Terima data resmi.** **Lakukan:** simpan PDF SOP dan tabel DOCX yang tersedia tanpa mengubah isi; catat pasangan yang disetujui PI, ID proyek, versi metadata, checksum, sumber, izin, dan format. Flowchart visual bukan prasyarat sesuai keputusan PI. **Bukti:** `docs/data_inventory.csv`. **Done:** sumber yang digunakan dan batas izinnya tercatat.
- [x] `M2-02` **Audit kelengkapan 7 SOP.** Audit teks PDF dan tabel DOCX tersedia; flowchart visual bukan prasyarat. **Bukti:** `GraphRAG_Implementation/docs/sop_audit.md`.
- [x] `M2-03` **Pilih 2 SOP pilot.** PI memilih SOP Permohonan Izin Cuti Akademik dan SOP Permohonan Izin Aktif Kuliah Setelah Cuti (2026-11-16); rationale dan batas approval ada di `GraphRAG_Implementation/docs/decision_log.md`. **Bukti:** keputusan PI tercatat; ID proyek tersedia, nomor resmi tidak ditemukan pada sumber.
- [x] `M2-04` Aturan notasi, sumber, dan batas interpretasi disetujui; lihat `GraphRAG_Implementation/docs/bpmn_modeling_rules.md`.
- [x] `M2-05` BPMN SOP cuti beserta pratinjau dan traceability dibuat, divalidasi, disetujui, dan dibekukan.
- [x] `M2-06` BPMN SOP aktif setelah cuti beserta pratinjau dan traceability dibuat, divalidasi, disetujui, dan dibekukan.
- [x] `M2-07` Validasi parser/struktur BPMN lulus; lihat `GraphRAG_Implementation/results/m2/bpmn_validation.json`. Review modeler BPMN khusus belum dilakukan.
- [x] `M2-08` PI menyetujui fidelitas semantik, tafsir pilihan pengambilan, konflik penandatangan, dan outcome status aktif pada 2026-11-17; lihat manifest dan decision log.
- [x] `M2-09` Jalur BPMN serta traversal graph untuk seluruh akhir proses tervalidasi; lihat `results/m2/path_check.md` dan `results/m2/ingestion_report.json`.
- [x] `M2-10` BPMN v1 dibekukan dengan checksum dan approval PI di `results/m2/pilot_manifest.json` (2026-11-17).

> [!warning] Perlakuan alur alternatif
> Jika SOP asli tidak mendefinisikan cabang "gagal/tidak lengkap", **jangan menambahkan jalur baru sebagai fakta SOP**. Tandai kekosongan sebagai keterbatasan data. Bila ingin membuat cabang simulasi, simpan terpisah dan jangan dicampur dengan pengujian SOP resmi.

> [!question] Pertanyaan review PI — M2
> Apakah aktivitas dan aktor berubah ketika dibuat BPMN? Apakah kondisi percabangan tersurat? Apa yang diketahui/tidak diketahui dari tujuh SOP? Mengapa dua SOP tersebut representatif untuk pilot?

**Gate M2:** Persetujuan PI atas kedua BPMN dicatat 2026-11-17 dan ingest lokal pilot telah dilakukan. Otoritas versi sumber dan hak publikasi tetap terbuka untuk penggunaan lanjutan.

---

# 4. M3 — BPMN parsing dan graph ingestion

Schema v0.1 disetujui PI. Rincian implementasi parser, mapper, dan ingestion ada di [`AGENTS_IMPLEMENT.md`](GraphRAG_Implementation/AGENTS_IMPLEMENT.md) dan [`implementation_task_tracker.md`](GraphRAG_Implementation/docs/implementation_task_tracker.md).

| Task ID | Ringkasan / bukti |
|---|---|
| `M3-01` | Schema v0.1 disetujui PI (2026-11-16); lihat proposal dan kontrak schema. |
| `M3-02` | BPMN→graph mapping diterapkan; seluruh elemen semantik pilot terpetakan, tidak ada elemen unsupported. |
| `M3-03` | Parser deterministik dan validasi kedua BPMN pilot lulus. |
| `M3-04` | Identitas stabil `[sop_id, model_id, bpmn_element_id]`; pertahankan ID BPMN asli. |
| `M3-05` | Constraint/index dan batasan edisi Neo4j; jangan jalankan migration pada DB live tanpa gate. |
| `M3-06` | Ingest fixture sintetis dan catat statistik/log. |
| `M3-07` | Dua BPMN approved/frozen di-ingest ke Neo4j Compose; run ID dan statistik tercatat di `results/m2/ingestion_report.json`. |
| `M3-08` | Fidelity 43 node/70 relasi, kondisi, cabang bawaan, lane, dan provenance tervalidasi. |
| `M3-09` | Dua jalur cuti dan satu jalur aktif dapat ditelusuri hingga seluruh event akhir. |
| `M3-10` | Provenance graph menyimpan ID SOP/model, ID BPMN, berkas sumber, dan hash; traceability sumber tersedia dalam CSV. |
| `M3-11` | Dokumentasikan backup/restore; reset DB perlu otorisasi eksplisit. |

**Gate M3:** ingest dan fidelity graph pilot selesai. Constraint/index Neo4j, fixture DB sintetis, backup/restore, dan review modeler masih perlu ditangani sebelum Text-to-Cypher.

---

# 5. M4 — Text-to-Cypher dan grounded answer generation

Rincian pipeline, safety controls, evidence, dan logging mengikuti M3 Text-to-Cypher di [`AGENTS_IMPLEMENT.md`](GraphRAG_Implementation/AGENTS_IMPLEMENT.md). Pertanyaan eksplorasi dan ground truth tetap perlu persetujuan PI.

| Task ID | Ringkasan / bukti |
|---|---|
| `M4-01` | Kontrak request/output dan trace lokal dibuat; lihat `docs/text_to_cypher_contract.md`. |
| `M4-02` | Katalog factual, sequential, conditional, multi-hop, paraphrase, dan unanswerable masih menunggu rancangan dan review PI. |
| `M4-03` | Entity/SOP aliases dan kebijakan ambiguitas berbasis evidence. |
| `M4-04` | Prompt v1 Bahasa Indonesia dan konteks skema aktual tersedia; adapter `neo4j-graphrag` memakai `OpenAILLM` untuk endpoint OpenAI-compatible. API key/model belum diisi dan penggunaan eksternal belum disetujui. |
| `M4-05` | Trace menyimpan query dan hasil validasi; validasi selalu terjadi sebelum eksekusi. |
| `M4-06` | Validasi allowlist/skema, larangan mutasi, `EXPLAIN`, routing `READ`, batas hasil, timeout, dan tes penolakan query diterapkan. Akun DB read-only belum tersedia; Neo4j Community tidak menyediakan role reader. |
| `M4-07` | Pemeriksaan syntax `EXPLAIN`, hasil eksekusi, penolakan skema, dan evaluasi semantic dipisah; evaluasi semantic menunggu test set. |
| `M4-08` | Parameter skalar, batas hasil, timeout, dan latensi retrieval diterapkan. |
| `M4-09` | Evidence mempertahankan provenance dan abstain bila provenance/ID evidence tidak valid. |
| `M4-10` | Prompt jawaban grounded dan jalur abstain tersedia melalui `GraphRAG`; belum ada panggilan LLM eksternal. |
| `M4-11` | Error query, provider, syntax, retrieval, dan evidence memiliki kategori; diuji secara lokal. |
| `M4-12` | Trace mendukung latensi, token, dan estimasi biaya per tahap bila dilaporkan provider; belum ada nilai provider nyata. |

Text-to-Cypher adalah graph-based retrieval, bukan sinonim untuk semua varian GraphRAG.
**Status 2026-11-17:** Pipeline `neo4j-graphrag` memakai `Text2CypherRetriever`, `OpenAILLM`, dan `GraphRAG`; 39 unit test, Ruff, dan smoke lokal lulus (`results/m4/graphrag_local_smoke.json`). Smoke menguji `EXPLAIN` dan query ber-routing `READ` tanpa panggilan LLM. Kredensial DB read-only belum tersedia karena deployment Neo4j Community tidak memiliki role reader. API key/model belum dikonfigurasi dan penggunaan endpoint eksternal belum disetujui; karena itu M4 masih menunggu hardening akses DB serta gate PI untuk LLM dan test set.
**Gate M4:** PI menyetujui provider/model, aturan penggunaan data dan biaya, prompt serta katalog pertanyaan sebelum panggilan LLM dan evaluasi.

---

# 6. M5 — Preliminary evaluation dan error analysis

**Tujuan:** mengetahui apakah ide layak dan di bagian mana pipeline masih gagal. **Belum** menyatakan metode mengungguli baseline secara final.

**Alur:** buat annotated pilot QA → jalankan pipeline → cek retrieval → cek final answer → kategorikan error → ukur biaya/latensi → diskusi feasibility.

## Checklist tindakan

- [ ] `M5-01` **Tetapkan tujuan pilot.** **Lakukan:** pilih apakah pilot memeriksa fidelity, Text-to-Cypher reliability, answer accuracy, atau efisiensi; hindari banyak klaim dari sedikit soal. **Bukti:** `docs/pilot_test_plan.md`. **Approval:** PI.
- [ ] `M5-02` **Susun ground truth pilot.** **Lakukan:** setiap pertanyaan punya SOP ID, expected answer, node/edge/condition yang mendukung, answerable flag; reviewed by PI (dan ahli SOP bila mungkin). **Bukti:** `data/evaluation/pilot_ground_truth.csv`. **Done:** label punya provenance.
- [ ] `M5-03` **Buat distribusi kategori.** **Lakukan:** hitung factual/sequential/conditional/multi-hop/unanswerable; hanya pertanyaan yang disokong dokumen masuk kategori answerable. **Bukti:** dataset summary. **Done:** tidak ada “kondisi palsu” disisipkan ke SOP nyata.
- [ ] `M5-04` **Buat metrik per lapisan.** **Lakukan:** graph fidelity (node/edge/path/condition), retrieval (success/evidence precision–recall), generation (correctness/faithfulness/abstention), operational (latency/tokens). **Bukti:** metric definitions, numerator/denominator. **Approval:** PI.
- [ ] `M5-05` **Tentukan evaluasi manual.** **Lakukan:** rubric benar/sebagian/salah, relevansi evidence, kesalahan alur; dua penilai bila tersedia. **Bukti:** `docs/annotation_guide.md`. **Done:** penilaian tidak ambigu.
- [ ] `M5-06` **Jalankan pilot dan simpan output per pertanyaan.** **Lakukan:** freeze data/model/prompt/schema, run ID, raw response, Cypher, rows, evidence, timing. **Bukti:** `results/m5/runs/<run-id>/`. **Done:** semua percobaan dapat diulang.
- [ ] `M5-07` **Hitung ringkasan metrik dengan script.** **Lakukan:** pisahkan per kategori dan per SOP; jangan hanya rata-rata keseluruhan. **Bukti:** metric CSV + script. **Done:** PI dapat merekalkulasi dari raw logs.
- [ ] `M5-08` **Error taxonomy.** **Lakukan:** tandai BPMN error, graph ingestion error, entity mismatch, invalid Cypher, valid-but-wrong Cypher, missing evidence, hallucinated generation, valid abstention. **Bukti:** error report dan contoh konkret.
- [ ] `M5-09` **Uji robustness ringkas.** **Lakukan:** parafrase, sinonim, pertanyaan out-of-scope, branch-specific questions; document failure. **Bukti:** robustness table. **Done:** bukan hanya happy path.
- [ ] `M5-10` **Rancang baseline (belum harus dieksekusi).** **Lakukan:** conventional RAG yang mendapat informasi setara dari BPMN sumber yang sama; tentukan fairness model, prompt, evaluasi. **Bukti:** baseline protocol. **Approval:** PI sebelum komparasi.
- [ ] `M5-11` **Buat laporan feasibility.** **Lakukan:** apa yang benar-benar berfungsi, kelas pertanyaan yang gagal, biaya, kompleksitas, risiko, kandidat iterasi. **Bukti:** `results/m5/feasibility_report.md`. **Done:** tanpa klaim generalisasi untuk 7 SOP dari 2 SOP pilot.

> [!question] Pertanyaan review PI — M5
> Apakah kesalahan berasal dari BPMN, graph, Cypher, atau LLM? Apakah pertanyaan kondisional benar-benar ada datanya? Apakah baseline akan menerima fakta yang identik? Apa yang belum dapat disimpulkan dari dua SOP pilot?

**Gate M5:** PI memeriksa data uji, subset hasil mentah, error cases dan rerun satu contoh sebelum menerima laporan.

---

# 7. M6 — Keputusan feasibility pra-penulisan

**Tujuan:** memutuskan desain penelitian berdasarkan bukti pilot, bukan tren GraphRAG.

**Alur:** ringkas evidence → bandingkan pilihan desain → review risiko → approve/revise/pivot → freeze keputusan untuk tahap riset berikutnya.

- [ ] `M6-01` **Jawab pertanyaan kelayakan.** **Lakukan:** apakah BPMN masuk graph tanpa hilang makna? apakah pertanyaan terbantu struktur graph? apakah Text-to-Cypher cukup reliabel? apakah evidence dapat ditelusuri? **Bukti:** decision matrix.
- [ ] `M6-02` **Bandingkan opsi arsitektur.** **Lakukan:** Text-to-Cypher murni vs penambahan entity linking/semantic retrieval; pertimbangkan biaya dan error, jangan menambah hybrid tanpa alasan. **Bukti:** architecture trade-off report.
- [ ] `M6-03` **Tentuskan batas klaim.** **Lakukan:** bedakan outcome pada pilot dengan hipotesis yang layak diuji pada 7 SOP. **Bukti:** `docs/research_claim_boundaries.md`. **Approval:** PI.
- [ ] `M6-04` **Kunci arah pengujian berikutnya.** **Lakukan:** usulkan kategori data evaluasi, baseline, kebijakan split dev/test, metrik, validasi ahli; hindari test leakage. **Bukti:** preregistration draft, bukan Bab III. **Approval:** PI.
- [ ] `M6-05` **Audit semua evidence.** **Lakukan:** periksa sumber, versi, skrip, config, raw logs, dokumentasi dan daftar limitasi; jangan buang eksperimen gagal. **Bukti:** `docs/evidence_audit.md`. **Done:** rerun dapat dilakukan.
- [ ] `M6-06` **Keputusan PI: lanjut, revisi, atau pivot.** **Lakukan:** PI memilih opsi dan alasannya. **Bukti:** `docs/decision_log.md` dengan tanggal/status approval. **Done:** perubahan fase perlu instruksi eksplisit PI.

> [!success] Exit criteria pra-penulisan
> 2 BPMN approved; graph Neo4j faithful; retrieval dan generasi punya trace; pilot error analysis tersedia; literatur inti sudah ditinjau; keputusan metodologis utama terdokumentasi; **belum ada isi Bab I–V yang ditulis agent**.

---

# 8. Peta keterkaitan dengan Master Checklist

> [!note] Prinsip sinkronisasi
> Master berisi kerangka **penelitian → naskah akhir**, sedangkan note ini adalah **implementasi khusus GraphRAG pada fase eksplorasi**. Referensi di bawah memakai nama bagian asli master, bukan membuat checklist ASAG menjadi berlaku untuk GraphRAG.

| Master Checklist (heading) | Proyek ini | Hubungan/keputusan |
|---|---|---|
| `0. Aturan operasional dan definisi selesai` | GOV-01 s.d. GOV-14 | Mengikuti integritas, evidence, review; drafting ditunda |
| `1.1. Dari ide ke pertanyaan penelitian` | M1, M5, M6 | Belum kunci gap/RQ sebelum literatur dan feasibility |
| `1.2. Audit data mentah` | M2 | Unit data: SOP, elemen BPMN, graph node/edge, pertanyaan; **bukan jawaban siswa** |
| `1.3. Desain pengujian sebelum implementasi` | M5–M6 | Fokus test cases, dev/final test, metrik proses/retrieval/answer |
| `1.4. Siapkan jalur reproduksibilitas` | M0, M3–M5 | Versioning repo, SOP, BPMN, schema, prompt, LLM, logs |
| `2. BAB I — PENDAHULUAN` | Proposal paralel | Boleh disusun sebagai proposal dari masalah, RQ, dan literatur yang didukung bukti; gap/kontribusi tetap tentatif sampai M1 ditinjau PI |
| `3. BAB II — TINJAUAN PUSTAKA` | M1 sebagai *reading* + proposal paralel | Sintesis proposal boleh ditulis dari sumber primer yang diverifikasi; jangan menyatakan novelty final sebelum review PI |
| `4. BAB III — METODOLOGI PENELITIAN` | Proposal paralel + M2–M6 engineering | Boleh mendeskripsikan rancangan yang direncanakan; tandai keputusan belum final dan sinkronkan dengan implementasi/evaluasi aktual |
| `5. BAB IV — HASIL DAN PEMBAHASAN` | M5 sebagai exploratory results | Menunggu eksperimen dan review PI; hasil exploratory bukan temuan final |
| `6. BAB V — PENUTUP` | Belum aktif | Tidak ada penyusunan kesimpulan skripsi |
| `8. Quality gates lintas bab` | Semua gates | Prinsip bukti dan konsistensi diterapkan sejak awal |
| `9. Protokol agentic drafting dan review` | GOV + kontrak agent | Saat ini hanya *research-engineering handoff*, bukan drafting |

### Sinkronisasi proposal dan engineering

- [x] `SYNC-01` Proposal Bab I–III boleh berjalan paralel dengan fase exploration berdasarkan instruksi PI; perubahan ke penulisan hasil/final tetap memerlukan persetujuan eksplisit PI.
- [ ] `SYNC-02` Keputusan graph schema, BPMN, baseline dan evaluasi dipindahkan ke evidence index master, bukan disalin sebagai hasil ilmiah yang sudah terbukti.
- [ ] `SYNC-03` Item ASAG yang tidak relevan ditandai `N/A — penelitian berbeda` pada *mapping* proyek, **tidak menghapus/mengubah** isi master asli.
- [ ] `SYNC-04` Semua task GraphRAG memiliki mapping ke bagian master atau alasan tugas tambahan (engineering khusus).
- [ ] `SYNC-05` Bab I–III dapat memakai sumber/literatur terverifikasi serta rancangan berstatus proposal; klaim implementasi/hasil hanya boleh memakai artefak `APPROVED`.

---

# 9. Kontrak kerja agent dan reviewer

## 9.1. Kontrak kerja agent engineering

Instruksi engineering dan format handoff terperinci ada di [`AGENTS_IMPLEMENT.md`](GraphRAG_Implementation/AGENTS_IMPLEMENT.md); panduan penulisan ada di [`AGENTS_SKRIPSI.md`](GraphRAG_skripsi/AGENTS_SKRIPSI.md). Gunakan task ID, laporkan evidence dan hasil aktual, lalu set `PENDING_REVIEW`; hanya PI yang menyetujui.

Urutan sumber kebenaran: SOP asli → BPMN approved → graph/query trace → log dan anotasi approved → full text serta metadata literatur terverifikasi. Jangan mengarang fakta, kondisi, graph edge, hasil, atau sumber; jangan mengubah SOP/BPMN approved diam-diam atau mengirim SOP terbatas ke layanan eksternal. Proposal Bab I–III boleh ditulis paralel dengan engineering, tetapi keputusan sementara harus diberi label dan klaim implementasi/hasil harus menunggu evidence yang disetujui. Bab IV–V tetap ditunda sampai hasil dievaluasi dan disetujui.

## 9.2. Aturan keputusan

Agent dapat menjalankan engineering reversible dalam kebijakan yang disetujui dan membantu proposal Bab I–III sesuai evidence yang tersedia. PI menyetujui interpretasi SOP/BPMN, pilot, schema final, evaluasi, biaya/layanan eksternal, tindakan destruktif, klaim final, serta penulisan Bab IV–V.

## 9.3. Format laporan milestone

Handoff milestone memuat task ID/status, input-output, perubahan/command, hasil verifikasi aktual, lokasi evidence, batasan/kegagalan, keputusan PI, dan next task. Untuk engineering gunakan format terperinci di `AGENTS_IMPLEMENT.md`.

---

# 10. Template kartu tugas dan review gate

Untuk tugas lintas milestone yang memerlukan handoff, gunakan kartu ringkas berikut. Tugas penulisan mengikuti [`docs/09_template_tugas_dashboard.md`](GraphRAG_skripsi/docs/09_template_tugas_dashboard.md).

```markdown
## TASK-ID — Judul
Status: TODO / IN_PROGRESS / PENDING_REVIEW / BLOCKED / APPROVED
Milestone + tujuan:
Input/source → langkah → output:
Evidence + verifikasi aktual:
Risiko/kegagalan; keputusan PI + tanggal:
```

---

# 11. Dashboard status

> [!info] Cara pakai
> Checkbox untuk pekerjaan baru tetap kosong sampai ada evidence; PI yang memberi status `APPROVED`. Status teknis rinci ada di tracker engineering. Task yang terhalang sumber/akses dicatat `BLOCKED` dengan alasan.

| Milestone | Deliverable review | Status awal | Approval PI |
|---|---|---|---|
| GOV | Roles, evidence policy, task registry | TODO | ☐ |
| M0 | Repository reproducible + smoke test Neo4j | COMPLETE (2026-11-15) | ✓ |
| M1 | Literature matrix + bukti indeks Scopus | TODO | ☐ |
| M2 | 2 BPMN pilot + traceability SOP | BPMN disetujui/dibekukan dan di-ingest lokal (2026-11-17); otoritas versi/hak sumber masih terbuka | ✓ BPMN / ☐ otoritas sumber |
| M3 | Schema v0.1 + Neo4j graph/fidelity | Schema approved; 43 node/70 relasi tervalidasi; hardening DB masih terbuka | ✓ schema / ✓ pilot graph |
| M4 | Text-to-Cypher + evidence-grounded answers | Pipeline dan smoke lokal lulus; menunggu akun DB read-only, persetujuan endpoint/biaya LLM, dan test set | ☐ |
| M5 | Pilot dataset + raw logs + error analysis | BLOCKED: M4 approval | ☐ |
| M6 | Feasibility decision | BLOCKED: M1–M5 | ☐ |

## Keputusan awal yang perlu disiapkan PI

- [ ] `PI-01` Tentukan lokasi repository dan model kerja agent (lokal/cloud, izin menjalankan commands).
- [ ] `PI-02` Sediakan SOP asli beserta hak penggunaan; jelaskan apakah boleh dikirim ke API LLM.
- [x] `PI-03` Pilih dua SOP setelah laporan audit kompleksitas M2-02: cuti akademik + aktif kuliah setelah cuti (2026-11-16); lihat decision log.
- [ ] `PI-04` Konfirmasi Neo4j Community atau Aura, sumber daya komputasi, serta batas biaya.
- [ ] `PI-05` Pilih LLM/protokol credential dan apakah tahap awal harus sepenuhnya lokal.
- [x] `PI-06` Review dan setujui schema v0.1 (2026-11-16).
- [ ] `PI-07` Setujui kebijakan evaluasi dan penilaian SOP sebelum pengujian resmi.

## Catatan penelitian yang belum boleh ditutup

- [ ] `OPEN-01` Apa kontribusi empiris yang bisa dipisahkan dari efek data BPMN yang lebih lengkap?
- [ ] `OPEN-02` Apa baseline conventional RAG yang menerima isi informasi setara?
- [ ] `OPEN-03` Bagaimana membedakan validitas sintaks Cypher, kebenaran logika, dan kualitas jawaban?
- [ ] `OPEN-04` Apa standar verifikasi/penilaian oleh ahli SOP yang realistis?
- [ ] `OPEN-05` Apakah tujuh SOP memiliki cukup jalur bersyarat untuk menguji keunggulan graph?

---

**Arah kerja:** *PI menyediakan sumber dan memutuskan → agent mengimplementasikan dan membuktikan → PI meninjau → baru lanjut gate berikutnya.*
