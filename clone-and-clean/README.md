# clone-and-clean — Plugin para Claude Code

Plugin que dá ao Claude Code um pipeline completo pra **clonar, limpar e reescrever páginas de lançamento** (landing pages de infoprodutos, páginas de vendas, captura, obrigado) preservando a identidade visual do original.

## O que o plugin faz

Recebe uma URL e entrega três artefatos organizados:

1. **`deploy-ready/`** — cópia 1:1 self-contained, pronta pra Vercel/Netlify
2. **`copy.md` + `info.md`** — copy por seção + metadados (pixels, stack, data)
3. **`clean/`** — reescrita em HTML semântico + CSS com design-tokens, fiel à composição visual do original

## Instalação no Claude Code

### Opção A — Via marketplace local (recomendado)

```bash
# No terminal, rode no diretório do seu projeto
/plugin marketplace add /caminho/para/clone-and-clean-plugin
/plugin install clone-and-clean
```

### Opção B — Instalação manual

Descompacte este `.plugin` na pasta global de plugins do Claude Code:

```bash
# macOS / Linux
mkdir -p ~/.claude/plugins/
unzip clone-and-clean.plugin -d ~/.claude/plugins/

# Confirmar que ficou assim:
ls ~/.claude/plugins/clone-and-clean/
# → .claude-plugin/  skills/  README.md  INSTALL.md
```

Reinicie o Claude Code e o plugin é detectado automaticamente.

### Opção C — Só a skill (sem plugin)

Se você quer só a skill sem a estrutura de plugin:

```bash
mkdir -p ~/.claude/skills/
cp -r skills/clone-and-clean ~/.claude/skills/
```

## Pré-requisitos

- **Claude Code** instalado (`npm install -g @anthropic-ai/claude-code`)
- **Claude in Chrome** (extensão do navegador) — pra capturar HTML renderizado e screenshots full-page
- **Python 3.9+** no PATH
- **zip/unzip** (qualquer Linux/Mac/WSL tem)

## Como usar

Num projeto aberto no Claude Code, peça:

> "Usa a skill clone-and-clean pra baixar https://exemplo.com/lancamento como cliente Fulano, nicho emagrecimento, tipo ingresso-pago, slug lancamento-jan-2026"

O Claude vai:

1. Abrir a URL via Claude in Chrome
2. Scroll até o fim (força lazy-load)
3. Capturar HTML + recursos + screenshot
4. Gerar `deploy-ready/`, `design-system/`, `copy.md`, `info.md`, `clean/`
5. **Rodar o loop de revisão visual seção a seção** (novidade v1.1)
6. Validar com `verify.py`
7. Empacotar 3 ZIPs e entregar links

## Estrutura do plugin

```
clone-and-clean-plugin/
├── .claude-plugin/
│   ├── plugin.json              ← manifest do plugin (nome, versão, autor)
│   └── marketplace.json         ← manifest de marketplace local
├── skills/
│   └── clone-and-clean/
│       ├── SKILL.md             ← instruções principais
│       ├── rules/
│       │   ├── deploy-ready.md      → pixels, WhatsApp, APIs
│       │   ├── design-system.md     → extração de tokens ANTES da reescrita
│       │   ├── fidelidade-visual.md → 10 regras de composição visual
│       │   ├── clean-rewrite.md     → princípios HTML semântico
│       │   └── copyright.md         → limites éticos
│       ├── scripts/
│       │   ├── load-jszip.js
│       │   ├── browser-capture.js
│       │   ├── extract-copy.js
│       │   ├── extract-palette.js        → paleta simples (fallback)
│       │   ├── extract-design-system.js  → tokens completos do DOM
│       │   ├── process-capture.py        → descompacta+curl+rewrite
│       │   ├── rewrite-css.py
│       │   └── verify.py
│       ├── templates/
│       │   ├── clean-base.html
│       │   └── info.md
│       └── examples/
│           └── cris-schumann-imersao-ecr01/
├── README.md                    ← este arquivo
└── INSTALL.md                   ← passo a passo detalhado
```

## Changelog

### v1.1.1 (2026-04-20)

- **Novo** `scripts/process-capture.py` — descompacta ZIP do Chrome, baixa assets faltantes via curl, reescreve `src/href` do HTML pra paths locais, invoca `rewrite-css.py` e gera relatório final. Fecha o gap entre Passo 2 (captura) e Passo 4 (deploy-ready).
- **Novo** `scripts/extract-design-system.js` — extração completa dos tokens do DOM real (brand, neutral, gradients, typography scale, radii, shadows, sections, components). Substitui `extract-palette.js` como fonte obrigatória do Passo 6.5.
- **Novo** `.claude-plugin/marketplace.json` — permite instalação via `/plugin marketplace add` apontando pro diretório local.
- **Correção** troubleshooting do SKILL.md não referencia mais `details-polyfill.js` inexistente.
- **Correção** INSTALL.md agora descreve fluxo offline real (`--skip-download` no `process-capture.py`).

### v1.1.0 (2026-04-19)

- **Nova regra** `rules/fidelidade-visual.md` com 10 regras inviolaveis:
  1. Alinhamento de texto preservado
  2. Logo sempre replicada
  3. Composição da hero intacta (2-col vs bg-full)
  4. Elementos visuais intermediários (imagens entre cards, ornamentos)
  5. Estrutura de grids não colapsa
  6. Popup vs inline do form preservado
  7. Proporções de imagem mantidas
  8. Hero com asset integrado → `background-image` da seção
  9. Painel cream contínuo com pessoa sobreposta → `.vs-panel` + `position: absolute`
  10. Emojis nativos → SVG inline com `stroke="currentColor"`
- **Novo Passo 7.5** no fluxo: loop de revisão visual seção a seção antes de avançar
- Passo 8 (validação) agora checa assets visuais críticos + zero hex hardcoded

### v1.0.0 (2026-04-10)

- Versão inicial
- Extração de design system obrigatória antes da clean
- Pipeline completo de 9 passos
- Exemplo Cris Schumann

## Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| Claude não encontra a skill | `SKILL.md` sem frontmatter YAML (`name:` + `description:`) | Verificar topo do arquivo |
| JSZip não carrega na aba | CSP bloqueando scripts externos | Rodar `load-jszip.js` primeiro; se bloqueado, salvar página como HTML e processar offline |
| Imagens faltando na galeria | Lightbox Elementor com lazy-load | Antes do capture, rodar `[...document.querySelectorAll('img[data-src]')].forEach(i => i.src = i.dataset.src)` |
| Clean divergiu visualmente | Pulou o Passo 7.5 (loop de revisão) | Reler `rules/fidelidade-visual.md` e reescrever seções divergentes |

## Licença

MIT — use, modifique, distribua livremente.
