# {{PROJECT_NAME}} — Design System

Design system extraído por **primia-design** em {{DATE}}.

## Fontes processadas

{{SOURCES_LIST}}

## O que tem aqui

```
{{PROJECT_SLUG}}/
├── README.md              ← este arquivo
├── decisions.md           ← cada decisão tomada e por quê
├── conflicts.md           ← divergências entre fontes (se houve)
├── tokens/
│   ├── design-tokens.json ← formato W3C, pra Style Dictionary etc.
│   ├── tokens.css         ← CSS variables, drop-in
│   ├── tokens.scss        ← SCSS variables + maps
│   ├── tailwind.config.js ← extend pro Tailwind
│   └── figma-tokens.json  ← Tokens Studio for Figma plugin
├── styleguide.html        ← visual completo, abre no navegador
├── components/            ← HTML/CSS dos componentes base
│   ├── button.html
│   ├── input.html
│   ├── card.html
│   ├── badge.html
│   ├── alert.html
│   └── typography.html
└── brand-assets/          ← logos e imagens extraídos (se houve)
```

## Como começar

**Pra revisar visualmente:** abra `styleguide.html` no navegador.

**Pra usar em projeto novo:**
- Tailwind: copie `tailwind.config.js` pra raiz do projeto
- Vanilla CSS: importe `tokens/tokens.css` no `<head>`
- SCSS: `@import` o `tokens/tokens.scss`

**Pra Figma:** instale o plugin "Tokens Studio" e importe `figma-tokens.json`.

## Hierarquia aplicada

{{HIERARCHY}}

Quando duas fontes discordaram, a fonte mais à esquerda venceu. Detalhes
em `decisions.md` e `conflicts.md`.

## Limites desta extração

- A skill **infere** a paleta semântica (success/warning/danger/info) baseado
  em hue. Quando não conseguiu inferir da fonte, usou defaults razoáveis
  (Tailwind). Veja `decisions.md` pra saber quais foram inferidos vs herdados.
- Os componentes em `components/` são HTML/CSS vanilla. Pra React/Vue/etc,
  use os tokens como base e implemente a sua biblioteca de componentes.
- A skill **não substitui** um designer. Use o resultado como **ponto de
  partida**, não como produto final. Revise antes de usar em produção.

## Próximos passos sugeridos

1. Revise `decisions.md` — discorda de algo? Edite os JSONs em `tokens/` e
   regenere o styleguide.
2. Resolva os conflitos listados em `conflicts.md` (se houver).
3. Compare `styleguide.html` com a marca/material original — algo ficou
   muito diferente?
4. Compartilhe com o time de dev e design pra alinhar antes de implementar.
