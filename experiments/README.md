# Experimentos da Engine V2

Esta pasta contém spikes reproduzíveis que ainda não fazem parte do pipeline de
marcos em `benchmarks/`.

## Núcleo Cython

`benchmark_cython_core_v2.py` compara, no mesmo processo e em ordem alternada:

1. V2 Python;
2. vínculos e pintura em Cython;
3. vínculos, pintura e visibilidade em Cython.

Ele também exige igualdade RGB nos seis goldens, em 48 combinações de
parâmetros e em três resoluções adicionais. `profile_cython_core_v2.py` perfila
a última variante.

Exemplo em Linux/WSL com Cython, NumPy, Pillow e Pydantic instalados:

```bash
CYTHON_BUILD_DIR=/tmp/estereograma-cython-build \
python experiments/benchmark_cython_core_v2.py \
  --warmup 3 --repeat 15 --output /tmp/cython-core-v2.json
```

Resultados exploratórios não são commitados. O marco oficial
`benchmarks/data/compiled.jsonl` só deve ser coletado depois de o núcleo existir
em um commit limpo.
