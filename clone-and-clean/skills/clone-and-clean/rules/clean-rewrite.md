# Regras para o artefato `clean/` (reescrita semântica)

O `clean/` é **a reescrita do zero** — a intenção é virar a **base real** que o usuário vai clonar pra cada novo lançamento. Fidelidade visual ~95%, mas estrutura HTML e performance devem ser significativamente melhores que o original.

## Princípios

1. **HTML semântico primeiro.** `<section>`, `<article>`, `<aside>`, `<figure>`, `<details>`, `<time>` — usar onde couber.
2. **CSS puro, zero framework.** Variáveis CSS (`--brand-red: #BC0000`) pra paleta. Grid/flexbox nativo. Sem Tailwind compilado nem Bootstrap.
3. **Zero JS framework.** Sem React, Vue, jQuery. JS inline mínimo (só pra countdown, idealmente).
4. **Zero Elementor, Swiper, Lottie, Beaver, Divi.** Se houver carrossel, usa CSS scroll-snap nativo ou substitui por grid.
5. **Só 2 fontes web.** Sempre a principal de body + a principal de headings, com `font-display: swap`. Nada de 7 variações.
6. **Imagens `loading="lazy"` em tudo abaixo da dobra.** Só `eager` no hero.
7. **Responsivo fluid com `clamp()`**. Evitar media queries extremas — usar `clamp(min, preferred, max)` pra tipografia e espaçamento.
8. **Mantém pixels originais.** Regra idêntica à do deploy-ready (ver `rules/deploy-ready.md`).

## Estrutura CSS do clean

Sempre gerar um bloco `<style>` inline (não arquivo externo, evita request bloqueante) com esta ordem:

```css
/* 1. Font-face */
/* 2. :root com variáveis de paleta */
/* 3. Reset mínimo (html, body, tipografia base) */
/* 4. Container + utilidades de layout (.container, .container-narrow) */
/* 5. Componentes reutilizáveis (.btn-primary, .card, .testimonial, .faq, ...) */
/* 6. Seções específicas (.hero, .marquee, .vs-grid, .gallery, .schedule, .buy-box, .guarantee, .bio-grid) */
/* 7. Footer + utilidades gerais (.text-center, .mt-4) */
```

## Componentes canônicos

Sempre reutilizar os mesmos nomes de classe pros mesmos papéis — isso faz o pacote virar template fácil de clonar:

| Componente | Classe | Uso |
|---|---|---|
| CTA principal | `.btn-primary` | Botão vermelho arredondado, Montserrat bold uppercase |
| Card genérico | `.card` | Fundo branco (ou translúcido em section.dark), borda sutil, hover lift |
| Seção escura | `section.dark` | Bg preto, texto branco, cards translúcidos |
| Seção cinza | `section.gray` | Bg #F5F5F5, para alternar ritmo visual |
| Seção vermelha | `section.red` | Bg da marca, pra CTAs de alto impacto |
| Grid de 3 colunas | `.cards-3` | Layout padrão de benefícios/features |
| Grid de 2 colunas | `.content-grid` | Listas de módulos/conteúdo programático |
| Grid de galeria | `.gallery` | Resultados, prints de depoimentos |
| FAQ | `.faq > details > summary` | Zero JS, nativo |
| Depoimentos | `.testimonials > .testimonial` | Foto + nome + @ + texto |
| Comparação dois lados | `.vs-grid` | Generalista × Especialista, Antes × Depois |
| Cronograma | `.schedule > .schedule-row` | Lista de horários |
| Box de compra | `.buy-box` | Bloco destacado com preço + CTA |
| Countdown topbar | `.topbar > .countdown > span` | Sticky topo, JS mínimo |
| WhatsApp float | `.wa-float` | Botão fixo bottom-right |

## Correções automáticas silenciosas

Aplicar automaticamente durante a reescrita e listar em `clean/CHANGES.md` com justificativa. Categorias típicas:

### Acessibilidade
- `<img>` sem `alt` → adicionar alt descritivo ou `alt=""` se decorativo
- `<button>` sem texto acessível → adicionar `aria-label`
- Heading order quebrado (h3 vindo antes de h2) → ajustar
- Contraste insuficiente de texto → aumentar
- Links externos sem `rel="noopener"` → adicionar

### Performance
- `<img>` sem `loading` abaixo da dobra → `loading="lazy"`
- `<img>` sem `width`/`height` → adicionar (previne CLS)
- Fonts sem `font-display: swap` → adicionar
- CSS externo → inline (um request a menos)

### Semântica
- `<div>` com role de landmark → substituir por `<section>`, `<main>`, `<aside>`
- FAQ com JS custom → substituir por `<details>`/`<summary>`
- Navegação em `<ul>` → envolver em `<nav>`
- Datas como texto → usar `<time>`

### Normalização visual
- Padding/margin com valores estranhos (13.7px, 47.2px) → arredondar pra múltiplos de 4 ou 8
- Cores quase-iguais (#111, #101010, #121212) → consolidar na variável `--brand-dark`
- Font-sizes em pixel hardcoded → `clamp(min, pref, max)` ou rem
- Border-radius inconsistente → padronizar (4 valores: sm, md, lg, pill)

### Trocas padronizadas
- WhatsApp → `TODO_WHATSAPP_NUMBER` (igual deploy-ready)
- Canonical → `href="#" data-todo`

## Fontes — escolha padrão

Se o original usa várias fontes, escolher **só 2** baseado em:
- Fonte de body: a mais usada em parágrafos (`getComputedStyle` de `body` e `p`)
- Fonte de headings: a mais usada em h1/h2/h3

Exemplo típico: Manrope (body) + Montserrat (headings). Copiar só esses 2 arquivos woff2 pra `clean/fonts/`.

## Paleta

Extrair top-10 cores mais usadas via `getComputedStyle` na original. Nomear:
- `--brand-dark` — cor de texto principal
- `--brand-red` (ou outra principal) — cor da marca
- `--brand-gray-900/700/500/300/100` — escala de cinzas
- `--brand-accent` — cor secundária (se existir)

Exportar em `clean/CHANGES.md` o mapeamento.

## JS permitido

- **Countdown:** inline, ~30 linhas, vanilla JS, usa `Date.parse` na data-alvo
- **Scroll smooth:** nativo via `html { scroll-behavior: smooth; }`
- **FAQ toggle:** nativo via `<details>`
- **Tabs/carrossel:** se absolutamente necessário, CSS-only (scroll-snap + anchors)

**Evitar a todo custo:**
- jQuery
- Swiper, Slick, Owl, Glide, Splide
- Lottie (substituir por imagem estática ou CSS animation se for simples)
- GSAP (usar `@keyframes` nativo)

## Validação obrigatória

Rodar `scripts/verify.py` contra `clean/`:
- 100% dos paths `src`/`href` locais resolvem em disco
- 100% dos pixels originais estão mantidos
- TODOs marcados e listados no README
- Sem referências ao domínio original (exceto feeds RSS e URLs de pixels hospedados no Google/Meta)

## Testar visualmente

Rodar servidor HTTP local e tirar screenshot full-page. Comparar com o screenshot do original. Se divergência > 20% em alguma seção, revisar.
