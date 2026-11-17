"""Buat laporan proyeksi graf lokal tanpa menulis ke Neo4j."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from fsm_graphrag.bpmn import map_bpmn_to_graph, parse_bpmn_file

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT.parent
PILOTS = (
    (
        VAULT / "data/bpmn/pilot_sop_a.bpmn",
        "FSM-SOP-CUTI-AKADEMIK",
        "FSM-SOP-CUTI-AKADEMIK-BPMN-v1",
    ),
    (
        VAULT / "data/bpmn/pilot_sop_b.bpmn",
        "FSM-SOP-AKTIF-SETELAH-CUTI",
        "FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v1",
    ),
)


def inspect(path: Path, sop_id: str, model_id: str) -> dict:
    document = parse_bpmn_file(path)
    projection = map_bpmn_to_graph(document, sop_id=sop_id, model_id=model_id)
    node_ids = [node.properties["graph_id"] for node in projection.nodes]
    node_id_set = set(node_ids)
    dangling = [
        {
            "jenis": relationship.type,
            "sumber": relationship.source_id,
            "tujuan": relationship.target_id,
        }
        for relationship in projection.relationships
        if relationship.source_id not in node_id_set or relationship.target_id not in node_id_set
    ]
    duplicate_ids = sorted(key for key, count in Counter(node_ids).items() if count > 1)
    conditions = [
        {
            "bpmn_id": relationship.properties["bpmn_id"],
            "nama": relationship.properties["name"],
            "kondisi": relationship.properties["condition"],
            "cabang_bawaan": relationship.properties["is_default"],
            "dari": relationship.properties["source_bpmn_id"],
            "ke": relationship.properties["target_bpmn_id"],
        }
        for relationship in projection.relationships
        if relationship.type == "FLOWS_TO"
        and (relationship.properties["condition"] or relationship.properties["is_default"])
    ]
    return {
        "sop_id": sop_id,
        "model_id": model_id,
        "berkas": path.name,
        "sha256_bpmn": document.source_sha256,
        "status_skema_mapper": projection.schema_status,
        "jumlah_node": len(projection.nodes),
        "node_per_label": dict(sorted(Counter(node.label for node in projection.nodes).items())),
        "jumlah_relasi": len(projection.relationships),
        "relasi_per_jenis": dict(
            sorted(Counter(rel.type for rel in projection.relationships).items())
        ),
        "alur_bersyarat_dan_bawaan": conditions,
        "elemen_tidak_didukung": list(projection.unsupported_elements),
        "id_node_ganda": duplicate_ids,
        "relasi_dengan_endpoint_tidak_ditemukan": dangling,
        "proyeksi_valid_secara_struktural": not duplicate_ids and not dangling,
        "database_ditulis": False,
        "catatan": "Proyeksi dari BPMN draf; bukan persetujuan semantik atau ingest Neo4j.",
    }


def main() -> None:
    models = [inspect(*pilot) for pilot in PILOTS]
    report = {
        "status": "PRA_INGEST_DRAF_MENUNGGU_REVIEW_PI",
        "database_ditulis": False,
        "seluruh_proyeksi_valid_secara_struktural": all(
            model["proyeksi_valid_secara_struktural"] for model in models
        ),
        "models": models,
    }
    output = ROOT / "results/m2/mapping_preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Laporan pra-ingest ditulis: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
