# Contribuindo

> Documento curto pro futuro-eu e pra eventual colaborador. Tudo aqui é
> consciente e propositalmente simples — projeto solo, escala humana.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
```

## Comandos do dia-a-dia

| O quê | Comando |
|---|---|
| Rodar testes | `pytest` |
| Lint | `ruff check .` |
| Auto-fix lint | `ruff check --fix .` |
| Rodar site local | `uvicorn app.main:app --reload` |
| Gerar presets | `python scripts/gerar_presets.py` |
| Gerar estereograma na CLI | `python -m app.stereogram <depth> <saida> [opções]` |

## Branching

**Trunk-based.** Tudo direto em `main` quando a mudança é segura. Use
branch (`refactor/algoritmo-x`, `feat/upload-depth-map`) só pra mudanças
grandes ou que podem quebrar coisas — abre PR contra `main` e merge
após CI verde.

## Commits

**Conventional Commits light**, sem escopos:

```
feat:     nova funcionalidade visível pro usuário
fix:      correção de bug
docs:     mudança só em documentação
refactor: muda código sem mudar comportamento
test:     adiciona ou ajusta testes
chore:    build, deps, CI, etc.
style:    formatação, semântica do código inalterada
perf:     melhoria de performance
```

Exemplos:
```
feat: adiciona textura pink_noise como default no gerador
fix: corrige cálculo de bbox no preset texto_3d
docs: redige artigo /aprender/historia
refactor: troca look-back por equivalence-class no gerador
```

## Versionamento

[SemVer](https://semver.org). Tags `v0.1.0`, `v0.2.0`, etc. marcam
marcos do projeto, não toda mudança. Cada tag tem entrada correspondente
no [CHANGELOG.md](CHANGELOG.md).

## Adicionando coisas

### Um novo artigo em `/aprender`
1. Crie `app/content/aprender/<slug>.md` com frontmatter `titulo`,
   `ordem`, `resumo`, `fontes`.
2. Reinicie o servidor (`uvicorn ... --reload` já faz isso).
3. Aparece automaticamente em `/aprender` e em `/aprender/<slug>`.

### Um novo preset no playground
1. Adicione função em `app/stereogram/patterns.py` que retorna `PIL.Image` em modo `L`.
2. Inclua a chamada em `scripts/gerar_presets.py` e rode-o pra gerar o PNG.
3. Adicione entrada em `app/stereogram/presets.py` (slug, titulo, dica).

### Uma obra na galeria
1. Salve a imagem em `app/static/img/galeria/<slug>.png` (atenção à licença!).
2. Acrescente entrada em `app/static/galeria.yaml` com `fonte`,
   `licenca`, `autor`, `descricao`.

## Direitos autorais na galeria

**Só obras de domínio público ou com licença aberta** (Wikimedia
Commons, CC-BY, CC-BY-SA, etc.). Cada entrada do YAML tem `fonte` (URL
original) e `licenca` (nome curto). Se uma obra estiver sem licença
clara, **não entra**.

## Quando algo der ruim

Se você está aqui debugando porque algo quebrou: cheque
[ARCHITECTURE.md](ARCHITECTURE.md) §10 ("Riscos conhecidos") antes de
sair caçando.
