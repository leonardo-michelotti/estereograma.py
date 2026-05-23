"""FastAPI app — estereograma.py portfolio."""

from __future__ import annotations

import base64
import io
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from app.content_loader import artigo_por_slug, carregar_artigos, vizinhos
from app.stereogram.generator import gerar_estereograma
from app.stereogram.presets import PRESETS, caminho_arquivo, preset_por_slug

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content"

app = FastAPI(title="estereograma.py", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

ARTIGOS = carregar_artigos(CONTENT_DIR / "aprender")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/aprender", response_class=HTMLResponse)
async def aprender_indice(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "aprender_indice.html",
        {"artigos": ARTIGOS},
    )


@app.get("/aprender/{slug}", response_class=HTMLResponse)
async def aprender_artigo(request: Request, slug: str) -> HTMLResponse:
    artigo = artigo_por_slug(ARTIGOS, slug)
    if artigo is None:
        raise HTTPException(status_code=404, detail=f"Artigo não encontrado: {slug}")
    anterior, proximo = vizinhos(ARTIGOS, slug)
    return templates.TemplateResponse(
        request,
        "artigo.html",
        {
            "artigo": artigo,
            "artigos": ARTIGOS,
            "anterior": anterior,
            "proximo": proximo,
        },
    )


@app.get("/galeria", response_class=HTMLResponse)
async def galeria(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "galeria.html", {"obras": []})


@app.get("/playground", response_class=HTMLResponse)
async def playground(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "playground.html",
        {"presets": PRESETS},
    )


@app.post("/playground/gerar", response_class=HTMLResponse)
async def playground_gerar(
    request: Request,
    preset: str = Form(...),
    textura: str = Form("pink_noise"),
    seed: int | None = Form(None),
    mu: float = Form(0.333),
    eye_separation: int = Form(200),
) -> HTMLResponse:
    p = preset_por_slug(preset)
    if p is None:
        raise HTTPException(status_code=400, detail=f"Preset desconhecido: {preset}")

    depth = Image.open(caminho_arquivo(p, STATIC_DIR))
    resultado = gerar_estereograma(
        depth_map=depth,
        largura=800,
        altura=600,
        eye_separation=eye_separation,
        mu=mu,
        textura=textura,  # type: ignore[arg-type]
        seed=seed,
    )

    buffer = io.BytesIO()
    resultado.save(buffer, format="PNG", optimize=True)
    b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    data_url = f"data:image/png;base64,{b64}"

    return templates.TemplateResponse(
        request,
        "partials/resultado.html",
        {"imagem": data_url, "preset": p, "dica": p.dica},
    )
