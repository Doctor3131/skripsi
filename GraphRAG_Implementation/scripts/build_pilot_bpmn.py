# ruff: noqa: E501 -- string SVG/XML dan uraian sumber dibiarkan utuh agar mudah diaudit.
"""Bangun BPMN pilot berbahasa Indonesia dan bukti turunannya secara deterministik."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import textwrap
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT.parent
NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
for prefix, uri in NS.items():
    if prefix != "xsi":
        ET.register_namespace(prefix, uri)
ET.register_namespace("xsi", NS["xsi"])


def q(prefix: str, local: str) -> str:
    return f"{{{NS[prefix]}}}{local}"


def element(parent: ET.Element, tag: str, attrs: dict | None = None, text: str | None = None):
    item = ET.SubElement(parent, q("bpmn", tag), attrs or {})
    if text is not None:
        item.text = text
    return item


def _task(
    element_id: str,
    name: str,
    step: str,
    lane: str | None,
    documentation: str = "",
    inputs: list[dict] | None = None,
    outputs: list[dict] | None = None,
) -> dict:
    return {
        "id": element_id,
        "tag": "userTask" if lane else "task",
        "name": name,
        "step": step,
        "lane": lane,
        "documentation": documentation,
        "inputs": inputs or [],
        "outputs": outputs or [],
    }


MODELS = [
    {
        "key": "cuti",
        "file": "pilot_sop_a.bpmn",
        "preview": "pilot_sop_a.svg",
        "sop_id": "FSM-SOP-CUTI-AKADEMIK",
        "model_id": "FSM-SOP-CUTI-AKADEMIK-BPMN-v2",
        "title": "Permohonan Izin Cuti Akademik",
        "source_title": "Permohonan Izin Cuti Akademik",
        "process_id": "Process_CutiAkademik",
        "namespace": "https://fsm.undip.ac.id/graphrag/bpmn/pilot/cuti-akademik/v2",
        "duration": "Waktu pemrosesan maksimal: tiga hari kerja.",
        "source_notes": (
            "PDF menjadi acuan urutan dan kondisi. Tabel DOCX melengkapi informasi pelaksana. "
            "Metadata pengesahan DOCX yang menyebut Rektor dicatat sebagai konflik metadata; "
            "aktivitas penandatanganan mengikuti uraian proses PDF yang menyebut Dekan."
        ),
        "lanes": [
            {
                "id": "Lane_Mahasiswa",
                "name": "Mahasiswa",
                "nodes": [
                    "Start_Cuti",
                    "Task_IsiFormCuti",
                    "Task_MintaPersetujuanProdi",
                    "Task_SerahkanKeDekan",
                    "Gateway_PilihanPengambilan",
                    "Task_AmbilSuratCuti",
                    "End_Cuti_Diambil",
                ],
            },
            {
                "id": "Lane_SubbagAkademik",
                "name": "Subbag Akademik dan Kemahasiswaan",
                "nodes": ["Task_PeriksaKelengkapan", "Task_PerbaruiStatus"],
            },
            {"id": "Lane_Dekan", "name": "Dekan", "nodes": ["Task_TandaTanganDekan"]},
            {
                "id": "Lane_SubbagSumberDaya",
                "name": "Subbag Sumber Daya",
                "nodes": ["Task_BeriNomorSurat"],
            },
        ],
        "data_objects": [
            {
                "id": "Ref_BerkasPersyaratanCuti",
                "object_id": "Object_BerkasPersyaratanCuti",
                "name": (
                    "Persyaratan: Form Cuti, transkrip, bukti SPP/UKT terakhir, "
                    "fotokopi KTM, dan dokumen pendukung"
                ),
                "after": "Task_IsiFormCuti",
                "source_step": "Langkah 1",
                "links": [("Task_IsiFormCuti", "input")],
            },
            {
                "id": "Ref_SuratIzinDekan",
                "object_id": "Object_SuratIzinDekan",
                "name": "Surat Izin Dekan",
                "after": "Task_TandaTanganDekan",
                "source_step": "Langkah 5",
                "links": [
                    ("Task_TandaTanganDekan", "output"),
                    ("Task_BeriNomorSurat", "input"),
                    ("Task_PerbaruiStatus", "input"),
                    ("Task_AmbilSuratCuti", "input"),
                ],
            },
        ],
        "nodes": [
            {
                "id": "Start_Cuti",
                "tag": "startEvent",
                "name": "Pengajuan cuti dimulai",
                "step": "Batas proses; bukan aktivitas tambahan",
                "lane": "Lane_Mahasiswa",
                "documentation": "Penanda awal proses untuk memodelkan delapan langkah SOP.",
            },
            _task(
                "Task_IsiFormCuti",
                "Mengunduh, mengisi, dan menandatangani Form Cuti; mengisi SIAP",
                "Langkah 1",
                "Lane_Mahasiswa",
                "Mahasiswa melampirkan seluruh persyaratan yang disebut dalam objek data.",
                inputs=[
                    {
                        "id": "Input_BerkasCuti",
                        "name": "Berkas persyaratan cuti",
                        "sources": ["Ref_BerkasPersyaratanCuti"],
                    }
                ],
            ),
            _task(
                "Task_MintaPersetujuanProdi",
                "Meminta persetujuan dan tanda tangan Ketua Program Studi",
                "Langkah 2",
                "Lane_Mahasiswa",
            ),
            _task(
                "Task_SerahkanKeDekan",
                "Menyerahkan Form Cuti yang telah ditandatangani kepada Dekan",
                "Langkah 3",
                "Lane_Mahasiswa",
                "Langkah yang sama menyatakan bahwa formulir kemudian didisposisikan ke Subbag Akademik dan Kemahasiswaan.",
            ),
            _task(
                "Task_PeriksaKelengkapan",
                "Memeriksa kelengkapan; memberi paraf dan memproses bila lengkap",
                "Langkah 4",
                "Lane_SubbagAkademik",
                "PDF menyatakan proses berlanjut jika persyaratan lengkap. SOP tidak menjelaskan hasil untuk persyaratan yang tidak lengkap.",
            ),
            _task(
                "Task_TandaTanganDekan",
                "Menandatangani Surat Izin Dekan",
                "Langkah 5",
                "Lane_Dekan",
                outputs=[
                    {
                        "id": "Output_SuratIzinDekan",
                        "name": "Surat Izin Dekan",
                        "target": "Ref_SuratIzinDekan",
                    }
                ],
            ),
            _task(
                "Task_BeriNomorSurat",
                "Memberi nomor surat dan mengirimkannya beserta tembusan",
                "Langkah 6",
                "Lane_SubbagSumberDaya",
                "Tembusan dikirim kepada Dosen Wali dan Ketua Program Studi.",
                inputs=[
                    {
                        "id": "Input_SuratUntukNomor",
                        "name": "Surat Izin Dekan",
                        "sources": ["Ref_SuratIzinDekan"],
                    }
                ],
            ),
            _task(
                "Task_PerbaruiStatus",
                "Memperbarui status mahasiswa, mengarsipkan, dan mengirim surat",
                "Langkah 7",
                "Lane_SubbagAkademik",
                inputs=[
                    {
                        "id": "Input_SuratUntukArsip",
                        "name": "Surat Izin Dekan",
                        "sources": ["Ref_SuratIzinDekan"],
                    }
                ],
            ),
            {
                "id": "Gateway_PilihanPengambilan",
                "tag": "exclusiveGateway",
                "name": "Mahasiswa memilih mengambil surat di loket?",
                "step": "Langkah 8",
                "lane": "Lane_Mahasiswa",
                "documentation": "Kata ‘dapat’ ditafsirkan sebagai pilihan; PI menyetujui tafsir ini pada 2026-11-17.",
                "default_flow_id": "Flow_Cuti_TidakDiambil",
            },
            _task(
                "Task_AmbilSuratCuti",
                "Mengambil Surat Izin Dekan di loket akademik",
                "Langkah 8",
                "Lane_Mahasiswa",
                inputs=[
                    {
                        "id": "Input_SuratUntukDiambil",
                        "name": "Surat Izin Dekan",
                        "sources": ["Ref_SuratIzinDekan"],
                    }
                ],
            ),
            {
                "id": "End_Cuti_Terkirim",
                "tag": "endEvent",
                "name": "Surat telah dikirim; proses layanan selesai",
                "step": "Langkah 7",
                "lane": None,
                "documentation": "Jalur selesai setelah surat dikirim apabila mahasiswa tidak mengambilnya di loket.",
            },
            {
                "id": "End_Cuti_Diambil",
                "tag": "endEvent",
                "name": "Surat Izin Dekan diambil mahasiswa",
                "step": "Langkah 8",
                "lane": "Lane_Mahasiswa",
                "documentation": "Hasil jalur pilihan jika mahasiswa mengambil surat di loket.",
            },
        ],
        "flows": [
            ("Flow_Cuti_00_01", "Start_Cuti", "Task_IsiFormCuti", None, None, "Batas proses"),
            (
                "Flow_Cuti_01_02",
                "Task_IsiFormCuti",
                "Task_MintaPersetujuanProdi",
                None,
                "Langkah 1",
                None,
            ),
            (
                "Flow_Cuti_02_03",
                "Task_MintaPersetujuanProdi",
                "Task_SerahkanKeDekan",
                None,
                "Langkah 2",
                None,
            ),
            (
                "Flow_Cuti_03_04",
                "Task_SerahkanKeDekan",
                "Task_PeriksaKelengkapan",
                None,
                "Langkah 3",
                "Setelah penyerahan, formulir didisposisikan ke Subbag Akademik dan Kemahasiswaan; pelaksana disposisi tidak disebutkan.",
            ),
            (
                "Flow_Cuti_Lengkap",
                "Task_PeriksaKelengkapan",
                "Task_TandaTanganDekan",
                "persyaratan lengkap",
                "Langkah 4",
                "Satu-satunya kelanjutan bersyarat yang disebutkan. Tidak ada alur untuk persyaratan tidak lengkap.",
            ),
            (
                "Flow_Cuti_05_06",
                "Task_TandaTanganDekan",
                "Task_BeriNomorSurat",
                None,
                "Langkah 5–6",
                None,
            ),
            (
                "Flow_Cuti_06_07",
                "Task_BeriNomorSurat",
                "Task_PerbaruiStatus",
                None,
                "Langkah 6–7",
                None,
            ),
            (
                "Flow_Cuti_07_08",
                "Task_PerbaruiStatus",
                "Gateway_PilihanPengambilan",
                None,
                "Langkah 7–8",
                "SOP mengirim surat kepada mahasiswa, lalu menyebut bahwa mahasiswa dapat mengambilnya di loket.",
            ),
            (
                "Flow_Cuti_PilihDiambil",
                "Gateway_PilihanPengambilan",
                "Task_AmbilSuratCuti",
                "mahasiswa memilih mengambil surat di loket",
                "Langkah 8",
                "Pilihan ini ditafsirkan dari kata ‘dapat’; PI menyetujui tafsir ini pada 2026-11-17.",
            ),
            (
                "Flow_Cuti_TidakDiambil",
                "Gateway_PilihanPengambilan",
                "End_Cuti_Terkirim",
                None,
                "Langkah 7–8",
                "Alur bawaan yang menutup proses setelah pengiriman; tidak menambah tugas/kegagalan baru.",
            ),
            (
                "Flow_Cuti_08_Selesai",
                "Task_AmbilSuratCuti",
                "End_Cuti_Diambil",
                None,
                "Langkah 8",
                None,
            ),
        ],
        "trace_notes": [
            {
                "id": "Process_CutiAkademik",
                "type": "SOURCE_CONFLICT",
                "location": "Metadata pengesahan DOCX; uraian proses PDF langkah 5",
                "note": "DOCX menyebut Rektor pada metadata pengesahan, sedangkan langkah proses menyebut Dekan menandatangani Surat Izin Dekan. Draf mengikuti langkah proses PDF.",
            },
            {
                "id": "Flow_Cuti_Lengkap",
                "type": "SOURCE_GAP_RECORDED",
                "location": "PDF halaman 1, langkah 4",
                "note": "Kondisi lengkap dinyatakan; tindakan untuk kondisi tidak lengkap tidak dinyatakan dan tidak dimodelkan.",
            },
            {
                "id": "Flow_Cuti_PilihDiambil",
                "type": "OPTIONALITY_INFERRED_APPROVED_BY_PI",
                "location": "PDF halaman 1, langkah 8 (‘Mahasiswa dapat mengambil’) dan langkah 7",
                "note": "‘Dapat’ dimodelkan sebagai aktivitas pilihan; jalur default selesai setelah surat dikirim. PI menyetujui tafsir ini pada 2026-11-17.",
            },
        ],
    },
    {
        "key": "aktif_setelah_cuti",
        "file": "pilot_sop_b.bpmn",
        "preview": "pilot_sop_b.svg",
        "sop_id": "FSM-SOP-AKTIF-SETELAH-CUTI",
        "model_id": "FSM-SOP-AKTIF-SETELAH-CUTI-BPMN-v2",
        "title": "Permohonan Izin Aktif Kuliah Setelah Cuti",
        "source_title": "Permohonan Izin Aktif Setelah Cuti",
        "process_id": "Process_AktifSetelahCuti",
        "namespace": "https://fsm.undip.ac.id/graphrag/bpmn/pilot/aktif-setelah-cuti/v2",
        "duration": "Durasi pada PDF: sekitar lima menit per langkah yang tercantum.",
        "source_notes": (
            "Nama proses mengikuti pilihan PI. Judul sumber PDF/DOCX yang dipasangkan adalah "
            "Permohonan Izin Aktif Setelah Cuti. PDF menjadi acuan urutan; tabel DOCX "
            "melengkapi informasi pelaksana dan menampilkan status aktif sebagai hasil."
        ),
        "lanes": [
            {
                "id": "Lane_MahasiswaAktif",
                "name": "Mahasiswa",
                "nodes": ["Start_Aktif", "Task_Lapor", "Task_RegistrasiSSO", "End_Aktif"],
            }
        ],
        "data_objects": [
            {
                "id": "Ref_BerkasAktif",
                "object_id": "Object_BerkasAktif",
                "name": "Surat Izin Cuti dan fotokopi Kartu Tanda Mahasiswa (KTM)",
                "after": "Task_Lapor",
                "source_step": "Langkah 1",
                "links": [("Task_Lapor", "input")],
            }
        ],
        "nodes": [
            {
                "id": "Start_Aktif",
                "tag": "startEvent",
                "name": "Proses pengaktifan kembali dimulai",
                "step": "Batas proses; bukan aktivitas tambahan",
                "lane": "Lane_MahasiswaAktif",
                "documentation": "Penanda awal proses untuk memodelkan langkah SOP.",
            },
            _task(
                "Task_Lapor",
                "Melapor kepada Ketua Program Studi dan Subbag Akademik dan Kemahasiswaan",
                "Langkah 1",
                "Lane_MahasiswaAktif",
                "Mahasiswa membawa Surat Izin Cuti dan fotokopi KTM.",
                inputs=[
                    {
                        "id": "Input_BerkasAktif",
                        "name": "Berkas untuk pelaporan",
                        "sources": ["Ref_BerkasAktif"],
                    }
                ],
            ),
            _task(
                "Task_RegistrasiSSO",
                "Melakukan registrasi daring melalui SSO masing-masing mahasiswa",
                "Langkah 2",
                "Lane_MahasiswaAktif",
                "Durasi yang tercantum pada sumber: sekitar lima menit.",
            ),
            {
                "id": "End_Aktif",
                "tag": "endEvent",
                "name": "Terdaftar sebagai peserta kuliah atau mahasiswa aktif di fakultas",
                "step": "Langkah 3; hasil proses",
                "lane": "Lane_MahasiswaAktif",
                "documentation": "PDF menomori status ini sebagai langkah 3; tabel DOCX menempatkannya sebagai hasil. Draf memodelkannya sebagai hasil akhir.",
            },
        ],
        "flows": [
            ("Flow_Aktif_00_01", "Start_Aktif", "Task_Lapor", None, None, "Batas proses"),
            ("Flow_Aktif_01_02", "Task_Lapor", "Task_RegistrasiSSO", None, "Langkah 1", None),
            (
                "Flow_Aktif_02_03",
                "Task_RegistrasiSSO",
                "End_Aktif",
                None,
                "Langkah 2–3",
                "Status aktif adalah hasil yang disebut sumber, bukan aktivitas kantor tambahan.",
            ),
        ],
        "trace_notes": [
            {
                "id": "End_Aktif",
                "type": "INTERPRETATION_RECORDED",
                "location": "PDF halaman 1, langkah 3; tabel DOCX, baris hasil registrasi",
                "note": "Status aktif dimodelkan sebagai hasil akhir, bukan tugas terpisah.",
            }
        ],
    },
]


def load_inventory() -> dict[str, dict]:
    with (ROOT / "docs/data_inventory.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = {row["sop_id"]: row for row in rows}
    for model in MODELS:
        row = result[model["sop_id"]]
        if row["source_pairing_status"] != "APPROVED_BY_PI":
            raise ValueError(f"Pasangan sumber belum disetujui: {model['sop_id']}")
    return result


def _write_io_spec(task_el: ET.Element, task: dict, model: dict, associations: list[dict]) -> None:
    inputs = task["inputs"]
    outputs = task["outputs"]
    if not inputs and not outputs:
        return
    io = element(task_el, "ioSpecification", {"id": f"Io_{task['id']}"})
    input_set_ids = []
    output_set_ids = []
    if inputs:
        input_container = element(io, "dataInputs", {"id": f"Inputs_{task['id']}"})
        for item in inputs:
            element(input_container, "dataInput", {"id": item["id"], "name": item["name"]})
            input_set_ids.append(item["id"])
    if outputs:
        output_container = element(io, "dataOutputs", {"id": f"Outputs_{task['id']}"})
        for item in outputs:
            element(output_container, "dataOutput", {"id": item["id"], "name": item["name"]})
            output_set_ids.append(item["id"])
    input_sets = element(io, "inputSets", {"id": f"InputSets_{task['id']}"})
    input_set = element(input_sets, "inputSet", {"id": f"InputSet_{task['id']}"})
    for item_id in input_set_ids:
        element(input_set, "dataInputRefs", text=item_id)
    output_sets = element(io, "outputSets", {"id": f"OutputSets_{task['id']}"})
    output_set = element(output_sets, "outputSet", {"id": f"OutputSet_{task['id']}"})
    for item_id in output_set_ids:
        element(output_set, "dataOutputRefs", text=item_id)
    for item in inputs:
        association_id = f"DA_{task['id']}_{item['id']}"
        association = element(task_el, "dataInputAssociation", {"id": association_id})
        for source_id in item["sources"]:
            element(association, "sourceRef", text=source_id)
        element(association, "targetRef", text=item["id"])
        associations.append(
            {
                "id": association_id,
                "sources": item["sources"],
                "target": item["id"],
                "activity": task["id"],
                "direction": "input",
            }
        )
    for item in outputs:
        association_id = f"DA_{task['id']}_{item['id']}"
        association = element(task_el, "dataOutputAssociation", {"id": association_id})
        element(association, "sourceRef", text=item["id"])
        element(association, "targetRef", text=item["target"])
        associations.append(
            {
                "id": association_id,
                "sources": [item["id"]],
                "target": item["target"],
                "activity": task["id"],
                "direction": "output",
            }
        )


@lru_cache(maxsize=1)
def _template_dimensions() -> dict[str, tuple[int, int]]:
    """Ambil ukuran shape dasar dari contoh Camunda yang disediakan PI."""
    path = VAULT / "data/bpmn/template_contoh.bpmn"
    root = ET.parse(path).getroot()
    sizes = {}
    for shape in root.findall(".//bpmndi:BPMNShape", NS):
        element_id = shape.get("bpmnElement", "")
        if not element_id.startswith(("Task_", "Gateway_", "Start_", "End_")):
            continue
        bounds = shape.find("dc:Bounds", NS)
        if bounds is not None:
            kind = (
                "gateway"
                if element_id.startswith("Gateway_")
                else "event"
                if element_id.startswith(("Start_", "End_"))
                else "task"
            )
            sizes.setdefault(
                kind, (int(float(bounds.get("width", "0"))), int(float(bounds.get("height", "0"))))
            )
    lane_shape = root.find(".//bpmndi:BPMNShape[@bpmnElement='Lane_Alumni']/dc:Bounds", NS)
    if lane_shape is None or not {"task", "gateway", "event"} <= sizes.keys():
        raise ValueError(f"Template BPMN tidak memiliki geometri yang diperlukan: {path}")
    sizes["lane"] = (
        int(float(lane_shape.get("width", "0"))),
        int(float(lane_shape.get("height", "0"))),
    )
    return sizes


def _positions(model: dict) -> tuple[dict, dict, int, int]:
    """Susun node dengan proporsi pool, lane, dan shape dari template BPMN."""
    dims = _template_dimensions()
    lane_height = max(dims["lane"][1], 200 if model["data_objects"] else dims["lane"][1])
    lane_top = {lane["id"]: 80 + index * lane_height for index, lane in enumerate(model["lanes"])}
    depth = {node["id"]: 0 for node in model["nodes"] if node["tag"] == "startEvent"}
    for _ in range(len(model["nodes"])):
        changed = False
        for _flow_id, source_id, target_id, *_ in model["flows"]:
            if source_id in depth:
                candidate = depth[source_id] + 1
                if candidate > depth.get(target_id, -1):
                    depth[target_id] = candidate
                    changed = True
        if not changed:
            break

    positions = {}
    grouped: dict[tuple[str, int], list[dict]] = {}
    for node in model["nodes"]:
        lane_id = node.get("lane") or model["lanes"][0]["id"]
        grouped.setdefault((lane_id, depth.get(node["id"], 0)), []).append(node)
    for (lane_id, layer), group in grouped.items():
        top = lane_top[lane_id]
        x = 322 if layer == 0 else 440 + (layer - 1) * 205
        for index, node in enumerate(group):
            kind = (
                "event"
                if node["tag"] in {"startEvent", "endEvent"}
                else "gateway"
                if node["tag"].endswith("Gateway")
                else "task"
            )
            width, height = dims[kind]
            if len(group) > 1:
                y = top + (24 if index == 0 else lane_height - height - 8)
            else:
                y = top + (lane_height - height) // 2
            positions[node["id"]] = {"x": x, "y": y, "w": width, "h": height, "lane": lane_id}

    for artifact in model["data_objects"]:
        parent = positions[artifact["after"]]
        positions[artifact["id"]] = {
            "x": parent["x"],
            "y": lane_top[parent["lane"]] + lane_height - 60,
            "w": 180,
            "h": 48,
            "lane": parent["lane"],
            "kind": "data",
        }
    max_right = max(pos["x"] + pos["w"] for pos in positions.values())
    width = max_right + 180
    height = 80 + len(model["lanes"]) * lane_height + 60
    return positions, lane_top, width, height


def build_xml(model: dict, inventory: dict[str, dict]) -> tuple[bytes, list[dict]]:
    source = inventory[model["sop_id"]]
    # Gunakan definitions dari template sebagai skeleton XML, tanpa membawa
    # proses legalisir atau fakta SOP yang terkandung di dalamnya.
    definitions = ET.parse(VAULT / "data/bpmn/template_contoh.bpmn").getroot()
    for child in list(definitions):
        definitions.remove(child)
    definitions.attrib.update(
        {
            "id": f"Definitions_{model['key']}_v2",
            "targetNamespace": model["namespace"],
            "exporter": "FSM GraphRAG deterministic pilot generator",
            "exporterVersion": "0.2",
        }
    )
    process = element(
        definitions,
        "process",
        {"id": model["process_id"], "name": model["title"], "isExecutable": "false"},
    )
    element(
        process,
        "documentation",
        text=(
            f"ID SOP proyek: {model['sop_id']}. ID model: {model['model_id']}. "
            f"Versi sumber: {source['source_version_label']}. "
            f"PDF acuan: {Path(source['raw_file']).name} (SHA-256 {source['raw_sha256']}). "
            f"Tabel pelengkap: {Path(source['flowchart_file']).name} "
            f"(SHA-256 {source['flowchart_sha256']}). {model['duration']} {model['source_notes']}"
        ),
    )
    lane_set = element(process, "laneSet", {"id": f"LaneSet_{model['key']}"})
    for lane in model["lanes"]:
        lane_el = element(lane_set, "lane", {"id": lane["id"], "name": lane["name"]})
        for node_id in lane["nodes"]:
            element(lane_el, "flowNodeRef", text=node_id)
    incoming = {node["id"]: [] for node in model["nodes"]}
    outgoing = {node["id"]: [] for node in model["nodes"]}
    for flow_id, source_id, target_id, *_ in model["flows"]:
        outgoing[source_id].append(flow_id)
        incoming[target_id].append(flow_id)
    associations: list[dict] = []
    for node in model["nodes"]:
        attrs = {"id": node["id"], "name": node["name"]}
        if node.get("default_flow_id"):
            attrs["default"] = node["default_flow_id"]
        node_el = element(process, node["tag"], attrs)
        if node.get("documentation"):
            element(node_el, "documentation", text=node["documentation"])
        for flow_id in incoming[node["id"]]:
            element(node_el, "incoming", text=flow_id)
        for flow_id in outgoing[node["id"]]:
            element(node_el, "outgoing", text=flow_id)
        if node["tag"] in {"userTask", "task"}:
            _write_io_spec(node_el, node, model, associations)
    for flow in model["flows"]:
        flow_id, source_id, target_id, condition, source_step, note = flow
        flow_el = element(
            process,
            "sequenceFlow",
            {"id": flow_id, "sourceRef": source_id, "targetRef": target_id},
        )
        if condition:
            flow_el.set(
                "name",
                "Jika persyaratan lengkap"
                if flow_id == "Flow_Cuti_Lengkap"
                else "Jika mahasiswa memilih mengambil surat",
            )
            element(
                flow_el,
                "conditionExpression",
                {q("xsi", "type"): "bpmn:tFormalExpression"},
                condition,
            )
        elif source_id == "Task_SerahkanKeDekan":
            flow_el.set("name", "Kemudian didisposisikan ke Subbag Akademik dan Kemahasiswaan")
        elif flow_id == "Flow_Cuti_TidakDiambil":
            flow_el.set("name", "Surat dikirim; tidak diambil di loket")
        if note:
            element(flow_el, "documentation", text=note)
    for artifact in model["data_objects"]:
        element(process, "dataObject", {"id": artifact["object_id"], "name": artifact["name"]})
        element(
            process,
            "dataObjectReference",
            {
                "id": artifact["id"],
                "dataObjectRef": artifact["object_id"],
                "name": artifact["name"],
            },
        )

    # Kolaborasi satu pool untuk menunjukkan nama prosedur tanpa menambahkan pelaksana baru.
    collaboration_id = f"Collaboration_{model['key']}"
    collaboration = element(definitions, "collaboration", {"id": collaboration_id})
    participant_id = f"Participant_{model['key']}"
    element(
        collaboration,
        "participant",
        {
            "id": participant_id,
            "name": model["title"],
            "processRef": model["process_id"],
        },
    )

    positions, lane_top, canvas_width, canvas_height = _positions(model)
    diagram = ET.SubElement(
        definitions, q("bpmndi", "BPMNDiagram"), {"id": f"Diagram_{model['key']}"}
    )
    plane = ET.SubElement(
        diagram,
        q("bpmndi", "BPMNPlane"),
        {"id": f"Plane_{model['key']}", "bpmnElement": collaboration_id},
    )
    lane_height = max(
        _template_dimensions()["lane"][1],
        200 if model["data_objects"] else _template_dimensions()["lane"][1],
    )
    participant = ET.SubElement(
        plane,
        q("bpmndi", "BPMNShape"),
        {"id": f"DI_{participant_id}", "bpmnElement": participant_id, "isHorizontal": "true"},
    )
    ET.SubElement(
        participant,
        q("dc", "Bounds"),
        {
            "x": "180",
            "y": "80",
            "width": str(canvas_width - 180),
            "height": str(len(model["lanes"]) * lane_height),
        },
    )
    for lane in model["lanes"]:
        shape = ET.SubElement(
            plane,
            q("bpmndi", "BPMNShape"),
            {"id": f"DI_{lane['id']}", "bpmnElement": lane["id"], "isHorizontal": "true"},
        )
        ET.SubElement(
            shape,
            q("dc", "Bounds"),
            {
                "x": "210",
                "y": str(lane_top[lane["id"]]),
                "width": str(canvas_width - 210),
                "height": str(lane_height),
            },
        )
        ET.SubElement(shape, q("bpmndi", "BPMNLabel"))
    for node in model["nodes"]:
        pos = positions[node["id"]]
        shape = ET.SubElement(
            plane,
            q("bpmndi", "BPMNShape"),
            {"id": f"DI_{node['id']}", "bpmnElement": node["id"]},
        )
        if node["tag"].endswith("Gateway"):
            shape.set("isMarkerVisible", "true")
        ET.SubElement(
            shape,
            q("dc", "Bounds"),
            {
                "x": str(pos["x"]),
                "y": str(pos["y"]),
                "width": str(pos["w"]),
                "height": str(pos["h"]),
            },
        )
        if node["tag"] in {"startEvent", "endEvent"} or node["tag"].endswith("Gateway"):
            label = ET.SubElement(shape, q("bpmndi", "BPMNLabel"))
            ET.SubElement(
                label,
                q("dc", "Bounds"),
                {
                    "x": str(pos["x"] - 25),
                    "y": str(pos["y"] + pos["h"] + 2),
                    "width": str(pos["w"] + 50),
                    "height": "30",
                },
            )
    for artifact in model["data_objects"]:
        pos = positions[artifact["id"]]
        shape = ET.SubElement(
            plane,
            q("bpmndi", "BPMNShape"),
            {"id": f"DI_{artifact['id']}", "bpmnElement": artifact["id"]},
        )
        ET.SubElement(
            shape,
            q("dc", "Bounds"),
            {
                "x": str(pos["x"]),
                "y": str(pos["y"]),
                "width": str(pos["w"]),
                "height": str(pos["h"]),
            },
        )

    node_positions = positions
    for flow in model["flows"]:
        flow_id, source_id, target_id, condition, _, _ = flow
        edge_label = ""
        if condition:
            edge_label = (
                "Jika persyaratan lengkap"
                if flow_id == "Flow_Cuti_Lengkap"
                else "Jika mahasiswa memilih mengambil surat"
            )
        elif flow_id == "Flow_Cuti_TidakDiambil":
            edge_label = "Surat dikirim; tidak diambil di loket"
        elif source_id == "Task_SerahkanKeDekan":
            edge_label = "Kemudian didisposisikan ke Subbag Akademik dan Kemahasiswaan"
        _add_edge(
            plane,
            f"DI_{flow_id}",
            flow_id,
            node_positions[source_id],
            node_positions[target_id],
            edge_label,
        )
    for association in associations:
        if association["direction"] == "input":
            origin = node_positions[association["sources"][0]]
            target = node_positions[association["activity"]]
        else:
            origin = node_positions[association["activity"]]
            target = node_positions[association["target"]]
        _add_edge(plane, f"DI_{association['id']}", association["id"], origin, target)

    ET.indent(definitions, space="  ")
    xml = ET.tostring(definitions, encoding="utf-8", xml_declaration=True)
    # Traceability records are generated from the same source declarations as the BPMN.
    trace = _trace_rows(model, source, associations)
    return xml, trace


def _edge_points(source: dict, target: dict, vertical: bool = False) -> list[tuple[float, float]]:
    if vertical:
        sx = source["x"] + source["w"] / 2
        tx = target["x"] + target["w"] / 2
        sy = source["y"] if source["y"] > target["y"] else source["y"] + source["h"]
        ty = target["y"] + target["h"] if source["y"] > target["y"] else target["y"]
        midy = (sy + ty) / 2
        return [(sx, sy), (sx, midy), (tx, midy), (tx, ty)]
    sx = source["x"] + source["w"]
    tx = target["x"]
    if tx < sx:
        sx, tx = source["x"], target["x"] + target["w"]
    sy = source["y"] + source["h"] / 2
    ty = target["y"] + target["h"] / 2
    midx = (sx + tx) / 2
    return [(sx, sy), (midx, sy), (midx, ty), (tx, ty)]


def _add_edge(
    parent: ET.Element,
    edge_id: str,
    bpmn_id: str,
    source: dict,
    target: dict,
    label: str = "",
) -> None:
    edge = ET.SubElement(parent, q("bpmndi", "BPMNEdge"), {"id": edge_id, "bpmnElement": bpmn_id})
    points = _edge_points(source, target, vertical="kind" in source or "kind" in target)
    for x, y in points:
        ET.SubElement(edge, q("di", "waypoint"), {"x": str(round(x)), "y": str(round(y))})
    if label:
        x, y = points[len(points) // 2]
        label_shape = ET.SubElement(edge, q("bpmndi", "BPMNLabel"))
        ET.SubElement(
            label_shape,
            q("dc", "Bounds"),
            {"x": str(round(x - 45)), "y": str(round(y - 18)), "width": "130", "height": "28"},
        )


def _trace_rows(model: dict, source: dict, associations: list[dict]) -> list[dict]:
    pdf = Path(source["raw_file"]).name
    docx = Path(source["flowchart_file"]).name
    rows = [
        {
            "sop_id": model["sop_id"],
            "model_id": model["model_id"],
            "bpmn_id": model["process_id"],
            "jenis_elemen": "proses",
            "berkas_sumber": pdf,
            "lokasi_sumber": "Judul dan seluruh langkah pada halaman 1; waktu total bila tercantum",
            "status": "SUMBER_UTAMA_PDF",
            "catatan": model["source_notes"],
        }
    ]
    lane_docx_rows = {
        "cuti": "Tabel pelaksana; judul kolom aktor",
        "aktif_setelah_cuti": "Tabel pelaksana; kolom Mahasiswa, Ketua Program Studi, Subbag Akademik dan Kemahasiswaan",
    }
    for lane in model["lanes"]:
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": lane["id"],
                "jenis_elemen": "lane",
                "berkas_sumber": docx,
                "lokasi_sumber": lane_docx_rows[model["key"]],
                "status": "AKTOR_DIDUKUNG_SUMBER",
                "catatan": f"Lane {lane['name']} hanya memuat aktivitas dengan pelaksana yang dinyatakan.",
            }
        )
    rows.append(
        {
            "sop_id": model["sop_id"],
            "model_id": model["model_id"],
            "bpmn_id": f"Participant_{model['key']}",
            "jenis_elemen": "participant",
            "berkas_sumber": pdf,
            "lokasi_sumber": "Judul SOP",
            "status": "CAKUPAN_PROSES",
            "catatan": "Pool prosedur; tidak menyatakan aktor tambahan.",
        }
    )
    node_by_id = {node["id"]: node for node in model["nodes"]}
    for node in model["nodes"]:
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": node["id"],
                "jenis_elemen": node["tag"],
                "berkas_sumber": pdf,
                "lokasi_sumber": node["step"],
                "status": (
                    "BATAS_PROSES"
                    if node["tag"] in {"startEvent", "endEvent"}
                    else "OPSIONALITAS_DITAFSIRKAN_DISETUJUI_PI"
                    if node["id"] == "Gateway_PilihanPengambilan"
                    else "SESUAI_TEKSTUAL"
                ),
                "catatan": node.get("documentation", ""),
            }
        )
        for io_item in (*node.get("inputs", []), *node.get("outputs", [])):
            rows.append(
                {
                    "sop_id": model["sop_id"],
                    "model_id": model["model_id"],
                    "bpmn_id": io_item["id"],
                    "jenis_elemen": "dataInput" if "sources" in io_item else "dataOutput",
                    "berkas_sumber": pdf,
                    "lokasi_sumber": node["step"],
                    "status": "DATA_DISEBUT_SUMBER",
                    "catatan": io_item["name"],
                }
            )
    for flow_id, _, _, condition, step, note in model["flows"]:
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": flow_id,
                "jenis_elemen": "sequenceFlow",
                "berkas_sumber": pdf,
                "lokasi_sumber": step or "Batas proses",
                "status": (
                    "OPSIONALITAS_DITAFSIRKAN_DISETUJUI_PI"
                    if flow_id == "Flow_Cuti_PilihDiambil"
                    else "ALUR_BERSYARAT_DIDUKUNG"
                    if condition
                    else "CABANG_BAWAAN_DITAFSIRKAN_PERLU_REVIEW_PI"
                    if flow_id == "Flow_Cuti_TidakDiambil"
                    else "URUTAN_DIDUKUNG"
                ),
                "catatan": note or "",
            }
        )
    for artifact in model["data_objects"]:
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": artifact["id"],
                "jenis_elemen": "dataObjectReference",
                "berkas_sumber": pdf,
                "lokasi_sumber": artifact["source_step"],
                "status": "DATA_DISEBUT_SUMBER",
                "catatan": artifact["name"],
            }
        )
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": artifact["object_id"],
                "jenis_elemen": "dataObject",
                "berkas_sumber": pdf,
                "lokasi_sumber": artifact["source_step"],
                "status": "DATA_DISEBUT_SUMBER",
                "catatan": artifact["name"],
            }
        )
    for association in associations:
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": association["id"],
                "jenis_elemen": f"dataAssociation_{association['direction']}",
                "berkas_sumber": pdf,
                "lokasi_sumber": node_by_id[association["activity"]]["step"],
                "status": "REFERENSI_DATA_DIDUKUNG",
                "catatan": "Relasi data BPMN; tidak menyatakan aturan REQUIRES/PRODUCES pada graph.",
            }
        )
    for item in model["trace_notes"]:
        rows.append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "bpmn_id": item["id"],
                "jenis_elemen": item["type"],
                "berkas_sumber": f"{pdf}; {docx}",
                "lokasi_sumber": item["location"],
                "status": item["type"],
                "catatan": item["note"],
            }
        )
    return rows


def _wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=True) or [""]


def build_svg(model: dict) -> bytes:
    positions, lane_top, width, height = _positions(model)
    lane_height = max(
        _template_dimensions()["lane"][1],
        200 if model["data_objects"] else _template_dimensions()["lane"][1],
    )
    pool_height = len(model["lanes"]) * lane_height
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><marker id="panah" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#334155"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="36" y="42" font-family="sans-serif" font-size="24" font-weight="700" fill="#172554">{html.escape(model["title"])}</text>',
        f'<rect x="180" y="80" width="{width - 180}" height="{pool_height}" fill="#ffffff" stroke="#64748b" stroke-width="2"/>',
    ]
    for lane in model["lanes"]:
        y = lane_top[lane["id"]]
        parts.append(
            f'<rect x="210" y="{y}" width="{width - 210}" height="{lane_height}" fill="#f8fafc" stroke="#94a3b8"/>'
        )
        label_y = y + lane_height / 2
        parts.append(
            f'<text x="224" y="{label_y}" transform="rotate(-90 224 {label_y})" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#334155">{html.escape(lane["name"])}</text>'
        )

    # Alur dan asosiasi digambar sebelum shape agar garis tidak menimpa teks node.
    for flow_id, source_id, target_id, _condition, _, _ in model["flows"]:
        source = positions[source_id]
        target = positions[target_id]
        points = _edge_points(source, target)
        path = "M " + " L ".join(f"{x:g} {y:g}" for x, y in points)
        parts.append(
            f'<path d="{path}" fill="none" stroke="#334155" stroke-width="2" marker-end="url(#panah)"/>'
        )
        label = {
            "Flow_Cuti_Lengkap": "Jika persyaratan lengkap",
            "Flow_Cuti_PilihDiambil": "Jika mahasiswa memilih mengambil",
            "Flow_Cuti_TidakDiambil": "Surat dikirim; tidak diambil",
        }.get(
            flow_id,
            "Disposisi ke Subbag Akademik dan Kemahasiswaan"
            if source_id == "Task_SerahkanKeDekan"
            else "",
        )
        if label:
            lines = _wrap(label, 24)
            mx = (points[1][0] + points[-2][0]) / 2
            sy, ty = points[0][1], points[-1][1]
            y0 = (sy + ty) / 2 - (len(lines) - 1) * 8
            for index, line in enumerate(lines):
                parts.append(
                    f'<text x="{mx if flow_id == "Flow_Cuti_PilihDiambil" else mx + 4}" y="{y0 + index * 16}" text-anchor="{"middle" if flow_id == "Flow_Cuti_PilihDiambil" else "start"}" font-family="sans-serif" font-size="12" fill="#7c2d12">{html.escape(line)}</text>'
                )

    for artifact in model["data_objects"]:
        data_pos = positions[artifact["id"]]
        # Pratinjau menjaga diagram tetap terbaca; seluruh asosiasi tetap ada di XML BPMN.
        for node_id, direction in artifact["links"][:1]:
            node_pos = positions[node_id]
            if direction == "input":
                sx = data_pos["x"] + data_pos["w"] / 2
                sy = data_pos["y"]
                tx = node_pos["x"] + node_pos["w"] / 2
                ty = node_pos["y"] + node_pos["h"]
            else:
                sx = node_pos["x"] + node_pos["w"] / 2
                sy = node_pos["y"] + node_pos["h"]
                tx = data_pos["x"] + data_pos["w"] / 2
                ty = data_pos["y"]
            my = (sy + ty) / 2
            parts.append(
                f'<path d="M {sx} {sy} V {my} H {tx} V {ty}" fill="none" stroke="#c2410c" stroke-width="1.5" stroke-dasharray="5 4"/>'
            )

    for node in model["nodes"]:
        pos = positions[node["id"]]
        if node["tag"] in {"startEvent", "endEvent"}:
            cx, cy = pos["x"] + pos["w"] / 2, pos["y"] + pos["h"] / 2
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="21" fill="#fff" stroke="#0f766e" stroke-width="3"/>'
            )
            if node["tag"] == "endEvent":
                parts.append(
                    f'<circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="#0f766e" stroke-width="2"/>'
                )
            lines = _wrap(node["name"], 20)
            for index, line in enumerate(lines):
                parts.append(
                    f'<text x="{cx}" y="{pos["y"] + pos["h"] + 18 + index * 14}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0f172a">{html.escape(line)}</text>'
                )
        elif node["tag"].endswith("Gateway"):
            cx, cy = pos["x"] + pos["w"] / 2, pos["y"] + pos["h"] / 2
            points = f"{cx},{pos['y']} {pos['x'] + pos['w']},{cy} {cx},{pos['y'] + pos['h']} {pos['x']},{cy}"
            parts.append(
                f'<polygon points="{points}" fill="#fef3c7" stroke="#b45309" stroke-width="2"/>'
            )
            lines = _wrap(node["name"], 24)
            for index, line in enumerate(lines):
                parts.append(
                    f'<text x="{cx}" y="{pos["y"] + pos["h"] + 18 + index * 14}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#0f172a">{html.escape(line)}</text>'
                )
        else:
            parts.append(
                f'<rect x="{pos["x"]}" y="{pos["y"]}" width="{pos["w"]}" height="{pos["h"]}" rx="6" fill="#eff6ff" stroke="#1d4ed8" stroke-width="2"/>'
            )
            lines = _wrap(node["name"], 24)
            text_height = 16
            start_y = pos["y"] + pos["h"] / 2 - (len(lines) - 1) * text_height / 2 + 5
            text_x = pos["x"] + pos["w"] / 2
            for index, line in enumerate(lines):
                parts.append(
                    f'<text x="{text_x}" y="{start_y + index * text_height}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0f172a">{html.escape(line)}</text>'
                )
    for artifact in model["data_objects"]:
        pos = positions[artifact["id"]]
        parts.append(
            f'<path d="M {pos["x"]} {pos["y"]} h {pos["w"] - 12} l 12 12 v {pos["h"] - 12} h {-pos["w"]} z" fill="#fff7ed" stroke="#c2410c" stroke-width="1.5"/>'
        )
        parts.append(
            f'<path d="M {pos["x"] + pos["w"] - 12} {pos["y"]} v 12 h 12" fill="none" stroke="#c2410c"/>'
        )
        lines = _wrap(artifact["name"], 36)
        for index, line in enumerate(lines[:3]):
            parts.append(
                f'<text x="{pos["x"] + pos["w"] / 2}" y="{pos["y"] + 17 + index * 13}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7c2d12">{html.escape(line)}</text>'
            )
    parts.append(
        f'<text x="36" y="{height - 22}" font-family="sans-serif" font-size="12" fill="#64748b">Pratinjau turunan BPMN · {html.escape(model["model_id"])} · bukan sumber SOP</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts).encode("utf-8")


def build_path_check(approved: bool = False) -> str:
    status = (
        "DISETUJUI PI; VERSI DIBEKUKAN"
        if approved
        else "REVISI STRUKTUR/TAMPILAN v2; MENUNGGU REVIEW PI"
    )
    return f"""# Pemeriksaan Jalur Pilot BPMN

Status: `{status}`. Pemeriksaan ini mengikuti hanya urutan dan kondisi pada PDF; bukan validasi terhadap flowchart visual.

## SOP Permohonan Izin Cuti Akademik

 Jalur yang dinyatakan: isi formulir dan persyaratan → minta persetujuan Ketua Program Studi → serahkan kepada Dekan dan disposisi ke Subbag Akademik dan Kemahasiswaan → pemeriksaan kelengkapan → **jika lengkap**, lanjut ke tanda tangan Dekan → pemberian nomor dan pengiriman tembusan → pembaruan status, pengarsipan, dan pengiriman kepada mahasiswa. Setelah pengiriman, model memuat jalur bawaan selesai tanpa pengambilan di loket atau jalur bersyarat saat mahasiswa memilih mengambil surat. PI menyetujui tafsir pilihan ini untuk pilot pada 2026-11-17; revisi v2 mengubah struktur/tampilan XML, bukan tafsir proses.

Untuk keadaan persyaratan tidak lengkap, SOP tidak menyatakan tindakan atau tujuan. BPMN tidak menambahkan jalur tersebut; pertanyaan tentang tindak lanjut harus dianggap tidak terjawab oleh sumber.

## SOP Permohonan Izin Aktif Kuliah Setelah Cuti

Jalur yang dinyatakan: mahasiswa melapor dengan Surat Izin Cuti dan fotokopi KTM → mahasiswa melakukan registrasi daring melalui SSO → hasilnya mahasiswa terdaftar sebagai peserta kuliah/mahasiswa aktif di fakultas.

PDF menomori status aktif sebagai langkah ketiga, sedangkan tabel DOCX menampilkannya sebagai hasil. Draf menggunakannya sebagai hasil akhir, bukan aktivitas tambahan.

## Keterkaitan antar-SOP

Prosedur dimodelkan sebagai dua proses terpisah. Hubungan konseptual dipakai untuk memilih pasangan pilot, tetapi tidak dibuat sebagai alur langsung dari akhir SOP cuti ke awal SOP aktif setelah cuti karena sumber tidak menyatakan transisi itu secara eksplisit.
"""


def main() -> None:
    inventory = load_inventory()
    bpmn_dir = VAULT / "data/bpmn"
    diagram_dir = VAULT / "data/diagram"
    results_dir = ROOT / "results/m2"
    for directory in (bpmn_dir, diagram_dir, results_dir):
        directory.mkdir(parents=True, exist_ok=True)
    manifest_path = results_dir / "pilot_manifest.json"
    previous_manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    )
    trace_rows = []
    revision_history = previous_manifest.get("revisi") or {
        "menggantikan": [
            {"model_id": item.get("model_id"), "bpmn_sha256": item.get("bpmn_sha256")}
            for item in previous_manifest.get("models", [])
        ],
        "ringkasan": "Struktur XML dan BPMN DI mengikuti pola template_contoh.bpmn; isi proses SOP dipertahankan.",
    }
    if previous_manifest.get("persetujuan_pi") and "persetujuan_sebelumnya" not in revision_history:
        revision_history["persetujuan_sebelumnya"] = previous_manifest["persetujuan_pi"]
    manifest = {
        "bahasa": "id",
        "status": "PENDING_REVIEW",
        "revisi": revision_history,
        "models": [],
    }
    for model in MODELS:
        xml, rows = build_xml(model, inventory)
        preview = build_svg(model)
        (bpmn_dir / model["file"]).write_bytes(xml)
        (diagram_dir / model["preview"]).write_bytes(preview)
        trace_rows.extend(rows)
        source = inventory[model["sop_id"]]
        manifest["models"].append(
            {
                "sop_id": model["sop_id"],
                "model_id": model["model_id"],
                "title": model["title"],
                "source_pdf": Path(source["raw_file"]).name,
                "source_pdf_sha256": source["raw_sha256"],
                "source_docx_table": Path(source["flowchart_file"]).name,
                "source_docx_sha256": source["flowchart_sha256"],
                "bpmn_file": model["file"],
                "bpmn_sha256": hashlib.sha256(xml).hexdigest(),
                "preview_file": model["preview"],
                "preview_sha256": hashlib.sha256(preview).hexdigest(),
            }
        )
    approved = previous_manifest.get("status") == "DISETUJUI_PI_DIBEKUKAN" and {
        item["model_id"]: item["bpmn_sha256"] for item in previous_manifest.get("models", [])
    } == {item["model_id"]: item["bpmn_sha256"] for item in manifest["models"]}
    if approved:
        manifest["status"] = previous_manifest["status"]
        manifest["persetujuan_pi"] = previous_manifest["persetujuan_pi"]
    fields = [
        "sop_id",
        "model_id",
        "bpmn_id",
        "jenis_elemen",
        "berkas_sumber",
        "lokasi_sumber",
        "status",
        "catatan",
    ]
    with (results_dir / "sop_bpmn_traceability.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(trace_rows)
    (results_dir / "path_check.md").write_text(build_path_check(approved), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Dibuat {len(MODELS)} BPMN, {len(MODELS)} pratinjau SVG, dan {len(trace_rows)} baris traceability."
    )


if __name__ == "__main__":
    main()
