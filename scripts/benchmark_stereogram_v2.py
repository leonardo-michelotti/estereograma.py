"""Compara oversampling 3× e 4× no motor V2.

Uso:
    python scripts/benchmark_stereogram_v2.py
    python scripts/benchmark_stereogram_v2.py --repeticoes 3
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import replace
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.stereogram.generator_v2 import (  # noqa: E402
    RenderConfigV2,
    render_stereogram_v2,
)
from app.stereogram.patterns import coracao_em_camadas, esfera, texto  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeticoes", type=int, default=1, choices=range(1, 11))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = RenderConfigV2()
    shapes = {
        "coração": coracao_em_camadas(base.width, base.height),
        "texto": texto("3D", base.width, base.height, profundidade_fundo=20),
        "esfera": esfera(base.width, base.height, raio=190, gamma=0.8),
    }

    print("forma     escala  mediana    buffer RGB")
    print("--------- ------ ----------- -----------")
    for oversample in (3, 4):
        config = replace(base, oversample=oversample)
        buffer_mib = config.width * config.height * oversample * 3 / 1024 / 1024
        for name, depth_map in shapes.items():
            samples = []
            for _ in range(args.repeticoes):
                started = perf_counter()
                render_stereogram_v2(depth_map, config)
                samples.append(perf_counter() - started)
            print(
                f"{name:<9} {oversample:>4}×  {statistics.median(samples):>8.3f} s"
                f"  {buffer_mib:>7.1f} MiB"
            )


if __name__ == "__main__":
    main()
