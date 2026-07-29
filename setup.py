"""Configuração mínima do núcleo Cython opcional da Engine V2."""

from __future__ import annotations

import os

from setuptools import Extension, setup


def extensions() -> list[Extension]:
    if os.environ.get("ESTEREOGRAMA_BUILD_CYTHON") != "1":
        return []

    import numpy as np
    from Cython.Build import cythonize

    modules = [
        Extension(
            "app.stereogram._core_v2",
            ["app/stereogram/_core_v2.pyx"],
            include_dirs=[np.get_include()],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        )
    ]
    return cythonize(
        modules,
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "cdivision": True,
        },
    )


setup(ext_modules=extensions())
