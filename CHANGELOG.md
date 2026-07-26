# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versionamento: [SemVer](https://semver.org/).

## [não publicado]

### Workstream A — Gerador
- Motor V2 integrado localmente ao `GenerationService`, com separação simétrica,
  remoção de superfícies ocultas, resolução de conflitos e oversampling 3×.
- Paleta mosaico aprovada como padrão; texturas orgânica, colorida e mono foram
  preservadas no contrato público do Estúdio.
- Fingerprint do cache versionado por engine e separação real dos pontos-guia
  incluída no resultado da geração.
- Motor legacy preservado para a CLI e para comparação de regressões.
- Contrato `GenerationParams` valida conteúdo, textura, profundidade, seed e
  limites dos parâmetros avançados antes de chamar o núcleo matemático.
- `GenerationService` orquestra presets e texto personalizado sem acoplar o
  gerador puro à camada HTTP.
- Cache temporário de PNG com hash determinístico, TTL de 30 minutos e limite
  de 100 MB; resultados repetidos não são processados novamente.

### Workstream B — Conteúdo & Site
- Estereograma principal da Home substituído pelo coração V2 aprovado, com
  depth map em duas camadas e pontos-guia calibrados para 108 px.
- Nova página `/como-funciona` com pipeline visual, simulador de profundidade
  usando a fórmula real, explicação das variáveis e trecho do gerador Python.
- Novo percurso `/como-ver` com treino de visão paralela em três passos,
  imagem real, pontos de alinhamento, reveal, ajuda não bloqueante e conclusão
  encaminhando ao Estúdio.
- Home v0.3 implementada no sistema “laboratório óptico editorial”, com hero,
  estereograma real, reveal acessível, jornada em três passos, obras, explicação
  do algoritmo e bloco open source.
- Layout responsivo alinhado às referências de 1440, 390 e largura mínima de
  320 px.
- Novo Estúdio em `/studio`, com formas, texto de até 12 caracteres, quatro
  texturas, três níveis de profundidade, reveal e download.
- Estúdio migrado para o sistema visual v0.3: controles segmentados, tiles de
  forma e textura, preview dominante, avançado recolhido e layout mobile com o
  canvas antes dos controles.
- Nova variação preserva o resultado anterior durante o processamento; falhas
  usam o estado de erro aprovado sem apagar a imagem válida.
- “Copiar link” inclui conteúdo, textura, profundidade, seed e conforto visual;
  abrir o link restaura os controles para reprodução.
- Renders e depth maps entregues por `/renders/{id}.png`; imagens deixaram de
  ser embutidas em base64 nos fragmentos HTML.
- `/playground` redireciona para o novo Estúdio.
- Estado de erro amigável preserva o último resultado válido no navegador.
- Rotas antigas de artigos e galeria redirecionam para as experiências completas,
  sem publicar skeletons ou páginas placeholder.
- Metadados Open Graph/X, imagem social própria, canonical, `robots.txt` e
  `sitemap.xml` preparados para o lançamento.
- README refeito como vitrine do produto, alinhado ao laboratório óptico
  editorial e organizado por experiência, engine, evidências e reprodução.

### Infra
- Instrument Sans e IBM Plex Mono hospedadas localmente, com licenças OFL.
- HTMX 1.9.12 versionado e servido pela própria aplicação.
- Testes de contrato, cache, rota do Estúdio, compatibilidade e entrega de PNG.
- Cabeçalhos CSP, proteção contra framing e política restrita de permissões.
- Limite de duas gerações simultâneas por processo, com erro recuperável.
- Dockerfile não-root, `/healthz` e `railway.toml` para Railway.
- Workflows separados de staging e produção, ambos desabilitados até receberem
  tokens de projeto e autorização explícita.
- Primeiro staging publicado no Railway e validado de ponta a ponta, incluindo
  geração e entrega de PNG pelo domínio público temporário.
- Produção publicada após aprovação do staging e validada no domínio Railway,
  com healthcheck, páginas, geração, SEO e segurança respondendo corretamente.
- Licença MIT do código e aviso CC BY-SA 4.0 do conteúdo adicionados.

### Workstream C — Estudo da engine
- Estudo aplicado documenta estereopsia, disparidade, oclusão, ecos,
  oversampling, limites de paralelização e a consequência prática de cada
  conceito.
- Cinco ADRs registram clean-room MIT, goldens, estratégia CPU/WebGL, gatilho
  de extração e governança dos benchmarks.
- Pipeline JSONL validado por Pydantic guarda configuração, ambiente
  sanitizado, Git SHA, hash da fonte, duração e hash RGB; relatórios são
  derivados e dados oficiais são imutáveis.
- Seis goldens protegem legacy e V2 pixel a pixel.
- V2 pura otimizada de 1.124–1.224 ms para 452–477 ms de mediana em
  900×560/3×, mantendo p95 abaixo de 495 ms e `CV ≤ 5%`.
- Coleta WebGL por timer query aprovada com 0,76–0,84 ms de mediana GPU,
  exportação PNG separada e `CV ≤ 1,63%`.
- Galeria A/B cega preparada; integração ao produto continua bloqueada até duas
  avaliações visuais em dias diferentes.

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
