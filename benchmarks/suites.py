"""Casos canônicos compartilhados por benchmark e testes dourados."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Literal

from PIL import Image

from app.stereogram.generator import gerar_estereograma
from app.stereogram.generator_v2 import (
    ENGINE_VERSION_V2,
    RenderConfigV2,
    render_stereogram_v2,
)
from app.stereogram.patterns import coracao_em_camadas, esfera

EngineName = Literal["legacy", "v2"]
DEPTH_FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "depth-maps"


@dataclass(frozen=True)
class EngineCase:
    slug: str
    engine: EngineName
    config: RenderConfigV2
    make_depth: Callable[[int, int], Image.Image]

    def render(self) -> Image.Image:
        depth = self.make_depth(self.config.width, self.config.height)
        if self.engine == "legacy":
            return gerar_estereograma(
                depth,
                largura=self.config.width,
                altura=self.config.height,
                eye_separation=self.config.eye_separation,
                mu=self.config.depth,
                textura="laboratorio",
                seed=self.config.seed,
            )
        return render_stereogram_v2(depth, self.config)

    @property
    def engine_version(self) -> str:
        return "legacy" if self.engine == "legacy" else ENGINE_VERSION_V2

    def serialized_config(self) -> dict[str, int | float | str | bool | None]:
        return asdict(self.config)


def _heart(width: int, height: int) -> Image.Image:
    return coracao_em_camadas(width, height)


def _text(width: int, height: int) -> Image.Image:
    with Image.open(DEPTH_FIXTURES / "texto-3d-v1.png") as fixture:
        depth = fixture.convert("L")
    if depth.size != (width, height):
        raise ValueError("o mapa canônico de texto exige resolução 900x560")
    return depth


def _sphere(width: int, height: int) -> Image.Image:
    return esfera(width, height, raio=190, gamma=0.8)


def golden_cases() -> tuple[EngineCase, ...]:
    base = RenderConfigV2()
    coarse_conflicts = replace(base, occlusion="conflicts", mosaic_cell=4)
    coarse_visibility = replace(base, occlusion="visibility", mosaic_cell=4)
    fine = replace(base, occlusion="visibility", mosaic_cell=2)
    return (
        EngineCase("01-controle-legacy", "legacy", base, _heart),
        EngineCase("02-v2-conflitos", "v2", coarse_conflicts, _heart),
        EngineCase("03-v2-visibilidade", "v2", coarse_visibility, _heart),
        EngineCase("04-v2-mosaico-fino", "v2", fine, _heart),
        EngineCase("05-v2-texto-3d", "v2", fine, _text),
        EngineCase("06-v2-esfera", "v2", fine, _sphere),
    )


def canonical_cases() -> tuple[EngineCase, ...]:
    base = RenderConfigV2()
    return (
        EngineCase("coracao", "v2", base, _heart),
        EngineCase("texto-3d", "v2", base, _text),
        EngineCase("esfera", "v2", base, _sphere),
    )
