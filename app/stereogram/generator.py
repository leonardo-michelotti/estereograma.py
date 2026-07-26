"""Gerador legacy de autostereogramas usado atualmente pelo site e pela CLI.

Referência: Thimbleby, Inglis & Witten (1994), "Displaying 3D Images:
Algorithms for Single Image Random Dot Stereograms", IEEE Computer 27(10).

Esta implementação aplica a separação simétrica e classes de equivalência, mas
não inclui a remoção completa de superfícies ocultas do artigo. Ela é preservada
sem mudanças de comportamento enquanto o motor V2 é validado e integrado.

Para cada linha:

1. Mantém-se um vetor `same[x]` (cada pixel começa em sua própria classe).
2. Varre-se a linha; em cada x calcula-se a separação estereoscópica
   `sep(z)` em função da profundidade, e une-se `same[left]` ↔ `same[right]`.
3. Colore-se a linha da direita pra esquerda: pixels que são raiz da classe
   recebem cor da textura base; o resto copia da sua raiz.

A fórmula de separação modela a geometria do olho:

    sep(z) = round((1 - μ·z) · E / (2 - μ·z))

onde E é a distância entre olhos em pixels e μ é o fator de depth-of-field
(quanto a profundidade afasta o objeto do plano da tela). Esse é o ponto
que faz o relevo parecer **volume real**, não só profundidade achatada.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from PIL import Image

TexturaTipo = Literal[
    "pink_noise",
    "random_dots",
    "random_dots_bw",
    "colorido",
    "laboratorio",
    "custom",
]


# -- texturas base --------------------------------------------------------- #


def _pink_noise_rgb(altura: int, largura: int, seed: int | None) -> np.ndarray:
    """Ruído 1/f bidimensional em três canais, oferecido como textura orgânica."""
    rng = np.random.default_rng(seed)
    canais = []
    fx = np.fft.fftfreq(largura)[None, :]
    fy = np.fft.fftfreq(altura)[:, None]
    f = np.sqrt(fx**2 + fy**2)
    f[0, 0] = 1.0  # evita div/0 no DC
    for _ in range(3):
        branco = rng.standard_normal((altura, largura))
        espectro = np.fft.fft2(branco) / np.sqrt(f)
        rosa = np.real(np.fft.ifft2(espectro))
        rosa = (rosa - rosa.min()) / (rosa.max() - rosa.min())
        canais.append(rosa)
    arr = np.stack(canais, axis=-1)
    # Aumenta o contraste pra ficar nítido sem virar ruído branco
    arr = np.clip((arr - 0.5) * 1.6 + 0.5, 0, 1)
    return (arr * 255).astype(np.uint8)


def _laboratorio_rgb(altura: int, largura: int, seed: int | None) -> np.ndarray:
    """Mosaico de alto contraste alinhado à identidade visual do projeto.

    Células de 4 px preservam detalhes suficientes para a fusão binocular,
    mas evitam o aspecto de estática RGB do ruído branco por pixel.
    """
    rng = np.random.default_rng(seed)
    palette = np.array(
        [
            [233, 214, 85],
            [32, 34, 28],
            [49, 92, 255],
            [255, 90, 69],
            [247, 242, 232],
        ],
        dtype=np.uint8,
    )
    cell = 4
    grid_height = (altura + cell - 1) // cell
    grid_width = (largura + cell - 1) // cell
    indices = rng.choice(
        len(palette),
        size=(grid_height, grid_width),
        p=[0.48, 0.19, 0.14, 0.12, 0.07],
    )
    mosaic = palette[indices]
    return np.repeat(np.repeat(mosaic, cell, axis=0), cell, axis=1)[:altura, :largura]


def _gerar_textura(
    tipo: TexturaTipo,
    largura: int,
    altura: int,
    textura_custom: Image.Image | None,
    seed: int | None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)

    if tipo == "pink_noise":
        return _pink_noise_rgb(altura, largura, seed)

    if tipo == "random_dots":
        return rng.integers(0, 256, size=(altura, largura, 3), dtype=np.uint8)

    if tipo == "random_dots_bw":
        mono = rng.integers(0, 2, size=(altura, largura), dtype=np.uint8) * 255
        return np.stack([mono, mono, mono], axis=-1)

    if tipo == "colorido":
        palette = np.array(
            [
                [231, 76, 60],
                [46, 204, 113],
                [52, 152, 219],
                [241, 196, 15],
                [155, 89, 182],
                [26, 188, 156],
            ],
            dtype=np.uint8,
        )
        idx = rng.integers(0, len(palette), size=(altura, largura))
        return palette[idx]

    if tipo == "laboratorio":
        return _laboratorio_rgb(altura, largura, seed)

    if tipo == "custom":
        if textura_custom is None:
            raise ValueError("textura='custom' exige textura_custom (PIL.Image).")
        tile = textura_custom.convert("RGB").resize((largura, altura), Image.Resampling.LANCZOS)
        return np.array(tile)

    raise ValueError(f"Tipo de textura desconhecido: {tipo}")


# -- algoritmo principal --------------------------------------------------- #


def gerar_estereograma(
    depth_map: Image.Image,
    largura: int = 800,
    altura: int = 600,
    eye_separation: int = 200,
    mu: float = 0.333,
    textura: TexturaTipo = "pink_noise",
    textura_custom: Image.Image | None = None,
    seed: int | None = None,
) -> Image.Image:
    """Gera um autostereograma a partir de um mapa de profundidade.

    Args:
        depth_map: imagem em escala de cinza. Branco = perto, preto = longe.
        largura, altura: dimensões da imagem de saída.
        eye_separation: distância entre olhos em pixels (E). 180–240 funciona
            bem em telas; valores mais altos pedem fusão mais larga (mais
            difícil em monitores pequenos).
        mu: fator de depth-of-field, 0..1. Tipicamente 1/3. Maior = mais
            profundidade percebida, mas pode dificultar a fusão.
        textura: pink_noise (default), laboratorio (mosaico mais legível),
            random_dots, random_dots_bw, colorido, ou custom.
        textura_custom: PIL.Image quando textura='custom'.
        seed: torna a geração determinística.
    """
    if eye_separation < 40:
        raise ValueError("eye_separation muito pequeno (mínimo 40).")
    if not 0.0 < mu < 1.0:
        raise ValueError("mu deve estar entre 0 e 1.")

    depth = depth_map.convert("L").resize((largura, altura))
    depth_arr = np.array(depth, dtype=np.float32) / 255.0  # 1=perto, 0=longe

    textura_arr = _gerar_textura(textura, largura, altura, textura_custom, seed)
    saida = np.zeros((altura, largura, 3), dtype=np.uint8)

    E = eye_separation

    for y in range(altura):
        same = np.arange(largura, dtype=np.int32)
        z_row = depth_arr[y]

        for x in range(largura):
            z = z_row[x]
            sep = int(round((1.0 - mu * z) * E / (2.0 - mu * z)))
            left = x - sep // 2
            right = left + sep
            if 0 <= left and right < largura:
                # union via cadeia de same[]
                cur = same[left]
                while cur != left and cur != right:
                    if cur < right:
                        left = cur
                        cur = same[left]
                    else:
                        same[left] = right
                        left = right
                        cur = same[left]
                same[left] = right

        # colore da direita pra esquerda: cada classe recebe uma cor da textura
        for x in range(largura - 1, -1, -1):
            if same[x] == x:
                saida[y, x] = textura_arr[y, x]
            else:
                saida[y, x] = saida[y, same[x]]

    return Image.fromarray(saida, mode="RGB")
