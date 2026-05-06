# Análise de Concorrentes — Meta Ad Library

> **Versão:** 1.2.0 — Maio/2026
> **Autor:** Hoberdan Silva
> **Audiência:** Alunos da Mentoria Primia + uso geral em Claude.ai. Roda em sandbox Claude.ai e em Claude Code local (Windows/Mac/Linux).

Skill customizada que automatiza inteligência competitiva publicitária na Biblioteca de Anúncios da Meta (Facebook + Instagram).

---

## Índice

- [O que essa skill faz](#o-que-essa-skill-faz)
- [Pré-requisitos](#pré-requisitos)
- [Como instalar](#como-instalar)
- [Como usar](#como-usar)
- [Onde os outputs ficam salvos](#onde-os-outputs-ficam-salvos)
- [Resolução de problemas](#resolução-de-problemas)
- [Avisos sobre fragilidade do scraping](#avisos-sobre-fragilidade-do-scraping)
- [Estrutura dos arquivos da skill](#estrutura-dos-arquivos-da-skill)
- [Créditos](#créditos)

---

## O que essa skill faz

A skill recebe nomes de concorrentes (ou links da Biblioteca de Anúncios da Meta) e produz um pacote completo de inteligência competitiva. Ela automatiza coleta, organização e geração de relatórios, mas a análise estratégica é feita pelo Claude lendo os dados.

Outputs gerados em cada execução:

- Planilha `.xlsx` com a base completa filtrável.
- Relatório executivo `.docx` em prosa, pronto pra apresentar.
- Apresentação `.pptx` com os anúncios campeões.
- Pasta com os criativos baixados (imagens e vídeos).
- Briefings criativos em Markdown, um por concorrente e um consolidado.
- Relatório HTML interativo offline com gráficos navegáveis.

---

## Pré-requisitos

Antes de instalar, confira se você tem:

**Python 3.10 ou mais novo.** Confira com:

```bash
python --version
```

No Windows, se o comando `python` não funcionar, tente:

```bash
py --version
```

Se nenhum dos dois funcionar, instale do site oficial python.org. Marque a opção "Add Python to PATH" durante a instalação.

**Git** (opcional, só se for clonar o repositório). Em alternativa, baixe o ZIP da skill e descompacte.

**Aproximadamente 3 GB de espaço livre.** O Whisper baixa um modelo de aproximadamente 500 MB no primeiro uso. Os criativos baixados ocupam o resto.

---

## Como instalar

A instalação tem 4 partes: descompactar a skill, criar virtualenv, instalar dependências Python, e instalar binários nativos (Chromium, Tesseract, ffmpeg).

### Passo 1: descompactar a skill

Decida onde a skill vai morar. O caminho padrão sugerido por SO:

- **Windows:** `C:\Users\<seu_usuario>\.claude\skills\analise-concorrentes-meta\`
- **Mac/Linux:** `~/.claude/skills/analise-concorrentes-meta/`

Descompacte o arquivo `analise-concorrentes-meta-v1.2.0.zip` (ou o `.skill`, que é um zip) nessa pasta. A estrutura final deve ter `SKILL.md` direto na raiz, sem pasta extra aninhada.

### Passo 2: criar virtualenv

Entre na pasta da skill e crie um ambiente Python isolado. Isso evita conflito com outros pacotes do sistema.

```bash
cd ~/.claude/skills/analise-concorrentes-meta
python -m venv .venv
```

Ative o virtualenv:

**Windows (PowerShell):**

```bash
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
source .venv/bin/activate
```

Quando ativo, o prompt mostra `(.venv)` na frente.

### Passo 3: instalar dependências Python

Com o virtualenv ativo, instale o que está em `scripts/requirements.txt`:

```bash
pip install -r scripts/requirements.txt
```

A lista canônica é:

- playwright
- openpyxl
- python-docx
- python-pptx
- requests
- beautifulsoup4
- yt-dlp
- openai-whisper
- pillow
- pytesseract

A primeira instalação demora alguns minutos porque o `openai-whisper` traz dependências pesadas (PyTorch).

Se aparecer o erro `externally-managed-environment` no Linux/Mac, é porque você não está no virtualenv. Volte ao Passo 2 e ative.

### Passo 4: instalar Chromium do Playwright

```bash
python -m playwright install chromium
```

Baixa cerca de 150 MB. Roda uma vez por máquina.

### Passo 5: instalar Tesseract OCR

**Windows.** Baixe o instalador do UB Mannheim em `https://github.com/UB-Mannheim/tesseract/wiki`. Durante a instalação, marque a opção "Add to PATH" e selecione o pacote `por` (português) na tela de idiomas.

**Mac:**

```bash
brew install tesseract tesseract-lang
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-por
```

### Passo 6: instalar ffmpeg

**Windows (PowerShell admin):**

```bash
winget install ffmpeg
```

Alternativa com Chocolatey:

```bash
choco install ffmpeg
```

**Mac:**

```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install -y ffmpeg
```

### Passo 7: sanity check

Confira que os imports principais funcionam. Com o virtualenv ativo:

```bash
python -c "import playwright, openpyxl, docx, pptx, requests, bs4, yt_dlp, whisper, PIL, pytesseract; print('OK')"
```

Se imprimir `OK`, todas as dependências Python estão prontas. Se aparecer `ModuleNotFoundError`, volte ao Passo 3.

---

## Como usar

A skill é acionada por linguagem natural numa conversa com o Claude. Frases-gatilho típicas:

- "Analisa os anúncios da Hotmart na biblioteca da Meta"
- "Espionar concorrente X, Y, Z"
- "Quero benchmarking de mídia paga em [nicho]"
- "O que [marca] tá rodando no Instagram?"
- Qualquer link `facebook.com/ads/library/...`

Pedido modelo, copia e adapta:

```
Quero uma análise de concorrentes na Meta Ad Library:
- Concorrentes: [Marca A], [Marca B], [Marca C]
- País: BR
- Status: ativos
- Período: últimos 90 dias
- Limite: 100 ads por concorrente
- Profundidade: estratégica completa
- Entregáveis: todos
```

Se você passar só os concorrentes, o Claude usa os defaults da skill (BR, ativos hoje, 90 dias, 100 ads, todos os entregáveis).

Tempo médio por concorrente: 15 a 30 minutos (Whisper é o gargalo).

---

## Onde os outputs ficam salvos

A skill usa 2 pastas:

- **`<work_dir>`:** artefatos intermediários (raw_ads.json, enriched_ads.json, criativos baixados).
- **`<output_dir>`:** entregáveis finais que você compartilha (xlsx, docx, pptx, html, briefings).

Caminhos sugeridos por SO:

| SO | `<work_dir>` | `<output_dir>` |
|---|---|---|
| Windows | `C:\Users\<user>\Documentos\meta-ads\workdir\` | `C:\Users\<user>\Documentos\meta-ads\entregaveis\` |
| Mac/Linux | `~/Documentos/meta-ads/workdir/` | `~/Documentos/meta-ads/entregaveis/` |
| Sandbox Claude.ai | `/home/claude/output/` | `/mnt/user-data/outputs/` |

Se você não disser onde quer salvar, o Claude vai perguntar antes de começar (ou usar o default `./meta-ads/` na pasta atual).

---

## Resolução de problemas

### Erro: `playwright._impl._errors.Error: Executable doesn't exist`

Significa que o navegador Chromium do Playwright não foi instalado. Rode:

```bash
python -m playwright install chromium
```

### Erro: `pytesseract.pytesseract.TesseractNotFoundError`

O Tesseract não está no PATH. No Windows, reinstale marcando "Add to PATH". No Mac/Linux, rode o comando de instalação do Passo 5.

A skill faz fallback automático: se o Tesseract não estiver disponível, o pipeline pula a etapa de OCR e gera os outros entregáveis normalmente.

### Erro: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

O ffmpeg não está instalado. Rode o comando do Passo 6 conforme seu SO.

A skill faz fallback automático aqui também: sem ffmpeg, a transcrição de vídeos é pulada e o relatório registra a limitação.

### Scraping retorna 0 anúncios ou aparece CAPTCHA

A Meta detectou o bot. Acontece principalmente quando você roda no sandbox Claude.ai (IP de datacenter). Soluções na ordem:

1. Aguarde 30 minutos e tente de novo.
2. Rode local com seu IP residencial (esse é o motivo principal de instalar local).
3. Use VPN com IP residencial.

Se você roda local e cai em CAPTCHA, a Meta pode ter bloqueado seu IP temporariamente por excesso de scraping. Espere algumas horas.

### Erro: `ModuleNotFoundError: No module named 'X'`

O virtualenv não está ativo, ou o `pip install` do Passo 3 falhou. Confirme que o prompt mostra `(.venv)` na frente. Se mostrar, rode de novo:

```bash
pip install -r scripts/requirements.txt
```

### Erro: `error: externally-managed-environment` (Linux/Mac)

Você está tentando instalar fora do virtualenv. Volte ao Passo 2 e ative o `.venv` antes de rodar `pip install`.

### Erro no Windows: `'python' is not recognized as an internal or external command`

O Python não está no PATH. Reinstale o Python marcando "Add Python to PATH" ou use `py` em vez de `python` em todos os comandos.

---

## Avisos sobre fragilidade do scraping

A Biblioteca de Anúncios da Meta é uma SPA que muda de estrutura sem aviso. Os seletores HTML que o `scrape_ad_library.py` usa podem quebrar quando a Meta atualizar o front. Sintomas típicos:

- Scraping retorna lista vazia mesmo com a página tendo anúncios.
- Erros tipo `ElementHandle has been disposed` ou `selector did not resolve`.

Quando isso acontecer, leia `references/scraping-troubleshooting.md` da skill — tem instruções pra adaptar os seletores.

---

## Estrutura dos arquivos da skill

```
analise-concorrentes-meta/
├── SKILL.md                     # Instruções principais para o Claude
├── README.md                    # Este arquivo
├── .gitignore
├── assets/
│   └── briefing-template.md     # Template parametrizado de briefing
├── references/
│   ├── frameworks-de-analise.md
│   ├── exemplos-de-recomendacoes.md
│   └── scraping-troubleshooting.md
└── scripts/
    ├── requirements.txt         # Lista canônica de dependências Python
    ├── scrape_ad_library.py     # Coleta via Playwright
    ├── download_creatives.py    # Download de imagens e vídeos
    ├── enrich_creatives.py      # OCR + Whisper + pHash
    ├── build_xlsx.py            # Gera planilha
    ├── build_docx.py            # Gera relatório executivo
    ├── build_pptx.py            # Gera apresentação
    ├── build_briefing.py        # Gera briefings criativos
    └── build_html_report.py     # Gera dashboard HTML interativo
```

---

## Créditos

**Desenvolvida por:** Hoberdan Silva
**Para:** Alunos da Mentoria Primia
**Versão:** 1.2.0 — Maio/2026

Esta skill é parte do material exclusivo da Mentoria Primia. Distribuição e uso restritos aos alunos e equipe da mentoria. Para dúvidas, melhorias ou bugs, contate diretamente Hoberdan Silva ou abra um chamado no canal interno da mentoria.
