"""Kosongkan semua node dan relasi pada database proyek yang dikonfigurasi."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from neo4j import GraphDatabase

from fsm_graphrag.config import load_settings

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/m2/database_reset_report.json"


def _counts(session) -> dict[str, int]:
    nodes = session.run("MATCH (n) RETURN count(n) AS jumlah").single(strict=True)["jumlah"]
    relationships = session.run("MATCH ()-[r]->() RETURN count(r) AS jumlah").single(strict=True)[
        "jumlah"
    ]
    return {"node": nodes, "relasi": relationships}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-empty-all-data",
        action="store_true",
        help="konfirmasi PI untuk menghapus semua node dan relasi di database neo4j proyek",
    )
    args = parser.parse_args()
    if not args.confirm_empty_all_data:
        parser.error("operasi destruktif memerlukan --confirm-empty-all-data")

    settings = load_settings()
    if settings.neo4j_database != "neo4j":
        raise RuntimeError(
            "Reset dibatasi ke database proyek 'neo4j'; database terkonfigurasi berbeda."
        )

    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        driver.verify_connectivity()
        with driver.session(database=settings.neo4j_database) as session:
            before = _counts(session)
            session.run("MATCH (n) DETACH DELETE n").consume()
            after = _counts(session)

    if after != {"node": 0, "relasi": 0}:
        raise RuntimeError(f"Database belum kosong setelah reset: {after}")

    report = {
        "status": "DATABASE_GRAPH_DATA_RESET",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "database": settings.neo4j_database,
        "jumlah_sebelum": before,
        "jumlah_sesudah": after,
        "otorisasi": "Arahan eksplisit PI dalam percakapan pada 2026-11-17.",
        "cakupan": (
            "Semua node dan relasi; indeks, konstrain, volume, autentikasi, "
            "dan konfigurasi dipertahankan."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "Database neo4j kosong: "
        f"{before['node']} node/{before['relasi']} relasi dihapus; "
        f"laporan {OUTPUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
