"""Orquestra depth map, geração determinística e cache de renders."""

from __future__ import annotations

import hashlib
import io
import json
import secrets
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from app.models.generation import GenerationParams, SubjectType
from app.services.render_cache import RenderCache
from app.stereogram.generator_v2 import (
    ENGINE_VERSION_V2,
    RenderConfigV2,
    render_stereogram_v2,
)
from app.stereogram.patterns import texto
from app.stereogram.presets import caminho_arquivo, preset_por_slug


@dataclass(frozen=True)
class GenerationResult:
    render_id: str
    depth_id: str
    params: GenerationParams
    cache_hit: bool
    duration_ms: int
    guide_separation: int
    engine_version: str


class GenerationBusyError(ValueError):
    """Indica que o limite de renders simultâneos foi atingido."""


class GenerationService:
    def __init__(self, static_dir: Path, cache: RenderCache | None = None) -> None:
        self.static_dir = static_dir
        self.cache = cache or RenderCache()
        self._generation_slots = threading.BoundedSemaphore(2)

    def generate(self, params: GenerationParams) -> GenerationResult:
        started = time.perf_counter()
        if params.seed is None:
            params = params.model_copy(update={"seed": secrets.randbits(32)})

        render_config = self._render_config(params)
        render_id = self._fingerprint(params)
        depth_id = f"{render_id}-depth"
        cached = self.cache.get(render_id)
        cached_depth = self.cache.get(depth_id)
        if cached is not None and cached_depth is not None:
            return GenerationResult(
                render_id,
                depth_id,
                params,
                True,
                self._elapsed(started),
                render_config.far_separation,
                ENGINE_VERSION_V2,
            )

        if not self._generation_slots.acquire(blocking=False):
            raise GenerationBusyError(
                "O laboratório está processando duas imagens. Aguarde alguns segundos e tente novamente."
            )
        try:
            cached = self.cache.get(render_id)
            cached_depth = self.cache.get(depth_id)
            if cached is not None and cached_depth is not None:
                return GenerationResult(
                    render_id,
                    depth_id,
                    params,
                    True,
                    self._elapsed(started),
                    render_config.far_separation,
                    ENGINE_VERSION_V2,
                )

            depth_map = self._depth_map(params)
            result = render_stereogram_v2(depth_map, render_config)
            self.cache.put(render_id, self._png_bytes(result))
            self.cache.put(depth_id, self._png_bytes(depth_map.convert("L")))
            return GenerationResult(
                render_id,
                depth_id,
                params,
                False,
                self._elapsed(started),
                render_config.far_separation,
                ENGINE_VERSION_V2,
            )
        finally:
            self._generation_slots.release()

    def render_path(self, render_id: str) -> Path | None:
        try:
            return self.cache.get(render_id)
        except ValueError:
            return None

    def _depth_map(self, params: GenerationParams) -> Image.Image:
        if params.subject_type is SubjectType.TEXT:
            return texto(params.subject, params.width, params.height)

        preset = preset_por_slug(params.subject)
        if preset is None or preset.slug not in {"esfera", "coracao"}:
            raise ValueError("Escolha uma forma disponível: esfera ou coração.")
        with Image.open(caminho_arquivo(preset, self.static_dir)) as image:
            return image.convert("L").copy()

    @staticmethod
    def _render_config(params: GenerationParams) -> RenderConfigV2:
        if params.seed is None:
            raise ValueError("A seed precisa ser resolvida antes da geração.")
        return RenderConfigV2(
            width=params.width,
            height=params.height,
            eye_separation=params.eye_separation,
            depth=params.engine_mu,
            texture=params.texture.value,  # type: ignore[arg-type]
            seed=params.seed,
        )

    @staticmethod
    def _fingerprint(params: GenerationParams) -> str:
        payload = json.dumps(
            {"engine": ENGINE_VERSION_V2, "params": params.model_dump(mode="json")},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def _png_bytes(image: Image.Image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    @staticmethod
    def _elapsed(started: float) -> int:
        return round((time.perf_counter() - started) * 1000)
