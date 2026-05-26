---
titulo: Do cálculo ao algoritmo
ordem: 6
glifo: ⌬
resumo: Look-back ingênuo vs. classes de equivalência (Thimbleby 1994) — incluindo o código real do gerador deste site.
fontes:
  - 'Thimbleby, H. W., Inglis, S., & Witten, I. H. (1994). Displaying 3D Images: Algorithms for SIRDS. <em>IEEE Computer</em>, 27(10), 38–48.'
  - 'Código-fonte deste site — <code>app/stereogram/generator.py</code>'
---

> **Skeleton — a redigir.**
>
> ## 1. O algoritmo ingênuo (look-back)
> - Pseudocódigo: para cada pixel, copia de x - pattern_width + shift
> - Por que parece funcionar à primeira vista
> - Pattern ringing: o artefato que aparece em bordas de objetos
>
> ## 2. A correção: classes de equivalência
> - Insight: pixels que devem ter mesma cor formam uma classe
> - Union-find por linha
> - Coloração right-to-left no final
>
> ## 3. Pseudocódigo verbatim (Thimbleby 1994)
> ```
> para cada y:
>     same[x] = x para todo x
>     para cada x:
>         sep = sep(z[y,x])
>         left = x - sep/2
>         right = left + sep
>         ...
> ```
>
> ## 4. O código real
> Reproduzir trecho relevante de `generator.py`, explicando linha a linha.
>
> ## 5. Texturas e qualidade percebida
> - Random dots: o clássico
> - Pink noise (1/f): por que é academicamente o melhor (link arXiv)
> - Padrões tileáveis: estilo "Magic Eye book"
>
> ## 6. Complexidade e performance
> - O(largura × altura × α), onde α é cadeia média de union-find
> - Python puro vs vetorização vs Numba
>
> ## 7. Extensões possíveis
> - Análise de oclusão (visibility test)
> - Estereogramas coloridos (Tyler-Clarke 1990)
> - Estereogramas animados
