import csv
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from fsm_graphrag.bpmn import parse_bpmn_file, validate_bpmn

PROJECT_ROOT = Path(__file__).parents[2]
VAULT_ROOT = PROJECT_ROOT.parent
BPMN_NS = {"b": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
DI_NS = {"di": "http://www.omg.org/spec/BPMN/20100524/DI"}


@pytest.mark.parametrize(
    ("filename", "process_id", "model_id"),
    [
        ("pilot_sop_a.bpmn", "Process_CutiAkademik", "FSM-SOP-CUTI-AKADEMIK-BPMN-v1"),
        (
            "pilot_sop_b.bpmn",
            "Process_AktifSetelahCuti",
            "FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v1",
        ),
    ],
)
def test_pilot_bpmn_parses_and_has_valid_references(
    filename: str, process_id: str, model_id: str
) -> None:
    path = VAULT_ROOT / "data" / "bpmn" / filename
    document = parse_bpmn_file(path)
    assert [process.id for process in document.processes] == [process_id]
    assert validate_bpmn(document) == ()
    assert document.unsupported_elements == ()
    assert model_id in ET.parse(path).getroot().find("b:process/b:documentation", BPMN_NS).text


def test_cuti_has_documented_completeness_and_optional_pickup_paths() -> None:
    path = VAULT_ROOT / "data" / "bpmn" / "pilot_sop_a.bpmn"
    document = parse_bpmn_file(path)
    conditions = [flow for flow in document.sequence_flows if flow.condition]
    assert len(conditions) == 2
    by_id = {flow.id: flow for flow in conditions}
    complete = by_id["Flow_Cuti_Lengkap"]
    assert complete.condition == "persyaratan lengkap"
    assert complete.source_ref == "Task_PeriksaKelengkapan"
    assert complete.target_ref == "Task_TandaTanganDekan"
    pickup = by_id["Flow_Cuti_PilihDiambil"]
    assert pickup.condition == "mahasiswa memilih mengambil surat di loket"
    assert pickup.source_ref == "Gateway_PilihanPengambilan"
    assert pickup.target_ref == "Task_AmbilSuratCuti"
    gateway = next(node for node in document.nodes if node.id == "Gateway_PilihanPengambilan")
    assert gateway.default_flow_id == "Flow_Cuti_TidakDiambil"
    default_flow = next(
        flow for flow in document.sequence_flows if flow.id == gateway.default_flow_id
    )
    assert default_flow.is_default
    assert "tidak lengkap" in next(
        node.documentation or "" for node in document.nodes if node.id == "Task_PeriksaKelengkapan"
    )


def test_active_after_leave_ends_at_status_outcome_without_branch() -> None:
    path = VAULT_ROOT / "data" / "bpmn" / "pilot_sop_b.bpmn"
    document = parse_bpmn_file(path)
    assert not any(flow.condition for flow in document.sequence_flows)
    outcome = next(node for node in document.nodes if node.id == "End_Aktif")
    assert outcome.kind == "endEvent"
    assert "mahasiswa aktif" in (outcome.name or "").lower()
    assert len([node for node in document.nodes if node.category == "activity"]) == 2


def test_pilot_traceability_covers_all_flow_nodes_and_flows() -> None:
    trace_path = PROJECT_ROOT / "results" / "m2" / "sop_bpmn_traceability.csv"
    with trace_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    traced_ids = {row["bpmn_id"] for row in rows}
    for filename in ("pilot_sop_a.bpmn", "pilot_sop_b.bpmn"):
        document = parse_bpmn_file(VAULT_ROOT / "data" / "bpmn" / filename)
        assert {node.id for node in document.nodes} <= traced_ids
        assert {flow.id for flow in document.sequence_flows} <= traced_ids


def test_pilot_files_include_bpmn_di_and_valid_svg_previews() -> None:
    for stem in ("pilot_sop_a", "pilot_sop_b"):
        bpmn = VAULT_ROOT / "data" / "bpmn" / f"{stem}.bpmn"
        root = ET.parse(bpmn).getroot()
        assert root.find("di:BPMNDiagram/di:BPMNPlane", DI_NS) is not None
        svg = VAULT_ROOT / "data" / "diagram" / f"{stem}.svg"
        assert ET.parse(svg).getroot().tag == "{http://www.w3.org/2000/svg}svg"
