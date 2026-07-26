"""Coleta dados brutos: python -m benchmarks.run --help."""

from __future__ import annotations

import argparse
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter_ns

import numpy as np

from benchmarks.environment import git_dirty, git_sha, runtime_metadata, source_sha256
from benchmarks.schema import BenchmarkRecord
from benchmarks.suites import canonical_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["v2"], default="v2")
    parser.add_argument("--suite", choices=["canonical"], default="canonical")
    parser.add_argument("--repeat", type=int, default=10, choices=range(1, 51))
    parser.add_argument("--warmup", type=int, default=2, choices=range(11))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--power", choices=["ac", "battery", "unknown"], default="unknown")
    parser.add_argument("--workload", choices=["dedicated", "shared", "unknown"], default="unknown")
    return parser.parse_args()


def rgb_hash(image: object) -> str:
    rgb = np.asarray(image, dtype=np.uint8)
    return hashlib.sha256(rgb.tobytes(order="C")).hexdigest()


def main() -> int:
    args = parse_args()
    if args.output.exists():
        raise SystemExit(f"recusado: o dataset bruto já existe: {args.output}")

    captured_at = datetime.now(UTC)
    source_hash = source_sha256()
    run_id = f"v2-{captured_at:%Y%m%dT%H%M%SZ}-{source_hash[:8]}"
    shared = {
        "run_id": run_id,
        "captured_at": captured_at,
        "git_sha": git_sha(),
        "git_dirty": git_dirty(),
        "source_sha256": source_hash,
        **runtime_metadata(args.power, args.workload),
    }

    records: list[BenchmarkRecord] = []
    for case in canonical_cases():
        total = args.warmup + args.repeat
        for index in range(total):
            started = perf_counter_ns()
            image = case.render()
            duration_ms = (perf_counter_ns() - started) / 1_000_000
            is_warmup = index < args.warmup
            records.append(
                BenchmarkRecord(
                    **shared,
                    engine=case.engine,
                    engine_version=case.engine_version,
                    case=case.slug,
                    config=case.serialized_config(),
                    width=case.config.width,
                    height=case.config.height,
                    oversample=case.config.oversample,
                    seed=case.config.seed,
                    execution_type="warmup" if is_warmup else "measure",
                    iteration=index + 1 if is_warmup else index - args.warmup + 1,
                    duration_ms=duration_ms,
                    rgb_sha256=rgb_hash(image),
                )
            )
            print(
                f"{case.slug:<10} {'warmup' if is_warmup else 'measure':<7} "
                f"{records[-1].iteration:>2}: {duration_ms:>8.2f} ms"
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(record.model_dump_json() + "\n")
    print(f"run_id={run_id}")
    print(f"dataset={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
