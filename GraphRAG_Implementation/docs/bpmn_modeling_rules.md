# Aturan Pemodelan BPMN Pilot

Status: `DISETUJUI PI DAN DIBEKUKAN` pada 2026-11-17. Checksum, cakupan persetujuan, dan bukti percakapan tercatat pada `results/m2/pilot_manifest.json`.

## Bahasa dan sumber

- Gunakan Bahasa Indonesia untuk nama proses, aktivitas, lane, event, kondisi, dokumentasi, pratinjau, dan bukti. Nama elemen XML dan atribut BPMN tetap mengikuti standar teknis.
- PDF naratif menjadi acuan utama untuk urutan dan kondisi proses. Tabel DOCX hanya melengkapi pelaksana dan metadata. Gambar logo atau flowchart yang tidak tersedia tidak dijadikan bukti proses.
- Jika PDF dan tabel DOCX berbeda, ikuti urutan/kondisi PDF untuk draf ini dan catat konflik pada traceability. Jangan menambahkan aktivitas yang hanya diasumsikan dari tanda `Y/N`.
- Isi setiap elemen dengan rujukan berkas dan nomor langkah. Pakai ID elemen stabil dan ID model yang disetujui PI.

## Batas representasi

- Gunakan event mulai dan selesai untuk membatasi tiap prosedur; gunakan aktivitas untuk tindakan yang dinyatakan sumber.
- Buat lane hanya jika pelaksana disebutkan dengan cukup jelas. Penerima laporan atau pihak yang dimintai tanda tangan tidak otomatis menjadi pelaksana aktivitas. Jika pelaksana pada kalimat pasif tidak jelas, jangan mengarang lane atau tugas.
- Pada SOP cuti, pertahankan aktivitas pemeriksaan kelengkapan dan alur bersyarat “persyaratan lengkap” menuju proses berikutnya. SOP tidak menjelaskan hasil jika persyaratan tidak lengkap; jangan tambahkan cabang, penolakan, atau pengembalian.
- Pada SOP cuti langkah 8, kata “dapat mengambil” dimodelkan sebagai pilihan: jalur bersyarat menuju aktivitas pengambilan surat, dengan jalur bawaan selesai setelah surat dikirim. PI menyetujui tafsir ini untuk model pilot pada 2026-11-17; ini tidak mengubah teks SOP sumber.
- Pada SOP aktif setelah cuti, modelkan pelaporan dan registrasi daring sebagai aktivitas mahasiswa. “Terdaftar sebagai peserta kuliah/mahasiswa aktif” dimodelkan sebagai hasil akhir, bukan tugas kantor terpisah.
- Data input/output hanya dimodelkan jika disebutkan. Relasi conceptual lintas SOP tidak dibuat sebagai edge BPMN/graph tanpa bukti proses atau keputusan semantik tersendiri.
- Identitas proyek: `FSM-SOP-CUTI-AKADEMIK` dan `FSM-SOP-AKTIF-SETELAH-CUTI`. ID model: `FSM-SOP-CUTI-AKADEMIK-BPMN-v1` dan `FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v1`.
- Model v1 dibekukan dan telah di-ingest ke Neo4j lokal setelah persetujuan PI. Tidak ada penggunaan layanan LLM eksternal.

## Status elemen dan konflik yang diketahui

- Cuti, langkah 3 menyebut penyerahan kepada Dekan lalu disposisi ke Subbag Akademik dan Kemahasiswaan. Pelaksana disposisi tidak eksplisit; representasikan sebagai label alur ke pemeriksaan, bukan tugas berlane.
- Cuti, langkah 4 menyatakan proses berikutnya bila lengkap. Tidak ada jalur untuk keadaan tidak lengkap.
- Cuti, langkah 7–8 menyebut surat dikirim lalu mahasiswa “dapat mengambil” surat di loket. Model memaknai “dapat” sebagai pilihan dan membuat akhir setelah pengiriman sebagai jalur bawaan; PI menyetujui tafsir ini untuk pilot pada 2026-11-17.
- Metadata persetujuan pada DOCX cuti menyebut Rektor, sementara uraian proses menyebut Dekan menandatangani Surat Izin Dekan. Model mengikuti langkah PDF dan menandai konflik metadata; PI menyetujui perlakuan ini untuk pilot pada 2026-11-17.
- SOP aktif setelah cuti mencantumkan status aktif sebagai langkah 3 di PDF, sedangkan tabel DOCX menempatkannya sebagai hasil. Model memperlakukannya sebagai hasil akhir; PI menyetujui tafsir ini untuk pilot pada 2026-11-17.
