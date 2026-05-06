# Convenções de nomenclatura de tokens

Este arquivo é referência pra Claude consultar quando estiver decidindo
nomes de tokens. Não é checklist obrigatório — é o padrão que a skill segue
pra ficar consistente.

## Princípios gerais

1. **Semântico antes de visual.** `primary.500` é melhor que `blue.500`.
   A marca pode mudar de azul pra verde sem quebrar consumidores.
2. **Escala numérica 50-900.** Convenção do Tailwind/Material. Mais granular
   que `light/medium/dark`, mais previsível pra dev.
3. **Step 500 é a cor base.** Mesmo quando a cor original extraída
   tem lightness diferente, ela é atribuída ao step com lightness mais
   próximo do alvo — não forçada a ser 500.
4. **Slots semânticos previsíveis.** `success`, `warning`, `danger`, `info`
   sempre existem. Quando não conseguimos inferir da fonte, usamos defaults
   (Tailwind).

## Cores

```
color.primary.50      // fundo muito claro, hover sutil
color.primary.100     // fundo de badge/alert
color.primary.200..400 // estados intermediários
color.primary.500     // base — botões, links, destaques
color.primary.600     // hover de botões primary
color.primary.700     // active, texto sobre primary.50
color.primary.800..900 // texto principal sobre fundo claro
color.primary.950     // raramente usado, contraste extremo
```

Slots especiais:
- `neutral` — escala completa de cinzas. Quase todo texto e fundo usa essa.
- `primary` — cor da marca. Botões, links, foco.
- `success`, `warning`, `danger`, `info` — estados.
- `accent` (opcional) — cor secundária pra contraste/criatividade.
- `white`, `black` — absolutos, sem escala.

## Tipografia

```
font.body       // família principal pra parágrafos
font.display    // família pra headings (pode ser igual a body)
font.mono       // monoespaçada pra código
text.xs..6xl    // escala de tamanhos
weight.400..700 // pesos disponíveis
```

A escala xs/sm/md/lg/xl segue:
- `md` é a base (geralmente 16px)
- `xs/sm` abaixo, `lg/xl/2xl/...` acima
- Quando a escala extraída tem mais steps que `xs..6xl`, usamos `step-N`

## Spacing

Escala em múltiplos de 4 ou 8 (decidido por menor erro de fit). Nomes:
```
space.0      // 0px
space.0_5    // 2px (snake-case porque CSS não aceita ponto)
space.1      // 4px
space.2      // 8px
space.3      // 12px
space.4      // 16px (base)
space.6      // 24px
space.8      // 32px
space.12     // 48px
...
```

## Radius

```
radius.none  // 0
radius.sm    // 2-4px
radius.md    // 6-8px (default da maioria dos elementos)
radius.lg    // 10-16px (cards)
radius.xl    // 20-24px
radius.2xl   // 28-32px
radius.full  // 9999px (pills, avatars)
```

## Shadows

```
shadow.sm    // sombra sutil — borders subtituídos
shadow.md    // sombra padrão de cards
shadow.lg    // sombra de elementos elevados (modals, dropdowns)
shadow.xl    // sombra de elementos flutuantes
```

## O que NÃO fazer

- ❌ Nomes hardcoded de cor: `color.azul-claro`, `color.cinza-escuro`
- ❌ Nomes de marca dentro do token: `color.cliente-acme.primary`
- ❌ Espaços ou caracteres especiais em chaves: `color.primary 500`
- ❌ Misturar units: alguns tokens em px e outros em rem no mesmo arquivo
- ❌ Steps "estranhos": usar 350, 450 fora de motivo (mantenha 50/100/200/.../900)
