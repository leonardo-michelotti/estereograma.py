# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento: [SemVer](https://semver.org/).

## [não publicado]

### Workstream A — Gerador
- _Em desenvolvimento_

### Workstream B — Conteúdo & Site
- Skeletons dos artigos restantes (história, visão binocular, teoria, cálculo, algoritmo)
- Galeria curada com obras CC/domínio público
- Página `/aprender/{slug}` com TOC lateral

### Infra
- Dockerfile + `fly.toml` (Fly.io)
- GitHub Actions CI

## [0.1.0] — 2026-05-23

### Adicionado

#### Gerador (`app/stereogram/`)
- Implementação do algoritmo de **classes de equivalência** (Thimbleby,
  Inglis & Witten 1994) — substitui o método ingênuo de look-back, sem
  pattern ringing.
- Fórmula de separação estereoscópica baseada em geometria do olhar:
  `sep(z) = round((1-μ·z)·E/(2-μ·z))`.
- Cinco texturas: `pink_noise` (default, FFT 1/f), `random_dots`,
  `random_dots_bw`, `colorido`, `custom`.
- Geradores sintéticos de depth maps (`patterns.py`): esfera com correção
  gamma, coração via equação implícita, texto em relevo.
- CLI standalone: `python -m app.stereogram <depth> <saida>` com tunáveis
  `--eye-separation`, `--mu`, `--textura`, `--seed`.
- 8 testes de unidade.

#### Site (FastAPI + Jinja + HTMX)
- Landing `/` com lead e instruções de visualização.
- Playground `/playground` com 3 presets, sliders pra μ e
  eye_separation, troca via HTMX sem reload, botão de download.
- Hub educativo `/aprender` com índice de 6 artigos.
- Artigo completo: **O que são estereogramas** (~1000 palavras, com
  fontes).
- Skeletons de 5 artigos restantes.
- Página `/galeria` (placeholder até curadoria).

#### Infra de conteúdo
- Loader de Markdown com frontmatter YAML em `app/content_loader.py`.
- Extensões habilitadas: fenced_code, tables, toc, footnotes, smarty.
- Estrutura `app/content/aprender/*.md` com campos `titulo`, `ordem`,
  `resumo`, `fontes`.

#### Documentação
- `ARCHITECTURE.md` — 11 seções cobrindo visão, stack, gerador,
  algoritmo, web, testes, deploy, roadmap, riscos.
- `README.md` público.
