# Benchmarks

Pipeline reproduzível da engine. Os dados brutos são JSON Lines validados e os
relatórios Markdown são derivados; não edite métricas manualmente.

```bash
python -m benchmarks.run --engine v2 --suite canonical --repeat 10 \
  --power ac --workload dedicated --output benchmarks/data/baseline.jsonl
python -m benchmarks.report benchmarks/data/baseline.jsonl \
  --output benchmarks/reports/baseline.md
```

`run.py` recusa sobrescrever um dataset. Somente `baseline.jsonl`,
`optimized.jsonl` e `webgl.jsonl` são versionados. O schema não registra
hostname ou usuário.

O laboratório WebGL produz arquivos brutos no navegador. Eles só entram no
pipeline depois da validação e do enriquecimento com a linhagem do fork:

```bash
python -m benchmarks.import_webgl webgl-heart.jsonl webgl-text-3d.jsonl \
  webgl-sphere.jsonl --fork <stereogram-webgl-lab> \
  --output benchmarks/data/webgl.jsonl
```

Não crie `webgl.jsonl` sem medições reais. A sessão visual cega está documentada
em [`ab/README.md`](ab/README.md).

Os goldens iniciais são criados uma única vez com:

```bash
python -m benchmarks.goldens --write-initial
```

Depois disso, `python -m benchmarks.goldens` apenas verifica. Regenerar exige
novo ADR, bump de engine e invalidação consciente do cache.
