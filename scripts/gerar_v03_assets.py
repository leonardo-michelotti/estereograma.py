"""Regenera os assets principais da Home com o motor V2 aprovado."""

from pathlib import Path

from app.stereogram.generator_v2 import RenderConfigV2, render_stereogram_v2
from app.stereogram.patterns import coracao_em_camadas

OUT = Path(__file__).resolve().parent.parent / "app" / "static" / "img" / "v03"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    depth = coracao_em_camadas(800, 600)
    depth.save(OUT / "hero-depth.png", optimize=True)

    hero = render_stereogram_v2(
        depth,
        RenderConfigV2(
            width=800,
            height=600,
            eye_separation=216,
            depth=0.26,
            oversample=3,
            mosaic_cell=2,
            occlusion="visibility",
            texture="mosaic",
            seed=24,
        ),
    )
    hero.save(OUT / "hero-estereograma.png", optimize=True)

    print(f"assets v0.3 gerados em {OUT}")


if __name__ == "__main__":
    main()
