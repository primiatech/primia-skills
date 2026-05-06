# Instalação do plugin `clone-and-clean` no Claude Code

Três caminhos de instalação — escolha o que se encaixa no seu fluxo.

## Pré-requisitos

```bash
# 1. Claude Code instalado (versão recente)
npm install -g @anthropic-ai/claude-code

# 2. Conferir versão
claude --version
```

Além disso:
- Extensão **Claude in Chrome** no navegador (pra capturar DOM renderizado)
- **Python 3.9+** e **zip/unzip** no PATH

## Caminho 1 — Via marketplace local (recomendado pra desenvolvimento)

Útil se você está iterando no plugin ou quer versionar localmente.

```bash
# 1. Descompactar o .plugin numa pasta sua
mkdir -p ~/plugins/
unzip clone-and-clean.plugin -d ~/plugins/

# 2. Dentro do Claude Code, rodar os slash commands:
/plugin marketplace add ~/plugins/clone-and-clean-plugin
/plugin install clone-and-clean

# 3. Conferir que instalou
/plugin list
```

## Caminho 2 — Instalação global direta

Instala o plugin em `~/.claude/plugins/` pra ficar disponível em todos os projetos.

```bash
mkdir -p ~/.claude/plugins/
unzip clone-and-clean.plugin -d ~/.claude/plugins/

# Conferir a estrutura:
ls ~/.claude/plugins/clone-and-clean-plugin/
# Deve ter:
#   .claude-plugin/plugin.json
#   skills/clone-and-clean/SKILL.md
#   README.md
#   INSTALL.md
```

Reinicie o Claude Code. A skill fica disponível automaticamente.

## Caminho 3 — Só a skill (sem estrutura de plugin)

Se você só quer a skill, sem a manifest de plugin:

```bash
mkdir -p ~/.claude/skills/
unzip clone-and-clean.plugin -d /tmp/ccp
cp -r /tmp/ccp/skills/clone-and-clean ~/.claude/skills/

# Conferir:
ls ~/.claude/skills/clone-and-clean/SKILL.md
```

## Testando a instalação

Abra um projeto no Claude Code e peça:

> "Quais skills você tem disponíveis?"

Claude deve listar `clone-and-clean`.

Em seguida, teste de verdade com uma URL simples:

> "Usa clone-and-clean pra baixar https://anthropic.com como inspiração, nicho AI, slug anthropic-home-test"

## Estrutura esperada depois da instalação

```
~/.claude/plugins/clone-and-clean-plugin/
├── .claude-plugin/
│   ├── plugin.json              ← lido pelo Claude Code no startup
│   └── marketplace.json         ← usado pelo /plugin marketplace add
└── skills/
    └── clone-and-clean/
        ├── SKILL.md             ← lido automaticamente quando skill é acionada
        ├── rules/
        │   ├── deploy-ready.md
        │   ├── design-system.md
        │   ├── fidelidade-visual.md
        │   ├── clean-rewrite.md
        │   └── copyright.md
        ├── scripts/
        │   ├── load-jszip.js
        │   ├── browser-capture.js
        │   ├── extract-copy.js
        │   ├── extract-palette.js
        │   ├── extract-design-system.js
        │   ├── process-capture.py
        │   ├── rewrite-css.py
        │   └── verify.py
        ├── templates/
        └── examples/
```

## Desinstalação

```bash
# Via slash command
/plugin uninstall clone-and-clean

# Ou direto
rm -rf ~/.claude/plugins/clone-and-clean-plugin
rm -rf ~/.claude/skills/clone-and-clean   # se usou o Caminho 3
```

## Atualização

Quando sair nova versão:

```bash
# Remover a antiga e instalar a nova
rm -rf ~/.claude/plugins/clone-and-clean-plugin
unzip clone-and-clean-v2.plugin -d ~/.claude/plugins/
```

Ou via slash command:

```bash
/plugin update clone-and-clean
```

## Troubleshooting

**"Claude não detecta a skill"**
- Conferir que `SKILL.md` tem frontmatter YAML (`---` + `name:` + `description:` + `---`)
- Conferir o path: `ls ~/.claude/plugins/clone-and-clean-plugin/.claude-plugin/plugin.json` tem que retornar OK
- Reiniciar o Claude Code completamente (`pkill -f claude && claude`)

**"Plugin instalou mas skill não aparece"**
- Rodar `/plugin list` pra confirmar que está instalado e enabled
- Conferir que o diretório `skills/clone-and-clean/` está dentro do plugin
- Ver logs: `claude --debug`

**"JSZip não carrega na aba da página a ser clonada"**
- CSP da página bloqueia scripts externos
- Salvar a página como HTML completo (Ctrl+S → "Página da web, completa"), zipar manualmente (`zip -r captura.zip pasta_salva/`) e processar com `python3 scripts/process-capture.py --zip captura.zip --out destino/ --skip-download`

**"verify.py reclama de copy ausente"**
- Conferir se o `copy.md` tem as strings exatas que você colocou no HTML
- O matching é case-insensitive desde a v1.1
