---
name: clone-and-clean
description: Clona páginas de vendas/lançamentos (HTML+CSS+JS+imagens) e gera três artefatos — captura fiel (deploy-ready), estrutura + copy extraídos, e uma versão reescrita em HTML semântico limpo (clean/) pronta pra virar base de novos lançamentos. Use quando o usuário quer "clonar uma página", "baixar uma landing page", "fazer scraping de uma página de vendas", "extrair copy de lançamento", "reusar estrutura de lançamento", "criar base de inspiração de infoprodutos" ou "gerar template de uma página concorrente".
---

# clone-and-clean — pipeline para clonar, limpar e reescrever páginas de lançamento

## O que essa skill faz

Recebe uma URL (geralmente WordPress + Elementor, mas funciona em qualquer site) e entrega **três artefatos** organizados por cliente:

1. **`deploy-ready/`** — cópia fiel da página original, 100% self-contained, pronta pra subir na Vercel/Netlify sem depender do servidor original
2. **`info.md` + `copy.md`** — metadados (pixels, stack, URL, data) e copy da página extraído seção por seção em markdown
3. **`clean/`** — versão **reescrita em HTML semântico + CSS puro com variáveis**, zero Elementor/jQuery/Swiper, mantendo copy, imagens e pixels. É a base real pra novos lançamentos.

## Quando usar essa skill

Gatilhos explícitos:
- "clone essa página"
- "baixa essa landing pra minha biblioteca"
- "quero a estrutura dessa página de vendas"
- "extrai o copy desse lançamento"
- "gera uma versão limpa dessa página"
- URL de página de vendas/captura/obrigado + contexto de "cliente" ou "inspiração"

Quando NÃO usar:
- Páginas que exigem login
- Aplicações SPA complexas (React/Vue/Angular com roteamento) — pipeline foi projetado pra páginas estáticas de lançamento
- Conteúdo protegido por copyright além do nível de template (não reproduzir textos longos de terceiros sem permissão)

## Pré-requisitos

- Ambiente: Claude Code rodando em um projeto com acesso a shell (bash) e Python 3
- Extensão **Claude in Chrome** instalada (usada pra baixar HTML renderizado, capturar screenshots full-page e inspecionar assets dinâmicos)
- Pasta de destino definida: `clientes/{nome-do-cliente}/{nicho}/{tipo-lancamento}/{slug}` ou `inspiracoes/{nicho}/{slug}`

## Fluxo de trabalho (o que o Claude DEVE fazer ao acionar essa skill)

### Passo 1 — Coletar inputs do usuário

Pergunte sempre (se não vier pronto):
- URL da página
- É cliente ou inspiração?
- Se cliente: nome, nicho, tipo de lançamento (ingresso-pago, captura, obrigado, vendas-evergreen, etc.)
- Se inspiração: nicho
- Slug da página (nome da pasta)

### Passo 2 — Capturar a página com Claude in Chrome

Use a extensão pra:
1. Navegar na URL
2. Fazer scroll até o fim (pra forçar carregar imagens lazy)
3. Extrair HTML renderizado completo (`document.documentElement.outerHTML`)
4. Capturar screenshot full-page via html2canvas
5. Listar **todos** os recursos carregados com `performance.getEntriesByType('resource')`
6. Identificar pixels/trackers (Meta, GTM, GA4, Google Ads, Clarity, LeadTracker, Hotjar, PixelYourSite)

**Transferência via JSZip:** como o bridge do Chrome tem limites de tamanho, sempre empacote HTML+assets+screenshot em um ZIP disparado como download (usar `JSZip.generateAsync({type:'blob'})` + blob URL + click anchor). Ver `scripts/browser-capture.js`.

### Passo 3 — Processar o ZIP no filesystem local

Rode `scripts/process-capture.py` passando o ZIP baixado. Ele:
- Descompacta em pasta temporária
- Baixa assets faltantes via `curl`/`wget`
- Reescreve todos os `url()` dos CSS pra paths locais
- Reescreve `src/href` do HTML pra paths locais
- Gera `manifest.json` com mapa url-original → arquivo-local

### Passo 4 — Produzir o artefato `deploy-ready/`

Aplica transformações listadas em `rules/deploy-ready.md`:
- Troca WhatsApp por `TODO_WHATSAPP_NUMBER`
- Comenta APIs dinâmicas de terceiros (progress bars, etc) com `<!-- TODO: reconfigurar endpoint -->`
- Troca canonical URL por `href="#" data-todo`
- Remove `wp-json`, `xmlrpc`, `wlwmanifest`, `speculationrules`
- **Mantém pixels originais** (esse é o padrão — ver rules)

### Passo 5 — Extrair copy em `copy.md`

Rode `scripts/extract-copy.py` que percorre o DOM e gera markdown por seção:
- Barra de urgência
- Hero (headline + sub + CTA + oferta)
- Marquee
- Seções numeradas com headings + parágrafos + bullets + iconboxes + toggles
- Cases/depoimentos
- FAQ (pergunta → resposta)
- Footer

### Passo 6 — Gerar `info.md`

Template em `templates/info.md`. Preencher com:
- Metadados do cliente/página
- URL original, data de captura
- Stack detectado (WP, Elementor, OMGF, plugins)
- Pixels/IDs identificados (com aviso de troca antes de publicar)
- Estrutura (ordem das seções)
- Notas especiais (ex: "vendas encerradas no momento da captura")

### Passo 6.5 — Extrair `design-system/` (**obrigatório antes do clean**)

**Regra dura — não pule.** Antes de reescrever a clean, rode `scripts/extract-design-system.js` dentro do DOM real da página original via Claude in Chrome. Gera três artefatos em `design-system/`:

- `design-system.json` — tokens machine-readable (brand, neutral, typography, radii, spacing, shadows, sections, components) com contagens reais no DOM
- `design-system.css` — `:root` com CSS variables + componentes canônicos (`.btn-primary`, `.card-dark`, `.vs-grid`, `.marquee`, etc) usando só as variáveis
- `README.md` — tabela de paleta, alternância de seções, combo tipográfico, exemplos, metodologia

**Regra crítica (aprendido na dor):** Na primeira execução (Cris Schumann), reescrevi o clean sem extrair design system antes → ficou "muito fora da realidade" (identidade visual divergente). A extração prévia força a reescrita a ser **tradução** e não criação. Ver `rules/design-system.md` pros detalhes.

### Passo 7 — Gerar `clean/` (reescrita semântica)

**Este é o diferencial da skill.** Ao invés de copiar o Elementor inchado, reescreve do zero **consumindo o design system do Passo 6.5**:

- HTML5 semântico (`<section>`, `<article>`, `<figure>`, `<details>` pra FAQ)
- **Link direto pro `design-system.css`** copiado em `clean/assets/` (zero valores hex hardcoded no clean)
- **Respeita a alternância de seções** do array `sections` do `design-system.json` — mesma ordem, mesma identidade (dark→marquee→dark→cream→dark→footer, etc)
- CSS customizado só em `<style>` no `<head>` pra detalhes específicos de página (spacing/posicionamento) — **nunca** pra redefinir paleta ou fonte
- Fontes **só** as 2 principais detectadas no design-system (tipicamente display + body)
- Zero jQuery, Swiper, Lottie, Elementor runtime
- JS inline mínimo (só countdown, FAQ toggle é nativo com `<details>`)
- Imagens com `loading="lazy"` abaixo da dobra
- `font-display: swap` em todas as fontes
- Design tokens completos extraídos via `scripts/extract-design-system.js` no Passo 6.5 (paleta, fontes, radii, spacing, sections). `extract-palette.js` é fallback mais simples pra casos de extração parcial.
- Componentes padronizados com classes semânticas (`.card`, `.btn-primary`, `.testimonial`, `.faq`, `.vs-grid`, etc — ver `templates/clean-base.html`)

**Correções automáticas silenciosas** (documentar em `clean/CHANGES.md`):
- Adicionar `alt=""` em imagens decorativas sem alt
- Adicionar `loading="lazy"` em imgs abaixo da dobra
- Corrigir hierarquia de headings (h1 único, h2 pras seções)
- Adicionar `aria-*` em componentes interativos
- Normalizar padding/margin pra valores redondos
- `<details>` nativo substitui JS de toggle

### Passo 7.5 — Loop de revisão visual seção a seção (**obrigatório**)

**Regra dura — não pule.** Depois de escrever cada seção do `clean/index.html`, comparar lado-a-lado com a seção correspondente na original **antes** de avançar para a próxima.

Para cada seção, checar:
- [ ] Alinhamento de texto (esquerda/centro/direita) idêntico ao original
- [ ] Logo presente onde o original tem logo (header/hero/footer)
- [ ] Estrutura de grid/colunas igual (2×2 continua 2×2, 2-col continua 2-col)
- [ ] Imagens intermediárias preservadas (modelos, mockups, ilustrações entre cards)
- [ ] Ornamentos/divisores/ícones no mesmo lugar e no mesmo estilo
- [ ] Tipo de ícone correto (check circulado ≠ número ≠ emoji ≠ SVG)
- [ ] Proporção de fotos igual (paisagem grande continua grande)
- [ ] Hero com asset único integrado → `background-image` da seção (não separar em colunas)
- [ ] Painel cream contínuo com pessoa sobreposta → `.vs-panel` com imagem `position: absolute` transbordando
- [ ] Form popup/modal no original → modal no clean (não inline)
- [ ] Zero emojis nativos (substituir por SVG inline com `stroke="currentColor"`)

**Regra crítica (aprendido na dor):** Na segunda execução da skill (Camila Vieira Posicione-se, 2026-04) quebrei 6 dessas checagens simultaneamente — hero centralizou, logo sumiu, grid virou card, fotos de modelos sumiram, thumbnail no lugar de paisagem, inline no lugar de modal. Hoberdan pediu reescrita completa.

Ver `rules/fidelidade-visual.md` com as 10 regras consolidadas.

### Passo 8 — Validar

Rode `scripts/verify.py` na pasta `clean/`:
- Todos os paths `src`/`href` locais existem em disco
- Todos os pixels originais estão mantidos
- TODOs estão marcados e documentados
- Sem referências remanescentes ao domínio original
- Assets visuais críticos presentes (logo, bg-hero integrado se aplicável)
- Zero valores hex hardcoded em `<style>` inline (só `var(--*)`)

### Passo 9 — Empacotar e entregar

Gerar três ZIPs em `downloads/`:
- `{slug}-deploy-ready.zip`
- `{slug}-clean.zip`
- `{slug}-FULL.zip` (raw HTML+CSS+JS+imagens original, pra consulta de referência)

Entregar links `computer://` pros ZIPs e pro `clean/index.html` pra teste direto.

## Regras invioláveis (carregar sempre)

Antes de executar, o Claude DEVE ler:
- `rules/deploy-ready.md` — o que acontece com pixels, WhatsApp, APIs dinâmicas, CSS/fonts
- `rules/design-system.md` — **extração de tokens ANTES da reescrita, senão o clean fica fora da realidade**
- `rules/fidelidade-visual.md` — **as 10 regras de fidelidade visual (alinhamento, logo, grid, modal, hero integrado, painel cream, ícones SVG) — clean é tradução, não redesign**
- `rules/clean-rewrite.md` — princípios da reescrita semântica
- `rules/copyright.md` — limites de copy que pode ser reproduzido

## Outputs esperados

```
clientes/{cliente}/{nicho}/{tipo}/{slug}/
├── index.html              ← HTML renderizado completo (raw)
├── assets/                 ← CSS, JS, fontes (raw)
├── images/                 ← Todas as imagens
├── deploy-ready/           ← Captura 1:1 self-contained
│   ├── index.html
│   ├── assets/
│   ├── images/
│   ├── README.md
│   └── info.md
├── design-system/          ← 🆕 Tokens extraídos do DOM real (obrigatório antes do clean)
│   ├── design-system.json  ← fonte de verdade machine-readable
│   ├── design-system.css   ← :root CSS variables + componentes canônicos
│   └── README.md           ← tabela de paleta, metodologia, exemplos
├── clean/                  ← Versão reescrita em HTML semântico
│   ├── index.html
│   ├── assets/
│   │   └── design-system.css  ← cópia/link do design-system/
│   ├── images/
│   ├── fonts/
│   ├── CHANGES.md          ← correções silenciosas aplicadas
│   └── README.md           ← instruções de deploy e checklist
├── copy.md                 ← Copy extraído seção por seção
├── info.md                 ← Metadados da captura
├── verify.py               ← validação: copy compliance + tokens + images + zero WP refs
├── screenshot-fullpage.jpg
└── downloads/
    ├── {slug}-deploy-ready.zip
    ├── {slug}-clean.zip
    └── {slug}-FULL.zip
```

## Exemplo de uso

**Usuário:** "Baixa `https://crisschumann.com/imersao-ecr01/` como cliente Cris, nicho psicologia, tipo ingresso-pago, slug imersao-ecr01"

**Claude:** [aciona skill clone-and-clean]
1. Abre a URL no Chrome via extensão
2. Scroll até o fim (força lazy-load)
3. Captura HTML + screenshot + lista de recursos
4. Descompacta no filesystem
5. Gera deploy-ready, copy.md, info.md, clean/
6. Valida e zipa
7. Entrega 3 links de ZIP + `computer://` pro `clean/index.html`

Ver `examples/cris-schumann/` pra caso real completo.

## Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Imagens faltando na galeria | Lightbox Elementor com lazy-load agressivo | Antes de extrair, rodar `[...document.querySelectorAll('img[data-src]')].forEach(i => i.src = i.dataset.src)` |
| CSS com `url()` quebrado | Paths relativos resolvidos errado pelo rewriter | Conferir `manifest.urlMap` — rodar `scripts/rewrite-css.py --verbose` |
| Página carrega lenta mesmo em produção | Pixels originais disparando | Normal — trocar IDs pelos do cliente novo desativa tracking indevido e libera o browser |
| `<details>` não abre no Safari antigo | Navegador ancestral (iOS < 15) | Suporte nativo é >97% do tráfego global — ignorar. Se o cliente tiver base legada relevante, importar polyfill de terceiros via CDN (ex: `details-element-polyfill`) |

## Evolução desta skill

Esta skill foi inicialmente calibrada com a página da Cris Schumann (WordPress + Elementor Pro + OMGF + PixelYourSite). Cada nova página processada deve:
1. Se surgir padrão novo (ex: plugin de countdown diferente, novo tipo de widget), adicionar caso em `scripts/` e documentar em `rules/`
2. Se surgir bug, adicionar linha no troubleshooting acima
3. Manter `examples/` atualizado com pelo menos 1 caso de cada nicho principal (psicologia, emagrecimento, educação, etc)
