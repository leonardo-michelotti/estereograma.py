# Relatório de benchmark da engine

> Gerado automaticamente a partir dos dados JSONL validados.

## Linhagem

| run_id | Git SHA | fonte | ambiente |
| --- | --- | --- | --- |
| `v2-20260729T022618Z-3ab3cde7` | `0de06baaa85e` | `3ab3cde7ea63` | CPython 3.12, Linux 6.17.0-1020-azure, x86_64, 4 CPUs lógicas |

## Resultados

| run_id | engine | tipo | caso | n | mín. ms | mediana ms | p95 ms | CV | outliers |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v2-20260729T022618Z-3ab3cde7` | v2 v2.0/cython | measure | coracao | 10 | 110.41 | 111.73 | 113.24 | 0.85% | 0 |
| `v2-20260729T022618Z-3ab3cde7` | v2 v2.0/cython | measure | esfera | 10 | 87.41 | 94.80 | 96.86 | 4.13% | 0 |
| `v2-20260729T022618Z-3ab3cde7` | v2 v2.0/cython | measure | texto-3d | 10 | 80.90 | 84.99 | 89.62 | 3.10% | 0 |

## Portões de decisão

- Estabilidade (`CV ≤ 5.0%`): **aprovada**.
- Meta V2 (mediana < 500 ms e p95 < 650 ms): **aprovada**.
- Meta WebGL render-only (mediana < 100 ms): **não aplicável**.
- Performance é válida apenas para o ambiente registrado acima.
