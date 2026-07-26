# Relatório de benchmark da engine

> Gerado automaticamente a partir dos dados JSONL validados.

## Linhagem

| run_id | Git SHA | fonte | ambiente |
| --- | --- | --- | --- |
| `v2-20260726T001320Z-6e9fe828` | `a94bd64aa4e6` + alterações locais | `6e9fe8288ba4` | CPython 3.13, Windows 11, AMD64, 16 CPUs lógicas |

## Resultados

| run_id | engine | caso | n | mín. ms | mediana ms | p95 ms | CV | outliers |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v2-20260726T001320Z-6e9fe828` | v2 v2.0 | coracao | 10 | 1200.34 | 1223.94 | 1315.63 | 3.45% | 0 |
| `v2-20260726T001320Z-6e9fe828` | v2 v2.0 | esfera | 10 | 1105.92 | 1124.82 | 1249.49 | 4.52% | 0 |
| `v2-20260726T001320Z-6e9fe828` | v2 v2.0 | texto-3d | 10 | 1149.94 | 1214.70 | 1233.43 | 2.14% | 0 |

## Portões de decisão

- Estabilidade (`CV ≤ 5.0%`): **aprovada**.
- Meta V2 (mediana < 500 ms e p95 < 650 ms): **não atingida**.
- Performance é válida apenas para o ambiente registrado acima.
