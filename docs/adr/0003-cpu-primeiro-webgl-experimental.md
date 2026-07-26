# ADR 0003 — CPU primeiro, WebGL experimental

- Status: aceito
- Data: 25/07/2026

## Contexto

A V2 foi aprovada visualmente, mas ainda executa loops críticos em Python. Uma
implementação WebGL promete tempo real, porém codifica profundidade por outra
estratégia e ainda não provou equivalência perceptiva.

## Decisão

Otimizar primeiro a V2 e usá-la como referência. WebGL será um fork público
separado e só poderá ser proposto como preview após benchmark sincronizado e
avaliação A/B cega.

## Consequências

Não entra JavaScript de geração no produto neste ciclo. CPU-servidor e
GPU-cliente são medidos separadamente porque respondem perguntas distintas.

## Evidência registrada

O marco otimizado `v2-20260726T002043Z-f3e212f7` atingiu medianas de
451,95–477,46 ms e p95 de 460,53–494,72 ms, com seis goldens RGB idênticos.
Numba/Cython não foram necessários. O laboratório WebGL foi criado no fork
público. O marco `webgl-20260726T014002Z-274293c9` atingiu 0,76–0,84 ms de
mediana GPU e 20,60–47,30 ms de exportação, com `CV ≤ 1,63%`. O portão de
performance passou; a adoção continua pendente de duas sessões A/B cegas.
