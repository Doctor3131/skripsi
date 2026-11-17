"""Pipeline Text-to-Cypher lokal dengan validasi fail-closed dan retrieval read-only."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from neo4j import READ_ACCESS, Driver
from neo4j.exceptions import ClientError

SCHEMA_LABELS = {
    "Process",
    "Activity",
    "Event",
    "Gateway",
    "Lane",
    "DataElement",
    "DataAssociation",
    "Participant",
    "TextAnnotation",
}
SCHEMA_RELATIONSHIPS = {
    "HAS_ELEMENT",
    "HAS_LANE",
    "CONTAINS_LANE",
    "IN_LANE",
    "FLOWS_TO",
    "HAS_DATA_ASSOCIATION",
    "HAS_SOURCE",
    "HAS_TARGET",
    "REPRESENTS_PROCESS",
    "MESSAGE_FLOWS_TO",
    "ATTACHED_TO",
    "ANNOTATES",
}
SCHEMA_PROPERTIES = {
    "graph_id",
    "bpmn_id",
    "name",
    "bpmn_kind",
    "documentation",
    "process_bpmn_id",
    "default_flow_bpmn_id",
    "parent_lane_bpmn_id",
    "is_executable",
    "direction",
    "owner_bpmn_id",
    "transformation",
    "text",
    "source_bpmn_id",
    "target_bpmn_id",
    "condition",
    "expression_language",
    "is_default",
    "association_direction",
    "sop_id",
    "model_id",
    "source_file_id",
    "source_sha256",
}
APPROVED_SOPS = {
    "FSM-SOP-CUTI-AKADEMIK": "Permohonan Izin Cuti Akademik",
    "FSM-SOP-AKTIF-SETELAH-CUTI": "Permohonan Izin Aktif Kuliah Setelah Cuti",
}
APPROVED_MODELS = {
    "FSM-SOP-CUTI-AKADEMIK": "FSM-SOP-CUTI-AKADEMIK-BPMN-v1",
    "FSM-SOP-AKTIF-SETELAH-CUTI": "FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v1",
}
MAX_RESULTS = 50
DEFAULT_TIMEOUT_SECONDS = 5.0
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(?:CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|ALTER|GRANT|DENY|REVOKE|"
    r"LOAD|CSV|CALL|APOC|DBMS|SHOW|TERMINATE|START|STOP|FOREACH|UNION|USE|"
    r"INSTALL|UNINSTALL|RENAME|YIELD|EXECUTE|EXISTS)\b",
    re.IGNORECASE,
)
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class PipelineError(RuntimeError):
    """Kegagalan pipeline dengan kategori yang dapat dicatat dan dianalisis."""

    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category
        self.trace: dict[str, object] | None = None


@dataclass(frozen=True)
class QuestionRequest:
    question: str
    sop_id: str | None = None
    model_id: str | None = None


@dataclass(frozen=True)
class SafeCypher:
    query: str
    parameters: dict[str, str | int | float | bool | None]


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    data: dict[str, object]


@dataclass
class PipelineTrace:
    request_id: str
    prompt_versions: dict[str, str] = field(
        default_factory=lambda: {
            "text_to_cypher": "v1",
            "jawaban_berbasis_evidence": "v1",
        }
    )
    generated_cypher: str | None = None
    query_validation: str = "BELUM_DIJALANKAN"
    query_execution: str = "BELUM_DIJALANKAN"
    error_category: str | None = None
    latensi_ms: dict[str, float] = field(default_factory=dict)
    token_usage: dict[str, int | None] = field(default_factory=dict)
    estimated_cost: dict[str, float | None] = field(default_factory=dict)
    retrieved_evidence_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PipelineResponse:
    answer: str
    evidence: tuple[Evidence, ...]
    abstain: bool
    trace: PipelineTrace


class CypherSafetyValidator:
    """Menerima hanya subset query graph baca-saja yang disetujui."""

    _ALLOWED_CLAUSE_WORDS = {
        "MATCH",
        "OPTIONAL",
        "WHERE",
        "WITH",
        "RETURN",
        "ORDER",
        "BY",
        "SKIP",
        "LIMIT",
        "AS",
        "AND",
        "OR",
        "XOR",
        "NOT",
        "IN",
        "IS",
        "NULL",
        "TRUE",
        "FALSE",
        "DISTINCT",
        "ASC",
        "DESC",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
    }
    _ALLOWED_FUNCTIONS = {
        "COUNT",
        "COLLECT",
        "HEAD",
        "LAST",
        "TAIL",
        "SIZE",
        "LENGTH",
        "NODES",
        "RELATIONSHIPS",
        "LABELS",
        "TYPE",
        "PROPERTIES",
        "ELEMENTID",
        "TOSTRING",
        "COALESCE",
        "ALL",
        "ANY",
        "NONE",
        "SINGLE",
        "REDUCE",
        "MIN",
        "MAX",
        "SUM",
        "AVG",
    }

    def validate(
        self,
        query: str,
        parameters: dict[str, object],
        *,
        sop_id: str | None = None,
        model_id: str | None = None,
    ) -> SafeCypher:
        candidate = query.strip()
        if not candidate:
            raise PipelineError("QUERY_KOSONG", "Provider tidak menghasilkan query Cypher.")
        if any(mark in candidate for mark in (";", "'", '"', "`", "//", "/*", "*/", "\\")):
            raise PipelineError(
                "QUERY_DITOLAK", "Query mengandung pemisah, literal, komentar, atau escape."
            )
        if re.search(r":\s*\$\s*\(|\[\s*\$[A-Za-z_]", candidate):
            raise PipelineError(
                "QUERY_DITOLAK", "Label, tipe relasi, atau properti dinamis tidak diizinkan."
            )
        if _FORBIDDEN_KEYWORDS.search(candidate):
            raise PipelineError("QUERY_DITOLAK", "Query mengandung klausa/prosedur terlarang.")
        if not re.match(r"^MATCH\b", candidate, re.IGNORECASE):
            raise PipelineError("QUERY_DITOLAK", "Query harus dimulai dengan MATCH.")
        if not re.search(r"\bRETURN\b", candidate, re.IGNORECASE):
            raise PipelineError(
                "QUERY_DITOLAK", "Query harus mengembalikan evidence dengan RETURN."
            )
        limit_match = re.search(r"\bLIMIT\s+\$maks_hasil\s*$", candidate, re.IGNORECASE)
        if not limit_match:
            raise PipelineError("QUERY_DITOLAK", "Query harus berakhir dengan LIMIT $maks_hasil.")
        labels_and_types = set(re.findall(r":\s*([A-Za-z_][A-Za-z0-9_]*)", candidate))
        unknown_schema_items = labels_and_types - SCHEMA_LABELS - SCHEMA_RELATIONSHIPS
        if unknown_schema_items:
            raise PipelineError(
                "SKEMA_TIDAK_VALID",
                "Label/tipe relasi tidak dikenal: " + ", ".join(sorted(unknown_schema_items)),
            )
        if not (labels_and_types & SCHEMA_LABELS):
            raise PipelineError("SKEMA_TIDAK_VALID", "Query harus menyebut label node skema.")
        property_names = set(re.findall(r"\.\s*([A-Za-z_][A-Za-z0-9_]*)", candidate))
        property_names.update(re.findall(r"[,{]\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", candidate))
        unknown_properties = property_names - SCHEMA_PROPERTIES
        if unknown_properties:
            raise PipelineError(
                "SKEMA_TIDAK_VALID",
                "Properti tidak dikenal: " + ", ".join(sorted(unknown_properties)),
            )
        for word in _IDENTIFIER.findall(candidate):
            if word.upper() in self._ALLOWED_CLAUSE_WORDS:
                continue
            if word.upper() in self._ALLOWED_FUNCTIONS:
                continue
            if word in SCHEMA_LABELS or word in SCHEMA_RELATIONSHIPS or word in SCHEMA_PROPERTIES:
                continue
            if word in parameters or word == "maks_hasil":
                continue
            # Variables and aliases are local identifiers; function-call names are allowlisted.
            if re.search(rf"\b{re.escape(word)}\s*\(", candidate, re.IGNORECASE):
                raise PipelineError("QUERY_DITOLAK", f"Fungsi tidak diizinkan: {word}")
        safe_parameters: dict[str, str | int | float | bool | None] = {}
        for key, value in parameters.items():
            if not _IDENTIFIER.fullmatch(key):
                raise PipelineError("PARAMETER_TIDAK_VALID", "Nama parameter tidak valid.")
            if value is not None and not isinstance(value, str | int | float | bool):
                raise PipelineError(
                    "PARAMETER_TIDAK_VALID", f"Parameter {key} harus bernilai skalar."
                )
            if isinstance(value, str) and len(value) > 500:
                raise PipelineError("PARAMETER_TIDAK_VALID", f"Parameter {key} terlalu panjang.")
            safe_parameters[key] = value
        if sop_id is not None:
            if sop_id not in APPROVED_SOPS:
                raise PipelineError("SOP_TIDAK_DIKENAL", "sop_id tidak ada dalam pilot.")
            safe_parameters["sop_id"] = sop_id
        if model_id is not None:
            if sop_id is None or APPROVED_MODELS.get(sop_id) != model_id:
                raise PipelineError(
                    "MODEL_TIDAK_DIKENAL", "model_id tidak cocok dengan SOP pilot yang dipilih."
                )
            safe_parameters["model_id"] = model_id
        referenced_parameters = set(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]*)", candidate))
        provided_parameters = set(safe_parameters) - {"maks_hasil"}
        missing_parameters = referenced_parameters - provided_parameters - {"maks_hasil"}
        unused_parameters = provided_parameters - referenced_parameters
        if missing_parameters:
            raise PipelineError(
                "PARAMETER_TIDAK_VALID",
                "Parameter query belum disediakan: " + ", ".join(sorted(missing_parameters)),
            )
        if unused_parameters:
            raise PipelineError(
                "PARAMETER_TIDAK_VALID",
                "Parameter tidak dipakai query: " + ", ".join(sorted(unused_parameters)),
            )
        safe_parameters["maks_hasil"] = MAX_RESULTS
        return SafeCypher(candidate, safe_parameters)


def _json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    labels = getattr(value, "labels", None)
    if labels is not None and hasattr(value, "items"):
        properties = dict(value)
        return {
            "jenis": "node",
            "label": sorted(labels),
            "properties": _json_safe(properties),
        }
    relationship_type = getattr(value, "type", None)
    if relationship_type is not None and hasattr(value, "items"):
        return {
            "jenis": "relasi",
            "tipe": str(relationship_type),
            "properties": _json_safe(dict(value)),
        }
    nodes = getattr(value, "nodes", None)
    relationships = getattr(value, "relationships", None)
    if nodes is not None and relationships is not None:
        return {
            "jenis": "jalur",
            "node": [_json_safe(node) for node in nodes],
            "relasi": [_json_safe(rel) for rel in relationships],
        }
    if value is None or isinstance(value, str | int | float | bool):
        return value
    return str(value)


def _has_provenance(value: object) -> bool:
    found: set[str] = set()

    def visit(item: object) -> None:
        if isinstance(item, dict):
            found.update(str(key) for key in item)
            for child in item.values():
                visit(child)
        elif isinstance(item, list | tuple):
            for child in item:
                visit(child)

    visit(value)
    return {"sop_id", "model_id", "source_file_id", "source_sha256"} <= found and bool(
        found & {"bpmn_id", "source_bpmn_id", "target_bpmn_id"}
    )


class Neo4jReadExecutor:
    """Menjalankan query yang telah disaring dalam transaksi read-only terbatas."""

    def __init__(
        self,
        driver: Driver,
        *,
        database: str = "neo4j",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_results: int = MAX_RESULTS,
    ) -> None:
        if not 1 <= max_results <= MAX_RESULTS:
            raise ValueError(f"max_results harus antara 1 dan {MAX_RESULTS}")
        self.driver = driver
        self.database = database
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results

    def execute(self, safe_query: SafeCypher) -> tuple[dict[str, object], ...]:
        parameters = {**safe_query.parameters, "maks_hasil": self.max_results}
        try:
            with self.driver.session(
                database=self.database,
                default_access_mode=READ_ACCESS,
            ) as session:
                with session.begin_transaction(timeout=self.timeout_seconds) as tx:
                    tx.run("EXPLAIN " + safe_query.query, parameters).consume()
                    result = tx.run(safe_query.query, parameters)
                    rows = [
                        {key: _json_safe(value) for key, value in record.items()}
                        for record in result
                    ]
                    result.consume()
                    return tuple(rows)
        except ClientError as exc:
            code = getattr(exc, "code", "")
            category = "CYPHER_SYNTAX_ERROR" if "SyntaxError" in code else "CYPHER_EXECUTION_ERROR"
            raise PipelineError(category, str(exc)) from exc
        except Exception as exc:
            raise PipelineError("NEO4J_UNAVAILABLE", str(exc)) from exc


def trace_to_dict(response: PipelineResponse) -> dict[str, object]:
    """Serialisasi trace tanpa kredensial/provider secrets."""
    return {
        "request_id": response.trace.request_id,
        "prompt_versions": response.trace.prompt_versions,
        "generated_cypher": response.trace.generated_cypher,
        "query_validation": response.trace.query_validation,
        "query_execution": response.trace.query_execution,
        "error_category": response.trace.error_category,
        "latensi_ms": response.trace.latensi_ms,
        "token_usage": response.trace.token_usage,
        "estimated_cost": response.trace.estimated_cost,
        "evidence_ids": response.trace.retrieved_evidence_ids,
        "abstain": response.abstain,
    }
