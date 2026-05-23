"""Catálogo de presets do playground.

Cada preset é uma entrada que aponta pra um depth map em
app/static/img/presets/ e carrega defaults sugeridos de geração.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Preset:
    slug: str
    titulo: str
    arquivo: str
    dica: str
    eye_separation: int = 200
    mu: float = 0.333


PRESETS: tuple[Preset, ...] = (
    Preset(
        slug="esfera",
        titulo="Esfera",
        arquivo="esfera.png",
        dica="Uma esfera saltando no centro.",
    ),
    Preset(
        slug="coracao",
        titulo="Coração",
        arquivo="coracao.png",
        dica="Um coração em alto-relevo.",
    ),
    Preset(
        slug="texto_3d",
        titulo='Texto "3D"',
        arquivo="texto_3d.png",
        dica='As letras "3D" em relevo.',
        eye_separation=180,
    ),
)


def preset_por_slug(slug: str) -> Preset | None:
    return next((p for p in PRESETS if p.slug == slug), None)


def caminho_arquivo(preset: Preset, base_dir: Path) -> Path:
    return base_dir / "img" / "presets" / preset.arquivo
