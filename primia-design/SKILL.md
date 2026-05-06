---
name: primia-design
version: 1.1.0
author: Primia
created: 2026-05-05
updated: 2026-05-06
audience: Alunos da Mentoria Primia + uso geral em Claude.ai. Roda em sandbox Claude.ai e em Claude Code local (Windows/Mac/Linux).
description: Gera um design system completo (tokens, style guide visual e componentes prontos) a partir de qualquer combinação de imagens, PDFs ou URLs de referência. Use SEMPRE que o usuário pedir em linguagem natural pra "fazer/criar/montar um design system", "extrair tokens/paleta/cores", "tirar a identidade visual", "criar style guide", "espelhar/replicar essa marca", "pegar a paleta desse site", "transformar esse manual em tokens", "fazer um design system baseado nisso", ou simplesmente anexar um PDF/imagem/URL e pedir pra "transformar em design system" / "tirar as cores e fontes" / "criar um manual visual baseado nisso". Aceita múltiplas fontes simultâneas (ex: PDF de manual de marca + URL do site + imagem do logo) e funde tudo aplicando hierarquia configurável. Entrega 6 formatos de output (W3C tokens JSON, CSS variables, SCSS, Tailwind config, Figma Tokens, styleguide HTML visual) + 6 componentes base HTML/CSS prontos (button, input, card, badge, alert, typography) + relatório de decisões + relatório de conflitos. Sempre roda autonomamente — nunca pergunta hierarquia, usa default silencioso PDF > URL > Imagem se o usuário não declarar.
---

# Primia Design

Cria um design system completo (tokens + style guide visual + componentes
base) a partir de qualquer combinação de imagens, PDFs ou URLs de referência.

## Quando usar

Acione esta skill sempre que o usuário pedir pra:

- **Extrair design tokens** de uma fonte: site, PDF de manual de marca,
  imagem com logo/paleta, screenshot
- **Criar um design system** baseado em referências visuais
- **Replicar/espelhar** a identidade visual de uma marca pra outro projeto
- **Transformar brand guidelines em código** consumível por dev e Figma
- **Auditar contraste WCAG** de uma paleta extraída
- **Gerar style guide** visual (HTML) a partir de tokens

Frases-gatilho típicas:
- "extrai os tokens desse site: [URL]"
- "tenho o manual da marca em PDF, monta o design system"
- "replica a identidade visual desse site no meu projeto"
- "cria um style guide a partir desse logo"
- "quero os design tokens do Linear/Vercel/Stripe pra usar como base"

## Quando NÃO usar

- Pra criar logos do zero (use uma skill de design generativo)
- Pra criar ilustrações ou ícones (não está no escopo)
- Pra implementar componentes em React/Vue/Svelte (entrega só HTML/CSS vanilla)
- Pra fazer design de produto/UX (skill é só extração + tokens, não decisão de UX)

## Pipeline completo (autônomo)

A skill roda sozinha do começo ao fim. Não pergunta nada. Sequência:

## Configuração de caminhos (agnóstica de SO)

Esta skill roda em dois ambientes diferentes. Antes de iniciar o pipeline,
defina os valores de `<uploads_dir>` e `<output_dir>` conforme o ambiente.
Nada nos scripts Python é hardcoded — eles recebem todos os paths via
flags `--input`, `--output`, etc. Os exemplos abaixo usam os placeholders
`<uploads_dir>` e `<output_dir>` que você substitui de acordo com a tabela:

| Ambiente | `<uploads_dir>` | `<output_dir>` |
|---|---|---|
| Sandbox Claude.ai | `/mnt/user-data/uploads/` | `/mnt/user-data/outputs/` |
| Windows local | (peça ao usuário, ex: `C:\Users\<user>\Documentos\design-system\inputs\`) | `C:\Users\<user>\Documentos\design-system\outputs\` |
| Mac/Linux local | `~/Documentos/design-system/inputs/` | `~/Documentos/design-system/outputs/` |
| Default sem especificação | `./design-system/inputs/` | `./design-system/outputs/` |

Se `<uploads_dir>` não existir ou estiver vazio, peça ao usuário onde está
o arquivo. Se `<output_dir>` não existir, crie automaticamente. **Nunca
assuma** o caminho `/mnt/user-data/...` em ambiente local — quebra em
Windows/Mac/Linux.

`<SKILL_DIR>` é o diretório onde esta skill está instalada (ex:
`~/.claude/skills/primia-design/` em local, `/mnt/skills/user/primia-design/`
em sandbox).

### 1. Detecção dos inputs

Identifique cada fonte fornecida:
- **URL** (string começando com http/https ou domínio)
- **PDF** (arquivo `.pdf` em `<uploads_dir>`)
- **Imagem** (`.png`, `.jpg`, `.jpeg`, `.webp` em `<uploads_dir>`)

Aceita múltiplas fontes simultaneamente.

### 2. Parsing da hierarquia (se declarada)

Leia o prompt do usuário procurando frases tipo:
- "X é fonte da verdade"
- "use X como referência principal"
- "X tem prioridade"
- "ignore Y"

Consulte `references/conflict-resolution.md` pra mapeamento completo.

**Se nada foi declarado**, use o default silencioso: `pdf,url,image`.
Não pergunte — apenas registre no `decisions.md` ao final.

### 3. Setup do ambiente

**Sandbox Claude.ai:**

```bash
mkdir -p <output_dir>/{slug-do-projeto}/{tokens,components,brand-assets,_intermediate}
pip install --break-system-packages -r <SKILL_DIR>/scripts/requirements.txt
python -m playwright install chromium 2>/dev/null
```

**Local (Windows/Mac/Linux):**

```bash
mkdir -p <output_dir>/{slug-do-projeto}/{tokens,components,brand-assets,_intermediate}
# Crie um virtualenv (recomendado):
python -m venv .venv
# Ativar:
#   Windows:  .venv\Scripts\activate
#   Mac/Linux: source .venv/bin/activate
pip install -r <SKILL_DIR>/scripts/requirements.txt
python -m playwright install chromium
```

#### Setup do Playwright

O Playwright é usado pra extrair tokens de sites SPA (React, Vue, Next.js).
Após `pip install`, é **obrigatório** rodar uma vez:

```bash
python -m playwright install chromium
```

Isso baixa cerca de 150MB de binário do Chromium e só precisa rodar **uma
vez por máquina**. Em sandbox Claude.ai, isso já é executado no setup
automático. Em ambiente local, sem esse passo, qualquer URL com SPA falha
com erro `Executable doesn't exist` no primeiro uso. Se isso acontecer,
o `extract_from_url.py` cai pra extração estática e segue o pipeline com
aviso — mas resultados ficam parciais.

`{slug-do-projeto}` = derive do nome da marca/site/PDF mencionado pelo
usuário. Se incerto, use `design-system-{timestamp}`.

### 4. Extração (uma chamada por fonte)

Pra cada fonte, rode o extrator apropriado e salve em `_intermediate/`:

```bash
# URL
python <SKILL_DIR>/scripts/extract_from_url.py "https://exemplo.com" \
    --output <output_dir>/{slug}/_intermediate/url.json

# Imagem
python <SKILL_DIR>/scripts/extract_from_image.py <uploads_dir>/logo.png \
    --output <output_dir>/{slug}/_intermediate/image.json

# PDF
python <SKILL_DIR>/scripts/extract_from_pdf.py <uploads_dir>/manual.pdf \
    --output <output_dir>/{slug}/_intermediate/pdf.json
```

Os 3 extratores produzem o mesmo formato intermediário
(ver `references/intermediate-format.md`).

### 5. Merge das fontes

```bash
python <SKILL_DIR>/scripts/merge_sources.py \
    --inputs <output_dir>/{slug}/_intermediate/*.json \
    --hierarchy "pdf,url,image" \
    --output-tokens <output_dir>/{slug}/_intermediate/merged.json \
    --output-conflicts <output_dir>/{slug}/conflicts.md
```

Substitua `pdf,url,image` pela hierarquia parseada do prompt (se houve).

### 6. Análise (3 scripts em paralelo conceitual)

```bash
python <SKILL_DIR>/scripts/analyze_colors.py \
    --input <output_dir>/{slug}/_intermediate/merged.json \
    --output <output_dir>/{slug}/_intermediate/colors.json

python <SKILL_DIR>/scripts/analyze_typography.py \
    --input <output_dir>/{slug}/_intermediate/merged.json \
    --output <output_dir>/{slug}/_intermediate/typography.json

python <SKILL_DIR>/scripts/analyze_spacing.py \
    --input <output_dir>/{slug}/_intermediate/merged.json \
    --output <output_dir>/{slug}/_intermediate/spacing.json
```

### 7. Check de contraste

```bash
python <SKILL_DIR>/scripts/check_contrast.py \
    --colors <output_dir>/{slug}/_intermediate/colors.json \
    --output <output_dir>/{slug}/_intermediate/contrast.json
```

Se houver pares falhando WCAG AA, registre no `decisions.md`.

### 8. Geração dos 5 formatos de tokens

```bash
python <SKILL_DIR>/scripts/generate_outputs.py \
    --colors <output_dir>/{slug}/_intermediate/colors.json \
    --typography <output_dir>/{slug}/_intermediate/typography.json \
    --spacing <output_dir>/{slug}/_intermediate/spacing.json \
    --output-dir <output_dir>/{slug}/tokens/
```

Gera: `design-tokens.json`, `tokens.css`, `tokens.scss`, `tailwind.config.js`,
`figma-tokens.json`.

### 9. Geração do styleguide.html

```bash
python <SKILL_DIR>/scripts/generate_styleguide.py \
    --colors <output_dir>/{slug}/_intermediate/colors.json \
    --typography <output_dir>/{slug}/_intermediate/typography.json \
    --spacing <output_dir>/{slug}/_intermediate/spacing.json \
    --contrast <output_dir>/{slug}/_intermediate/contrast.json \
    --tokens-css <output_dir>/{slug}/tokens/tokens.css \
    --project-name "{Nome da marca}" \
    --output <output_dir>/{slug}/styleguide.html
```

### 10. Cópia dos componentes

```bash
cp <SKILL_DIR>/assets/components/*.html \
    <output_dir>/{slug}/components/
```

### 11. Cópia/manipulação de brand-assets

Se a extração identificou logos (em `merged.json` → `brand_assets`):
- URL: faça `requests.get` em cada `logo_candidates[].src` e salve em `brand-assets/`
- PDF: as imagens já foram extraídas como temporárias — re-extraia
  com pypdf direto pra `brand-assets/`
- Imagem: copie a própria imagem de input pra `brand-assets/source-image.png`

### 12. Geração do README e decisions.md

**README.md:** use o template em `<SKILL_DIR>/assets/readme-template.md`,
substituindo:
- `{{PROJECT_NAME}}` → nome real da marca
- `{{PROJECT_SLUG}}` → slug usado
- `{{DATE}}` → data atual
- `{{SOURCES_LIST}}` → lista markdown das fontes processadas
- `{{HIERARCHY}}` → frase explicando a hierarquia aplicada e origem dela

**decisions.md:** use o template em `<SKILL_DIR>/assets/decisions-template.md`,
substituindo todos os placeholders `{{...}}`. Os principais são:
- `{{PROJECT_NAME}}`, `{{DATE}}`
- `{{HIERARCHY_HUMAN}}` (ex: "PDF > URL > Imagem")
- `{{HIERARCHY_ORIGIN}}` ("default silencioso" ou "declarada pelo usuário")
- `{{HIERARCHY_NOTE}}` (citação literal da frase do usuário, se houver)
- `{{PRIMARY_COLOR}}` (hex)
- `{{NEUTRAL_NOTE}}` (1-2 frases sobre como a neutral foi gerada)
- `{{SUCCESS_STATUS}}`/`{{WARNING_STATUS}}`/`{{DANGER_STATUS}}`/`{{INFO_STATUS}}`
  → "inferido" ou "default" pra cada slot
- `{{SUCCESS_COLOR}}` etc. → hex de cada cor semântica
- `{{FONT_BODY}}`, `{{FONT_DISPLAY}}`, `{{FONT_MONO}}`
- `{{TYPO_SCALE_NAME}}`, `{{TYPO_SCALE_RATIO}}`, `{{TYPO_FIT_ERROR}}`
- `{{SPACING_STEP}}` (4 ou 8)
- `{{RADIUS_NOTE}}`, `{{SHADOW_NOTE}}` (1-2 frases cada)
- `{{CONTRAST_TOTAL}}`, `{{CONTRAST_AA}}`, `{{CONTRAST_AAA}}`,
  `{{CONTRAST_AA_LARGE}}`, `{{CONTRAST_FAIL}}` (números do `contrast.json`)
- `{{CONTRAST_WARNINGS}}` (lista dos pares falhando, se houver)
- `{{LIMITATIONS}}` (bullets do que não foi possível extrair)
- `{{EXTRACTION_WARNINGS}}` (warnings de cada fonte — vem de
  `_intermediate/*.json` no campo `warnings`)

Os valores vêm de `_intermediate/colors.json`, `_intermediate/typography.json`,
`_intermediate/spacing.json` e `_intermediate/contrast.json`.

### 13. Limpeza

Remova `_intermediate/` (são artefatos internos):
```bash
rm -rf <output_dir>/{slug}/_intermediate
```

### 14. Apresentação

Use `present_files` listando os arquivos na ordem:
1. `styleguide.html` (mais relevante — abre visual)
2. `README.md`
3. `decisions.md`
4. `tokens/tailwind.config.js` (ou outro formato relevante pro contexto)

Mensagem ao usuário deve ser curta: 1-2 parágrafos resumindo o que foi
extraído (cor primary, fontes, número de tokens) + o que olhar primeiro.

## Estrutura final do output

```
<output_dir>/{slug-do-projeto}/
├── README.md
├── decisions.md
├── conflicts.md
├── styleguide.html
├── tokens/
│   ├── design-tokens.json
│   ├── tokens.css
│   ├── tokens.scss
│   ├── tailwind.config.js
│   └── figma-tokens.json
├── components/
│   ├── button.html
│   ├── input.html
│   ├── card.html
│   ├── badge.html
│   ├── alert.html
│   └── typography.html
└── brand-assets/
    └── (logos, imagens extraídas)
```

## References disponíveis

Consulte estes arquivos quando precisar de contexto adicional:

- `references/token-naming.md` — convenções de nomenclatura
- `references/intermediate-format.md` — schema do JSON intermediário
- `references/conflict-resolution.md` — parsing de hierarquia do prompt
- `references/output-formats.md` — specs dos 6 formatos de output
- `references/modular-scales.md` — escalas tipográficas comuns
- `references/component-templates.md` — guia dos componentes base

## Dependências Python

Lista canônica em `<SKILL_DIR>/scripts/requirements.txt`:

- `requests`, `beautifulsoup4` — extração de URL estática
- `playwright` (com chromium) — extração de URL dinâmica/SPA
- `Pillow`, `numpy`, `scikit-learn` — k-means de imagens
- `pypdf` — leitura de PDF

**Instalação:**
- Sandbox Claude.ai: `pip install --break-system-packages -r <SKILL_DIR>/scripts/requirements.txt`
- Local: `pip install -r <SKILL_DIR>/scripts/requirements.txt` (preferencialmente dentro de virtualenv)

Após o pip, rode `python -m playwright install chromium` uma vez.

## Limites e princípios

1. **Sempre autônomo.** Nunca pergunte hierarquia, formato preferido, ou
   confirmação. Decida e registre em `decisions.md`.
2. **Confia no usuário.** Não emite avisos de copyright. O usuário é
   responsável pelo uso das marcas que processa.
3. **Falha silenciosamente em fontes.** Se uma das múltiplas fontes
   falhar (ex: PDF corrompido), continue com as demais e mencione no
   `decisions.md`. Não derruba o pipeline.
4. **Não inventa dados.** Quando não dá pra inferir (ex: PDF sem texto =
   sem tipografia), o campo fica null/default e isso vai pro `decisions.md`
   explícito.
5. **HTML vanilla.** Componentes são puro HTML+CSS. Pra React/Vue/etc, o
   usuário implementa em cima dos tokens.

## Verificação rápida da skill

Pra testar que tudo está funcionando, rode com uma URL simples:

```bash
mkdir -p /tmp/test-primia/{_intermediate,tokens,components}
python <SKILL_DIR>/scripts/extract_from_url.py https://stripe.com \
    --output /tmp/test-primia/_intermediate/url.json
python <SKILL_DIR>/scripts/merge_sources.py \
    --inputs /tmp/test-primia/_intermediate/url.json \
    --output-tokens /tmp/test-primia/_intermediate/merged.json \
    --output-conflicts /tmp/test-primia/conflicts.md
python <SKILL_DIR>/scripts/analyze_colors.py \
    --input /tmp/test-primia/_intermediate/merged.json \
    --output /tmp/test-primia/_intermediate/colors.json
# ... e assim por diante
```

Se o styleguide.html abrir e mostrar swatches + tipografia + componentes,
está funcionando.
