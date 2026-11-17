# SOP Source Audit — provisional, 2026-11-16

**Status: `PENDING_REVIEW` (M2-02 partial).** Seven PDFs and seven DOCX files were inspected locally. The PI approved the PDF/DOCX pairings and directed generation of project-local IDs on 2026-11-16. The IDs are not official SOP numbers; date-based version labels come from DOCX headers and are not verified as authoritative. PI instruction covers local processing for this inventory task; source-owner rights remain unverified and external service use is not authorized. No source was modified or sent externally. Hashes, IDs, version labels, and authorization scope are in [`data_inventory.csv`](data_inventory.csv).

## Scope and audit limits

- The PDFs contain readable narrative process descriptions (page 1). DOCX files contain SOP header metadata and activity/actor/quality-standard tables.
- The DOCX files do **not** contain distinct process-flow diagrams. Their embedded JPEGs resolve to the Undip logo; the IRS and active-after-leave files also contain a 70-byte transparent PNG. The documents provide an actor matrix with `Y/N` marks, but the marks' branch semantics and connector paths cannot be reliably reconstructed from extracted text alone.
- Accordingly, this is a text-PDF versus DOCX-table audit, not a visual-flowchart audit. PI later approved PDF as the primary source and the DOCX table as supplementary, so a visual flowchart is not required for these pilot drafts.
- The inventory assigns project-local IDs at the PI's direction; no official SOP numbers are asserted. DOCX header dates are recorded as source version labels only; effective dates and authoritative-version status are unknown. Local processing is authorized for this inventory task; source-owner rights are not verified and external service use is unauthorized.
- Locations below identify PDF page 1 and DOCX activity rows by their displayed sequence/description. No BPMN decisions have been made.

## Cross-document findings

1. The PI approved all seven PDF/DOCX pairings by title on 2026-11-16. Project-local IDs are assigned; no common official SOP number is visible in the extracted metadata.
2. All DOCX headers state creation date 24 December 2024. Six state a revision date in July/August 2025; the academic-leave DOCX states `-`. Effective dates are blank/not stated in the extracted headers.
3. A distinct flowchart is absent from every DOCX. The shared logo image is byte-identical in five files; the two remaining DOCX files share a different logo image. This repeated image is not process evidence.
4. The PDFs are narrative renderings and sometimes make conditions or step boundaries more explicit than the DOCX table. These differences are recorded below as source conflicts/ambiguities, not resolved interpretations.

## Per-SOP audit

### Permohonan Izin Cuti Akademik

- **Sources:** `../data/raw/SOP_Izin_Cuti_Akademik.pdf`, page 1; `../data/flowchart/SOP Permohonan Izin Cuti Akademik_rev.docx`, header and activity table.
- **Process evidence:** PDF lists eight actions: prepare/sign form and complete SIAP entry; obtain program-head approval; submit to Dean and route to Academic Affairs; completeness check/paraf; Dean signs; Subbag Sumber Daya numbers and distributes; Academic Affairs updates status/archives/sends; student may collect at counter. Required documents are form, transcript, latest SPP/UKT payment proof, KTM copy, and supporting documents. Maximum processing time: three working days. DOCX activity rows follow the same broad sequence and show a parallel actor matrix.
- **Actors visible:** student, program head, Academic Affairs and Student Affairs unit, Human Resources unit, Dean. PDF explicitly mentions disposition to Academic Affairs.
- **Condition/ambiguity:** PDF step 4 says “Jika lengkap” (if complete), while the DOCX step wording says the unit checks completeness, initials, and processes it without an equally explicit textual condition. DOCX `Y/N` matrix cells exist, but their branch meaning/path is not recoverable from the available text. No rejection/incomplete-document outcome is stated in the PDF; do not invent one.
- **Source conflict/review:** DOCX approval header says Rector; this is not mirrored in the extracted PDF narrative. Confirm source authority and whether the PDF is a derivative. Revision metadata differs in specificity: DOCX says `-`.
- **Gateway evidence:** one explicit completeness condition in PDF text; branch outcome is unspecified. Candidate for PI review if a documented branch is required.

### Legalisir Ijazah dan Transkrip

- **Sources:** `../data/raw/SOP_Legalisir_Ijazah_Dan_Transkrip.pdf`, page 1; `../data/flowchart/SOP Legalisir Ijazah dan Transkrip.docx`, header and activity table.
- **Process evidence:** six actions: alumnus submits copies and originals; Academic Affairs checks authenticity/conformity and stamps; supervisor initials; Dean/Vice Dean signs; staff retrieve and stamp; alumnus collects with original and signs collection book. Stated total maximum: three working days. DOCX table has the same six activities and actor columns.
- **Actors visible:** alumnus, Academic Affairs staff, Academic Affairs supervisor, Dean/Vice Dean.
- **Documents/outputs:** copies of diploma/transcript/accreditation certificate plus originals; application bundle; legalization approval; supervisor initial; signature; faculty stamp; legalized documents.
- **Conditions/ambiguities:** no explicit decision condition in the narrative. The first activity's “application bundle” is named as required material but its exact constituent set is described in the activity text. The DOCX image is only the logo, not a flow diagram.
- **Source conflict:** no material sequence conflict identified in extracted text. DOCX gives creation/revision metadata; PDF narrative does not.

### Pengajuan Proposal Kegiatan Organisasi Mahasiswa

- **Sources:** `../data/raw/SOP_Pengajuan_Proposal_Kegiatan_Organisasi_Mahasiswa.pdf`, page 1; `../data/flowchart/SOP Pengajuan Proposal Kegiatan Organisasi Mahasiswa_rev.docx`, header and activity table.
- **Process evidence:** five actions: student submits proposal for registration and room allocation (if event is at FSM); supervisor verifies compliance and initials; Vice Dean evaluates substance; Vice Dean endorses; student collects approved proposal. DOCX table follows the same order. Maximum service time: three days.
- **Actors visible:** student, advisor, department chair, BEM/student senate, Academic Affairs supervisor, Vice Dean. The narrative only explicitly assigns actions to the student, supervisor, and Vice Dean; involvement of other actor columns in specific steps is not clear in extracted text.
- **Documents/outputs:** proposal; supervisor initials; Vice Dean approval/endorsement; approved proposal.
- **Condition/ambiguity:** “if the activity is at FSM” qualifies registration/room allocation, but no separate branch outcome is described. The DOCX `Y/N` marks do not resolve which actors/conditions they encode.
- **Source conflict:** no material sequence conflict identified in extracted text. DOCX image is only the logo.

### Surat Pengajuan Rekomendasi Beasiswa

- **Sources:** `../data/raw/SOP_Pengajuan_Rekomendasi_Beasiswa.pdf`, page 1; `../data/flowchart/SOP Pengajuan Beasiswa_rev.docx`, header and activity table.
- **Process evidence:** five actions: student completes recommendation form at BAK; BAK checks/verifies; BAK initials and assigns letter number; Vice Dean signs; student collects and records receipt. PDF gives approximate times 30 minutes, one day, 10 minutes, two days, and five minutes, with total maximum three days 45 minutes. DOCX table gives the corresponding sequence and timings.
- **Actors visible:** student, BAK/Academic Affairs and Student Affairs, Vice Dean.
- **Documents/outputs:** recommendation letter form and legalized KHS; recommendation letter; collection record. PDF says the initial required/output bundle is a recommendation letter and legalized KHS.
- **Conditions/ambiguities:** no explicit branch in the narrative. DOCX `Y/N` markers are not interpretable as a branch without the visual connector/legend.
- **Source conflict:** no material sequence conflict identified in extracted text. Title wording varies slightly between filename and formal title (“Surat Pengajuan Rekomendasi Beasiswa”).

### Pengisian Isian Rencana Studi (IRS)

- **Sources:** `../data/raw/SOP_Pengisian_IRS.pdf`, page 1; `../data/flowchart/SOP Pengisian IRS_rev.docx`, header and activity table.
- **Process evidence:** six actions: pay tuition; her-registration in SIAP; fill/correct/print provisional IRS in SIAP; consult academic advisor; advisor approves online if courses and SKS are suitable; student may check IRS online if needed. PDF states each activity takes about 10 minutes and total maximum is three working days. DOCX activity table has the same sequence and condition language.
- **Actors visible:** student, academic advisor, program administrative staff (the narrative explicitly assigns steps to student/advisor; staff participation in specific actions is unclear).
- **Documents/outputs:** payment proof, IRS printout/online IRS, advisor approval in SIAP, IRS SIAP file.
- **Conditions/ambiguities:** suitability of courses/SKS is an explicit approval condition in both sources; “check IRS if needed” is optional. No alternative/revision path after an unsuitable selection is stated. The matrix does not supply an interpretable branch path.
- **Source conflict:** no material sequence conflict identified in extracted text. The qualification field contains a dotted placeholder in the DOCX.

### Permohonan Izin Aktif Setelah Cuti

- **Sources:** `../data/raw/SOP_Permohonan_Izin_Aktif_Setelah_Cuti.pdf`, page 1; `../data/flowchart/SOP Permohonan Izin Aktif Setelah Cuti_rev.docx`, header and activity table.
- **Process evidence:** PDF lists reporting with leave letter and KTM copy; online SSO registration; then student status as course participant/active student. It gives about five minutes for each listed item. DOCX table has two apparent action rows (reporting and SSO registration) and the active-student status appears as an output/result row, rather than an independently worded action.
- **Actors visible:** student, program head, Academic Affairs and Student Affairs. The text says the student reports to both program head and the unit.
- **Documents/outputs:** leave authorization letter, KTM photocopy, active-student status.
- **Conditions/ambiguities:** no explicit gateway or alternate path. It is unclear whether the PDF's third numbered item is a separate process activity or the result of registration; retain this as a step-boundary ambiguity.
- **Source conflict:** PDF treats active status as step 3; DOCX table structure suggests it may be an output/result. PI should resolve before BPMN modeling. DOCX image is only the logo.

### Permohonan Izin Keterlambatan Pembayaran UKT

- **Sources:** `../data/raw/SOP_Permohonan_Izin_Keterlambatan_Pembayaran_UKT.pdf`, page 1; `../data/flowchart/SOP Permohonan Izin Keterlambatan Pembayaran UKT_rev.docx`, header and activity table.
- **Process evidence:** eleven actions: student prepares/signs request; obtains advisor and program-head signatures; submits to supervisor; supervisor checks/initials; Vice Dean for Resources processes and signs; Subbag Sumber Daya processes; student submits to Vice Rector II via Academic Manager; Vice Rector II directs it to Finance Directorate; cashier opens payment system; student pays at bank. DOCX activity table has the same broad sequence. PDF states maximum service time of three days; detailed per-step durations are not present in extracted text.
- **Actors visible:** student, academic advisor, program head, Academic Affairs, Human Resources/Sumber Daya unit, Vice Dean, Directorate Academic Affairs, Finance/Accounting/Tax Directorate, Vice Rector II, Academic Manager, UKT cashier. Some actor names in DOCX lane headers do not map cleanly to the narrative steps.
- **Documents/outputs:** request form and supporting requirements; delayed-payment request letter; payment system access. The exact supporting-document list is not specified in the extracted narrative.
- **Conditions/ambiguities:** no explicit decision condition or rejection path stated. “Wakil Dekan Sumber Daya” and process wording in the DOCX are retained as written; no role/title normalization performed.
- **Source conflict:** no material sequence conflict identified in extracted text. DOCX contains a link for downloading the form; source content/requirements behind that link were not fetched or audited.

## PI review queue

1. Confirm whether official SOP numbers exist, which revision/effective date is authoritative, and the permitted usage scope. Project-local IDs and metadata-based version labels are already recorded; the PDF/DOCX pairings have PI approval.
2. The PI decided visual flowcharts are not a prerequisite for these pilots. No additional diagram input is required to continue.
3. Review the leave-SOP metadata/condition and active-after-leave step-boundary interpretations before BPMN freeze. The current drafts preserve the source gap rather than invent an outcome.
4. The PI selected Permohonan Izin Cuti Akademik and Permohonan Izin Aktif Kuliah Setelah Cuti on 2026-11-16. The latter corresponds to the available source titled “Permohonan Izin Aktif Setelah Cuti”; confirm the official title/ID during source approval. See `docs/decision_log.md`. The cuti completeness wording and active-after-cuti step boundary remain for PI review.

**Gate:** Pilot selection and the text-led source hierarchy are approved. This audit does not resolve semantic conflicts, approve BPMNs, or authorize graph ingestion. The BPMNs are drafts pending PI review; visual flowcharts are not a prerequisite.
