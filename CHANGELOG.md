# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento: [SemVer](https://semver.org/).

## [não publicado]

### Workstream A — Gerador
- _Em desenvolvimento_

### Workstream B — Conteúdo & Site
- Artigos 2–6 completos (história, visão binocular, teoria, cálculo, algoritmo)
- Galeria curada com obras CC/domínio público
- D2: redesign `/aprender` com trilha visual e indicadores de progresso
- D3: página de artigo — TOC lateral fixo, drop cap, sidenotes, navegação prev/next

### Infra
- Dockerfile + `fly.toml` (Fly.io)

---

## [0.2.0-dev] — 2026-05-24

> D1 — Redesign completo da home + fundação do hub educativo.

### Adicionado

#### Design system (`app/static/css/style.css`)
- Paleta dark-retro com tokens CSS: `--bg #1A0B2E`, `--purple #B388FF`, `--orange #FFA940`,
  `--fg #F5EFDC` — inspiração psicodélica roxa/laranja.
- Overlay de ruído SVG no `<body>` (5% opacidade, `mix-blend-mode: overlay`) — textura analógica.
- Tipografia tripla: **Syne** (display/headings), **Inter** (corpo), **JetBrains Mono** (código).
- Gradiente animado em `h1/h2`: roxo → laranja via `-webkit-background-clip: text`.
- Tokens de glow (`--glow-orange`, `--glow-purple`) reutilizados em botões, cards e imagens.
- Componentes: `.botao` (primário/terciário), `.porta` com hover glow e seta, reveal toggle CSS puro.

#### Home (`app/templates/index.html`) — redesign D1
- Seção `.hero`: grid 2 colunas — texto (kicker + h1 + lead + CTAs) + estereograma do coração
  com toggle "ver figura escondida" (checkbox puro, sem JS).
- Seção `.tutorial`: "nunca conseguiu ver?" com 4 passos numerados + mini-estereograma da
  esfera com seu próprio toggle de resposta.
- Seção `.portas`: 3 cards de navegação (01 Aprender · 02 Galeria · 03 Playground) com número
  tipográfico Syne, texto teaser e `→`.
- Seção `.sobre`: parágrafo curto sobre o projeto + link para o GitHub.

#### Imagens hero (`app/static/img/hero/`)
- `coracao_estereo.png` (800×600, ~195 KB) — estereograma do coração, `mu=0.45`, `seed=42`.
- `coracao_depth.png` — depth map do coração para o reveal.
- `mini_estereo.png` (400×300, ~116 KB) — estereograma da esfera para o tutorial, `mu=0.4`.
- `mini_depth.png` — depth map da esfera.
- Script gerador: `scripts/gerar_hero.py`.

#### Hub educativo
- `app/content_loader.py` — loader de Markdown com frontmatter YAML; retorna `list[Artigo]`
  ordenada por `ordem`; exposta globalmente via `templates.env.globals["artigos_global"]`.
- `app/content/aprender/o-que-sao.md` — artigo completo (~1 000 palavras): definição,
  3 famílias (par estéreo / RDS Julesz / SIRDS Tyler), anatomia do SIRDS, como ver,
  onde aparecem.
- Skeletons dos artigos 2–6 (`historia.md`, `visao-binocular.md`, `teoria.md`,
  `calculo.md`, `algoritmo.md`) — com YAML e seções comentadas.
- Rotas novas: `GET /aprender` (índice) e `GET /aprender/{slug}` (artigo com prev/next).
- Templates: `aprender_indice.html`, `artigo.html`.

#### Base template (`app/templates/base.html`)
- Rodapé 3 colunas: marca + tagline · links dos 6 artigos · links do projeto (GitHub, galeria,
  playground).
- Navbar com classe `.ativo` no link da rota atual.

#### Infra
- GitHub Actions CI (`.github/workflows/ci.yml`) — matrix Python 3.11 + 3.12,
  `ruff check` + `pytest` na cada push/PR para `main`.
- `CONTRIBUTING.md` — Conventional Commits (light), comandos de setup local.

### Corrigido
- Variável `l` renomeada para `cur` em `generator.py` para passar ruff E741.
- `test_repeticao_horizontal_em_regiao_plana` ajustado para testar `depth=255`
  (perto, shift=0) em vez de `depth=0` — alinhado com a fórmula `sep(z)`.

### Documentação
- `ARCHITECTURE.md` expandido com §§ de design system, conteúdo educativo, rotas atualizadas.

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
