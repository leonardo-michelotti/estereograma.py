"""Exporta os insumos canônicos para o fork WebGL, sem código compartilhado."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from PIL import Image

from app.stereogram.generator_v2 import RenderConfigV2, _texture_tile
from app.stereogram.patterns import coracao_em_camadas, esfera, texto


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Diretório resources/ do fork WebGL")
    args = parser.parse_args()

    heightmaps = args.output / "heightmaps"
    tiles = args.output / "tiles"
    heightmaps.mkdir(parents=True, exist_ok=True)
    tiles.mkdir(parents=True, exist_ok=True)

    config = RenderConfigV2()
    assets = {
        "lab-heart.png": coracao_em_camadas(config.width, config.height),
        "lab-text-3d.png": texto("3D", config.width, config.height, profundidade_fundo=20),
        "lab-sphere.png": esfera(config.width, config.height, raio=190, gamma=0.8),
    }
    for filename, image in assets.items():
        image.convert("L").save(heightmaps / filename, format="PNG", optimize=True)

    output_config = replace(config, oversample=1)
    tile = _texture_tile(output_config, output_config.far_separation)
    Image.fromarray(tile, mode="RGB").save(tiles / "lab-mosaic.png", format="PNG", optimize=True)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
