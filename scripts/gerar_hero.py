"""Gera os PNGs do hero da home (estereograma + reveal da figura escondida)."""

from pathlib import Path

from app.stereogram.generator import gerar_estereograma
from app.stereogram.patterns import coracao, esfera

OUT = Path(__file__).resolve().parent.parent / "app" / "static" / "img" / "hero"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Coração — depth map base (reveal da figura escondida)
    depth = coracao(800, 600)
    depth.save(OUT / "coracao_depth.png")

    # Estereograma destaque do hero
    estereo = gerar_estereograma(
        depth_map=depth,
        largura=800,
        altura=600,
        eye_separation=210,
        mu=0.45,
        textura="pink_noise",
        seed=42,
    )
    estereo.save(OUT / "coracao_estereo.png", optimize=True)

    # Mini estereograma do tutorial inline (esfera, depth+mu suaves)
    mini_depth = esfera(400, 300)
    mini_depth.save(OUT / "mini_depth.png")
    mini_estereo = gerar_estereograma(
        depth_map=mini_depth,
        largura=400,
        altura=300,
        eye_separation=180,
        mu=0.4,
        textura="pink_noise",
        seed=7,
    )
    mini_estereo.save(OUT / "mini_estereo.png", optimize=True)

    print(f"hero em {OUT}")


if __name__ == "__main__":
    main()
