import json
import sys
from datetime import UTC, datetime

from PIL import Image

from benchmarks.ab_gallery import build_gallery
from benchmarks.goldens import verify_goldens
from benchmarks.import_webgl import _sanitize_hardware
from benchmarks.report import main as report_main
from benchmarks.report import outlier_count, percentile_95
from benchmarks.schema import BenchmarkRecord, HardwareInfo


def _record(*, iteration: int = 1, duration_ms: float = 450.0) -> BenchmarkRecord:
    return BenchmarkRecord(
        run_id="v2-20260725T120000Z-deadbeef",
        captured_at=datetime.now(UTC),
        git_sha="deadbeef",
        git_dirty=True,
        source_sha256="a" * 64,
        engine="v2",
        engine_version="v2.0",
        case="coracao",
        config={"seed": 42},
        width=900,
        height=560,
        oversample=3,
        seed=42,
        execution_type="measure",
        iteration=iteration,
        duration_ms=duration_ms,
        rgb_sha256="b" * 64,
        python_version="3.12.0",
        runtime="CPython 3.12",
        operating_system="Windows",
        hardware=HardwareInfo(architecture="AMD64", logical_cpus=8),
    )


def test_schema_de_benchmark_roundtrip_sem_identificadores_pessoais():
    record = _record()
    payload = record.model_dump_json()
    assert "hostname" not in payload
    assert "username" not in payload
    assert BenchmarkRecord.model_validate_json(payload) == record


def test_estatisticas_do_relatorio_sao_deterministicas():
    values = [10.0, 11.0, 12.0, 13.0, 100.0]
    assert percentile_95(values) == 82.6
    assert outlier_count(values) == 1


def test_relatorio_recusa_amostra_insuficiente(tmp_path, monkeypatch):
    dataset = tmp_path / "single.jsonl"
    output = tmp_path / "single.md"
    dataset.write_text(_record().model_dump_json() + "\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["benchmarks.report", str(dataset), "--output", str(output)],
    )

    assert report_main() == 2
    report = output.read_text(encoding="utf-8")
    assert "Runs com amostras insuficientes" in report
    assert "n=1" in report


def test_relatorio_lista_runs_com_cv_reprovado(tmp_path, monkeypatch):
    dataset = tmp_path / "unstable.jsonl"
    output = tmp_path / "unstable.md"
    records = [
        _record(iteration=index, duration_ms=1.0 if index < 10 else 100.0)
        for index in range(1, 11)
    ]
    dataset.write_text(
        "".join(record.model_dump_json() + "\n" for record in records),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["benchmarks.report", str(dataset), "--output", str(output)],
    )

    assert report_main() == 2
    report = output.read_text(encoding="utf-8")
    assert "Runs que precisam ser repetidos" in report
    assert "`coracao`: CV" in report


def test_goldens_da_engine_permanecem_pixel_a_pixel_identicos():
    assert verify_goldens() == []


def test_galeria_ab_separa_apresentacao_do_mapa_privado(tmp_path):
    webgl = tmp_path / "webgl"
    webgl.mkdir()
    for name in ("webgl-heart.png", "webgl-text-3d.png", "webgl-sphere.png"):
        Image.new("RGB", (2, 2), "black").save(webgl / name)

    output = tmp_path / "sessao.html"
    mapping = tmp_path / "privado" / "sessao.json"
    build_gallery(webgl, "dia-1", output, mapping)

    assert "V2" not in output.read_text(encoding="utf-8")
    assert "WebGL" not in output.read_text(encoding="utf-8")
    reveal = json.loads(mapping.read_text(encoding="utf-8"))
    assert set(reveal["mapping"]) == {"coracao", "texto-3d", "esfera"}


def test_importador_webgl_remove_ids_e_versoes_de_driver():
    sanitized = _sanitize_hardware("ANGLE GPU 0x1234 driver 31.0.15.1234")
    assert "0x1234" not in sanitized
    assert "31.0.15.1234" not in sanitized
