import numpy as np
import pytest
from PIL import Image

from app.stereogram.generator import gerar_estereograma
from app.stereogram.patterns import esfera


def test_dimensoes_saida():
    depth = esfera(400, 300)
    saida = gerar_estereograma(depth, largura=400, altura=300, seed=42)
    assert saida.size == (400, 300)
    assert saida.mode == "RGB"


def test_determinismo_com_seed():
    depth = esfera(200, 150)
    a = gerar_estereograma(depth, largura=200, altura=150, seed=7)
    b = gerar_estereograma(depth, largura=200, altura=150, seed=7)
    assert np.array_equal(np.array(a), np.array(b))


def test_seeds_diferentes_produzem_imagens_diferentes():
    depth = esfera(200, 150)
    a = gerar_estereograma(depth, largura=200, altura=150, seed=1)
    b = gerar_estereograma(depth, largura=200, altura=150, seed=2)
    assert not np.array_equal(np.array(a), np.array(b))


def test_repeticao_em_regiao_plana_perto():
    """Em região totalmente 'perto' (z=1), separação = E·(1-mu)/(2-mu).
    Dois pixels separados por essa distância devem ter a mesma cor.
    """
    depth = Image.new("L", (400, 100), 255)
    E, mu = 180, 0.333
    saida = np.array(
        gerar_estereograma(depth, largura=400, altura=100, eye_separation=E, mu=mu, seed=42)
    )
    sep = round((1 - mu) * E / (2 - mu))
    assert np.array_equal(saida[:, 150], saida[:, 150 + sep])


def test_eye_separation_invalido():
    depth = esfera(100, 100)
    with pytest.raises(ValueError):
        gerar_estereograma(depth, eye_separation=10)


def test_mu_invalido():
    depth = esfera(100, 100)
    with pytest.raises(ValueError):
        gerar_estereograma(depth, mu=0.0)
    with pytest.raises(ValueError):
        gerar_estereograma(depth, mu=1.5)


def test_textura_custom_exige_imagem():
    depth = esfera(100, 100)
    with pytest.raises(ValueError):
        gerar_estereograma(depth, textura="custom", textura_custom=None)


def test_pink_noise_e_default():
    depth = esfera(100, 100)
    # Garante que o default pink_noise funciona sem erro
    saida = gerar_estereograma(depth, largura=100, altura=100, seed=42)
    assert saida.size == (100, 100)


def test_textura_laboratorio_e_deterministica():
    depth = esfera(160, 120)
    a = gerar_estereograma(depth, 160, 120, textura="laboratorio", seed=24)
    b = gerar_estereograma(depth, 160, 120, textura="laboratorio", seed=24)
    assert np.array_equal(np.array(a), np.array(b))
    assert len(np.unique(np.array(a).reshape(-1, 3), axis=0)) >= 4
