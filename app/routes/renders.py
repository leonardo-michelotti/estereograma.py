"""Entrega segura dos PNGs temporários gerados pelo Estúdio."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.generation_service import GenerationService


def create_renders_router(generation_service: GenerationService) -> APIRouter:
    router = APIRouter()

    @router.get("/renders/{render_id}.png", response_class=FileResponse)
    def render(render_id: str) -> FileResponse:
        path = generation_service.render_path(render_id)
        if path is None:
            raise HTTPException(status_code=404, detail="Este render expirou ou não existe.")
        return FileResponse(
            path,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=1800, immutable"},
        )

    return router
