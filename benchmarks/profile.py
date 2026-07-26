"""Perfila os casos canônicos e escreve um relatório de hotspots."""

from __future__ import annotations

import argparse
import cProfile
import pstats
from pathlib import Path

from benchmarks.suites import canonical_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    chunks = []
    for case in canonical_cases():
        case.render()
        profiler = cProfile.Profile()
        profiler.enable()
        case.render()
        profiler.disable()
        stats = pstats.Stats(profiler).strip_dirs().sort_stats("cumtime")
        rows = []
        for (filename, line, function), values in stats.stats.items():
            if filename != "generator_v2.py":
                continue
            primitive_calls, total_calls, own_time, cumulative_time, _ = values
            rows.append((cumulative_time, own_time, total_calls, primitive_calls, line, function))
        rows.sort(reverse=True)
        chunks.extend(
            [
                f"## {case.slug}",
                "",
                "| função | chamadas | próprio s | acumulado s |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for cumulative, own, total, _primitive, line, function in rows[: args.limit]:
            chunks.append(f"| `{function}` (L{line}) | {total} | {own:.4f} | {cumulative:.4f} |")
        chunks.append("")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(chunks), encoding="utf-8", newline="\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
