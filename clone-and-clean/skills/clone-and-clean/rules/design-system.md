# Regra invinolável — extração de design system ANTES da reescrita clean

## Por que essa regra existe

Na primeira execução da skill (Cris Schumann ECR01), a reescrita clean ficou **"muito fora da realidade"** — visualmente divergente da original. Raiz: tratei "reescrita limpa" como licença pra redesenhar. Resultado: clean perdeu a identidade dark/roxo/vermelho e virou um genérico vermelho-sobre-branco.

A correção foi **extrair um design system do DOM real ANTES de escrever o clean/** e obrigar a reescrita a consumir esses tokens. Isso transformou a reescrita num ato de tradução (copiar tokens + estrutura) e não de criação (inventar identidade).

## Quando acionar

**Sempre**, entre o Passo 6 (`info.md`) e o Passo 7 (`clean/`). Não pule.

## Pipeline de extração (JS rodando no DOM da página original renderizada)

1. **`getComputedStyle(document.body)`** → family base, size, line-height, color, background
2. **Contagem das top-20 cores** em `getComputedStyle` de todos os elementos (`*`), por `color`, `backgroundColor`, `borderColor`. Ordenar por ocorrência.
3. **Contagem das top-5 font-family** em `h1,h2,h3,h4,h5,p,a,span,div,button`. Separar display (serif/Montserrat) vs body (sans/Inter/Manrope).
4. **Mapeamento bg por seção**: enumerar `section, .e-con, [class*="section"]` e extrair `backgroundColor`, `backgroundImage`, `backgroundSize`, `color`. Classificar cada uma como clima (dark/light/tonal).
5. **Headings**: para cada nível (h1..h3), coletar `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing` real.
6. **Border-radius**: enumerar valores distintos com contagem.
7. **Box-shadow**: enumerar valores distintos com contagem.
8. **Spacing**: coletar `padding` e `margin` das sections, detectar unidade base.

## Artefatos obrigatórios

### `design-system/design-system.json`

```json
{
  "$schema": "https://anthropic.com/cowork/design-tokens-v1",
  "meta": { "project": "...", "source": "URL", "extractedAt": "YYYY-MM-DD", "method": "..." },
  "brand": { "primary": { "value": "#HEX", "role": "CTA", "rgbCount": N }, ... },
  "neutral": { ... },
  "gradients": { ... },
  "typography": {
    "families": { "display": {...}, "primary": {...} },
    "scale": { "h1": {...}, "h2": {...}, "bodyLg": {...}, ... }
  },
  "radii": { "sm": "6px", "lg": "14px", "pill": "100px", ... },
  "spacing": { "section": "4rem", "gap": "2rem", ... },
  "shadows": { "card": "...", ... },
  "sections": [
    { "id": "hero", "bg": "bg-image + dark", "text": "white" },
    { "id": "descubra", "bg": "cream #F4EADB", "text": "text" },
    ...
  ],
  "components": {
    "btn-primary": { "bg": "primary", "borderRadius": "pill", "textTransform": "uppercase", ... },
    "card-dark": { ... },
    ...
  }
}
```

### `design-system/design-system.css`

- `:root` com todos os tokens como CSS variables (`--brand-primary`, `--color-text`, `--font-display`, `--radius-pill`, `--section-y`, …)
- Reset mínimo (box-sizing, margin, img responsivo)
- Tipografia (`h1..h3`, `p`, `.eyebrow`, `.handwritten`)
- Layout (`.container`, `section`, variants)
- Section theme helpers (`.bg-dark`, `.bg-cream`, `.bg-dark-2`, …) — um por clima identificado
- Componentes (`.btn-primary`, `.btn-ghost`, `.card`, `.vs-grid`, `.check-list`, `.no-list`, `.benefit`, `.marquee`, `.hero`, `.bio-grid`, `.quote`)
- Grid utilities (`.grid-2`, `.grid-3`)
- Media queries mobile pra grids (<768px)

### `design-system/README.md`

- Tabela de paleta real (token → hex → uso → ocorrências)
- Tabela de alternância de seções (ordem, bg, text, papel)
- Combo tipográfico (qual display + qual body, usage counts)
- Exemplo de HTML consumindo o sistema (1 por seção-tipo)
- Metodologia de extração (pipeline acima, replicável)
- Seção "Diferenças vs. outros clientes" comparando tokens — ajuda reutilização

## Regra de ouro da reescrita clean

Depois de extrair o design system:

- O `clean/index.html` **DEVE** linkar `assets/design-system.css` (copiado do design-system/)
- Toda cor, fonte, radius, spacing usado no clean **DEVE** vir de uma CSS variable do design system — **nunca valor hardcoded**
- Nome de classes semântico (`.bg-dark`, `.btn-primary`, `.benefit`, `.vs-col`) — reutilizar as canônicas do design-system.css
- Custom overrides só em `<style>` no `<head>` do clean, e só pra detalhes de posição/spacing específicos da página — nunca pra redefinir paleta, fonte ou raio
- **Respeitar a alternância de seções do array `sections` do JSON**: se a original tem 1 seção clara entre 5 escuras, o clean tem 1 seção clara entre 5 escuras. Mesma ordem. Mesma identidade.

## Validação

`verify.py` (Passo 8) deve checar:
- `clean/index.html` contém `href="assets/design-system.css"`
- Tokens esperados aparecem no HTML ou no CSS (`var(--brand-primary)`, `var(--font-display)`, `--color-green-darkest`, etc)
- Classes canônicas usadas (`.bg-dark`, `.btn-primary`, `.vs-grid`, `.marquee`, `.benefit`)
- **Zero valores hex hardcoded nas custom `<style>` inline** (só `var(--*)`)

## Reutilização cross-cliente

O `design-system/design-system.css` de um cliente é um **template de identidade** reutilizável. Pra clonar o layout mas trocar identidade, edite só os 7 tokens em `:root { --brand-* }` + os 2 tokens de `--font-*`. Toda a alternância de seções, componentes e spacing continua respeitada.

Exemplo: Cris Schumann (vermelho+preto+roxo) vs Camila Vieira (verde+cream) — ambos usam mesmo layout base (`.vs-grid`, `.benefit`, `.bg-dark`), só trocam 7 cores e 2 fontes.
