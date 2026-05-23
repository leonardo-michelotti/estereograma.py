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

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import markdown as md
import yaml


@dataclass(frozen=True)
class Artigo:
    slug: str
    titulo: str
    ordem: int
    resumo: str
    html: str
    fontes: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None


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


def _render_md(corpo: str) -> str:
    return md.markdown(
        corpo,
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
            "toc": {"permalink": False, "toc_depth": "2-4"},
        },
    )


def carregar_artigos(base_dir: Path) -> list[Artigo]:
    """Carrega todos os .md de base_dir, ordenados pelo campo `ordem`."""
    artigos: list[Artigo] = []
    for arquivo in sorted(base_dir.glob("*.md")):
        bruto = arquivo.read_text(encoding="utf-8")
        meta, corpo = _parse_frontmatter(bruto)
        artigos.append(
            Artigo(
                slug=arquivo.stem,
                titulo=str(meta.get("titulo", arquivo.stem)),
                ordem=int(meta.get("ordem", 999)),
                resumo=str(meta.get("resumo", "")),
                html=_render_md(corpo),
                fontes=tuple(meta.get("fontes", []) or []),
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
