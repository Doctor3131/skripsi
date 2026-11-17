"""Uji EXPLAIN dan eksekusi read-only memakai query tetap, tanpa LLM."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from neo4j import GraphDatabase

from fsm_graphrag.config import load_settings
from fsm_graphrag.text_to_cypher import (
    APPROVED_MODELS,
    APPROVED_SOPS,
    CypherSafetyValidator,
    Neo4jReadExecutor,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/m4/read_only_smoke.json"
QUERY = (
    "MATCH (p:Process {sop_id: $sop_id, model_id: $model_id}) "
    "-[:HAS_ELEMENT]->(a:Activity) "
    "RETURN p.sop_id AS sop_id, p.model_id AS model_id, a.bpmn_id AS bpmn_id, "
    "a.name AS nama, a.source_file_id AS berkas_sumber, "
    "a.source_sha256 AS source_sha256 LIMIT $maks_hasil"
)


def main() -> None:
    settings = load_settings()
    validator = CypherSafetyValidator()
    results = []
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        executor = Neo4jReadExecutor(driver, database=settings.neo4j_database)
        for sop_id in APPROVED_SOPS:
            safe = validator.validate(
                QUERY,
                {},
                sop_id=sop_id,
                model_id=APPROVED_MODELS[sop_id],
            )
            rows = executor.execute(safe)
            if not rows or any(not row.get("source_sha256") for row in rows):
                raise SystemExit(f"Evidence kosong/tanpa provenance untuk {sop_id}.")
            results.append(
                {
                    "sop_id": sop_id,
                    "model_id": APPROVED_MODELS[sop_id],
                    "jumlah_hasil": len(rows),
                    "contoh_bpmn_id": rows[0]["bpmn_id"],
                    "provenance_lengkap": True,
                }
            )
    report = {
        "status": "LULUS",
        "run_id": datetime.now(UTC).strftime("m4-read-smoke-%Y%m%dT%H%M%S%fZ"),
        "mode": "EXPLAIN_dan_transaksi_READ_ACCESS",
        "llm_dipanggil": False,
        "provider_eksternal_dipakai": False,
        "maks_hasil_per_query": 50,
        "hasil": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Smoke read-only lulus: {len(results)} SOP; {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
