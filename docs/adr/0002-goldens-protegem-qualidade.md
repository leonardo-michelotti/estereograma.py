# ADR 0002 — resultados dourados protegem a qualidade

- Status: aceito
- Data: 25/07/2026

## Contexto

Um PNG válido não prova que a profundidade permaneceu fácil de perceber.
Otimizações também podem alterar arredondamentos de forma quase invisível.

## Decisão

Os seis casos do laboratório são fixtures. Mudanças internas da V2 exigem
igualdade exata dos bytes RGB nos cinco casos V2; o controle legacy também
permanece protegido.

## Consequências

Uma diferença cosmética intencional exige ADR próprio, nova versão da engine,
novos goldens e invalidação explícita de cache.
