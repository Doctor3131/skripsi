"""Ingest dua BPMN pilot yang disetujui ke Neo4j secara idempoten."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from neo4j import Driver, GraphDatabase, ManagedTransaction

from fsm_graphrag.bpmn import map_bpmn_to_graph, parse_bpmn_file, validate_bpmn
from fsm_graphrag.bpmn.mapping import GraphMappingDraft, ProposedGraphRelationship
from fsm_graphrag.config import load_settings

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT.parent
OUTPUT = ROOT / "results/m2/ingestion_report.json"
PILOTS = (
    (
        VAULT / "data/bpmn/pilot_sop_a.bpmn",
        "FSM-SOP-CUTI-AKADEMIK",
        "FSM-SOP-CUTI-AKADEMIK-BPMN-v2",
    ),
    (
        VAULT / "data/bpmn/pilot_sop_b.bpmn",
        "FSM-SOP-AKTIF-SETELAH-CUTI",
        "FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v2",
    ),
)
ALLOWED_LABELS = {
    "Process",
    "Activity",
    "Event",
    "Gateway",
    "Lane",
    "DataElement",
    "Participant",
    "TextAnnotation",
    "DataAssociation",
}
ALLOWED_RELATIONSHIPS = {
    "HAS_ELEMENT",
    "IN_LANE",
    "ATTACHED_TO",
    "CONTAINS_LANE",
    "HAS_LANE",
    "REPRESENTS_PROCESS",
    "MESSAGE_FLOWS_TO",
    "ANNOTATES",
    "FLOWS_TO",
    "HAS_DATA_ASSOCIATION",
    "HAS_SOURCE",
    "HAS_TARGET",
}


def _relationship_id(relationship: ProposedGraphRelationship) -> str:
    explicit = relationship.properties.get("graph_id")
    if explicit:
        return str(explicit)
    identity = [
        "relationship",
        relationship.type,
        relationship.source_id,
        relationship.target_id,
        relationship.properties.get("bpmn_id"),
        relationship.properties.get("association_direction"),
    ]
    payload = json.dumps(identity, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _projection_rows(projection: GraphMappingDraft) -> tuple[list[dict], list[dict]]:
    node_rows = []
    ids: set[str] = set()
    for node in projection.nodes:
        if node.label not in ALLOWED_LABELS:
            raise ValueError(f"Label tidak didukung: {node.label}")
        graph_id = str(node.properties["graph_id"])
        if graph_id in ids:
            raise ValueError(f"ID graf node berulang: {graph_id}")
        ids.add(graph_id)
        node_rows.append({"graph_id": graph_id, "properties": node.properties})

    relationship_rows = []
    relationship_ids: set[str] = set()
    for relationship in projection.relationships:
        if relationship.type not in ALLOWED_RELATIONSHIPS:
            raise ValueError(f"Tipe relasi tidak didukung: {relationship.type}")
        if relationship.source_id not in ids or relationship.target_id not in ids:
            raise ValueError(
                f"Endpoint relasi {relationship.type} tidak terproyeksi: "
                f"{relationship.source_id} → {relationship.target_id}"
            )
        graph_id = _relationship_id(relationship)
        if graph_id in relationship_ids:
            raise ValueError(f"ID graf relasi berulang: {graph_id}")
        relationship_ids.add(graph_id)
        properties = {**relationship.properties, "graph_id": graph_id}
        relationship_rows.append(
            {
                "graph_id": graph_id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "properties": properties,
            }
        )
    return node_rows, relationship_rows


def _write_projection(
    tx: ManagedTransaction,
    node_groups: dict[str, list[dict]],
    relationship_groups: dict[str, list[dict]],
) -> dict:
    node_count = 0
    relationship_count = 0
    for label, rows in sorted(node_groups.items()):
        result = tx.run(
            f"UNWIND $rows AS row MERGE (n:{label} {{graph_id: row.graph_id}}) "
            "SET n += row.properties RETURN count(n) AS jumlah",
            rows=rows,
        ).single(strict=True)
        node_count += result["jumlah"]
    for rel_type, rows in sorted(relationship_groups.items()):
        result = tx.run(
            "UNWIND $rows AS row "
            "MATCH (s {graph_id: row.source_id}), (t {graph_id: row.target_id}) "
            f"MERGE (s)-[r:{rel_type} {{graph_id: row.graph_id}}]->(t) "
            "SET r += row.properties RETURN count(r) AS jumlah",
            rows=rows,
        ).single(strict=True)
        relationship_count += result["jumlah"]
    return {"node_ditulis": node_count, "relasi_ditulis": relationship_count}


def _read_existing_state(driver: Driver, database: str, projections: list[dict]) -> dict:
    sop_ids = [projection["sop_id"] for projection in projections]
    graph_node_ids = [
        row["graph_id"] for projection in projections for row in projection["node_rows"]
    ]
    graph_relationship_ids = [
        row["graph_id"] for projection in projections for row in projection["relationship_rows"]
    ]
    with driver.session(database=database) as session:
        node_counts = [
            dict(record)
            for record in session.run(
                "MATCH (n) WHERE n.sop_id IN $sop_ids "
                "RETURN n.sop_id AS sop_id, n.model_id AS model_id, labels(n) AS labels, "
                "count(*) AS jumlah ORDER BY sop_id, model_id, labels",
                sop_ids=sop_ids,
            )
        ]
        relationship_counts = [
            dict(record)
            for record in session.run(
                "MATCH ()-[r]->() WHERE r.sop_id IN $sop_ids "
                "RETURN r.sop_id AS sop_id, r.model_id AS model_id, type(r) AS jenis, "
                "count(*) AS jumlah ORDER BY sop_id, model_id, jenis",
                sop_ids=sop_ids,
            )
        ]
        source_hash_conflicts = []
        for projection in projections:
            hashes = session.run(
                "MATCH (n) WHERE n.sop_id = $sop_id AND n.model_id = $model_id "
                "RETURN collect(DISTINCT n.source_sha256) AS hashes",
                sop_id=projection["sop_id"],
                model_id=projection["model_id"],
            ).single()
            existing_hashes = set(hashes["hashes"] if hashes else ()) - {None}
            if existing_hashes and existing_hashes != {projection["source_sha256"]}:
                source_hash_conflicts.append(
                    {
                        "sop_id": projection["sop_id"],
                        "model_id": projection["model_id"],
                        "hash_lama": sorted(existing_hashes),
                        "hash_baru": projection["source_sha256"],
                    }
                )
        duplicate_nodes = session.run(
            "UNWIND $ids AS graph_id OPTIONAL MATCH (n {graph_id: graph_id}) "
            "WITH graph_id, count(n) AS jumlah WHERE jumlah > 1 "
            "RETURN collect({graph_id: graph_id, jumlah: jumlah}) AS duplikat",
            ids=graph_node_ids,
        ).single()["duplikat"]
        duplicate_relationships = session.run(
            "UNWIND $ids AS graph_id OPTIONAL MATCH ()-[r {graph_id: graph_id}]->() "
            "WITH graph_id, count(r) AS jumlah WHERE jumlah > 1 "
            "RETURN collect({graph_id: graph_id, jumlah: jumlah}) AS duplikat",
            ids=graph_relationship_ids,
        ).single()["duplikat"]
    return {
        "node_eksisting_menurut_model_dan_label": node_counts,
        "relasi_eksisting_menurut_model_dan_jenis": relationship_counts,
        "konflik_hash_model": source_hash_conflicts,
        "id_node_berulang_di_database": duplicate_nodes,
        "id_relasi_berulang_di_database": duplicate_relationships,
    }


def build_projections() -> list[dict]:
    projections = []
    for path, sop_id, model_id in PILOTS:
        document = parse_bpmn_file(path)
        issues = validate_bpmn(document)
        errors = [issue for issue in issues if issue.severity == "error"]
        if errors:
            raise ValueError(
                f"BPMN {path.name} tidak valid: " + "; ".join(i.message for i in errors)
            )
        if document.unsupported_elements:
            raise ValueError(
                f"BPMN {path.name} berisi elemen tidak didukung: "
                + ", ".join(document.unsupported_elements)
            )
        projection = map_bpmn_to_graph(document, sop_id=sop_id, model_id=model_id)
        node_rows, relationship_rows = _projection_rows(projection)
        projections.append(
            {
                "sop_id": sop_id,
                "model_id": model_id,
                "source_sha256": document.source_sha256,
                "projection": projection,
                "node_rows": node_rows,
                "relationship_rows": relationship_rows,
            }
        )
    return projections


def _group_rows(projections: list[dict]) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    node_groups: dict[str, list[dict]] = defaultdict(list)
    relationship_groups: dict[str, list[dict]] = defaultdict(list)
    for projection_record in projections:
        for node, row in zip(
            projection_record["projection"].nodes,
            projection_record["node_rows"],
            strict=True,
        ):
            node_groups[node.label].append(row)
        for relationship, row in zip(
            projection_record["projection"].relationships,
            projection_record["relationship_rows"],
            strict=True,
        ):
            relationship_groups[relationship.type].append(row)
    return dict(node_groups), dict(relationship_groups)


def _validate_graph(session, projections: list[dict]) -> dict:
    model_ids = [projection["model_id"] for projection in projections]
    relationship_counts = [
        dict(record)
        for record in session.run(
            "MATCH ()-[r]->() WHERE r.model_id IN $model_ids "
            "RETURN r.sop_id AS sop_id, r.model_id AS model_id, type(r) AS jenis, "
            "count(*) AS jumlah ORDER BY sop_id, model_id, jenis",
            model_ids=model_ids,
        )
    ]
    expected_relationship_counts: dict[tuple[str, str], int] = defaultdict(int)
    for projection in projections:
        for relationship in projection["projection"].relationships:
            expected_relationship_counts[(projection["model_id"], relationship.type)] += 1
    actual_relationship_counts = {
        (record["model_id"], record["jenis"]): record["jumlah"] for record in relationship_counts
    }
    relationship_counts_match = actual_relationship_counts == dict(expected_relationship_counts)

    actual_special_flows = [
        dict(record)
        for record in session.run(
            "MATCH ()-[r:FLOWS_TO]->() WHERE r.model_id IN $model_ids "
            "AND (r.condition IS NOT NULL OR r.is_default = true) "
            "RETURN r.sop_id AS sop_id, r.model_id AS model_id, r.bpmn_id AS bpmn_id, "
            "r.source_bpmn_id AS dari, r.target_bpmn_id AS ke, r.condition AS kondisi, "
            "r.is_default AS cabang_bawaan ORDER BY model_id, bpmn_id",
            model_ids=model_ids,
        )
    ]
    expected_special_flows = sorted(
        (
            {
                "sop_id": projection["sop_id"],
                "model_id": projection["model_id"],
                "bpmn_id": relationship.properties["bpmn_id"],
                "dari": relationship.properties["source_bpmn_id"],
                "ke": relationship.properties["target_bpmn_id"],
                "kondisi": relationship.properties["condition"],
                "cabang_bawaan": relationship.properties["is_default"],
            }
            for projection in projections
            for relationship in projection["projection"].relationships
            if relationship.type == "FLOWS_TO"
            and (relationship.properties["condition"] or relationship.properties["is_default"])
        ),
        key=lambda item: (item["model_id"], item["bpmn_id"]),
    )
    special_flows_match = actual_special_flows == expected_special_flows

    paths = []
    for projection in projections:
        events = [
            node.properties for node in projection["projection"].nodes if node.label == "Event"
        ]
        starts = [event for event in events if event["bpmn_kind"] == "startEvent"]
        expected_end_ids = {
            event["bpmn_id"] for event in events if event["bpmn_kind"] == "endEvent"
        }
        reached_end_ids: set[str] = set()
        model_paths = []
        for start in starts:
            records = session.run(
                "MATCH p=(s:Event {sop_id: $sop_id, model_id: $model_id, "
                "bpmn_id: $start_id})-[:FLOWS_TO*1..30]->(e:Event {bpmn_kind: 'endEvent'}) "
                "WHERE all(r IN relationships(p) WHERE r.sop_id = $sop_id "
                "AND r.model_id = $model_id) "
                "RETURN [n IN nodes(p) | n.bpmn_id] AS node_ids, "
                "[r IN relationships(p) | r.bpmn_id] AS flow_ids, "
                "last(nodes(p)).bpmn_id AS end_id ORDER BY end_id, flow_ids",
                sop_id=projection["sop_id"],
                model_id=projection["model_id"],
                start_id=start["bpmn_id"],
            )
            for record in records:
                path = dict(record)
                reached_end_ids.add(path["end_id"])
                model_paths.append(path)
        paths.append(
            {
                "sop_id": projection["sop_id"],
                "model_id": projection["model_id"],
                "jalur_ditemukan": model_paths,
                "akhir_yang_diharapkan": sorted(expected_end_ids),
                "akhir_yang_dicapai": sorted(reached_end_ids),
                "seluruh_akhir_terjangkau": reached_end_ids == expected_end_ids,
            }
        )

    missing_provenance = (
        session.run(
            "MATCH (n) WHERE n.model_id IN $model_ids "
            "AND (n.sop_id IS NULL OR n.source_file_id IS NULL OR n.source_sha256 IS NULL) "
            "RETURN count(n) AS node_tanpa_provenance",
            model_ids=model_ids,
        ).single(strict=True)["node_tanpa_provenance"]
        + session.run(
            "MATCH ()-[r]->() WHERE r.model_id IN $model_ids "
            "AND (r.sop_id IS NULL OR r.source_file_id IS NULL OR r.source_sha256 IS NULL) "
            "RETURN count(r) AS relasi_tanpa_provenance",
            model_ids=model_ids,
        ).single(strict=True)["relasi_tanpa_provenance"]
    )
    paths_match = all(path["seluruh_akhir_terjangkau"] for path in paths)
    return {
        "jumlah_relasi_per_model_dan_jenis": relationship_counts,
        "jumlah_relasi_cocok_dengan_proyeksi": relationship_counts_match,
        "alur_bersyarat_dan_bawaan_di_database": actual_special_flows,
        "alur_bersyarat_dan_bawaan_cocok": special_flows_match,
        "hasil_traversal_jalur": paths,
        "seluruh_akhir_terjangkau": paths_match,
        "elemen_tanpa_provenance": missing_provenance,
        "provenance_lengkap": missing_provenance == 0,
        "validasi_graph_lulus": relationship_counts_match
        and special_flows_match
        and paths_match
        and missing_provenance == 0,
    }


def main() -> int:
    settings = load_settings()
    run_id = datetime.now(UTC).strftime("m2-ingest-%Y%m%dT%H%M%S%fZ")
    projections = build_projections()
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        before = _read_existing_state(driver, settings.neo4j_database, projections)
    if (
        before["konflik_hash_model"]
        or before["id_node_berulang_di_database"]
        or before["id_relasi_berulang_di_database"]
    ):
        raise RuntimeError(
            "Preflight database gagal; tidak ada data ditulis: " + json.dumps(before)
        )

    expected_node_total = sum(len(projection["node_rows"]) for projection in projections)
    expected_relationship_total = sum(
        len(projection["relationship_rows"]) for projection in projections
    )
    model_ids = {projection["model_id"] for projection in projections}
    prior_node_total = sum(
        record["jumlah"]
        for record in before["node_eksisting_menurut_model_dan_label"]
        if record["model_id"] in model_ids
    )
    prior_relationship_total = sum(
        record["jumlah"]
        for record in before["relasi_eksisting_menurut_model_dan_jenis"]
        if record["model_id"] in model_ids
    )

    node_groups, relationship_groups = _group_rows(projections)
    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        with driver.session(database=settings.neo4j_database) as session:
            write_counts = session.execute_write(
                _write_projection, node_groups, relationship_groups
            )
            post_state = list(
                session.run(
                    "MATCH (n) WHERE n.sop_id IN $sop_ids "
                    "RETURN n.sop_id AS sop_id, n.model_id AS model_id, labels(n) AS labels, "
                    "count(*) AS jumlah ORDER BY sop_id, model_id, labels",
                    sop_ids=[projection["sop_id"] for projection in projections],
                )
            )
            node_totals = session.run(
                "MATCH (n) WHERE n.model_id IN $model_ids RETURN count(n) AS jumlah",
                model_ids=[projection["model_id"] for projection in projections],
            ).single(strict=True)["jumlah"]
            relationship_totals = session.run(
                "MATCH ()-[r]->() WHERE r.model_id IN $model_ids RETURN count(r) AS jumlah",
                model_ids=[projection["model_id"] for projection in projections],
            ).single(strict=True)["jumlah"]
            actual_node_total = expected_node_total
            actual_relationship_total = expected_relationship_total
            if node_totals != actual_node_total or relationship_totals != actual_relationship_total:
                raise RuntimeError(
                    "Statistik pasca-ingest tidak sesuai: "
                    f"node {node_totals}/{actual_node_total}, "
                    f"relasi {relationship_totals}/{actual_relationship_total}"
                )
            after = [dict(record) for record in post_state]
            graph_validation = _validate_graph(session, projections)
            if not graph_validation["validasi_graph_lulus"]:
                raise RuntimeError(
                    "Validasi graph pasca-ingest gagal: "
                    + json.dumps(graph_validation, ensure_ascii=False)
                )

    report = {
        "status": "INGEST_LULUS",
        "run_id": run_id,
        "database": settings.neo4j_database,
        "target_uri": settings.neo4j_uri,
        "hasil_sebelum_ingest": before,
        "hasil_tulis_transaksi": write_counts,
        "idempoten_diulang": prior_node_total == expected_node_total
        and prior_relationship_total == expected_relationship_total,
        "jumlah_eksisting_sebelum_run": {
            "node": prior_node_total,
            "relasi": prior_relationship_total,
        },
        "jumlah_node_terverifikasi": node_totals,
        "jumlah_relasi_terverifikasi": relationship_totals,
        "statistik_node_setelah_ingest": after,
        "validasi_graph": graph_validation,
        "models": [
            {
                "sop_id": projection["sop_id"],
                "model_id": projection["model_id"],
                "source_sha256": projection["source_sha256"],
                "jumlah_node": len(projection["node_rows"]),
                "jumlah_relasi": len(projection["relationship_rows"]),
            }
            for projection in projections
        ],
        "catatan": (
            "Ingest memakai MERGE tanpa penghapusan; reset penuh sebelum run ini "
            "tercatat di results/m2/database_reset_report.json."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Ingest lulus: {node_totals} node, {relationship_totals} relasi; "
        f"{OUTPUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
