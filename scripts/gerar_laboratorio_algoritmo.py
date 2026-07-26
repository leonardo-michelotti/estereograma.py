"""Gera uma galeria isolada para avaliar visualmente o novo algoritmo."""

from __future__ import annotations

import html
import sys
from dataclasses import replace
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.stereogram.generator import gerar_estereograma  # noqa: E402
from app.stereogram.patterns import coracao_em_camadas, esfera, texto  # noqa: E402
from app.stereogram.generator_v2 import (  # noqa: E402
    RenderConfigV2,
    render_stereogram_v2,
)

OUTPUT = ROOT / "exemplos" / "algoritmo-v2"


def add_guides(image: Image.Image, separation: int) -> Image.Image:
    margin = 54
    canvas = Image.new("RGB", (image.width, image.height + margin), (247, 242, 232))
    canvas.paste(image, (0, margin))
    draw = ImageDraw.Draw(canvas)
    center = image.width // 2
    radius = 7
    for x in (center - separation // 2, center + separation // 2):
        draw.ellipse(
            (x - radius, 20 - radius, x + radius, 20 + radius),
            fill=(255, 90, 69),
            outline=(32, 34, 28),
            width=2,
        )
    draw.line((0, margin - 1, image.width, margin - 1), fill=(32, 34, 28), width=1)
    return canvas


def save_candidate(
    filename: str,
    separation: int,
    renderer: Callable[[], Image.Image],
) -> str:
    target = OUTPUT / filename
    add_guides(renderer(), separation).save(target, optimize=True)
    return filename


def make_gallery(cards: list[tuple[str, str, str]]) -> None:
    rendered_cards = []
    for filename, title, description in cards:
        rendered_cards.append(
            f"""
            <article>
              <div class="copy"><span>{html.escape(filename[:2])}</span>
                <h2>{html.escape(title)}</h2><p>{html.escape(description)}</p>
              </div>
              <img src="{html.escape(filename)}" width="900" alt="{html.escape(title)}">
            </article>
            """
        )

    page = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Laboratório do algoritmo — estereograma.py</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #20221c; color: #f7f2e8;
      font-family: Arial, sans-serif; }}
    header {{ max-width: 980px; margin: 0 auto; padding: 42px 40px 24px; }}
    h1 {{ margin: 0 0 12px; font-size: 38px; letter-spacing: -1.5px; }}
    header p {{ max-width: 720px; color: #cbc7bc; line-height: 1.5; }}
    main {{ max-width: 980px; margin: auto; padding: 0 40px 80px; }}
    article {{ margin: 28px 0 64px; }}
    .copy {{ display: grid; grid-template-columns: 34px 1fr; align-items: baseline; }}
    .copy span {{ color: #ff5a45; font: 700 12px monospace; }}
    h2 {{ margin: 0; font-size: 22px; }}
    .copy p {{ grid-column: 2; margin: 7px 0 16px; color: #cbc7bc; }}
    img {{ display: block; width: 900px; max-width: none; border: 1px solid #0d0e0b;
      box-shadow: 10px 10px 0 #0d0e0b; image-rendering: auto; }}
    .hint {{ border-top: 1px solid #57594f; padding-top: 18px; font-size: 14px; }}
  </style>
</head>
<body>
  <header>
    <h1>Qual deles abre mais fácil?</h1>
    <p>Veja em 100% de zoom. Relaxe o foco até os dois pontos corais virarem
    três; mantenha o ponto central e desça os olhos para a imagem.</p>
    <p class="hint">A primeira imagem é o controle antigo. As demais ainda não
    estão conectadas ao site.</p>
  </header>
  <main>{"".join(rendered_cards)}</main>
</body>
</html>"""
    (OUTPUT / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    base = RenderConfigV2()
    heart = coracao_em_camadas(base.width, base.height)

    old = gerar_estereograma(
        heart,
        largura=base.width,
        altura=base.height,
        eye_separation=base.eye_separation,
        mu=base.depth,
        textura="laboratorio",
        seed=base.seed,
    )
    cards: list[tuple[str, str, str]] = []
    name = save_candidate("01-controle-atual.png", base.far_separation, lambda: old)
    cards.append((name, "Controle atual", "Mesmo coração, paleta, profundidade e semente."))

    links = replace(base, occlusion="conflicts", mosaic_cell=4)
    name = save_candidate(
        "02-v2-conflitos.png",
        links.far_separation,
        lambda: render_stereogram_v2(heart, links),
    )
    cards.append(
        (name, "V2 — restrição mais próxima", "Remove conflitos e pinta do centro para fora.")
    )

    visible = replace(base, occlusion="visibility", mosaic_cell=4)
    name = save_candidate(
        "03-v2-visibilidade.png",
        visible.far_separation,
        lambda: render_stereogram_v2(heart, visible),
    )
    cards.append(
        (name, "V2 — visibilidade", "Também remove vínculos escondidos pelo primeiro plano.")
    )

    fine = replace(base, occlusion="visibility", mosaic_cell=2)
    name = save_candidate(
        "04-v2-mosaico-fino.png",
        fine.far_separation,
        lambda: render_stereogram_v2(heart, fine),
    )
    cards.append(
        (name, "V2 — mosaico fino", "Mesmas cores, pontos menores para reforçar os contornos.")
    )

    text_depth = texto("3D", base.width, base.height, profundidade_fundo=20)
    name = save_candidate(
        "05-v2-texto-3d.png",
        fine.far_separation,
        lambda: render_stereogram_v2(text_depth, fine),
    )
    cards.append(
        (name, "Teste cego — texto 3D", "Se o motor estiver bom, as duas letras devem saltar.")
    )

    sphere_config = replace(fine, oversample=3)
    sphere_depth = esfera(base.width, base.height, raio=190, gamma=0.8)
    name = save_candidate(
        "06-v2-esfera.png",
        sphere_config.far_separation,
        lambda: render_stereogram_v2(sphere_depth, sphere_config),
    )
    cards.append(
        (name, "Teste de volume — esfera", "Avalia gradação contínua, não apenas silhuetas planas.")
    )

    make_gallery(cards)
    print(f"Galeria gerada em {OUTPUT / 'index.html'}")


if __name__ == "__main__":
    main()
