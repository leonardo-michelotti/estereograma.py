# Protocolo A/B cego

Cada sessão compara coração, texto e esfera sem revelar a engine. Avalie:

1. facilidade de fusão;
2. clareza da profundidade;
3. presença de ecos, faixas ou artefatos.

Faça duas sessões em dias diferentes, a 100% de zoom e na mesma tela. A ordem e
os lados são derivados do identificador da sessão; o mapa privado não é aberto
até as respostas estarem registradas.

```bash
python -m benchmarks.ab_gallery --webgl-dir <downloads> --session dia-1 \
  --output benchmarks/sessions/dia-1.html \
  --mapping benchmarks/sessions/private/dia-1.json
```

O WebGL só pode virar preview se tiver mediana abaixo de 100 ms e não perder em
nenhum dos três critérios para coração, texto ou esfera.
