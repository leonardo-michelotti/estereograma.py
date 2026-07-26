# ADR 0005 — dados de benchmark versionados e reproduzíveis

- Status: aceito
- Data: 25/07/2026

## Contexto

Tabelas preenchidas manualmente perdem linhagem e facilitam comparar execuções
feitas em condições diferentes.

## Decisão

Cada medição é um registro JSONL validado, com schema versionado, configuração,
ambiente sanitizado, Git SHA, duração e hash RGB. Dados de marcos são imutáveis;
relatórios são derivados por código.

Goldens só podem ser regenerados com alteração deliberada de
`ENGINE_VERSION_V2` e registro arquitetural correspondente.

## Consequências

O repositório guarda baseline, resultado otimizado e WebGL; medições ad hoc são
ignoradas. Nenhum hostname, usuário ou identificador pessoal é coletado.
