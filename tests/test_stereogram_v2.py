import inspect
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest
from PIL import Image

import app.stereogram as public_stereogram
from app.stereogram.generator_v2 import (
    ENGINE_IMPLEMENTATION_V2,
    ENGINE_VERSION_V2,
    RenderConfigV2,
    _visibility_mask,
    render_stereogram_v2,
    separation,
)


def test_api_publica_v2_permanece_compativel():
    assert public_stereogram.ENGINE_VERSION_V2 == ENGINE_VERSION_V2 == "v2.0"
    assert public_stereogram.RenderConfigV2 is RenderConfigV2
    assert public_stereogram.render_stereogram_v2 is render_stereogram_v2
    assert list(inspect.signature(RenderConfigV2).parameters) == [
        "width",
        "height",
        "eye_separation",
        "depth",
        "oversample",
        "mosaic_cell",
        "depth_blur",
        "occlusion",
        "texture",
        "seed",
    ]
    assert list(inspect.signature(render_stereogram_v2).parameters) == [
        "depth_map",
        "config",
    ]


def test_ci_pode_exigir_nucleo_compilado():
    if os.environ.get("ESTEREOGRAMA_EXPECT_COMPILED") == "1":
        assert ENGINE_IMPLEMENTATION_V2 == "cython"


def test_separacao_diminui_quando_objeto_se_aproxima():
    far = separation(0.0, 216, 0.26)
    near = separation(1.0, 216, 0.26)
    assert far == 108
    assert near < far


def test_configuracao_aprovada_e_o_padrao():
    config = RenderConfigV2()
    assert config.oversample == 3
    assert config.mosaic_cell == 2
    assert config.occlusion == "visibility"
    assert config.texture == "mosaic"
    assert config.far_separation == 108


def test_render_experimental_e_deterministico():
    depth = Image.new("L", (180, 120), 0)
    config = RenderConfigV2(width=180, height=120, eye_separation=80, oversample=2)
    first = render_stereogram_v2(depth, config)
    second = render_stereogram_v2(depth, config)
    assert first.size == (180, 120)
    assert np.array_equal(np.asarray(first), np.asarray(second))


def test_render_concorrente_preserva_pixels():
    depth = Image.new("L", (180, 120), 127)
    config = RenderConfigV2(width=180, height=120, eye_separation=80, oversample=2)
    with ThreadPoolExecutor(max_workers=4) as executor:
        outputs = list(
            executor.map(
                lambda image: np.asarray(render_stereogram_v2(image, config)),
                [depth.copy() for _ in range(4)],
            )
        )
    assert all(np.array_equal(outputs[0], output) for output in outputs[1:])


@pytest.mark.parametrize("occlusion", ["conflicts", "visibility"])
def test_modos_de_oclusao_geram_imagem(occlusion):
    depth = Image.new("L", (180, 120), 0)
    config = RenderConfigV2(
        width=180,
        height=120,
        eye_separation=80,
        oversample=1,
        occlusion=occlusion,
    )
    assert render_stereogram_v2(depth, config).size == (180, 120)


@pytest.mark.parametrize("texture", ["organic", "color", "mono", "mosaic"])
def test_texturas_publicas_funcionam_no_v2(texture):
    depth = Image.new("L", (180, 120), 0)
    config = RenderConfigV2(
        width=180,
        height=120,
        eye_separation=80,
        oversample=1,
        texture=texture,
    )
    output = np.asarray(render_stereogram_v2(depth, config))
    assert len(np.unique(output.reshape(-1, 3), axis=0)) >= 2


def test_plano_distante_repete_na_separacao_dos_guias():
    depth = Image.new("L", (240, 120), 0)
    config = RenderConfigV2(
        width=240,
        height=120,
        eye_separation=80,
        oversample=1,
        depth_blur=0,
    )
    output = np.asarray(render_stereogram_v2(depth, config))
    separation_px = config.far_separation
    assert np.array_equal(output[:, 140], output[:, 140 + separation_px])


def test_visibilidade_remove_fundo_encoberto():
    depth = np.zeros((1, 120), dtype=np.float32)
    depth[:, 50:70] = 1.0
    visible = _visibility_mask(depth, eye_separation=80, mu=0.3)
    assert not visible.all()
    assert visible[0, 60]


def test_configuracao_recusa_profundidade_desconfortavel():
    depth = Image.new("L", (180, 120), 0)
    with pytest.raises(ValueError):
        render_stereogram_v2(depth, RenderConfigV2(width=180, height=120, depth=0.8))
