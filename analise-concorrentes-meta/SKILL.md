---
name: analise-concorrentes-meta
description: |
  Realiza análise de inteligência competitiva publicitária na Biblioteca de Anúncios da Meta (Facebook/Instagram Ad Library), via scraping da interface pública. Use SEMPRE que o usuário mencionar "análise de concorrente", "espionar concorrente", "biblioteca de anúncios", "Meta Ad Library", "Facebook Ads Library", "anúncios do concorrente", "inteligência competitiva de mídia", "benchmarking de anúncios", "o que [marca] está rodando", "criativos do concorrente", ou colar uma URL do tipo `facebook.com/ads/library/`. Também acionar quando o usuário pedir para mapear ofertas, ângulos, copies ou criativos de uma marca específica para inspiração ou benchmark. Entrega: planilha .xlsx com base completa, relatório .docx executivo, .pptx com anúncios campeões, pasta com criativos baixados, transcrições de vídeos e análise comparativa multi-concorrente.
metadata:
  author: Hoberdan Silva
  version: 1.2.0
  created: 2026-05-05
  updated: 2026-05-06
  audience: "Alunos da Mentoria Primia + uso geral em Claude.ai. Roda em sandbox Claude.ai e em Claude Code local (Windows/Mac/Linux)."
---

# Análise de Concorrentes — Meta Ad Library

> **Skill desenvolvida por Hoberdan Silva para os alunos da Mentoria Primia.**
> Uso interno e educacional. Versão 1.2.0 — Maio/2026.

Você é um analista sênior de inteligência publicitária. Sua função é coletar, estruturar e interpretar anúncios da Biblioteca de Anúncios da Meta (Facebook + Instagram) para gerar inteligência competitiva acionável — não apenas listar criativos, mas extrair **padrões estratégicos, ângulos de oferta, sinais de performance e oportunidades de mercado**.

A Biblioteca de Anúncios é pública e não exige autenticação. URL base: `https://www.facebook.com/ads/library/`.

---

## Fluxo de execução (sempre nesta ordem)

1. **Coleta de inputs** — Confirmar com o usuário: concorrentes (nomes/IDs/URLs), país, período, categoria de anúncio, profundidade desejada.
2. **Setup do ambiente** — Instalar dependências necessárias (Playwright, yt-dlp, Whisper, python-docx, openpyxl, python-pptx, requests).
3. **Scraping** — Rodar `scripts/scrape_ad_library.py` para capturar anúncios.
4. **Download de criativos** — Baixar imagens e vídeos via `scripts/download_creatives.py`.
5. **Enriquecimento** — Transcrever vídeos (Whisper) e extrair texto de imagens (OCR) via `scripts/enrich_creatives.py`.
6. **Análise estratégica** — VOCÊ (Claude) lê a base enriquecida e identifica padrões. Esta é a parte crítica que **não pode ser automatizada por script** — requer raciocínio.
7. **Geração dos entregáveis** — `.xlsx`, `.docx`, `.pptx` e pasta de criativos.
8. **Apresentação** — `present_files` com a planilha em primeiro lugar.

---

## Configuração de caminhos (agnóstica de SO)

A skill usa **3 placeholders** no lugar de paths fixos. Antes de rodar qualquer script, decida o valor de cada um conforme o ambiente:

| Placeholder | Significado | Sandbox Claude.ai | Windows local | Mac/Linux local | Default sem especificação |
|---|---|---|---|---|---|
| `<work_dir>` | Artefatos intermediários (raw_ads, enriched_ads, etc) | `/home/claude/output/` | `C:\Users\<user>\Documentos\meta-ads\workdir\` | `~/Documentos/meta-ads/workdir/` | `./meta-ads/workdir/` |
| `<output_dir>` | Entregáveis finais (xlsx, docx, pptx, html, briefings) | `/mnt/user-data/outputs/` | `C:\Users\<user>\Documentos\meta-ads\entregaveis\` | `~/Documentos/meta-ads/entregaveis/` | `./meta-ads/entregaveis/` |
| `<SKILL_DIR>` | Pasta da skill instalada | `/mnt/skills/.../analise-concorrentes-meta/` | `C:\Users\<user>\.claude\skills\analise-concorrentes-meta\` | `~/.claude/skills/analise-concorrentes-meta/` | (caminho onde a skill foi descompactada) |

**Importante:** os scripts Python já recebem todos os paths via flag CLI (`--output-dir`, `--enriched`, `--analysis`). Nenhum caminho está hardcoded no código — só nos exemplos deste SKILL.md, onde uso os placeholders acima.

Quando o ambiente não for óbvio, **pergunte ao usuário** onde quer salvar o trabalho antes de começar. Em sandbox Claude.ai use sempre os defaults da primeira coluna.

---

## Setup obrigatório (rodar uma vez no início)

A skill tem 3 camadas de dependências: pacotes Python, browser do Playwright, e binários nativos (Tesseract, ffmpeg).

### Camada 1: pacotes Python

A lista canônica está em `<SKILL_DIR>/scripts/requirements.txt`. Use sempre esse arquivo, não duplique a lista em outro lugar.

**Sandbox Claude.ai:**

```bash
pip install --break-system-packages -r <SKILL_DIR>/scripts/requirements.txt
```

**Local (Windows/Mac/Linux), dentro de virtualenv:**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r <SKILL_DIR>/scripts/requirements.txt
```

### Camada 2: Chromium do Playwright (todos os SOs)

```bash
python -m playwright install chromium
```

Baixa cerca de 150MB. Roda uma vez por máquina.

### Camada 3: Setup de binários nativos

Tesseract OCR e ffmpeg são binários nativos (não-Python). Cada SO instala diferente:

**Tesseract OCR**

- **Windows:** baixe o instalador do UB Mannheim (`https://github.com/UB-Mannheim/tesseract/wiki`) e marque "Add to PATH" durante a instalação. Selecione também o pacote `por` (português) na tela de idiomas.
- **Mac:** `brew install tesseract tesseract-lang`
- **Linux:** `sudo apt-get install -y tesseract-ocr tesseract-ocr-por`
- **Sandbox Claude.ai:** já incluso no setup automático.

**ffmpeg**

- **Windows:** `winget install ffmpeg` (PowerShell admin) ou `choco install ffmpeg` (Chocolatey).
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt-get install -y ffmpeg`
- **Sandbox Claude.ai:** já incluso no setup automático.

### Comportamento de fallback

Se Tesseract ou ffmpeg não estiverem instalados, a skill **degrade graciosamente**: pula a etapa correspondente (OCR ou transcrição), registra a limitação no relatório final, e não derruba o pipeline. Os outros entregáveis continuam sendo gerados normalmente.

---

## Etapa 1 — Briefing inteligente

**Princípio:** minimizar fricção. Aluno apressado não responde 6 perguntas — abandona a sessão.

**Faça UMA pergunta inicial**, anunciando todos os defaults numa linha só. Estrutura:

> "Pra começar, me passa só os concorrentes (nome, link da Biblioteca ou Page ID — pode ser lista separada por vírgula).
>
> **Vou usar como padrão:** Brasil 🇧🇷 · ativos hoje · últimos 90 dias · 100 ads por concorrente · análise estratégica completa.
>
> Se quiser mudar algum desses parâmetros, me diga junto. Senão, manda só os concorrentes."

### Defaults a aplicar quando não especificado

| Parâmetro | Default |
|---|---|
| País | `BR` |
| Status | `active` (apenas em veiculação hoje) |
| Período | últimos 90 dias |
| Categoria | `all` |
| Limite por concorrente | 100 ads |
| Profundidade | análise estratégica completa (todos os 6 entregáveis) |
| Idioma do relatório | PT-BR |

### Quando re-perguntar (e quando NÃO)

- ✅ **Pergunte:** se o usuário não passou nenhum concorrente.
- ✅ **Pergunte:** se passou algo ambíguo ("os concorrentes da Hotmart" — quem exatamente?).
- ❌ **NÃO pergunte:** se o usuário já especificou parâmetros na primeira mensagem ("analisa Hotmart e Eduzz, últimos 30 dias"). Confirme em uma linha e siga.
- ❌ **NÃO pergunte:** se o usuário disse "usa o padrão" ou similar. Os defaults já estão escolhidos.

### Override em uma linha

Aceite formatos curtos como:
- "Hotmart, Eduzz, Kiwify — últimos 30 dias"
- "Magazine Luiza · só vídeo · top 50"
- "esse link aqui [URL] — modo express"

**"Modo express"** = pular transcrição de vídeo + limitar a 30 ads/concorrente. Mencione isso na resposta de confirmação.

### Após o briefing, confirme em UMA linha:

> "Beleza — vou analisar **Hotmart, Eduzz, Kiwify** (BR, ativos, 90 dias, 100 ads cada). Estimativa: ~45-60 min. Começando a coletar agora."

Não detalhe etapas. Não liste o que vai fazer. Só fala que começou.

---

## Etapa 2 — Scraping

Use `scripts/scrape_ad_library.py`. Ele recebe parâmetros via CLI e gera `raw_ads.json` por concorrente em `<work_dir>/<concorrente>/`.

**Importante:**

- A interface da Meta Ad Library é uma SPA pesada em JavaScript — não tente requests diretos. Use Playwright headless.
- A página usa scroll infinito. O script faz scroll programático até o limite ou esgotar resultados.
- A Meta às vezes renderiza CAPTCHA ou bloqueia temporariamente. Se acontecer, o script salva o que coletou e avisa. Não fica em loop infinito.
- Os seletores da Meta mudam com frequência. O script usa estratégia de fallback. Se quebrar, leia `references/scraping-troubleshooting.md`.

**Comando padrão:**

```bash
python <SKILL_DIR>/scripts/scrape_ad_library.py \
  --advertiser "Nome do Concorrente" \
  --country BR \
  --active-status all \
  --ad-type all \
  --limit 100 \
  --output-dir <work_dir>/concorrente-slug
```

Para cada anúncio o script captura: `ad_archive_id`, `page_id`, `page_name`, `start_date`, `end_date`, `days_running`, `platforms`, `creative_type`, `body_text`, `headline`, `description`, `cta_type`, `link_url`, `media_urls`, `variations_count`, `eu_disclosures` (quando disponível).

---

## Etapa 3 — Download dos criativos

Rode `scripts/download_creatives.py`. Ele baixa cada mídia para `<work_dir>/<concorrente>/creatives/` com nomenclatura `<ad_archive_id>_<index>.<ext>`.

Vídeos via `yt-dlp` (mais robusto pra CDN da Meta). Imagens via requests com headers de browser. Falhas individuais não param o processo — log e continue.

---

## Etapa 4 — Enriquecimento

Rode `scripts/enrich_creatives.py`. Ele:

1. **Transcreve vídeos** com Whisper (modelo `small`, bom equilíbrio velocidade/qualidade em pt-BR).
2. **OCR em imagens** com Tesseract (`por+eng`).
3. **Hash perceptual** (pHash) de cada imagem para detectar duplicatas e variações sutis.
4. Atualiza `raw_ads.json` com `transcript`, `ocr_text`, `phash` → `enriched_ads.json`.

Se Whisper/Tesseract não instalaram, pule sem falhar e avise no relatório.

---

## Etapa 5 — Análise estratégica (você, Claude)

**Esta é a etapa que mais agrega valor — não delegue para script.**

Leia `enriched_ads.json` consolidado e produza análise nas dimensões abaixo. Para cada uma, busque **evidências concretas** (cite IDs de anúncios) — nunca generalize sem base.

### 5.1 — Sinais de performance (proxy)

Anúncios com **`days_running` ≥ 30** são candidatos a "vencedores" — ninguém deixa anúncio ruim rodando tanto tempo. Liste top 10 por concorrente em ordem de longevidade.

Diferencie: "Saiba mais" + tom institucional ≠ performance; "Compre agora" + oferta + urgência = conversão funcionando.

### 5.2 — Mapeamento de ofertas

Identifique padrões: preços recorrentes, descontos ("50% OFF", "de R$ X por R$ Y"), bundles, garantias, bônus, escassez ("últimas vagas", "só hoje").

### 5.3 — Ângulos de comunicação

Classifique cada anúncio (ou grupo similar) em um ângulo clássico:
- **Dor**: começa com problema do cliente
- **Desejo/aspiração**: cenário ideal
- **Prova social**: depoimento, "X mil pessoas já..."
- **Autoridade**: especialista, mídia, certificações
- **Novidade**: "lançamento", "novo método"
- **Curiosidade**: pergunta, paradoxo, "o segredo que..."
- **Comparação**: "diferente de", "ao contrário de"
- **Storytelling**: narrativa pessoal

Conte por concorrente. Identifique ângulo dominante e secundário.

### 5.4 — Estágio de funil

- **Topo (awareness)**: educa, gera curiosidade. CTA leve ("Saiba mais").
- **Meio (consideração)**: produto, comparações, demos. CTA médio ("Ver mais").
- **Fundo (conversão)**: oferta direta, urgência, preço. CTA forte ("Compre agora").

Calcule distribuição percentual por concorrente. Quem investe em topo (marca crescendo) vs fundo (extração).

### 5.5 — Estrutura de copy

Frameworks recorrentes: AIDA, PAS, Antes/Depois/Ponte, Lista de benefícios, Storytelling pessoal. Identifique o dominante por concorrente com 2-3 exemplos.

### 5.6 — Hooks de vídeo (primeiros 3 segundos)

Lendo as transcrições, identifique aberturas:
- Pergunta direta ("Você sabia que...")
- Afirmação chocante ("99% das pessoas erram nisso")
- Demonstração visual silenciosa
- Depoimento começando in media res
- Padrão interrompido

Liste os 5 hooks mais usados pelos campeões.

### 5.7 — Cadência de testes

A partir de `start_date`: anúncios novos por semana, períodos de aceleração (lançamento?), pausas.

### 5.8 — Comparativo entre concorrentes

Matriz: Concorrente | Volume | Ativos | Mediana de dias no ar | Ângulo dominante | Estágio dominante | Formato dominante | Cadência semanal.

Identifique:
- Quem tem portfólio mais "saudável" (mix de funil + longevidade alta)
- **Gaps**: ângulos/ofertas que ninguém está explorando — oportunidade
- **Sobreposições**: onde todos competem — saturação

### 5.9 — Recomendações acionáveis

5-10 recomendações concretas, cada uma vinculada a evidência:

> ❌ Ruim: "Teste mais vídeos"
> ✅ Bom: "Teste hook de pergunta direta nos primeiros 3s — 7 dos 10 anúncios mais longevos dos concorrentes (IDs: X, Y, Z) abrem assim, e nenhum dos seus criativos atuais usa esse padrão."

---

## Etapa 6 — Entregáveis

Gere todos os arquivos em `<output_dir>/`. **Sempre os 6 entregáveis** por padrão (a menos que o aluno tenha pedido modo express na Etapa 1):

| # | Arquivo | Função | Audiência |
|---|---|---|---|
| 6.1 | `analise_concorrentes.xlsx` | Base navegável | Quem vai explorar dado |
| 6.2 | `relatorio_executivo.docx` | Leitura linear | Diretor/cliente |
| 6.3 | `apresentacao.pptx` | Reunião | Apresentação ao time |
| 6.4 | `criativos/` | Swipe file | Copy/diretor de arte |
| 6.5 | `briefings/` | Insumo de produção | Quem vai criar os anúncios |
| 6.6 | `relatorio_html/` | Dashboard interativo | Compartilhar via link |

### 6.1 — Planilha base (.xlsx)

Use `scripts/build_xlsx.py`. **Em sandbox Claude.ai, antes de rodar leia `/mnt/skills/public/xlsx/SKILL.md`** se disponível (ele tem padrões de formatação). Em ambiente local sem essa skill auxiliar, prossiga normalmente — o script já está autossuficiente.

Abas:
- **Resumo**: contagem por concorrente, ativos, mediana de dias no ar, formato dominante.
- **Anúncios**: uma linha por anúncio, todos os campos do `enriched_ads.json` + colunas analíticas (`angulo_classificado`, `funil_classificado`, `framework_copy`, `oferta_principal`).
- **Top Longevos**: top 20 por `days_running` global.
- **Comparativo**: matriz da seção 5.8.
- **Recomendações**: as 5-10 da seção 5.9.

Cabeçalhos em negrito com fundo, primeira linha congelada, larguras ajustadas.

### 6.2 — Relatório executivo (.docx)

Use `scripts/build_docx.py`. **Em sandbox Claude.ai, antes de rodar leia `/mnt/skills/public/docx/SKILL.md`** se disponível. Em ambiente local, prossiga direto.

Estrutura:

```
[Capa] Análise Competitiva — [Concorrentes] — [Data]

1. Resumo Executivo (1 página, 5 bullets dos achados mais importantes)
2. Metodologia (coleta, período, limitações)
3. Panorama Geral (volume, distribuição, gráficos)
4. Análise por Concorrente
   4.1 [Concorrente A]
       - Perfil de operação
       - Top 5 anúncios longevos (com screenshots)
       - Ângulos dominantes
       - Ofertas recorrentes
       - Estrutura de funil
   4.2 [Concorrente B]
   ...
5. Análise Comparativa
6. Oportunidades Identificadas (gaps de mercado)
7. Recomendações Estratégicas (numeradas, com evidência)
8. Anexo: lista completa de IDs analisados
```

Use estilos `Heading 1/2/3`. Insira screenshots dos top criativos.

### 6.3 — Apresentação executiva (.pptx)

Use `scripts/build_pptx.py`. **Em sandbox Claude.ai, antes de rodar leia `/mnt/skills/public/pptx/SKILL.md`** se disponível. Em ambiente local, prossiga direto.

Estrutura sugerida:
1. Capa
2. Sumário executivo (5 bullets)
3. Metodologia (1 slide)
4. Panorama (1 slide com gráficos)
5. Para cada concorrente: overview + top 3 criativos + ângulos
6. Comparativo (1-2 slides)
7. Oportunidades (1 slide)
8. Recomendações (1-3 slides)
9. Próximos passos

### 6.4 — Pasta de criativos

Mova de `<work_dir>/<concorrente>/creatives/` para `<output_dir>/criativos/<concorrente>/` mantendo nomenclatura.

### 6.5 — Briefings criativos (.md)

Use `scripts/build_briefing.py`. Este é o entregável que **fecha o ciclo análise → ação** — pega o que foi analisado e transforma em insumo de produção pronto pro copywriter ou direto pro próprio aluno.

**Gera dois tipos:**

1. **Um briefing por concorrente** (`briefings/<concorrente>.md`) — replicar o vencedor identificado de cada um.
2. **Um briefing consolidado** (`briefings/_consolidado.md`) — mistura insights de todos pra criar um anúncio original que junta o que cada concorrente faz melhor.

**Estrutura:** o template parametrizado fica em `<SKILL_DIR>/assets/briefing-template.md` e usa placeholders `{{...}}` no padrão dos templates de skills do projeto Primia. O script consome o template e substitui os placeholders pelos campos preenchidos no `analysis.json`. Não duplique a estrutura aqui — quem quiser ajustar o layout do briefing edita o template diretamente.

**Comando:**

```bash
python <SKILL_DIR>/scripts/build_briefing.py \
  --enriched <work_dir>/concorrente1/enriched_ads.json <work_dir>/concorrente2/enriched_ads.json \
  --analysis <work_dir>/analysis.json \
  --output-dir <output_dir>/briefings
```

O script consome o mesmo `analysis.json` que os outros builders. As seções "Avatar", "Hook recomendado" e "Copy de feed" você (Claude) preenche no `analysis.json` durante a Etapa 5 — adicione o campo `briefing` em cada `by_competitor` e um `briefing_consolidado` no nível raiz.

### 6.6 — Relatório HTML interativo

Use `scripts/build_html_report.py`. Gera uma **pasta auto-contida** (`relatorio_html/`) que abre offline em qualquer navegador.

**Por que HTML local com assets:**
- Funciona sem internet (Chart.js empacotado localmente)
- Imagens dos criativos ficam embutidas (cliente vê na hora)
- O aluno pode subir num Drive/Notion compartilhado e o link funciona

**Estrutura da pasta:**

```
relatorio_html/
├── index.html              # Dashboard principal com navegação
├── concorrente_<slug>.html # Uma página por concorrente
├── assets/
│   ├── styles.css          # CSS único, paleta Mentoria Primia
│   ├── chart.min.js        # Chart.js empacotado (sem CDN)
│   ├── app.js              # Lógica de navegação e charts
│   └── data.json           # Dados pra alimentar os gráficos
└── creativos/
    └── <concorrente>/      # Symlinks ou cópias dos criativos
```

**Conteúdo do index.html:**

1. **Hero**: nome dos concorrentes, período, total de ads
2. **Sumário executivo**: 5 cards com os achados principais
3. **Gráficos comparativos**:
   - Barra: volume de ads por concorrente
   - Pizza: distribuição de formatos (vídeo/imagem/carrossel)
   - Barra horizontal: top 10 anúncios mais longevos (cross-concorrente)
   - Heatmap: ângulos × concorrentes
4. **Cards de concorrentes**: clicáveis, levam pra página individual
5. **Recomendações**: lista numerada com prioridade

**Conteúdo de cada concorrente_<slug>.html:**

1. Header com nome + métricas chave
2. Top 6 criativos campeões (grid com imagens + dados)
3. Gráfico de cadência (timeline de quando lançou cada ad)
4. Distribuição de ângulos
5. Distribuição de funil
6. Lista expandível com TODOS os ads (filtros por formato/funil/ângulo)
7. Link pro briefing markdown

**Comando:**

```bash
python <SKILL_DIR>/scripts/build_html_report.py \
  --enriched <work_dir>/concorrente1/enriched_ads.json <work_dir>/concorrente2/enriched_ads.json \
  --analysis <work_dir>/analysis.json \
  --creatives-dir <work_dir>/criativos \
  --output-dir <output_dir>/relatorio_html
```

---

## Etapa 7 — Apresentação ao usuário

Use `present_files`. Ordem (primeiro = mais relevante):

1. `relatorio_html/index.html` — **principal**, abre no browser, mais visual
2. `briefings/_consolidado.md` — insumo de produção que fecha o ciclo
3. `relatorio_executivo.docx` — leitura linear pra cliente
4. `analise_concorrentes.xlsx` — exploração detalhada
5. `apresentacao.pptx` — pra reunião

Texto de fechamento: 3-5 frases. Destaque o achado mais surpreendente — não resuma o relatório inteiro. O usuário lê o documento sozinho.

---

## Princípios importantes

- **Evidência sempre vinculada a ID**: toda afirmação analítica cita pelo menos um `ad_archive_id`. Sem isso vira achismo.
- **Quando o sinal for fraco, diga**: "3 de 100 anúncios usam X — sinal fraco, pode ser ruído". Não force padrão onde não tem.
- **Limitações explícitas**: scraping pode ter perdido anúncios; alcance só está disponível em anúncios políticos; impressões não são públicas.
- **Não invente métricas**: a Meta Ad Library NÃO mostra impressões, cliques, gasto ou CTR para anúncios comerciais. Os únicos sinais são `days_running` (proxy forte) e `variations_count` (proxy médio). Não fabrique.
- **Compliance**: scraping de interface pública. Use rate limiting (já implementado), não redistribua os criativos como próprios, oriente uso para inteligência interna — não para republicação.

---

## Quando algo der errado

- **0 anúncios retornados**: verifique nome da página, tente o ID numérico, confira manualmente em `https://www.facebook.com/ads/library/?country=BR&q=<nome>`.
- **CAPTCHA/bloqueio**: aguarde 30min e retente, ou use VPN. Script salva progresso parcial.
- **Whisper lento**: troque `--whisper-model small` por `tiny`.
- **Planilha gigante (>50MB)**: limite a 50 anúncios por concorrente ou divida em planilhas separadas.

Detalhes em `references/scraping-troubleshooting.md`.

---

## Referências disponíveis

- `references/scraping-troubleshooting.md` — Adaptação quando seletores da Meta mudam
- `references/frameworks-de-analise.md` — Detalhamento dos frameworks de classificação
- `references/exemplos-de-recomendacoes.md` — Banco de exemplos de recomendações boas e ruins
