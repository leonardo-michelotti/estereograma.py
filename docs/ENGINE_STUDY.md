# Engine V2 — estudo aplicado de engenharia

> Estado: CPU e coleta WebGL concluídas; A/B em avaliação · engine de referência: `v2.0` · última revisão: 25/07/2026

## 1. Pergunta de engenharia

Como reduzir a latência da geração sem tornar o estereograma mais difícil de
fundir, introduzir ecos ou perder a reprodutibilidade que permite comparar duas
implementações?

O estudo não trata velocidade como um objetivo isolado. A ordem de prioridade é:

1. preservar a percepção de profundidade já aprovada;
2. preservar exatamente os pixels da V2 durante otimizações internas;
3. reduzir a latência e o custo computacional;
4. avaliar GPU como arquitetura complementar, não como substituição presumida.

## 2. Da visão binocular ao pixel

### 2.1 Estereopsia e disparidade

Julesz demonstrou que padrões sem contorno reconhecível podem produzir
profundidade quando os olhos encontram correspondências com disparidade
horizontal. Para o produto, isso explica por que a textura não precisa desenhar
o coração ou a esfera: a forma vive nas correspondências, não na cor isolada.

**Consequência:** os testes não podem validar apenas se o PNG foi criado. Eles
precisam proteger a periodicidade do plano distante e os vínculos que codificam
o relevo.

### 2.2 Mapa de profundidade

A entrada é uma imagem em escala de cinza normalizada em `z ∈ [0, 1]`. Na
convenção da V2, `0` é o plano distante e `1` é a superfície próxima. A engine
redimensiona e suaviza essa entrada antes de calcular os vínculos.

**Consequência:** coração em camadas, texto e esfera formam uma suíte canônica:
degraus testam descontinuidades; texto testa contornos finos; esfera testa
gradiente contínuo.

### 2.3 Separação binocular simétrica

Para profundidade `z`, distância ocular em pixels `E` e intensidade `μ`, a V2
usa a relação descrita por Thimbleby, Inglis e Witten:

```text
sep(z) = round(((1 - μz) × E) / (2 - μz))
```

O par é colocado simetricamente ao redor do ponto observado:

```text
left  = x - sep(z) // 2
right = left + sep(z)
```

A simetria evita o deslocamento lateral dependente da profundidade presente em
algoritmos simples de look-back.

**Consequência:** `sep(0)` determina o período e os pontos-guia; `sep(1)` deve
ser menor. A primeira hipótese de desempenho é calcular todas as separações de
uma vez, sem alterar a fórmula ou o arredondamento.

### 2.4 Vínculos, conflitos e superfícies ocultas

Cada vínculo afirma que dois pixels devem receber a mesma cor. Quando vínculos
competem, a V2 preserva a restrição que representa a superfície mais próxima.
Antes disso, a máscara de visibilidade verifica se outra superfície interrompe
o caminho até os olhos. Essa etapa reduz fragmentos repetidos — os “ecos” — nas
bordas de saltos de profundidade.

**Consequência:** há testes distintos para conflitos e visibilidade. Uma
otimização que acelere o loop, mas mude qualquer vínculo, é rejeitada pelo hash
RGB dourado.

### 2.5 Oversampling

A engine trabalha em uma largura virtual três vezes maior e reduz o resultado
com Lanczos. O custo principal cresce aproximadamente com
`altura × largura × oversampling`; a máscara de visibilidade adiciona um termo
proporcional ao alcance horizontal inspecionado.

**Consequência:** `3×` permanece fixo na comparação. Diminuí-lo produziria um
benchmark mais rápido, mas responderia outra pergunta e poderia alterar bordas.

## 3. Três famílias comparadas

| Família | Como codifica profundidade | Ponto forte | Limite relevante |
| --- | --- | --- | --- |
| Legacy | classes de equivalência `same[]` | implementação Python simples e histórica | textura e oclusão não correspondem à V2 aprovada |
| V2 | vínculos simétricos, visibilidade e pintura do centro para fora | qualidade aprovada e implementação clean-room | loops sequenciais ainda executados em Python |
| WebGL | deslocamentos iterativos de faixas em fragment shader | preview em GPU e cenas em movimento | não explicita a mesma política de oclusão da V2 |

O código GPL de `gnudles/stereograma` é somente uma referência comportamental.
O experimento WebGL parte do projeto MIT de Jérémie Piellard e permanece em um
fork separado, com a atribuição original.

## 4. Hipóteses verificáveis

| ID | Hipótese | Evidência necessária | Decisão associada |
| --- | --- | --- | --- |
| H1 | Pré-calcular `sep(z)` elimina o maior volume de chamadas escalares | cProfile + mediana/p95 antes e depois | manter apenas com RGB idêntico e ganho acima do ruído |
| H2 | Reutilizar índices e buffers reduz alocações por linha | profiling e benchmark isolado | manter apenas se o ganho superar o CV do baseline |
| H3 | A V2 pura pode chegar a 500 ms em 900×560/3× | dez repetições aceitas com CV ≤ 5% | dispensar núcleo compilado se a meta for atingida |
| H4 | Compilar os loops sequenciais supera a V2 pura sem mudar pixels | spikes Numba/Cython | escolher conforme latência, build, cold start e manutenção |
| H5 | WebGL entrega preview abaixo de 100 ms | tempo GPU sincronizado e exportação separados | considerar apenas como preview se a qualidade não cair |

## 5. Método experimental

- Máquina oficial conectada à energia, modo de energia fixo e sem carga
  concorrente relevante.
- Duas execuções de aquecimento e dez medições por caso.
- Marco aceito somente com coeficiente de variação `CV ≤ 5%`.
- Dados brutos em JSON Lines, validados e imutáveis; tabelas são derivadas.
- Hash calculado sobre os bytes RGB descomprimidos, nunca sobre o arquivo PNG.
- Performance não bloqueia CI compartilhado; determinismo e goldens bloqueiam.

O orçamento de 500 ms reserva o restante de um segundo percebido para criar o
depth map, codificar o PNG, acessar o cache e transportar a resposta.

## 6. Profiling inicial

Execuções aquecidas de coração, texto e esfera em 900×560/3× sob `cProfile`
registraram:

| Hotspot | Tempo acumulado | Participação aproximada |
| --- | ---: | ---: |
| `_build_links` | 1,089–1,100 s | 65,1–65,3% |
| `_paint_row` | 0,410–0,420 s | 24,6–25,1% |
| `_visibility_mask` | 0,107–0,118 s | 6,4–7,0% |

`separation()` foi chamada entre 1,46 e 1,51 milhão de vezes por render e
respondeu por 0,447–0,455 s dentro de `_build_links`. Isso prioriza H1 antes de
qualquer mudança em textura, resolução ou paralelismo. O relatório completo e
reproduzível está em `benchmarks/reports/profile-baseline.md`.

## 7. Limites de paralelização

Linhas diferentes são independentes e podem ser distribuídas quando o núcleo
libera o GIL. Dentro de uma linha, porém, os vínculos e a pintura consultam
resultados anteriores; uma vetorização ingênua muda a semântica. Threads Python
não são adotadas enquanto os loops permanecem sob o GIL, e multiprocessamento
não é presumido vantajoso no Railway de um worker/CPU limitado.

## 8. Evidências e decisão

Os datasets oficiais ficam em `benchmarks/data/`, os relatórios derivados em
`benchmarks/reports/` e cada decisão cita `run_id` e Git SHA. O fechamento deve
comparar V2 pura, V2 compilada e V2 servidor + WebGL preview sem misturar custo
do servidor com latência da GPU do usuário.

### 8.1 Resultado da otimização CPU

O baseline `v2-20260726T001320Z-6e9fe828` foi comparado ao marco otimizado
`v2-20260726T002043Z-f3e212f7`, ambos no mesmo ambiente e com `CV ≤ 5%`:

| Caso | baseline mediana | otimizada mediana | p95 otimizado | redução |
| --- | ---: | ---: | ---: | ---: |
| coração | 1.223,94 ms | 477,46 ms | 488,09 ms | 61,0% |
| texto 3D | 1.214,70 ms | 451,95 ms | 460,53 ms | 62,8% |
| esfera | 1.124,82 ms | 472,92 ms | 494,72 ms | 58,0% |

H1 e H2 foram confirmadas: separações e restrições passaram a ser calculadas em
bloco, índices foram reutilizados e a pintura materializa o RGB por linha. H3
também foi confirmada. Como a V2 pura ultrapassou os dois portões de performance,
H4 não foi executada: adicionar Numba ou Cython agora aumentaria build, cold
start e manutenção sem resolver uma necessidade medida.

Os seis casos dourados permaneceram RGB idênticos. O relatório comparativo está
em `benchmarks/reports/comparison.md` e o profiling posterior em
`benchmarks/reports/profile-optimized.md`.

### 8.2 Estado do experimento WebGL

O fork MIT público está em
[`leonardo-michelotti/stereogram-webgl`](https://github.com/leonardo-michelotti/stereogram-webgl).
O laboratório fixa 900×560, os mesmos três depth maps, mosaico, período de 108 px
e faixa de disparidade equivalente. Ele sincroniza o tempo de GPU e mede a
exportação PNG separadamente.

O marco `webgl-20260726T014002Z-274293c9` foi coletado em Chrome/WebGL 2 sobre
Intel UHD via ANGLE/Direct3D 11. O tempo vem de timer query da GPU; cada uma das
30 amostras contém 200 draws e reporta o custo médio por draw:

| Caso | GPU mediana | p95 | CV | exportação PNG |
| --- | ---: | ---: | ---: | ---: |
| coração | 0,78 ms | 0,80 ms | 1,41% | 27,20 ms |
| texto 3D | 0,84 ms | 0,87 ms | 1,63% | 47,30 ms |
| esfera | 0,76 ms | 0,78 ms | 1,35% | 20,60 ms |

H5 passou pelo portão de performance de 100 ms. Isso ainda não aprova a adoção:
CPU mede geração no servidor, enquanto a coluna GPU mede apenas o shader no
cliente; exportação, transferência e UX são custos separados. Duas sessões A/B
cegas, em dias diferentes, ainda avaliarão facilidade de fusão, clareza e
artefatos. Até esse portão ser cumprido, a decisão vigente é **V2 pura no
servidor; WebGL experimento aprovado tecnicamente, mas não preview de produto**.

O toolchain herdado do fork também registra 19 achados de `npm audit` (1 baixo,
9 moderados e 9 altos). O servidor do laboratório deve permanecer local; uma
eventual adoção exige revisão de dependências separada, sem `audit fix`
automático que altere a base experimental.

## Referências

- Bela Julesz, [*Binocular Depth Perception of Computer-Generated Patterns*](https://doi.org/10.1002/j.1538-7305.1960.tb03954.x), 1960.
- H. W. Thimbleby, S. J. Inglis e I. H. Witten, [*Displaying 3D Images: Algorithms for Single-Image Random-Dot Stereograms*](https://hdl.handle.net/10289/47), 1994.
- W. A. Steer, [*Stereograms — technical description*](https://www.techmind.org/stereo/stech.html).
- Khronos Group, [*WebGL 2.0 Specification*](https://registry.khronos.org/webgl/specs/latest/2.0/).
- Jérémie Piellard, [`stereogram-webgl`](https://github.com/piellardj/stereogram-webgl), implementação MIT usada no experimento de GPU.
