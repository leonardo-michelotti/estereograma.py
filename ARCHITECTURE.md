# Arquitetura — estereograma.py

> Documento vivo da arquitetura do projeto. Atualizar a cada decisão estrutural.

---

## 1. Visão

**estereograma.py** é um portfólio online + ferramenta interativa, focado em
estereogramas (autostereograms / Magic Eye). Combina quatro facetas em um único
site:

| Faceta | Quem serve | Onde mora |
|---|---|---|
| Hero educativo | Leigos que nunca conseguiram "ver" um | `/` |
| Galeria autoral | Visitantes curiosos / recrutadores | `/galeria` |
| Playground interativo | Público geral lúdico | `/playground` |
| "Como funciona" | Curiosos técnicos | `/como-funciona` |

### Princípios

1. **Gerador é o coração.** Tudo se apoia no módulo `app/stereogram/`. Site
   sem gerador funcional é inútil.
2. **Python ponta-a-ponta.** Stack escolhida pra evitar contexto-switch de
   linguagem e maximizar produtividade.
3. **Sem banco no MVP.** Galeria é arquivos + YAML; redeploy a cada push.
4. **JS mínimo.** HTMX cobre toda interatividade do playground.
5. **Acessibilidade educativa.** Cada estereograma exibido tem revelação
   opcional da figura escondida — leigos não devem ficar de fora.

---

## 2. Stack

| Camada | Tecnologia | Por quê |
|---|---|---|
| Backend web | **FastAPI** + **Uvicorn** | Async nativo, tipagem forte, devx excelente |
| Templates | **Jinja2** | Padrão, integra zero-config com FastAPI |
| Interatividade | **HTMX** (via CDN) | Form → POST → swap, sem build step nem framework JS |
| Processamento de imagem | **NumPy** + **Pillow** | Combo padrão; numpy pro algoritmo, pillow pro I/O |
| Persistência | **YAML** em disco | Galeria estática, versionada no git |
| Estilo | CSS puro (Tailwind via CDN se necessário) | Decisão final na Fase 3 |
| Testes | **pytest** | Padrão |
| Lint | **ruff** | Rápido, substitui flake8 + isort + black |
| Deploy | **Fly.io** | Free tier generoso, Dockerfile, `fly deploy` |

### Versões mínimas

- Python ≥ 3.11 (uso de `Literal`, `|` em tipos, `Self`)
- NumPy ≥ 1.26
- Pillow ≥ 10.0
- FastAPI ≥ 0.110

---

## 3. Estrutura de pastas

```
estereograma.py/
├── app/
│   ├── __init__.py
│   ├── main.py                 # [Fase 2] FastAPI app + rotas
│   ├── stereogram/             # ★ NÚCLEO — gerador independente
│   │   ├── __init__.py
│   │   ├── __main__.py         # CLI: python -m app.stereogram
│   │   ├── generator.py        # função principal gerar_estereograma()
│   │   ├── patterns.py         # depth maps sintéticos (esfera, coração, texto)
│   │   └── presets.py          # [Fase 2] catálogo de presets do playground
│   ├── templates/              # [Fase 2] Jinja
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── galeria.html
│   │   ├── playground.html
│   │   ├── como_funciona.html
│   │   └── partials/
│   │       └── resultado.html
│   └── static/
│       ├── css/
│       ├── img/
│       │   ├── galeria/        # obras autorais (.png) + reveals (.gif)
│       │   └── presets/        # depth maps gerados por scripts/gerar_presets.py
│       └── galeria.yaml        # [Fase 3] metadata das obras
├── scripts/
│   └── gerar_presets.py        # roda patterns.* e salva PNGs em static/img/presets/
├── tests/
│   ├── __init__.py
│   └── test_generator.py
├── exemplos/                   # PNGs gerados para validação manual (gitignore opcional)
├── pyproject.toml
├── Dockerfile                  # [Fase 2] pra Fly.io
├── fly.toml                    # [Fase 2]
├── README.md
└── ARCHITECTURE.md             # este arquivo
```

### Convenções

- **Idioma:** código em português (nomes de funções, variáveis, docstrings).
  Exceções: termos técnicos consagrados (`shift`, `pattern_width`, `seed`).
- **Tipagem:** type hints obrigatórios em toda função pública. `from __future__
  import annotations` no topo dos módulos pra postergar avaliação.
- **Erros:** levantar `ValueError` com mensagem clara em PT-BR pra problemas
  de uso. Validar nos limites públicos, confiar nas funções internas.

---

## 4. Módulo gerador (`app/stereogram/`)

### 4.1 API pública

```python
def gerar_estereograma(
    depth_map: PIL.Image.Image,
    largura: int = 800,
    altura: int = 600,
    eye_separation: int = 200,
    mu: float = 0.333,
    textura: Literal[
        "pink_noise", "random_dots", "random_dots_bw", "colorido", "custom"
    ] = "pink_noise",
    textura_custom: PIL.Image.Image | None = None,
    seed: int | None = None,
) -> PIL.Image.Image
```

### 4.2 Algoritmo — classes de equivalência (Thimbleby/Inglis/Witten 1994)

Referência canônica: *Displaying 3D Images: Algorithms for Single Image Random
Dot Stereograms*, IEEE Computer 27(10), 1994. Substitui o método ingênuo de
look-back, que sofre de "pattern ringing" (artefatos em torno de objetos).

**Fórmula de separação estereoscópica:**

```
sep(z) = round((1 - μ·z) · E / (2 - μ·z))
```

- `E` (eye_separation): distância entre os olhos em pixels (~180–240 em telas)
- `μ` (mu): fator de depth-of-field, tipicamente ≈ 1/3
- `z ∈ [0, 1]`: profundidade normalizada (1 = perto, 0 = longe)

Essa fórmula modela a geometria real do olhar — sem ela, o relevo parece um
"disco em profundidade" em vez de um objeto volumétrico.

**Algoritmo, linha por linha:**

```
para cada y:
    same[x] = x  para todo x   # cada pixel em sua própria classe
    para cada x da esquerda pra direita:
        sep = sep(z[y, x])
        left = x - sep // 2
        right = left + sep
        se 0 <= left e right < largura:
            # union via cadeia de same[]
            l = same[left]
            enquanto l != left e l != right:
                se l < right: left = l;  l = same[left]
                senão:        same[left] = right; left = right; l = same[left]
            same[left] = right

    # colore da direita pra esquerda
    para x = largura-1 .. 0:
        se same[x] == x:  saida[y, x] = textura[y, x]   # raiz da classe
        senão:            saida[y, x] = saida[y, same[x]]
```

**Por que funciona melhor que o look-back:**

- Pixels que devem ter a **mesma cor** são unidos numa estrutura tipo
  union-find, em vez de copiados em cadeia. Isso elimina o acúmulo de erros
  que gera as "franjas" típicas do look-back.
- A coloração right-to-left garante que cada classe inteira receba a cor da
  sua raiz consistentemente.
- A fórmula de separação não-linear preserva a percepção de **volume**, não
  só de profundidade chapada.

**Complexidade:** O(largura × altura × α) por linha, onde α é o tamanho médio
da cadeia em `same[]` (efetivamente quase constante com path compression). Em
Python puro, ~800×600 leva 2–4s; aceitável pro dev. Se virar gargalo no
playground, vetorizar parte da iteração ou anexar `@numba.njit`.

### 4.3 Texturas (`_gerar_textura` em generator.py)

| Tipo | Descrição | Quando usar |
|---|---|---|
| `pink_noise` (default) | Ruído 1/f via FFT, organicamente texturizado | Default — academicamente o melhor pra profundidade ([arXiv 1506.05036](https://arxiv.org/abs/1506.05036)) |
| `random_dots` | Ruído branco RGB | Clássico Magic Eye colorido |
| `random_dots_bw` | Ruído branco preto/branco binário | Alto contraste, lembra estilo Magic Eye book |
| `colorido` | Amostra de paleta de 6 cores saturadas | Visual mais "pop", mais ruidoso |
| `custom` | Imagem fornecida pelo usuário, redimensionada com Lanczos | Branding / temática |

### 4.4 Depth maps sintéticos (`patterns.py`)

Funções puras que retornam `PIL.Image.Image` em modo `L`:

- `esfera(largura, altura, raio)` — gradiente radial (sqrt para parecer esfera)
- `coracao(largura, altura)` — máscara via equação implícita
- `texto(palavra, largura, altura)` — texto em relevo (tenta Arial, fallback default)

Adicionar novos depth maps aqui mantém a base de presets crescível sem mexer no gerador.

### 4.5 CLI (`__main__.py`)

```bash
python -m app.stereogram <depth_map.png> <saida.png> \
    [--largura 800] [--altura 600] \
    [--eye-separation 200] [--mu 0.333] \
    [--textura pink_noise|random_dots|random_dots_bw|colorido|custom] \
    [--textura-custom path] [--seed 42]
```

Reusável em scripts e CI. Não depende do FastAPI.

---

## 5. Camada web (Fase 2+)

### 5.1 Rotas

| Rota | Método | Renderiza | Fase |
|---|---|---|---|
| `/` | GET | `index.html` (hero + CTA) | 2 |
| `/playground` | GET | `playground.html` (form) | 2 |
| `/playground/gerar` | POST | `partials/resultado.html` (HTMX swap) | 2 |
| `/galeria` | GET | `galeria.html` (grid) | 3 |
| `/galeria/{slug}` | GET | detalhe da obra | 3 |
| `/como-funciona` | GET | `como_funciona.html` | 5 |
| `/static/*` | GET | arquivos estáticos via `StaticFiles` | 2 |

### 5.2 Padrão HTMX no playground

```html
<form hx-post="/playground/gerar"
      hx-target="#resultado"
      hx-swap="innerHTML"
      hx-indicator="#carregando">
  <select name="preset">...</select>
  <select name="textura">...</select>
  <button>Gerar</button>
  <span id="carregando" class="htmx-indicator">gerando…</span>
</form>
<div id="resultado"></div>
```

O endpoint `/playground/gerar` devolve um fragmento Jinja
(`partials/resultado.html`) com a tag `<img>` apontando pra um data-URL
base64 do PNG gerado em memória — evita persistir arquivos.

Para uploads (Fase 4): mesma rota aceita `multipart/form-data` via
`UploadFile` do FastAPI.

### 5.3 Gerenciamento da galeria

Estrutura de `app/static/galeria.yaml`:

```yaml
- slug: dinossauro-2026
  titulo: Dinossauro
  imagem: galeria/dinossauro.png
  figura_escondida: galeria/dinossauro_reveal.gif
  descricao: |
    Primeiro estereograma autoral, padrão random dots com depth map desenhado à mão.
  data: 2026-04-12
  tags: [random-dots, animal]
  parametros:
    pattern_width: 120
    profundidade_max: 0.4
    seed: 42
```

Carregado uma vez no startup do FastAPI (`@app.on_event("startup")` ou
lifespan handler), armazenado num módulo singleton. Recarrega a cada deploy.

Não há sistema de admin — adicionar obra = commit + push.

---

## 6. Estratégia de testes

### 6.1 Unit (atual)

`tests/test_generator.py` cobre:
- Dimensões e modo da imagem de saída
- Determinismo com `seed` fixa
- Diferenciação com seeds distintas
- Período de repetição em região plana de profundidade
- Validação de parâmetros (`pattern_width` mínimo, `textura=custom` sem imagem)

### 6.2 Integração (Fase 2+)

`TestClient` do FastAPI para:
- Status codes de todas as rotas GET
- POST `/playground/gerar` retorna fragmento HTML válido contendo `<img>`
- Upload inválido (formato errado, > tamanho máx) retorna erro amigável

### 6.3 Validação manual visual

Não é automatizável: humano olha o PNG e confirma que vê o 3D. Rodar a cada
mudança não-trivial no algoritmo:

```bash
python -m app.stereogram app/static/img/presets/esfera.png /tmp/test.png --seed 42
```

---

## 7. Deploy

### 7.1 Alvo: Fly.io

Razões:
- Free tier generoso (~3 VMs pequenas)
- Dockerfile simples (sem buildpacks mágicos)
- `fly deploy` direto do CLI
- Domínio `.fly.dev` grátis pra começar

### 7.2 Dockerfile (esboço pra Fase 2)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app/ ./app/
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 7.3 Variáveis de ambiente

- `ENV` — `development` | `production`
- `MAX_UPLOAD_MB` — limite do upload (default 5)
- `RATE_LIMIT_PER_MIN` — Fase 4

---

## 8. Roadmap

| Fase | Entregável | Status |
|---|---|---|
| **1** | Gerador standalone + CLI + presets + testes | ✅ Concluída |
| **2** | FastAPI app + playground com presets + deploy inicial | ⏳ Próxima |
| **3** | Galeria via YAML + hero polido + reveal animado | ⏳ |
| **4** | Upload de depth map + rate limiting | ⏳ |
| **5** | "Como funciona" + SEO + analytics (opcional) | ⏳ |

### Critérios de saída por fase

- **F1:** `pytest` passa + estereograma de teste gerado e o 3D é visível
- **F2:** site online no `*.fly.dev`, playground gera < 2s sem reload
- **F3:** ≥ 5 obras na galeria, navegação fluida, reveal funciona
- **F4:** upload de PNG cinza qualquer → estereograma; uploads inválidos retornam erro amigável
- **F5:** Lighthouse mobile ≥ 85 em performance e acessibilidade

---

## 9. Decisões adiadas (com gatilho de revisão)

| Decisão | Padrão atual | Quando revisitar |
|---|---|---|
| Banco de dados | Nenhum (YAML) | Quando quiser editar galeria pela web |
| Sistema de contato | Nenhum (e-mail no rodapé) | Se receber spam por scrapping |
| i18n PT/EN | Só PT-BR | Quando primeiro acesso fora do Brasil |
| Domínio próprio | `*.fly.dev` | Quando o portfólio for divulgado publicamente |
| Otimização do gerador | Loop Python puro | Quando geração demorar > 3s percebidos |
| Análise de oclusão | Não verifica (visible=True implícito) | Se aparecerem artefatos nas bordas de objetos com fortes saltos de profundidade — adicionar o teste de visibilidade do Thimbleby 1994 |
| Analytics | Nenhum | Após primeiro mês de tráfego real |

---

## 10. Riscos conhecidos

1. **Performance do gerador** em depth maps grandes (1920×1080+) — O(n²) em
   Python puro. Mitigação: limite explícito de dimensões no playground;
   migrar pra NumPy vetorizado quando necessário.

2. **Uploads maliciosos** (Fase 4) — PIL tem CVEs históricos; PNGs gigantes
   podem causar OOM. Mitigação: validar dimensões e tamanho **antes** de
   abrir com PIL; usar `Image.MAX_IMAGE_PIXELS`.

3. **Cold start no free tier** — usuário pode esperar 5–10s no primeiro
   acesso. Mitigação aceitável pro estágio atual; revisitar se virar dor.

4. **Acessibilidade** — visitantes não enxergam o 3D. Mitigação: cada
   estereograma exibido tem a figura escondida revelável (GIF lado-a-lado
   ou overlay), garantida no design da galeria e do hero.

---

## 11. Como atualizar este documento

- Ao concluir uma fase, marcar com ✅ na tabela do §8.
- Ao tomar uma decisão arquitetural (mudar stack, adicionar dependência
  pesada, mudar deploy target), adicionar entrada com data no §9 ou §10.
- Nomes de arquivos novos no núcleo do gerador → atualizar §3 e §4.
