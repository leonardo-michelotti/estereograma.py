"""Carrega artigos em Markdown com frontmatter YAML do diretório app/content/.

Cada arquivo tem o formato:

    ---
    titulo: O que são estereogramas
    ordem: 1
    resumo: Explicação introdutória...
    ---

    # Conteúdo Markdown aqui

A coleção é carregada uma vez na inicialização. Para recarregar em
desenvolvimento, basta reiniciar o servidor (uvicorn --reload faz isso).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from markdown import Markdown

# Palavras por minuto pra leitura técnica em português (média conservadora).
WPM_LEITURA = 220

# Marcadores que indicam que o artigo é um esboço/skeleton.
_PADROES_ESBOCO = (
    re.compile(r"<blockquote>.*?\bskeleton\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"<blockquote>.*?\ba\s+redigir\b", re.IGNORECASE | re.DOTALL),
)


@dataclass(frozen=True)
class Artigo:
    slug: str
    titulo: str
    ordem: int
    resumo: str
    html: str
    fontes: tuple[str, ...] = ()
    glifo: str = "◉"
    tempo_leitura: int = 1
    status: str = "pronto"  # "pronto" | "esboco"
    toc_html: str = ""
    metadata: dict[str, Any] | None = None

    @property
    def esboco(self) -> bool:
        return self.status == "esboco"


def _parse_frontmatter(texto: str) -> tuple[dict[str, Any], str]:
    """Divide um arquivo `---\\nyaml\\n---\\nconteudo` em (meta, corpo)."""
    if not texto.startswith("---\n"):
        return {}, texto
    fim = texto.find("\n---\n", 4)
    if fim == -1:
        return {}, texto
    yaml_bloco = texto[4:fim]
    corpo = texto[fim + 5 :]
    meta = yaml.safe_load(yaml_bloco) or {}
    return meta, corpo


def _render_md(corpo: str) -> tuple[str, str]:
    """Renderiza o markdown e devolve (html, toc_html)."""
    instancia = Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "attr_list",
            "footnotes",
            "sane_lists",
            "smarty",
        ],
        extension_configs={
            "toc": {"permalink": False, "toc_depth": "2-3"},
            "footnotes": {"BACKLINK_TEXT": "↩"},
        },
    )
    html = instancia.convert(corpo)
    return html, instancia.toc


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _contar_palavras(html: str) -> int:
    """Conta palavras no texto extraído do HTML."""
    texto = _TAG_RE.sub(" ", html)
    texto = _WS_RE.sub(" ", texto).strip()
    return len(texto.split()) if texto else 0


def _detectar_status(html: str, meta: dict[str, Any]) -> str:
    """Frontmatter `status:` ganha de detecção automática."""
    declarado = meta.get("status")
    if declarado:
        return str(declarado)
    for padrao in _PADROES_ESBOCO:
        if padrao.search(html):
            return "esboco"
    return "pronto"


def carregar_artigos(base_dir: Path) -> list[Artigo]:
    """Carrega todos os .md de base_dir, ordenados pelo campo `ordem`."""
    artigos: list[Artigo] = []
    for arquivo in sorted(base_dir.glob("*.md")):
        bruto = arquivo.read_text(encoding="utf-8")
        meta, corpo = _parse_frontmatter(bruto)
        html, toc_html = _render_md(corpo)
        palavras = _contar_palavras(html)
        tempo = max(1, round(palavras / WPM_LEITURA))
        artigos.append(
            Artigo(
                slug=arquivo.stem,
                titulo=str(meta.get("titulo", arquivo.stem)),
                ordem=int(meta.get("ordem", 999)),
                resumo=str(meta.get("resumo", "")),
                html=html,
                fontes=tuple(meta.get("fontes", []) or []),
                glifo=str(meta.get("glifo", "◉")),
                tempo_leitura=tempo,
                status=_detectar_status(html, meta),
                toc_html=toc_html,
                metadata=meta,
            )
        )
    artigos.sort(key=lambda a: (a.ordem, a.slug))
    return artigos


def artigo_por_slug(artigos: list[Artigo], slug: str) -> Artigo | None:
    return next((a for a in artigos if a.slug == slug), None)


def vizinhos(artigos: list[Artigo], slug: str) -> tuple[Artigo | None, Artigo | None]:
    """Retorna (anterior, proximo) para navegação prev/next."""
    indices = {a.slug: i for i, a in enumerate(artigos)}
    if slug not in indices:
        return None, None
    i = indices[slug]
    anterior = artigos[i - 1] if i > 0 else None
    proximo = artigos[i + 1] if i + 1 < len(artigos) else None
    return anterior, proximo
