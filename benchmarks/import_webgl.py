"""Converte medições brutas do navegador no dataset WebGL versionado."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from benchmarks.schema import BenchmarkRecord, HardwareInfo


CASE_NAMES = {
    "heart": "coracao",
    "coracao": "coracao",
    "text-3d": "texto-3d",
    "texto-3d": "texto-3d",
    "sphere": "esfera",
    "esfera": "esfera",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--fork", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--power", choices=("ac", "battery", "unknown"), default="unknown")
    parser.add_argument("--workload", choices=("dedicated", "shared", "unknown"), default="unknown")
    return parser.parse_args()


def _git(fork: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=fork, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _source_hash(fork: Path) -> str:
    files = (
        "src/shaders/stereogram.frag",
        "src/ts/benchmark.ts",
        "src/ts/engine.ts",
        "src/ts/gl-utils/gl-canvas.ts",
    )
    digest = hashlib.sha256()
    for relative in files:
        digest.update(relative.encode())
        digest.update((fork / relative).read_bytes())
    return digest.hexdigest()


def _sanitize_hardware(value: object) -> str:
    """Mantém a família da GPU, removendo IDs e versões de driver."""

    text = re.sub(r"\s+", " ", str(value or "masked")).strip()
    text = re.sub(r"0x[0-9a-f]+", "<id>", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d+(?:\.\d+){2,}\b", "<version>", text)
    return text[:120]


def _read_raw(paths: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in paths:
        with path.open(encoding="utf-8") as stream:
            rows.extend(json.loads(line) for line in stream if line.strip())
    return rows


def import_records(
    paths: list[Path], fork: Path, power: str, workload: str
) -> list[BenchmarkRecord]:
    raw = _read_raw(paths)
    if not raw:
        raise ValueError("nenhuma medição encontrada")
    cases = {CASE_NAMES.get(str(row.get("case")), "") for row in raw}
    if cases != {"coracao", "texto-3d", "esfera"}:
        raise ValueError(f"esperados coração, texto-3d e esfera; recebidos: {sorted(cases)}")

    sha = _git(fork, "rev-parse", "HEAD")
    dirty = bool(_git(fork, "status", "--porcelain"))
    source_hash = _source_hash(fork)
    captured = min(
        datetime.fromisoformat(str(row["capturedAt"]).replace("Z", "+00:00")) for row in raw
    )
    run_id = f"webgl-{captured.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}-{sha[:8]}"
    records: list[BenchmarkRecord] = []
    for row in raw:
        case = CASE_NAMES.get(str(row.get("case")))
        if case is None:
            raise ValueError(f"caso WebGL desconhecido: {row.get('case')!r}")
        records.append(
            BenchmarkRecord(
                run_id=run_id,
                captured_at=datetime.fromisoformat(str(row["capturedAt"]).replace("Z", "+00:00")),
                git_sha=sha,
                git_dirty=dirty,
                source_sha256=source_hash,
                engine="webgl",
                engine_version=sha[:12],
                case=case,
                config={
                    "stripes_width": int(row["stripesWidth"]),
                    "depth": float(row["depth"]),
                    "depth_amplitude": float(row["depthAmplitude"]),
                    "gpu_vendor": _sanitize_hardware(row.get("gpuVendor")),
                    "gpu_renderer": _sanitize_hardware(row.get("gpuRenderer")),
                    "synchronization": str(row["synchronization"]),
                    "draws_per_sample": int(row.get("drawsPerSample", 1)),
                },
                width=int(row["width"]),
                height=int(row["height"]),
                oversample=1,
                seed=None,
                execution_type=str(row["executionType"]),
                iteration=int(row["iteration"]),
                duration_ms=float(row["durationMs"]),
                rgb_sha256=str(row["rgbSha256"]),
                python_version=None,
                runtime=str(row["runtime"]),
                operating_system=platform.system(),
                hardware=HardwareInfo(
                    architecture=platform.machine() or "unknown",
                    logical_cpus=max(1, int(row["logicalCpus"])),
                    power=power,
                    workload=workload,
                ),
            )
        )
    return records


def main() -> int:
    args = parse_args()
    if args.output.exists():
        raise SystemExit(f"recusado: {args.output} já existe")
    records = import_records(args.inputs, args.fork.resolve(), args.power, args.workload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(record.model_dump_json() + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
