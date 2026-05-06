# Formatos de output

A skill gera 6 formatos. Cada um é determinístico — gerado pelo
`generate_outputs.py` (5 deles) e `generate_styleguide.py` (HTML visual).

## 1. design-tokens.json (W3C DTCG)

Padrão emergente do W3C Design Tokens Community Group. Suportado por
Style Dictionary e ferramentas modernas. Cada token tem `$value` e `$type`.

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "color": {
    "primary": {
      "500": { "$value": "#3b82f6", "$type": "color" }
    }
  },
  "typography": {
    "fontFamily": {
      "body": { "$value": "Inter, system-ui, sans-serif", "$type": "fontFamily" }
    }
  }
}
```

## 2. tokens.css (CSS Variables)

Pra projetos vanilla ou que querem usar CSS custom properties direto.

```css
:root {
  --color-primary-500: #3b82f6;
  --font-body: "Inter", system-ui, sans-serif;
  --space-4: 16px;
  --radius-md: 8px;
}
```

## 3. tokens.scss (SCSS Variables)

Pra projetos SCSS. Inclui também maps SCSS pra cada escala (útil pra `@each`).

```scss
$color-primary-500: #3b82f6;

// Map pra iteração
$color-primary: ("50": #eff6ff, "500": #3b82f6, "900": #1e3a8a);
```

## 4. tailwind.config.js

Extend do theme do Tailwind. Drop-in.

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {"50": "#eff6ff", "500": "#3b82f6", ...}
      },
      fontFamily: {
        body: ["Inter", "system-ui", "sans-serif"]
      }
    }
  }
}
```

## 5. figma-tokens.json (Tokens Studio)

Formato do plugin Tokens Studio for Figma. Permite que o designer
importe os tokens direto no Figma.

```json
{
  "global": {
    "colors": {
      "primary": {
        "500": { "value": "#3b82f6", "type": "color" }
      }
    }
  },
  "$themes": [],
  "$metadata": { "tokenSetOrder": ["global"] }
}
```

## 6. styleguide.html

Página HTML autocontida (CSS inline, fontes via Google Fonts quando
disponível) mostrando visualmente todos os tokens + componentes base
em uso. É o que o cliente revisa.

Não tem schema — é apresentação. Deve ter as seções:
- Cores (swatches por escala)
- Tipografia (famílias + escala de tamanhos + pesos)
- Spacing (barras visuais)
- Radius (formas com cada radius)
- Shadows (cards com cada shadow)
- Contraste (tabela WCAG com pares relevantes)
- Componentes (button/input/card/badge/alert/typography)

## Compatibilidade entre formatos

Todos os formatos derivam dos mesmos arquivos intermediários
(`colors.json`, `typography.json`, `spacing.json`). Modificar um deles e
regenerar mantém os 6 outputs sincronizados.
