# Relatório de benchmark da engine

> Gerado automaticamente a partir dos dados JSONL validados.

## Linhagem

| run_id | Git SHA | fonte | ambiente |
| --- | --- | --- | --- |
| `v2-20260726T001320Z-6e9fe828` | `a94bd64aa4e6` + alterações locais | `6e9fe8288ba4` | CPython 3.13, Windows 11, AMD64, 16 CPUs lógicas |
| `v2-20260726T002043Z-f3e212f7` | `a94bd64aa4e6` + alterações locais | `f3e212f71fb3` | CPython 3.13, Windows 11, AMD64, 16 CPUs lógicas |
| `webgl-20260726T014002Z-274293c9` | `274293c9f674` | `46e054a4299d` | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36, Windows, AMD64, 16 CPUs lógicas |

## Resultados

| run_id | engine | tipo | caso | n | mín. ms | mediana ms | p95 ms | CV | outliers |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v2-20260726T001320Z-6e9fe828` | v2 v2.0 | measure | coracao | 10 | 1200.34 | 1223.94 | 1315.63 | 3.45% | 0 |
| `v2-20260726T001320Z-6e9fe828` | v2 v2.0 | measure | esfera | 10 | 1105.92 | 1124.82 | 1249.49 | 4.52% | 0 |
| `v2-20260726T001320Z-6e9fe828` | v2 v2.0 | measure | texto-3d | 10 | 1149.94 | 1214.70 | 1233.43 | 2.14% | 0 |
| `v2-20260726T002043Z-f3e212f7` | v2 v2.0 | measure | coracao | 10 | 460.12 | 477.46 | 488.09 | 2.10% | 0 |
| `v2-20260726T002043Z-f3e212f7` | v2 v2.0 | measure | esfera | 10 | 459.33 | 472.92 | 494.72 | 2.51% | 1 |
| `v2-20260726T002043Z-f3e212f7` | v2 v2.0 | measure | texto-3d | 10 | 441.42 | 451.95 | 460.53 | 1.31% | 1 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | export | coracao | 1 | 27.20 | 27.20 | 27.20 | 0.00% | 0 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | gpu | coracao | 30 | 0.76 | 0.78 | 0.80 | 1.41% | 2 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | export | esfera | 1 | 20.60 | 20.60 | 20.60 | 0.00% | 0 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | gpu | esfera | 30 | 0.75 | 0.76 | 0.78 | 1.35% | 3 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | export | texto-3d | 1 | 47.30 | 47.30 | 47.30 | 0.00% | 0 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | gpu | texto-3d | 30 | 0.83 | 0.84 | 0.87 | 1.63% | 0 |

## Comparação entre primeiro e último run

| caso | baseline ms | atual ms | redução da mediana |
| --- | ---: | ---: | ---: |

> Comparação cruzada de núcleos: CPU inclui a geração da imagem;
> GPU mede apenas o shader sincronizado. A exportação aparece separada;
> esses números não representam a mesma latência end-to-end.

| coracao | 1223.94 | 0.78 | 99.9% |
| esfera | 1124.82 | 0.76 | 99.9% |
| texto-3d | 1214.70 | 0.84 | 99.9% |

## Portões de decisão

- Estabilidade (`CV ≤ 5.0%`): **aprovada**.
- Meta V2 (mediana < 500 ms e p95 < 650 ms): **aprovada**.
- Meta WebGL render-only (mediana < 100 ms): **aprovada**.
- Performance é válida apenas para o ambiente registrado acima.
