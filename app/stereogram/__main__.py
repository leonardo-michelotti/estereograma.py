"""CLI: python -m app.stereogram <depth_map> <saida> [opções]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from app.stereogram.generator import gerar_estereograma


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gera um autostereograma a partir de um depth map "
        "(algoritmo de classes de equivalência, Thimbleby 1994)."
    )
    parser.add_argument("depth_map", type=Path, help="Imagem de profundidade (escala de cinza).")
    parser.add_argument("saida", type=Path, help="Caminho do PNG de saída.")
    parser.add_argument("--largura", type=int, default=800)
    parser.add_argument("--altura", type=int, default=600)
    parser.add_argument(
        "--eye-separation",
        type=int,
        default=200,
        help="Distância entre olhos em pixels (E). Tipicamente 180-240.",
    )
    parser.add_argument(
        "--mu",
        type=float,
        default=0.333,
        help="Fator de depth-of-field (0-1). Maior = mais 3D, mais difícil fundir.",
    )
    parser.add_argument(
        "--textura",
        choices=["pink_noise", "random_dots", "random_dots_bw", "colorido", "custom"],
        default="pink_noise",
    )
    parser.add_argument("--textura-custom", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)

    if not args.depth_map.exists():
        print(f"erro: depth map não encontrado: {args.depth_map}", file=sys.stderr)
        return 1

    depth = Image.open(args.depth_map)
    textura_custom = Image.open(args.textura_custom) if args.textura_custom else None

    resultado = gerar_estereograma(
        depth_map=depth,
        largura=args.largura,
        altura=args.altura,
        eye_separation=args.eye_separation,
        mu=args.mu,
        textura=args.textura,
        textura_custom=textura_custom,
        seed=args.seed,
    )
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    resultado.save(args.saida)
    print(f"ok: {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
