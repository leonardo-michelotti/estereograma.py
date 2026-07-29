"""Composição da aplicação FastAPI do estereograma.py."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import absolute_url, canonical_url
from app.routes.renders import create_renders_router
from app.routes.studio import create_studio_router
from app.services.generation_service import GenerationService
from app.stereogram.generator_v2 import ENGINE_IMPLEMENTATION_V2, ENGINE_VERSION_V2

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
app = FastAPI(title="estereograma.py", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals["absolute_url"] = absolute_url
templates.env.globals["canonical_url"] = canonical_url
generation_service = GenerationService(STATIC_DIR)
app.include_router(create_studio_router(templates, generation_service))
app.include_router(create_renders_router(generation_service))


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self'; font-src 'self'; style-src 'self'; "
        "script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "form-action 'self'; frame-ancestors 'none'"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/como-ver", response_class=HTMLResponse)
async def como_ver(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "como_ver.html", {})


@app.get("/como-funciona", response_class=HTMLResponse)
async def como_funciona(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "como_funciona.html", {})


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    return {
        "status": "ok",
        "engine_version": ENGINE_VERSION_V2,
        "engine_implementation": ENGINE_IMPLEMENTATION_V2,
    }


@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots(request: Request) -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {absolute_url(request, '/sitemap.xml')}\n"


@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap(request: Request) -> Response:
    urls = ("/", "/studio", "/como-ver", "/como-funciona")
    items = "".join(f"<url><loc>{absolute_url(request, path)}</loc></url>" for path in urls)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{items}</urlset>"
    )
    return Response(xml, media_type="application/xml")


@app.get("/aprender", include_in_schema=False)
async def aprender_indice() -> RedirectResponse:
    return RedirectResponse("/como-ver", status_code=308)


@app.get("/aprender/{slug}", include_in_schema=False)
async def aprender_artigo(slug: str) -> RedirectResponse:
    destinos = {
        "o-que-sao": "/como-ver",
        "historia": "/como-ver",
        "visao-binocular": "/como-ver",
        "teoria": "/como-funciona",
        "calculo": "/como-funciona",
        "algoritmo": "/como-funciona",
    }
    destino = destinos.get(slug)
    if destino is None:
        raise HTTPException(status_code=404, detail=f"Artigo não encontrado: {slug}")
    return RedirectResponse(destino, status_code=308)


@app.get("/galeria", include_in_schema=False)
async def galeria() -> RedirectResponse:
    return RedirectResponse("/#obra", status_code=308)
