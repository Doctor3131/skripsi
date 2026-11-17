"""Validasi struktur BPMN pilot dan simpan laporan berbahasa Indonesia."""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from fsm_graphrag.bpmn import parse_bpmn_file, validate_bpmn

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT.parent
EXPECTED = {
    "pilot_sop_a.bpmn": {
        "sop_id": "FSM-SOP-CUTI-AKADEMIK",
        "model_id": "FSM-SOP-CUTI-AKADEMIK-BPMN-v1",
        "conditions": [
            (
                "Flow_Cuti_Lengkap",
                "persyaratan lengkap",
                "Task_PeriksaKelengkapan",
                "Task_TandaTanganDekan",
            ),
            (
                "Flow_Cuti_PilihDiambil",
                "mahasiswa memilih mengambil surat di loket",
                "Gateway_PilihanPengambilan",
                "Task_AmbilSuratCuti",
            ),
        ],
        "default_flow": "Flow_Cuti_TidakDiambil",
    },
    "pilot_sop_b.bpmn": {
        "sop_id": "FSM-SOP-AKTIF-SETELAH-CUTI",
        "model_id": "FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v1",
        "conditions": [],
        "default_flow": None,
    },
}


def _check(name: str, passed: bool, detail: str) -> dict:
    return {"pemeriksaan": name, "status": "LULUS" if passed else "GAGAL", "detail": detail}


def _all_xml_ids(root: ET.Element) -> list[str]:
    return [value for item in root.iter() if (value := item.get("id")) is not None]


def main() -> None:
    with (ROOT / "docs/data_inventory.csv").open(encoding="utf-8", newline="") as stream:
        inventory = {row["sop_id"]: row for row in csv.DictReader(stream)}
    with (ROOT / "results/m2/sop_bpmn_traceability.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        trace = list(csv.DictReader(stream))
    traced = {row["bpmn_id"] for row in trace}
    reports = []
    for filename, expected in EXPECTED.items():
        path = VAULT / "data/bpmn" / filename
        xml_root = ET.parse(path).getroot()
        document = parse_bpmn_file(path)
        issues = validate_bpmn(document)
        ids = _all_xml_ids(xml_root)
        unique_ids = len(ids) == len(set(ids))
        semantic_ids = {
            *(process.id for process in document.processes),
            *(node.id for node in document.nodes),
            *(flow.id for flow in document.sequence_flows),
            *(lane.id for lane in document.lanes),
            *(artifact.id for artifact in document.data_artifacts),
            *(association.id for association in document.data_associations if association.id),
            *(participant.id for participant in document.participants),
        }
        source = inventory[expected["sop_id"]]
        source_hashes_match = (
            hashlib.sha256((ROOT / source["raw_file"]).read_bytes()).hexdigest()
            == source["raw_sha256"]
            and hashlib.sha256((ROOT / source["flowchart_file"]).read_bytes()).hexdigest()
            == source["flowchart_sha256"]
        )
        conditional_flows = [flow for flow in document.sequence_flows if flow.condition]
        actual_conditions = [
            (flow.id, flow.condition, flow.source_ref, flow.target_ref)
            for flow in conditional_flows
        ]
        condition_ok = actual_conditions == expected["conditions"]
        default_ok = not expected["default_flow"] or any(
            flow.id == expected["default_flow"] and flow.is_default
            for flow in document.sequence_flows
        )
        model_text = " ".join(
            node.text or ""
            for node in xml_root.findall(
                ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}documentation"
            )
        )
        model_id_ok = expected["model_id"] in model_text
        trace_ok = semantic_ids <= traced
        checks = [
            _check(
                "XML terbaca sebagai BPMN 2.0", True, f"{len(document.processes)} proses ditemukan."
            ),
            _check("ID elemen XML unik", unique_ids, f"{len(ids)} ID ditemukan."),
            _check(
                "Referensi struktur dan alur valid",
                not issues,
                "; ".join(issue.message for issue in issues)
                or "Tidak ada masalah parser/validator.",
            ),
            _check("ID model sesuai keputusan PI", model_id_ok, expected["model_id"]),
            _check(
                "Kondisi/alur bersyarat sesuai sumber",
                condition_ok and default_ok,
                "Alur kelengkapan, pilihan pengambilan, dan cabang bawaan cocok dengan draf; "
                "SOP aktif tidak memiliki kondisi.",
            ),
            _check(
                "Hash sumber cocok dengan inventaris",
                source_hashes_match,
                "PDF dan tabel DOCX cocok dengan SHA-256 inventaris.",
            ),
            _check(
                "Elemen semantik terlacak",
                trace_ok,
                f"{len(semantic_ids)} elemen semantik dibandingkan dengan indeks traceability.",
            ),
        ]
        reports.append(
            {
                "berkas": filename,
                "sop_id": expected["sop_id"],
                "model_id": expected["model_id"],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "jumlah_node": len(document.nodes),
                "jumlah_sequence_flow": len(document.sequence_flows),
                "jumlah_lane": len(document.lanes),
                "jumlah_data_element": len(document.data_artifacts),
                "jumlah_asosiasi_data": len(document.data_associations),
                "pemeriksaan": checks,
                "status": "LULUS"
                if all(check["status"] == "LULUS" for check in checks)
                else "GAGAL",
            }
        )
    report = {
        "status": "LULUS" if all(item["status"] == "LULUS" for item in reports) else "GAGAL",
        "jenis_validasi": (
            "Parser dan pemeriksaan struktur/referensi lokal; bukan validasi XSD BPMN penuh."
        ),
        "catatan": [
            "Validasi struktur ini tidak menggantikan review semantik PI; approval tercatat "
            "di pilot_manifest.json.",
            "Skrip ini hanya membaca BPMN; hasil ingest Neo4j ada di ingestion_report.json.",
        ],
        "hasil": reports,
    }
    output = ROOT / "results/m2/bpmn_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validasi {report['status']}: {len(reports)} model; laporan {output.relative_to(ROOT)}")
    if report["status"] != "LULUS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
