---
titulo: O cálculo
ordem: 5
resumo: A fórmula de separação estereoscópica — geometria simples que vira a alma do algoritmo.
fontes:
  - 'Thimbleby, H. W., Inglis, S., & Witten, I. H. (1994). Displaying 3D Images: Algorithms for SIRDS. <em>IEEE Computer</em>, 27(10), 38–48.'
---

> **Skeleton — a redigir.**
>
> ## 1. Variáveis do problema
> - E: distância entre olhos (em pixels)
> - D: distância observador-tela
> - z: profundidade normalizada [0, 1]
> - μ: depth-of-field (fração do D usada como range de profundidade)
>
> ## 2. Derivação da fórmula de separação
> ```
> sep(z) = round((1 - μz) · E / (2 - μz))
> ```
> - Triângulos semelhantes na geometria do olhar
> - Por que μ entra duas vezes
> - O que acontece quando z=0 (longe) e z=1 (perto)
>
> ## 3. Calibração de E
> - Tipicamente E = 2.5 polegadas × DPI ≈ 180-240px em tela
> - Por que valores maiores dificultam fusão
>
> ## 4. Calibração de μ
> - Tipicamente μ ≈ 1/3
> - Trade-off: mais profundidade vs. fusão mais difícil
>
> ## 5. Resolução de profundidade
> - Quantos níveis de z são distinguíveis na prática
> - Limite: sep(z) muda em incrementos inteiros (pixels)
>
> ## 6. Erros comuns
> - Usar fórmula linear (`shift = pattern_width * depth`) — achata o relevo
> - Não considerar geometria → relevo parece "disco em profundidade"
