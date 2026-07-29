"""Mede escalabilidade por threads do render Cython da Engine V2."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.stereogram.generator_v2 import ENGINE_IMPLEMENTATION_V2, render_stereogram_v2
from benchmarks.suites import canonical_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", default="1,2,4,8")
    parser.add_argument("--requests", type=int, default=16)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-cython", action="store_true")
    return parser.parse_args()


def percentile_95(values: list[float]) -> float:
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[94]


def main() -> int:
    args = parse_args()
    workers = tuple(int(value) for value in args.workers.split(","))
    if not workers or any(value < 1 for value in workers):
        raise ValueError("workers deve conter inteiros positivos")
    if args.requests < max(workers):
        raise ValueError("requests deve ser maior ou igual ao maior número de workers")
    if args.require_cython and ENGINE_IMPLEMENTATION_V2 != "cython":
        raise RuntimeError(
            f"núcleo Cython obrigatório; implementação ativa: {ENGINE_IMPLEMENTATION_V2}"
        )

    case = canonical_cases()[0]
    depth = case.make_depth(case.config.width, case.config.height)

    def render_once() -> tuple[float, str]:
        started = time.perf_counter_ns()
        image = render_stereogram_v2(depth.copy(), case.config)
        duration_ms = (time.perf_counter_ns() - started) / 1_000_000
        return duration_ms, hashlib.sha256(image.tobytes()).hexdigest()

    for _ in range(args.warmup):
        render_once()

    runs: list[dict[str, float | int]] = []
    reference_hash: str | None = None
    for worker_count in workers:
        wall_started = time.perf_counter_ns()
        cpu_started = time.process_time_ns()
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            results = list(executor.map(lambda _: render_once(), range(args.requests)))
        cpu_seconds = (time.process_time_ns() - cpu_started) / 1_000_000_000
        wall_seconds = (time.perf_counter_ns() - wall_started) / 1_000_000_000
        durations = [duration for duration, _ in results]
        hashes = {rgb_hash for _, rgb_hash in results}
        if len(hashes) != 1:
            raise AssertionError("renders concorrentes produziram hashes diferentes")
        current_hash = hashes.pop()
        if reference_hash is None:
            reference_hash = current_hash
        elif current_hash != reference_hash:
            raise AssertionError("hash RGB mudou entre níveis de concorrência")
        runs.append(
            {
                "workers": worker_count,
                "requests": args.requests,
                "wall_seconds": wall_seconds,
                "cpu_seconds": cpu_seconds,
                "cpu_wall_ratio": cpu_seconds / wall_seconds,
                "throughput_renders_s": args.requests / wall_seconds,
                "median_latency_ms": statistics.median(durations),
                "p95_latency_ms": percentile_95(durations),
            }
        )

    serial_throughput = float(runs[0]["throughput_renders_s"])
    for run in runs:
        run["throughput_speedup"] = float(run["throughput_renders_s"]) / serial_throughput

    payload = {
        "experiment": "cython-v2-thread-load",
        "implementation": ENGINE_IMPLEMENTATION_V2,
        "case": case.slug,
        "rgb_sha256": reference_hash,
        "warmup": args.warmup,
        "runs": runs,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8", newline="\n")
        print(args.output)
    else:
        print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
