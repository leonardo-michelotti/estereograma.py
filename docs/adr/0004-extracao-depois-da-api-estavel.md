# ADR 0004 — extração somente depois da API estável

- Status: aceito
- Data: 25/07/2026

## Contexto

Separar a engine agora criaria versionamento e integração entre repositórios
antes de o contrato e o núcleo de desempenho estarem comprovados.

## Decisão

A V2 permanece em `app/stereogram/`. Um futuro `estereograma-core` será avaliado
depois do benchmark, da otimização e da estabilização de entrada e saída.

## Consequências

As APIs atuais são mantidas e não se cria uma abstração genérica para uma
segunda engine que ainda não está integrada.
