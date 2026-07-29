# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True

"""Núcleo sequencial compilado da Engine V2.

O contrato público permanece em ``generator_v2.py``. Este módulo recebe apenas
matrizes já validadas e preparadas, preservando no Python a fórmula, a textura,
o redimensionamento e a política de fallback.
"""

import numpy as np
cimport numpy as cnp
from libc.math cimport ceil


ctypedef cnp.float32_t float32_t
ctypedef cnp.int32_t int32_t
ctypedef cnp.uint8_t uint8_t


def visibility_mask(
    cnp.ndarray[float32_t, ndim=2, mode="c"] depth,
    int eye_separation,
    double mu,
):
    """Calcula a máscara de visibilidade com aritmética float32 explícita."""
    cdef Py_ssize_t height = depth.shape[0]
    cdef Py_ssize_t width = depth.shape[1]
    cdef Py_ssize_t x, y, offset
    cdef Py_ssize_t max_offset = max(
        1, <Py_ssize_t>ceil(mu * eye_separation / (2.0 * (2.0 - mu)))
    )
    cdef float mu32 = <float>mu
    cdef float center, ray_depth
    cdef cnp.ndarray[uint8_t, ndim=2] visible = np.ones(
        (height, width), dtype=np.uint8
    )

    if max_offset + 1 > width // 2:
        max_offset = width // 2 - 1

    with nogil:
        for offset in range(1, max_offset + 1):
            for y in range(height):
                for x in range(offset, width - offset):
                    center = depth[y, x]
                    ray_depth = center + (
                        2.0 * (2.0 - mu32 * center) * offset
                    ) / (mu32 * eye_separation)
                    if ray_depth < 1.0 and not (
                        depth[y, x - offset] < ray_depth
                        and depth[y, x + offset] < ray_depth
                    ):
                        visible[y, x] = 0

    return visible


def render_rows(
    cnp.ndarray[int32_t, ndim=2, mode="c"] left_map,
    cnp.ndarray[int32_t, ndim=2, mode="c"] right_map,
    cnp.ndarray[uint8_t, ndim=2, mode="c"] active_map,
    cnp.ndarray[uint8_t, ndim=3, mode="c"] texture,
    int virtual_period,
):
    """Resolve vínculos e pinta linhas com a mesma semântica da V2 Python."""
    cdef Py_ssize_t height = left_map.shape[0]
    cdef Py_ssize_t width = left_map.shape[1]
    cdef Py_ssize_t center = width // 2
    cdef Py_ssize_t x, y
    cdef int left, right, old_left, old_right, source, color

    cdef cnp.ndarray[int32_t, ndim=1] look_left = np.empty(width, dtype=np.int32)
    cdef cnp.ndarray[int32_t, ndim=1] look_right = np.empty(width, dtype=np.int32)
    cdef cnp.ndarray[int32_t, ndim=1] colors = np.empty(width, dtype=np.int32)
    cdef cnp.ndarray[uint8_t, ndim=3] output = np.empty(
        (height, width, 3), dtype=np.uint8
    )

    with nogil:
        for y in range(height):
            for x in range(width):
                look_left[x] = x
                look_right[x] = x
                colors[x] = x % virtual_period

            for x in range(width):
                if active_map[y, x] == 0:
                    continue

                left = left_map[y, x]
                right = right_map[y, x]
                old_left = look_left[right]
                old_right = look_right[left]

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

            for x in range(center, width):
                source = look_left[x]
                if source != x and source >= center:
                    colors[x] = colors[source]

            for x in range(center - 1, -1, -1):
                source = look_right[x]
                if source != x:
                    colors[x] = colors[source]

            for x in range(width):
                color = colors[x]
                output[y, x, 0] = texture[y, color, 0]
                output[y, x, 1] = texture[y, color, 1]
                output[y, x, 2] = texture[y, color, 2]

    return output
