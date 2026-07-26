# Relatório de benchmark da engine

> Gerado automaticamente a partir dos dados JSONL validados.

## Linhagem

| run_id | Git SHA | fonte | ambiente |
| --- | --- | --- | --- |
| `webgl-20260726T014002Z-274293c9` | `274293c9f674` | `46e054a4299d` | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36, Windows, AMD64, 16 CPUs lógicas |

## Resultados

| run_id | engine | tipo | caso | n | mín. ms | mediana ms | p95 ms | CV | outliers |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | export | coracao | 1 | 27.20 | 27.20 | 27.20 | 0.00% | 0 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | gpu | coracao | 30 | 0.76 | 0.78 | 0.80 | 1.41% | 2 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | export | esfera | 1 | 20.60 | 20.60 | 20.60 | 0.00% | 0 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | gpu | esfera | 30 | 0.75 | 0.76 | 0.78 | 1.35% | 3 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | export | texto-3d | 1 | 47.30 | 47.30 | 47.30 | 0.00% | 0 |
| `webgl-20260726T014002Z-274293c9` | webgl 274293c9f674 | gpu | texto-3d | 30 | 0.83 | 0.84 | 0.87 | 1.63% | 0 |

## Portões de decisão

- Estabilidade (`CV ≤ 5.0%`): **aprovada**.
- Meta V2 (mediana < 500 ms e p95 < 650 ms): **não aplicável**.
- Meta WebGL render-only (mediana < 100 ms): **aprovada**.
- Performance é válida apenas para o ambiente registrado acima.
