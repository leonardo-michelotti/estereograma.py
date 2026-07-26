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

As entradas dos casos também precisam ser determinísticas. Mapas de profundidade
que dependem de renderizadores externos, como fontes do sistema, são versionados
como fixtures. A geração de texto do produto usa uma fonte local e versões fixadas;
ela tem um teste separado do contrato RGB da engine.

## Consequências

Uma diferença cosmética intencional exige ADR próprio, nova versão da engine,
novos goldens e invalidação explícita de cache.

Trocar apenas o mecanismo que produz uma entrada não muda a versão da engine,
desde que o mesmo mapa de profundidade continue produzindo os mesmos pixels RGB.
