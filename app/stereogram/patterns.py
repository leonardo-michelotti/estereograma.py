"""Geradores de depth maps sintéticos para presets e testes."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def esfera(
    largura: int = 800,
    altura: int = 600,
    raio: int | None = None,
    gamma: float = 0.65,
) -> Image.Image:
    """Esfera centralizada — gradiente radial com correção gamma.

    gamma < 1 acentua o centro (curvatura mais "redonda" percebida);
    gamma = 1 é o gradiente esférico matemático puro.
    """
    raio = raio or min(largura, altura) // 3
    cx, cy = largura // 2, altura // 2
    y, x = np.ogrid[:altura, :largura]
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    altura_z = np.sqrt(np.clip(raio**2 - dist**2, 0, None)) / raio
    altura_z = altura_z**gamma
    img = (altura_z * 255).astype(np.uint8)
    return Image.fromarray(img, mode="L")


def coracao(largura: int = 800, altura: int = 600) -> Image.Image:
    """Coração — equação paramétrica clássica."""
    y, x = np.ogrid[:altura, :largura]
    nx = (x - largura / 2) / (largura / 4)
    ny = (altura / 2 - y) / (altura / 4)
    eq = (nx**2 + ny**2 - 1) ** 3 - nx**2 * ny**3
    mask = eq <= 0
    img = np.zeros((altura, largura), dtype=np.uint8)
    img[mask] = 220
    return Image.fromarray(img, mode="L")


def coracao_em_camadas(largura: int = 800, altura: int = 600) -> Image.Image:
    """Coração grande com um segundo plano interno, pensado para o treino."""
    y, x = np.ogrid[:altura, :largura]

    def mascara(escala_x: float, escala_y: float, centro_y: float) -> np.ndarray:
        nx = (x - largura / 2) / (largura * escala_x)
        ny = (centro_y - y) / (altura * escala_y)
        return (nx**2 + ny**2 - 1) ** 3 - nx**2 * ny**3 <= 0

    externo = mascara(0.29, 0.34, altura * 0.48)
    interno = mascara(0.15, 0.18, altura * 0.49)
    img = np.zeros((altura, largura), dtype=np.uint8)
    img[externo] = 165
    img[interno] = 255
    return Image.fromarray(img, mode="L")


def texto(
    palavra: str,
    largura: int = 800,
    altura: int = 600,
    profundidade_fundo: int = 40,
) -> Image.Image:
    """Texto em relevo. Strokes finos somem no estereograma, então usamos
    fonte grande + bold + fill total (255) e damos um piso de profundidade
    pro fundo (não totalmente preto) — isso dá mais contraste percebido."""
    img = Image.new("L", (largura, altura), profundidade_fundo)
    draw = ImageDraw.Draw(img)
    # tenta fontes bold conhecidas (Windows/macOS/Linux), cai pra default
    candidatos = ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"]
    font = None
    for nome in candidatos:
        try:
            font = ImageFont.truetype(nome, size=int(altura * 0.55))
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), palavra, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # offset do bbox: textbbox pode começar em y > 0
    x = (largura - tw) // 2 - bbox[0]
    y = (altura - th) // 2 - bbox[1]
    draw.text((x, y), palavra, fill=255, font=font)
    return img
