"""Configuração pequena e explícita para URLs públicas."""

from __future__ import annotations

import os

from fastapi import Request

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")


def absolute_url(request: Request, path: str) -> str:
    """Monta URLs absolutas para metadados, sitemap e compartilhamento."""

    base = PUBLIC_BASE_URL or str(request.base_url).rstrip("/")
    return f"{base}/{path.lstrip('/')}"


def canonical_url(request: Request) -> str:
    return absolute_url(request, request.url.path)
