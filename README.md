# estereograma.py

Hub educativo, galeria curada e ferramenta interativa para gerar
**autostereogramas** (Magic Eye / SIRDS) — escrito do zero em Python.

> Estereogramas são imagens 2D que escondem cenas em três dimensões. Esse
> site é um portfólio autoral, um livro-guia sobre o tema, e um gerador
> que você usa no navegador.

## Em três partes

- **Aprender** — guia em seis seções: o que são, história, fisiologia da
  visão binocular, teoria, o cálculo, e como o cálculo vira algoritmo.
- **Galeria** — coletânea curada de estereogramas em domínio público ou
  com licença aberta, com crédito a quem fez.
- **Playground** — escolhe forma e textura, ajusta profundidade, e gera
  um estereograma em segundos.

## Stack

100% Python no backend:

- **FastAPI** + **Jinja2** + **HTMX** — site reativo sem framework JS
- **NumPy** + **Pillow** — geração de imagens
- **Markdown** — conteúdo dos artigos
- **PyYAML** — galeria

Gerador implementa o algoritmo de **classes de equivalência** descrito em
Thimbleby, Inglis & Witten (1994), evitando os artefatos do método
ingênuo de look-back.

## Rodando local

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # Linux/macOS
pip install -e ".[dev]"

# gerar os depth maps presets (esfera, coração, texto "3D")
python scripts/gerar_presets.py

# subir o site
uvicorn app.main:app --reload
# → http://127.0.0.1:8000
```

## Usando só o gerador (CLI)

```bash
python -m app.stereogram app/static/img/presets/esfera.png saida.png --seed 42
```

Parâmetros principais:
- `--eye-separation` (px, default 200) — distância entre olhos virtual
- `--mu` (0..1, default 0.333) — depth-of-field, controla o "salto" 3D
- `--textura` — `pink_noise` (default), `random_dots`, `random_dots_bw`, `colorido`, `custom`
- `--seed` — determinismo

## Testes

```bash
pytest
```

## Documentação

- [ARCHITECTURE.md](ARCHITECTURE.md) — arquitetura técnica, decisões, roadmap
- [CHANGELOG.md](CHANGELOG.md) — histórico de versões
- [CONTRIBUTING.md](CONTRIBUTING.md) — convenções de commit e fluxo de trabalho

## Licença

Código sob MIT. Conteúdo dos artigos sob
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Obras
na galeria pertencem aos respectivos autores e seguem suas próprias
licenças (declaradas em cada item).
