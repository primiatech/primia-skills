# Componentes base

A skill entrega 6 arquivos HTML em `components/` mostrando os tokens em uso.
São snippets standalone, copy-paste — não dependem de framework.

## O que cada componente cobre

### button.html
Botão é o componente mais visível. Cobre:
- 4 variantes: primary, secondary, ghost, danger
- 3 tamanhos: sm, md (default), lg
- Estado disabled
- Estados de hover, focus, active

Tokens consumidos: `color.primary.*`, `color.neutral.*`, `color.danger.*`,
`radius.md`, `text.md/sm/lg`, `font.body`.

### input.html
Inputs textuais. Cobre:
- `<input type="text">` padrão
- `<textarea>`
- Estado de erro (`.input-error`)
- Estado disabled
- Wrapper `.field` com label + help text + error message

Tokens: `color.neutral.*`, `color.primary.500/100`, `color.danger.500/100/600`,
`radius.md`, `text.md/sm`, `font.body`.

### card.html
Container pra agrupar conteúdo. Cobre:
- Card padrão (border + shadow.sm)
- Card elevado (shadow.lg)
- Card flat (sem shadow)
- Footer com ações

Tokens: `color.white`, `color.neutral.*`, `radius.lg`, `shadow.sm/lg`,
`text.lg`, `font.display/body`.

### badge.html
Tags inline pra status. Cobre:
- 6 cores semânticas: primary, success, warning, danger, info, neutral
- 2 estilos: padrão (subtle) e solid

Tokens: `color.{slot}.100/700` (subtle) e `color.{slot}.500` (solid),
`radius.full`, `text.sm`.

### alert.html
Bloco de mensagem prominente. Cobre:
- 4 variantes: info, success, warning, danger
- Estrutura com ícone + título + corpo

Tokens: `color.{slot}.50/500/900`, `radius.md`, `text.md`.

### typography.html
Demonstração da escala tipográfica. Cobre:
- h1 a h6 (`text.6xl` a `text.lg`)
- Body text (`text.md`)
- Small text (`text.sm`)
- Link inline
- `<code>` inline
- Blockquote

Tokens: toda a família `text.*`, `font.display/body/mono`, `color.primary.*`,
`color.neutral.*`, `radius.sm`.

## Por que esse conjunto

Esses 6 componentes juntos exercitam 100% dos tokens gerados. Se o
designer mudar uma cor primary ou um tamanho de fonte, o impacto fica
visível imediatamente em pelo menos um componente. Servem tanto como:
- **Documentação viva** dos tokens (cliente vê o token em uso)
- **Smoke test** dos tokens (se algum estiver com valor inválido, quebra aqui)
- **Boilerplate** pro time de dev começar a montar a UI real

## Limites

A skill **não** gera:
- Componentes de framework (React/Vue/Svelte) — só HTML/CSS vanilla
- Componentes complexos: tabs, accordion, dropdown, modal, tooltip,
  date picker, autocomplete, etc.
- Ícones (depende de licença/biblioteca)
- Variações de estado completas (loading, skeleton, empty state)

Se o cliente precisar de uma biblioteca de componentes completa, esses
6 servem de ponto de partida — não de produto final.
