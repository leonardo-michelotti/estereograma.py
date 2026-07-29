"""Perfila o render completo com o spike Cython já compilado."""

from __future__ import annotations

import argparse
import cProfile
import pstats
from pathlib import Path

from benchmark_cython_core_v2 import render_stereogram_compiled_visibility

from benchmarks.suites import canonical_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=15)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lines: list[str] = []
    for case in canonical_cases():
        depth = case.make_depth(case.config.width, case.config.height)
        render_stereogram_compiled_visibility(depth, case.config)
        profiler = cProfile.Profile()
        profiler.enable()
        render_stereogram_compiled_visibility(depth, case.config)
        profiler.disable()

        stats = pstats.Stats(profiler).strip_dirs().sort_stats("cumulative")
        lines.extend((f"## {case.slug}", "", "```text"))
        from io import StringIO

        stream = StringIO()
        stats.stream = stream
        stats.print_stats(args.limit)
        lines.extend(stream.getvalue().strip().splitlines())
        lines.extend(("```", ""))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
