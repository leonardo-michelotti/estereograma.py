# ADR 0001 — engine própria clean-room sob MIT

- Status: aceito
- Data: 25/07/2026

## Contexto

Implementações públicas maduras têm licenças e objetivos diferentes. A base
C++ mais completa é GPL-3.0, enquanto o produto pretende manter código MIT.

## Decisão

A V2 é a engine oficial. Sua implementação parte das descrições matemáticas
publicadas, sem copiar código GPL. Projetos externos servem para comparar
comportamento, arquitetura e desempenho.

## Consequências

O projeto mantém liberdade de distribuição e assume a responsabilidade por
testes, documentação e manutenção do algoritmo.
