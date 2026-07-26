from pathlib import Path

import pytest

from app.models.generation import GenerationParams
from app.services.generation_service import GenerationService
from app.services.render_cache import RenderCache


def test_texto_limita_doze_caracteres():
    with pytest.raises(ValueError, match="12 caracteres"):
        GenerationParams(subject_type="text", subject="MUITO TEXTO AQUI")


def test_generation_service_reaproveita_cache(tmp_path: Path):
    static_dir = Path(__file__).parents[1] / "app" / "static"
    service = GenerationService(static_dir, RenderCache(tmp_path))
    params = GenerationParams(width=240, height=120, eye_separation=120, seed=42)

    first = service.generate(params)
    second = service.generate(params)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.render_id == first.render_id
    assert first.engine_version == "v2.0"
    assert first.guide_separation == 60
    assert service.render_path(first.render_id).is_file()
    assert service.render_path(first.depth_id).is_file()


def test_cache_muda_quando_a_versao_do_motor_muda():
    params = GenerationParams(seed=42)
    fingerprint = GenerationService._fingerprint(params)
    assert len(fingerprint) == 32
    assert fingerprint != GenerationService._fingerprint(params.model_copy(update={"seed": 43}))
