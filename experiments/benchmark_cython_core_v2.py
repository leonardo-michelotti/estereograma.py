"""Compara o spike Cython com a Engine V2 Python sem alterar a integração."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import statistics
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
for path in (ROOT, EXPERIMENTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pyximport

os.environ["ESTEREOGRAMA_V2_FORCE_PYTHON"] = "1"
pyximport.install(
    build_dir=os.environ.get("CYTHON_BUILD_DIR", "/tmp/estereograma-cython-build"),
    setup_args={"include_dirs": [np.get_include()]},
    language_level=3,
    inplace=False,
)

from app.stereogram._core_v2 import render_rows, visibility_mask

from app.stereogram.generator_v2 import (
    RenderConfigV2,
    _constraint_maps,
    _paint_row,
    _prepare_depth,
    _separation_map,
    _texture_tile,
    _validate,
    _visibility_mask,
    render_stereogram_v2,
    separation,
)
from benchmarks.goldens import rgb_hash
from benchmarks.suites import canonical_cases, golden_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def prepare(
    depth_map: Image.Image,
    config: RenderConfigV2,
    *,
    compiled_visibility: bool = False,
) -> tuple[np.ndarray, ...]:
    depth = _prepare_depth(depth_map, config)
    scale = config.oversample
    virtual_width = config.width * scale
    virtual_eye_separation = config.eye_separation * scale
    virtual_period = separation(0.0, virtual_eye_separation, config.depth)
    texture = np.ascontiguousarray(_texture_tile(config, virtual_period))
    separations = _separation_map(depth, virtual_eye_separation, config.depth)

    if config.occlusion == "visibility":
        output_depth = depth[:, ::scale][:, : config.width]
        if compiled_visibility:
            visibility = visibility_mask(
                np.ascontiguousarray(output_depth, dtype=np.float32),
                config.eye_separation,
                config.depth,
            ).astype(bool, copy=False)
        else:
            visibility = _visibility_mask(output_depth, config.eye_separation, config.depth)
        visibility = np.repeat(visibility, scale, axis=1)[:, :virtual_width]
    else:
        visibility = None

    left, right, active = _constraint_maps(separations, visibility)
    return (
        np.ascontiguousarray(left, dtype=np.int32),
        np.ascontiguousarray(right, dtype=np.int32),
        np.ascontiguousarray(active, dtype=np.uint8),
        texture,
        np.asarray([virtual_period], dtype=np.int32),
    )


def render_rows_python(
    left: np.ndarray,
    right: np.ndarray,
    active: np.ndarray,
    texture: np.ndarray,
    virtual_period: int,
) -> np.ndarray:
    height, width = left.shape
    base_indices = tuple(range(width))
    base_colors = tuple(index % virtual_period for index in base_indices)
    virtual = np.empty((height, width, 3), dtype=np.uint8)
    from app.stereogram.generator_v2 import _build_links

    for y in range(height):
        links = _build_links(
            left[y].tolist(),
            right[y].tolist(),
            active[y].tolist(),
            base_indices,
        )
        virtual[y] = _paint_row(*links, texture[y], base_colors)
    return virtual


def render_stereogram_compiled(depth_map: Image.Image, config: RenderConfigV2) -> Image.Image:
    _validate(config)
    left, right, active, texture, period_array = prepare(depth_map, config)
    virtual = render_rows(left, right, active, texture, int(period_array[0]))
    high_res = Image.fromarray(virtual, mode="RGB")
    return high_res.resize((config.width, config.height), Image.Resampling.LANCZOS)


def render_stereogram_compiled_visibility(
    depth_map: Image.Image, config: RenderConfigV2
) -> Image.Image:
    _validate(config)
    left, right, active, texture, period_array = prepare(
        depth_map, config, compiled_visibility=True
    )
    virtual = render_rows(left, right, active, texture, int(period_array[0]))
    high_res = Image.fromarray(virtual, mode="RGB")
    return high_res.resize((config.width, config.height), Image.Resampling.LANCZOS)


def summarize(samples: list[float]) -> dict[str, object]:
    ordered = sorted(samples)
    return {
        "samples_ms": samples,
        "median_ms": statistics.median(samples),
        "p95_ms": float(np.percentile(ordered, 95)),
    }


def measure_pair(
    python_callable,
    cython_callable,
    warmup: int,
    repeat: int,
) -> tuple[dict[str, object], dict[str, object]]:
    """Alterna a ordem para reduzir viés de frequência, carga e aquecimento."""
    for index in range(warmup):
        ordered = (python_callable, cython_callable)
        if index % 2:
            ordered = tuple(reversed(ordered))
        for callable_ in ordered:
            callable_()

    samples = {"python": [], "cython": []}
    for index in range(repeat):
        ordered = (("python", python_callable), ("cython", cython_callable))
        if index % 2:
            ordered = tuple(reversed(ordered))
        for name, callable_ in ordered:
            started = time.perf_counter_ns()
            callable_()
            samples[name].append((time.perf_counter_ns() - started) / 1_000_000)
    return summarize(samples["python"]), summarize(samples["cython"])


def measure_variants(
    callables: dict[str, object], warmup: int, repeat: int
) -> dict[str, dict[str, object]]:
    names = list(callables)
    samples: dict[str, list[float]] = {name: [] for name in names}
    for index in range(warmup + repeat):
        start = index % len(names)
        ordered = names[start:] + names[:start]
        for name in ordered:
            callable_ = callables[name]
            started = time.perf_counter_ns()
            callable_()  # type: ignore[operator]
            duration = (time.perf_counter_ns() - started) / 1_000_000
            if index >= warmup:
                samples[name].append(duration)
    return {name: summarize(values) for name, values in samples.items()}


def verify_all_goldens() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for case in golden_cases():
        expected = case.render().convert("RGB")
        if case.engine == "legacy":
            rows_actual = expected
            visibility_actual = expected
        else:
            depth = case.make_depth(case.config.width, case.config.height)
            rows_actual = render_stereogram_compiled(depth, case.config)
            visibility_actual = render_stereogram_compiled_visibility(depth, case.config)
        equal = np.array_equal(np.asarray(expected), np.asarray(rows_actual))
        visibility_equal = np.array_equal(
            np.asarray(expected), np.asarray(visibility_actual)
        )
        results.append(
            {
                "case": case.slug,
                "equal": equal,
                "visibility_equal": visibility_equal,
                "rgb_sha256": rgb_hash(visibility_actual),
            }
        )
        if not equal or not visibility_equal:
            raise AssertionError(f"golden divergente: {case.slug}")
    return results


def verify_parameter_matrix() -> dict[str, object]:
    """Compara Python/Cython fora da configuração canônica aprovada."""
    results: list[dict[str, object]] = []
    textures = ("organic", "color", "mono", "mosaic")
    occlusions = ("conflicts", "visibility")
    oversamples = (1, 2, 3)
    seeds = (0, 42)

    for texture, occlusion, oversample, seed in itertools.product(
        textures, occlusions, oversamples, seeds
    ):
        config = RenderConfigV2(
            width=240,
            height=160,
            eye_separation=80,
            depth=0.31,
            oversample=oversample,
            mosaic_cell=3,
            depth_blur=0.4,
            occlusion=occlusion,  # type: ignore[arg-type]
            texture=texture,  # type: ignore[arg-type]
            seed=seed,
        )
        y, x = np.ogrid[: config.height, : config.width]
        depth = Image.fromarray(
            (((x * 3 + y * 5) % 256)).astype(np.uint8), mode="L"
        )
        expected = render_stereogram_v2(depth, config)
        actual = render_stereogram_compiled_visibility(depth, config)
        if not np.array_equal(np.asarray(expected), np.asarray(actual)):
            raise AssertionError(
                f"matriz divergente: {texture}/{occlusion}/{oversample}/{seed}"
            )
        results.append(
            {
                "texture": texture,
                "occlusion": occlusion,
                "oversample": oversample,
                "seed": seed,
                "rgb_sha256": rgb_hash(actual),
            }
        )

    resolutions: list[dict[str, object]] = []
    for width, height, eye_separation, oversample in (
        (180, 120, 80, 1),
        (320, 200, 96, 2),
        (640, 400, 160, 3),
    ):
        config = RenderConfigV2(
            width=width,
            height=height,
            eye_separation=eye_separation,
            oversample=oversample,
            seed=7,
        )
        depth = Image.fromarray(
            np.linspace(0, 255, width * height, dtype=np.uint8).reshape(height, width),
            mode="L",
        )
        expected = render_stereogram_v2(depth, config)
        actual = render_stereogram_compiled_visibility(depth, config)
        if not np.array_equal(np.asarray(expected), np.asarray(actual)):
            raise AssertionError(f"resolução divergente: {width}x{height}/{oversample}x")
        resolutions.append(
            {
                "width": width,
                "height": height,
                "oversample": oversample,
                "rgb_sha256": rgb_hash(actual),
            }
        )

    return {
        "combinations": len(results),
        "resolutions": resolutions,
        "results": results,
    }


def main() -> int:
    args = parse_args()
    result: dict[str, object] = {
        "experiment": "cython-core-v2",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "warmup": args.warmup,
        "repeat": args.repeat,
        "goldens": verify_all_goldens(),
        "parameter_matrix": verify_parameter_matrix(),
        "cases": {},
    }

    cases: dict[str, object] = result["cases"]  # type: ignore[assignment]
    for case in canonical_cases():
        depth = case.make_depth(case.config.width, case.config.height)
        left, right, active, texture, period_array = prepare(depth, case.config)
        period = int(period_array[0])

        pure_virtual = render_rows_python(left, right, active, texture, period)
        compiled_virtual = render_rows(left, right, active, texture, period)
        if not np.array_equal(pure_virtual, compiled_virtual):
            raise AssertionError(f"núcleo divergente: {case.slug}")

        core_python, core_cython = measure_pair(
            lambda left=left, right=right, active=active, texture=texture, period=period: render_rows_python(
                left, right, active, texture, period
            ),
            lambda left=left, right=right, active=active, texture=texture, period=period: render_rows(
                left, right, active, texture, period
            ),
            args.warmup,
            args.repeat,
        )
        config = case.config
        variants = measure_variants(
            {
                "python": lambda depth=depth, config=config: render_stereogram_v2(
                    depth, config
                ),
                "cython": lambda depth=depth, config=config: render_stereogram_compiled(
                    depth, config
                ),
                "cython_visibility": lambda depth=depth, config=config: render_stereogram_compiled_visibility(
                    depth, config
                ),
            },
            args.warmup,
            args.repeat,
        )
        pure = variants["python"]
        compiled = variants["cython"]
        compiled_visibility = variants["cython_visibility"]
        pure_median = float(pure["median_ms"])
        compiled_median = float(compiled["median_ms"])
        cases[case.slug] = {
            "config": asdict(case.config),
            "virtual_sha256": hashlib.sha256(compiled_virtual.tobytes()).hexdigest(),
            "core_python": core_python,
            "core_cython": core_cython,
            "python": pure,
            "cython": compiled,
            "cython_visibility": compiled_visibility,
            "median_speedup": pure_median / compiled_median,
            "median_speedup_visibility": pure_median
            / float(compiled_visibility["median_ms"]),
        }
        print(
            f"{case.slug:<10} Python {pure_median:8.2f} ms | "
            f"Cython {compiled_median:8.2f} ms | "
            f"+visibility {float(compiled_visibility['median_ms']):8.2f} ms | "
            f"{pure_median / float(compiled_visibility['median_ms']):5.2f}x"
        )

    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(args.output)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
