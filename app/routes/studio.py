"""Rotas do Estúdio e compatibilidade com o playground antigo."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models.generation import GenerationParams
from app.services.generation_service import GenerationService
from app.stereogram.presets import PRESETS


def create_studio_router(
    templates: Jinja2Templates,
    generation_service: GenerationService,
) -> APIRouter:
    router = APIRouter()

    @router.get("/studio", response_class=HTMLResponse)
    def studio(
        request: Request,
        subject_type: str = "preset",
        subject: str = "esfera",
        texture: str = "mosaic",
        depth: str = "comfortable",
        seed: int | None = None,
        eye_separation: int = 200,
    ) -> HTMLResponse:
        presets = [preset for preset in PRESETS if preset.slug in {"esfera", "coracao"}]
        try:
            initial = GenerationParams(
                subject_type=subject_type,
                subject=subject,
                texture=texture,
                depth=depth,
                seed=seed,
                eye_separation=eye_separation,
            )
        except ValidationError:
            initial = GenerationParams()
        return templates.TemplateResponse(
            request,
            "studio.html",
            {
                "presets": presets,
                "initial": initial,
                "restored": bool(request.query_params),
            },
        )

    @router.get("/playground", include_in_schema=False)
    def old_playground() -> RedirectResponse:
        return RedirectResponse("/studio", status_code=308)

    @router.post("/studio/preview", response_class=HTMLResponse)
    def studio_preview(
        request: Request,
        subject_type: str = Form("preset"),
        subject: str = Form("esfera"),
        text_subject: str = Form(""),
        texture: str = Form("mosaic"),
        depth: str = Form("comfortable"),
        seed: int | None = Form(None),
        mu: float | None = Form(None),
        eye_separation: int = Form(200),
    ) -> HTMLResponse:
        selected_subject = text_subject if subject_type == "text" else subject
        try:
            params = GenerationParams(
                subject_type=subject_type,
                subject=selected_subject,
                texture=texture,
                depth=depth,
                seed=seed,
                mu=mu,
                eye_separation=eye_separation,
            )
            result = generation_service.generate(params)
        except (ValidationError, ValueError) as error:
            return templates.TemplateResponse(
                request,
                "partials/studio_error.html",
                {"message": _error_message(error)},
                status_code=400,
            )

        return templates.TemplateResponse(
            request,
            "partials/studio_result.html",
            {"result": result},
        )

    return router


def _error_message(error: ValidationError | ValueError) -> str:
    if isinstance(error, ValidationError):
        first = error.errors()[0]
        return str(first.get("ctx", {}).get("error") or first["msg"])
    return str(error)
