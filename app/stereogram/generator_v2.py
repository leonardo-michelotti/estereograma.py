"""Motor V2 de autostereogramas usado pela aplicação e pela API Python.

O contrato público permanece neste módulo. Um núcleo Cython interno acelera os
loops sequenciais quando foi compilado; a implementação Python pixel-idêntica é
mantida como fallback para ambientes sem toolchain C.

A implementação parte da descrição matemática de Thimbleby, Inglis & Witten:
separação binocular simétrica, remoção de pontos ocultos e restrições de
igualdade entre pixels. O código abaixo é uma implementação independente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image, ImageFilter

OcclusionMode = Literal["conflicts", "visibility"]
TextureModeV2 = Literal["organic", "color", "mono", "mosaic"]
ENGINE_VERSION_V2 = "v2.0"
_FORCE_PYTHON = os.environ.get("ESTEREOGRAMA_V2_FORCE_PYTHON") == "1"
_render_rows_compiled = None
_visibility_mask_compiled = None
if not _FORCE_PYTHON:
    try:
        from app.stereogram._core_v2 import render_rows as _render_rows_compiled
        from app.stereogram._core_v2 import visibility_mask as _visibility_mask_compiled
    except ImportError:
        pass

ENGINE_IMPLEMENTATION_V2 = (
    "cython"
    if _render_rows_compiled is not None and _visibility_mask_compiled is not None
    else "python"
)

LAB_PALETTE = np.array(
    [
        [233, 214, 85],  # amarelo
        [32, 34, 28],  # quase preto
        [49, 92, 255],  # azul laboratório
        [255, 90, 69],  # coral
        [247, 242, 232],  # papel
    ],
    dtype=np.uint8,
)

LAB_WEIGHTS = np.array([0.48, 0.19, 0.14, 0.12, 0.07])


@dataclass(frozen=True)
class RenderConfigV2:
    width: int = 900
    height: int = 560
    eye_separation: int = 216
    depth: float = 0.26
    oversample: int = 3
    mosaic_cell: int = 2
    depth_blur: float = 0.65
    occlusion: OcclusionMode = "visibility"
    texture: TextureModeV2 = "mosaic"
    seed: int = 24

    @property
    def far_separation(self) -> int:
        """Distância dos pontos-guia e repetição do plano mais distante."""
        return round(self.eye_separation / 2)

    @property
    def near_separation(self) -> int:
        return separation(1.0, self.eye_separation, self.depth)


def separation(z: float, eye_separation: int, depth: float) -> int:
    """Converte profundidade normalizada em separação binocular simétrica."""
    return round((1.0 - depth * z) * eye_separation / (2.0 - depth * z))


def _separation_map(depth: np.ndarray, eye_separation: int, mu: float) -> np.ndarray:
    """Calcula todas as separações preservando a aritmética escalar da V2.

    O mapa de profundidade é float32. A implementação original convertia cada
    amostra para ``float`` antes da fórmula; por isso promovemos explicitamente
    para float64 e usamos o mesmo arredondamento para o inteiro par mais próximo.
    """
    depth64 = depth.astype(np.float64, copy=False)
    numerator = (1.0 - mu * depth64) * eye_separation
    denominator = 2.0 - mu * depth64
    return np.rint(numerator / denominator).astype(np.int32)


def _constraint_maps(
    separations: np.ndarray,
    visibility: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Prepara limites e validade dos vínculos fora do loop Python."""
    width = separations.shape[1]
    centers = np.arange(width, dtype=np.int32)[None, :]
    left = centers - separations // 2
    right = left + separations
    active = (left >= 0) & (right < width)
    if visibility is not None:
        active &= visibility
    return left, right, active


def _validate(config: RenderConfigV2) -> None:
    if config.width < 160 or config.height < 100:
        raise ValueError("A saída precisa ter pelo menos 160 × 100 px.")
    if config.eye_separation < 40 or config.eye_separation >= config.width:
        raise ValueError("eye_separation deve estar entre 40 e a largura da saída.")
    if not 0.0 < config.depth < 0.6:
        raise ValueError("depth deve estar entre 0 e 0.6 para uma fusão confortável.")
    if not 1 <= config.oversample <= 8:
        raise ValueError("oversample deve estar entre 1 e 8.")
    if not 1 <= config.mosaic_cell <= 8:
        raise ValueError("mosaic_cell deve estar entre 1 e 8.")
    if config.texture not in {"organic", "color", "mono", "mosaic"}:
        raise ValueError(f"Textura V2 desconhecida: {config.texture}")


def _prepare_depth(depth_map: Image.Image, config: RenderConfigV2) -> np.ndarray:
    depth = depth_map.convert("L").resize(
        (config.width, config.height),
        Image.Resampling.BICUBIC,
    )
    if config.depth_blur:
        depth = depth.filter(ImageFilter.GaussianBlur(config.depth_blur))

    virtual_width = config.width * config.oversample
    depth = depth.resize((virtual_width, config.height), Image.Resampling.BICUBIC)
    return np.asarray(depth, dtype=np.float32) / 255.0


def _visibility_mask_python(depth: np.ndarray, eye_separation: int, mu: float) -> np.ndarray:
    """Marca pontos visíveis simultaneamente pelos dois olhos.

    A verificação é feita na resolução de saída e depois ampliada pelo chamador.
    Para cada deslocamento horizontal, comparamos a superfície real com a altura
    do raio que ligaria o ponto aos olhos. Uma superfície mais próxima interrompe
    o vínculo e evita o eco nas bordas do objeto.
    """
    height, width = depth.shape
    visible = np.ones((height, width), dtype=bool)
    max_offset = max(1, int(np.ceil(mu * eye_separation / (2 * (2 - mu)))))

    for offset in range(1, min(max_offset + 1, width // 2)):
        center = depth[:, offset : width - offset]
        ray_depth = center + (2 * (2 - mu * center) * offset) / (mu * eye_separation)
        active = ray_depth < 1.0
        clear_left = depth[:, : width - 2 * offset] < ray_depth
        clear_right = depth[:, 2 * offset :] < ray_depth
        visible[:, offset : width - offset] &= ~active | (clear_left & clear_right)

    return visible


def _visibility_mask(depth: np.ndarray, eye_separation: int, mu: float) -> np.ndarray:
    """Usa o núcleo compilado quando disponível, com fallback pixel-idêntico."""
    if _visibility_mask_compiled is None:
        return _visibility_mask_python(depth, eye_separation, mu)
    return _visibility_mask_compiled(
        np.ascontiguousarray(depth, dtype=np.float32), eye_separation, mu
    ).astype(bool, copy=False)


def _texture_tile(config: RenderConfigV2, virtual_period: int) -> np.ndarray:
    rng = np.random.default_rng(config.seed)
    if config.texture == "mono":
        palette = LAB_PALETTE[[1, 4]]
        weights = np.array([0.52, 0.48])
        cell = 1
    elif config.texture == "organic":
        palette = LAB_PALETTE[[0, 1, 4]]
        weights = np.array([0.58, 0.30, 0.12])
        cell = config.mosaic_cell
    elif config.texture == "color":
        palette = LAB_PALETTE
        weights = np.array([0.28, 0.14, 0.23, 0.23, 0.12])
        cell = max(1, config.mosaic_cell - 1)
    else:
        palette = LAB_PALETTE
        weights = LAB_WEIGHTS
        cell = config.mosaic_cell

    cell_x = cell * config.oversample
    cell_y = cell
    grid_width = (virtual_period + cell_x - 1) // cell_x
    grid_height = (config.height + cell_y - 1) // cell_y
    indices = rng.choice(
        len(palette),
        size=(grid_height, grid_width),
        p=weights,
    )
    grid = palette[indices]
    tile = np.repeat(np.repeat(grid, cell_y, axis=0), cell_x, axis=1)
    return tile[: config.height, :virtual_period]


def _build_links(
    left_row: list[int],
    right_row: list[int],
    active_row: list[bool],
    base_indices: tuple[int, ...],
) -> tuple[list[int], list[int]]:
    """Cria vínculos bidirecionais, mantendo a restrição mais próxima."""
    look_left = list(base_indices)
    look_right = list(base_indices)

    for left, right, active in zip(left_row, right_row, active_row, strict=True):
        if not active:
            continue

        old_left = look_left[right]
        old_right = look_right[left]

        # Um vínculo menor representa uma superfície mais próxima. Só
        # substituímos restrições anteriores quando a atual está à frente.
        if old_left != right and old_left >= left:
            continue
        if old_right != left and old_right <= right:
            continue

        if old_left != right:
            look_right[old_left] = old_left
        if old_right != left:
            look_left[old_right] = old_right

        look_left[right] = left
        look_right[left] = right

    return look_left, look_right


def _paint_row(
    look_left: list[int],
    look_right: list[int],
    texture_row: np.ndarray,
    base_colors: tuple[int, ...],
) -> np.ndarray:
    """Pinta do centro para fora para não favorecer um sentido de leitura."""
    width = len(look_left)
    colors = list(base_colors)
    center = width // 2

    for x in range(center, width):
        source = look_left[x]
        if source != x and source >= center:
            colors[x] = colors[source]

    for x in range(center - 1, -1, -1):
        source = look_right[x]
        if source != x:
            colors[x] = colors[source]

    return texture_row[np.asarray(colors, dtype=np.int32)]


def _render_rows_python(
    left_map: np.ndarray,
    right_map: np.ndarray,
    active_map: np.ndarray,
    texture: np.ndarray,
    virtual_period: int,
) -> np.ndarray:
    height, virtual_width = left_map.shape
    base_indices = tuple(range(virtual_width))
    base_colors = tuple(index % virtual_period for index in base_indices)
    virtual = np.empty((height, virtual_width, 3), dtype=np.uint8)
    for y in range(height):
        links = _build_links(
            left_map[y].tolist(),
            right_map[y].tolist(),
            active_map[y].tolist(),
            base_indices,
        )
        virtual[y] = _paint_row(*links, texture[y], base_colors)
    return virtual


def _render_rows(
    left_map: np.ndarray,
    right_map: np.ndarray,
    active_map: np.ndarray,
    texture: np.ndarray,
    virtual_period: int,
) -> np.ndarray:
    if _render_rows_compiled is None:
        return _render_rows_python(
            left_map, right_map, active_map, texture, virtual_period
        )
    return _render_rows_compiled(
        np.ascontiguousarray(left_map, dtype=np.int32),
        np.ascontiguousarray(right_map, dtype=np.int32),
        np.ascontiguousarray(active_map, dtype=np.uint8),
        np.ascontiguousarray(texture, dtype=np.uint8),
        virtual_period,
    )


def render_stereogram_v2(depth_map: Image.Image, config: RenderConfigV2) -> Image.Image:
    """Renderiza um autostereograma V2 sem depender da aplicação web."""
    _validate(config)
    depth = _prepare_depth(depth_map, config)
    scale = config.oversample
    virtual_width = config.width * scale
    virtual_eye_separation = config.eye_separation * scale
    virtual_period = separation(0.0, virtual_eye_separation, config.depth)
    texture = _texture_tile(config, virtual_period)
    separations = _separation_map(depth, virtual_eye_separation, config.depth)
    if config.occlusion == "visibility":
        output_depth = depth[:, ::scale][:, : config.width]
        visibility = _visibility_mask(output_depth, config.eye_separation, config.depth)
        visibility = np.repeat(visibility, scale, axis=1)[:, :virtual_width]
    else:
        visibility = None

    left_map, right_map, active_map = _constraint_maps(separations, visibility)
    virtual = _render_rows(left_map, right_map, active_map, texture, virtual_period)

    high_res = Image.fromarray(virtual, mode="RGB")
    return high_res.resize((config.width, config.height), Image.Resampling.LANCZOS)
