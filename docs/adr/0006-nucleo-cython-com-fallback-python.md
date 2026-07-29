# ADR 0006 — núcleo Cython com fallback Python

- Status: aceito
- Data: 28/07/2026

## Contexto

A V2 Python pura já atendia o orçamento de 500 ms, mas o profiling ainda
atribuía aproximadamente metade do render aos loops sequenciais de vínculos e
pintura. Na primeira sessão A/B cega, a V2 venceu WebGL em coração e esfera nos
três critérios perceptivos; WebGL venceu apenas texto. Por decisão do autor, não
esperaremos uma segunda sessão para escolher a arquitetura.

Um spike Cython compilou somente vínculos, pintura e visibilidade. Em WSL2,
Python 3.12, 900×560/3× e 15 repetições alternadas, a mediana caiu de
253–267 ms para 58,9–61,5 ms; o p95 compilado ficou entre 67,5 e 84,2 ms.
Os seis goldens, 48 combinações de textura/oclusão/oversampling/seed e três
resoluções adicionais permaneceram pixel a pixel idênticos.

## Decisão

A Engine V2 continua sendo a engine oficial no servidor. Seus loops críticos
passam a ter um núcleo Cython interno, compilado explicitamente nos ambientes
Linux de CI e container. O caminho Python permanece como fallback automático.
Os loops compilados liberam o GIL enquanto operam exclusivamente sobre buffers
já validados, permitindo que renders independentes avancem em paralelo.

`RenderConfigV2`, `render_stereogram_v2`, `ENGINE_VERSION_V2` e os pixels RGB
não mudam. A implementação compilada não cria uma nova engine nem altera a
versão óptica `v2.0`.

WebGL não será adotado como preview com a evidência perceptiva atual.

## Consequências

- CI testa o núcleo compilado em Python 3.11, 3.12 e 3.13 e também força o
  fallback Python.
- Build local sem `ESTEREOGRAMA_BUILD_CYTHON=1` continua produzindo wheel puro,
  sem exigir compilador.
- Docker compila o módulo em estágio de build; nenhum deploy é autorizado por
  esta decisão.
- Benchmarks novos registram `implementation` e calculam a linhagem sobre o
  Python e o `.pyx`.
- O próximo hotspot medido é o mapa NumPy de separações; só será movido para C
  após um novo experimento com ganho relevante e igualdade RGB.
- Um ensaio exploratório com 16 renders elevou o throughput de 11,2 para 17,2
  renders/s em duas threads antes de liberar o GIL; depois, passou de 12,0 para
  23,8 renders/s, preservando o hash RGB. O limite operacional permanece em
  duas gerações até haver medição no ambiente de deploy.
