"""Bekukan checksum BPMN pilot setelah persetujuan eksplisit PI."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT.parent
RESULTS = ROOT / "results/m2"
APPROVAL = {
    "status": "DISETUJUI_PI",
    "tanggal": "2026-11-17",
    "cakupan": [
        "SOP cuti: kata ‘dapat mengambil’ dimodelkan sebagai pilihan; jalur bawaan selesai "
        "setelah surat dikirim.",
        "SOP cuti: tindak lanjut persyaratan tidak lengkap tidak dimodelkan karena sumber "
        "tidak menyatakannya.",
        "Konflik penandatangan: uraian PDF yang menyebut Dekan diikuti; metadata DOCX yang "
        "menyebut Rektor dicatat sebagai konflik.",
        "SOP aktif setelah cuti: status aktif dimodelkan sebagai hasil akhir, bukan aktivitas "
        "kantor.",
    ],
    "bukti": "Persetujuan PI dalam percakapan pada 2026-11-17 (‘oke boleh’) setelah keempat "
    "tafsir ditinjau.",
}


def main() -> None:
    manifest_path = RESULTS / "pilot_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validation = json.loads((RESULTS / "bpmn_validation.json").read_text(encoding="utf-8"))
    if validation.get("status") != "LULUS":
        raise SystemExit("Validasi BPMN belum lulus; manifest tidak dibekukan.")
    for model in manifest["models"]:
        path = VAULT / "data/bpmn" / model["bpmn_file"]
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != model["bpmn_sha256"]:
            raise SystemExit(f"Checksum tidak cocok untuk {path.name}; manifest tidak dibekukan.")
    manifest["status"] = "DISETUJUI_PI_DIBEKUKAN"
    manifest["persetujuan_pi"] = APPROVAL
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Manifest BPMN disetujui PI dan checksum dibekukan.")


if __name__ == "__main__":
    main()
