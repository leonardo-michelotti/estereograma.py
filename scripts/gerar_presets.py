"""Gera os depth maps preset em app/static/img/presets/."""

from pathlib import Path

from app.stereogram.patterns import coracao, esfera, texto

OUT = Path(__file__).resolve().parent.parent / "app" / "static" / "img" / "presets"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    esfera().save(OUT / "esfera.png")
    coracao().save(OUT / "coracao.png")
    texto("3D").save(OUT / "texto_3d.png")
    print(f"presets em {OUT}")


if __name__ == "__main__":
    main()
