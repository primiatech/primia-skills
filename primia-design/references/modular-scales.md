# Escalas modulares de tipografia

Tabela de referência das escalas modulares mais usadas em design systems.
O `analyze_typography.py` testa cada uma e escolhe a que melhor encaixa
nos tamanhos extraídos.

## As 8 escalas

| Nome | Ratio | Quando aparece | Sensação |
|---|---|---|---|
| Minor Second     | 1.067 | UIs muito densas, dashboards | Variação sutil, ritmo apertado |
| Major Second     | 1.125 | Bootstrap, UIs equilibradas | Variação suave, conservadora |
| Minor Third      | 1.200 | Material Design | Variação clara mas calma |
| Major Third      | 1.250 | Tailwind aproximado, web típica | Equilíbrio popular |
| Perfect Fourth   | 1.333 | Sites editoriais, blogs | Hierarquia evidente |
| Augmented Fourth | 1.414 | Landing pages | Forte mas controlada |
| Perfect Fifth    | 1.500 | Páginas de marketing | Hierarquia dramática |
| Golden Ratio     | 1.618 | Posters, hero sections | Máximo contraste |

## Como o algoritmo decide

Para cada escala candidata:
1. Define base = tamanho extraído mais próximo de 16px
2. Para cada tamanho extraído, calcula em qual "step" da escala ele cairia: `n = round(log(size/base) / log(ratio))`
3. Calcula o tamanho ideal nesse step: `ideal = base * ratio^n`
4. Soma o erro relativo: `|size - ideal| / size`

A escala com menor erro acumulado vence. Empate é raro — quando acontece,
escalas mais comuns (1.2, 1.25, 1.333) têm leve vantagem por serem
mais previsíveis pra dev.

## Mapeamento de steps pra nomes

```
step -2  →  xs   (12px se base=16)
step -1  →  sm   (14px)
step  0  →  md   (16px - base)
step +1  →  lg   (18-20px)
step +2  →  xl   (22-25px)
step +3  →  2xl  (24-32px)
step +4  →  3xl  (29-40px)
step +5  →  4xl  (36-50px)
step +6  →  5xl  (43-65px)
step +7  →  6xl  (51-85px)
```

Tamanhos fora dessa faixa recebem nome `step-N` (ex: `step-9`, `step--3`).

## Escalas observadas em design systems reais

- **Tailwind**: ratio inconstante (não segue uma escala única) — usa
  tamanhos pragmáticos: 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72, 96, 128.
- **Material Design 3**: usa categorias (display/headline/title/body/label)
  cada uma com 3 tamanhos. Aproxima 1.2.
- **Bootstrap**: ratio 1.25 (`$font-size-base * 1.25^n`).
- **IBM Carbon**: usa tipo "expressivo" com ratio ~1.2.
