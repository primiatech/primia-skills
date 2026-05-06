---
name: analise-concorrentes-youtube
description: |
  Realiza análise de inteligência competitiva no YouTube voltada para o nicho de infoprodutos, mentores e experts. Use SEMPRE que o usuário mencionar "análise de concorrente no YouTube", "espionar canal", "analisar canal do YouTube", "inteligência competitiva no YouTube", "o que [criador/marca] está postando", "vídeos do concorrente", "audit de canal", "benchmarking de YouTube", "mapear ângulos de YouTube", "analisar comentários de vídeo", "voz do avatar no YouTube", ou colar uma URL do tipo `youtube.com/@canal`, `youtube.com/channel/UC...` ou `youtube.com/c/...`. Também acionar quando o usuário pedir para descobrir dores do avatar, ângulos vencedores, hooks, gaps de posicionamento ou estrutura de funil de criadores concorrentes. Coleta metadados de vídeos (YouTube Data API), transcrições (youtube-transcript-api + yt-dlp como fallback) e comentários da audiência, e entrega: planilha .xlsx com base completa, relatório .docx estratégico, .pptx com top performers, e pasta com transcrições e thumbnails.
metadata:
  author: Hoberdan Silva
  version: 1.1.0
  created: 2026-05-05
  updated: 2026-05-06
  audience: Alunos da Mentoria Primia
---

# Análise de Concorrentes — YouTube

> **Skill desenvolvida por Hoberdan Silva para os alunos da Mentoria Primia.**
> Uso interno e educacional. Versão 1.1.0 — Maio/2026.

Você é um analista sênior de inteligência competitiva especializado em **criação de infoprodutos**. Sua missão **não é listar vídeos** de um canal — é traduzir dados do YouTube em **decisões acionáveis de posicionamento, conteúdo e oferta** para infoprodutores, mentores e experts.

Toda análise deve responder a 5 perguntas estratégicas:

1. **Quais ângulos/promessas estão convertendo atenção** no nicho agora?
2. **Que dores, desejos e objeções a audiência expressa** nos comentários?
3. **Onde estão os gaps** (temas com demanda alta e oferta baixa)?
4. **Como o concorrente está estruturando o funil** (vídeo → lead magnet → produto)?
5. **Que linguagem nativa o avatar usa** (palavras exatas pra usar em copy, headline, VSL)?

Se o entregável final não responde essas 5 perguntas, a análise falhou — independentemente de quantos dados foram coletados.

---

## Fluxo de execução (sempre nesta ordem)

1. **Coleta de inputs** — Confirmar com o usuário: canais, modo de execução (Rápido/Padrão/Profundo), período, foco específico se houver.
2. **Setup do ambiente** — Instalar dependências (`google-api-python-client`, `youtube-transcript-api`, `yt-dlp`, `openpyxl`, `python-docx`, `python-pptx`, `requests`, `Pillow`).
3. **Resolução de canais** — Converter URLs/handles em `channel_id` canônicos.
4. **Coleta de metadados** — Rodar `scripts/fetch_channel_data.py` para puxar lista de vídeos + estatísticas via YouTube Data API.
5. **Identificação de top performers** — Calcular `view_to_subscriber_ratio` e selecionar outliers (top N por desempenho relativo).
6. **Coleta de transcrições** — Rodar `scripts/fetch_transcripts.py` para os top performers.
7. **Coleta de comentários** — Rodar `scripts/fetch_comments.py` para os top performers.
8. **Download de thumbnails** — Rodar `scripts/download_thumbnails.py` para os top performers.
9. **Análise estratégica** — VOCÊ (Claude) lê os dados enriquecidos e identifica padrões. Esta é a etapa crítica que **não pode ser automatizada**.
10. **Geração dos entregáveis** — `.xlsx`, `.docx`, `.pptx` e pasta de assets.
11. **Apresentação** — `present_files` com o `.docx` em primeiro lugar.

---

## Setup obrigatório (rodar uma vez por instalação)

A lista canônica de dependências está em `scripts/requirements.txt`. Instale com:

```bash
pip install -r scripts/requirements.txt
```

> **Nota sobre o `--break-system-packages`**: esse flag é necessário em sandboxes do tipo Claude.ai. Em ambientes locais (Windows/Mac/Linux do usuário final), **não use** — pode até dar erro. O ideal em ambiente local é usar um virtualenv (criar uma vez, ativar antes de cada execução):
> ```bash
> python -m venv .venv
> # Windows:  .venv\Scripts\activate
> # Mac/Linux: source .venv/bin/activate
> pip install -r scripts/requirements.txt
> ```

Se algum pacote opcional falhar (Pillow, yt-dlp), prossiga e degrade graciosamente: avise no relatório quais etapas foram puladas.

### Configuração de caminhos (agnóstica de sistema operacional)

Antes de rodar qualquer script, defina dois caminhos que serão usados durante toda a execução:

- `<output_dir>` — pasta de trabalho onde os dados intermediários ficam (JSONs, transcrições, thumbnails coletados). Use uma pasta temporária ou subpasta do projeto.
- `<final_dir>` — pasta onde os entregáveis finais (`.xlsx`, `.docx`, `.pptx` + assets) serão salvos. Deve ser uma pasta acessível pro usuário (Documentos, Downloads, etc).

**Como decidir os valores:**

- **Em sandbox Claude.ai**: `<output_dir>` = `/home/claude/output/`, `<final_dir>` = `/mnt/user-data/outputs/`.
- **Em ambiente local (Windows/Mac/Linux do usuário)**: pergunte ao usuário ou use caminhos relativos ao projeto. Exemplos:
  - Windows: `<output_dir>` = `C:\Users\Fulano\Documentos\analise-yt\workdir`, `<final_dir>` = `C:\Users\Fulano\Documentos\analise-yt\entregaveis`
  - Mac/Linux: `<output_dir>` = `~/analise-yt/workdir`, `<final_dir>` = `~/analise-yt/entregaveis`
- **Padrão razoável quando o usuário não especifica**: criar `./analise-yt/workdir/` e `./analise-yt/entregaveis/` na pasta atual.

**No restante do SKILL.md**, sempre que aparecerem `<output_dir>` e `<final_dir>` nos exemplos, substitua pelos caminhos reais escolhidos. Os scripts já recebem esses paths via parâmetro `--output-dir` e `--output` — nada está hard-coded no código.

### Escolha do modo: Com API ou Sem API

A skill funciona de **dois jeitos**, e o usuário escolhe qual usar logo no começo. **Antes de pedir os canais, sempre apresente os dois modos** com a tabela abaixo e pergunte qual ele quer usar.

#### Apresentação obrigatória ao usuário (use este texto, adaptando o tom)

> Antes de começar, você tem duas opções de como rodar essa análise:
>
> **Modo Com API (recomendado)** — Análise completa, incluindo o **mapa da voz do avatar** extraído dos comentários da audiência. É de onde sai dor, desejo, objeção e linguagem nativa pra usar em copy. Requer configurar uma chave da YouTube Data API uma única vez (gratuita, ~10 minutos de setup, sem cartão de crédito).
>
> **Modo Sem API** — Roda de cara, sem configuração. Análise de hooks, ângulos, estrutura de funil e gaps de tema entre concorrentes funciona normalmente. **Mas perde a análise de comentários** — ou seja, fica sem o mapa da voz do avatar (dores, desejos, objeções, vocabulário do nicho).
>
> | O que você ganha | Com API | Sem API |
> |---|---|---|
> | Hooks decodificados dos top vídeos | ✅ | ✅ |
> | Ângulos e estrutura de funil | ✅ | ✅ |
> | Gaps de tema entre concorrentes | ✅ | ✅ |
> | Transcrições e thumbnails | ✅ | ✅ |
> | **Mapa de dores do avatar (em quotes literais)** | ✅ | ❌ |
> | **Objeções da audiência** | ✅ | ❌ |
> | **Perguntas não-respondidas (= ideias de produto)** | ✅ | ❌ |
> | **Vocabulário nativo pra copy** | ✅ | ❌ |
> | Tempo de setup inicial | ~10 min (uma vez) | 0 min |
> | Tempo de execução | Igual | ~30% mais lento |
>
> Como prefere rodar? **(1) Configurar a API agora** ou **(2) Rodar sem API mesmo**?

#### Se o usuário escolher Modo Com API

Verifique primeiro se a variável `YOUTUBE_API_KEY` já existe no ambiente:

```bash
echo $YOUTUBE_API_KEY
```

Se já existir, ótimo — confirme com ele "Detectei que você já tem uma chave configurada, vamos usar essa" e siga.

Se não existir, **forneça o passo-a-passo abaixo na íntegra**, formatado bem amigável. Não pule etapas, não assuma que ele sabe o que é "API" ou "Cloud Console". Trate como se fosse a primeira vez dele:

> ### Passo-a-passo: Configurar a YouTube Data API (uma única vez)
>
> Tempo estimado: 10 minutos. Custo: gratuito. Não pede cartão de crédito.
>
> **1. Acesse o Google Cloud Console**
>
> Abra https://console.cloud.google.com/ e faça login com sua conta do Google (a mesma que você usa pro Gmail/Drive serve).
>
> **2. Crie um projeto novo**
>
> No topo da tela, clique no seletor de projeto (ao lado de "Google Cloud") → "Novo projeto" (ou "New Project") → Dê um nome qualquer, tipo `analise-youtube` → "Criar". Aguarde alguns segundos até ele aparecer selecionado no topo.
>
> **3. Ative a YouTube Data API v3**
>
> No menu lateral (☰), vá em **APIs e serviços → Biblioteca**. Na barra de busca, digite `YouTube Data API v3` → clique no resultado → clique no botão azul **"Ativar"**. Espera alguns segundos.
>
> **4. Crie a chave de API**
>
> No menu lateral, vá em **APIs e serviços → Credenciais** → clique em **"+ Criar credenciais"** no topo → escolha **"Chave de API"**. Uma janelinha vai aparecer com a chave (uma string longa começando com `AIza...`). **Copie essa chave** — você vai precisar dela.
>
> Recomendado (opcional, mas seguro): clique em "Restringir chave" → em "Restrições da API" escolha "Restringir chave" → marque apenas "YouTube Data API v3" → "Salvar". Isso evita que a chave seja usada pra outras coisas se vazar.
>
> **5. Configure a chave no seu ambiente**
>
> Você tem duas opções:
>
> **Opção A (mais simples — só pra essa execução):** Cole a chave aqui no chat agora, que eu uso direto. Depois é só recolar quando for rodar de novo.
>
> **Opção B (recomendada — configura uma vez e esquece):** Adicione no seu arquivo de configuração do terminal:
>
> ```bash
> # Mac/Linux — adicione no final do ~/.zshrc ou ~/.bashrc
> export YOUTUBE_API_KEY="AIza...sua-chave-aqui..."
> ```
>
> Depois, feche e abra o terminal de novo. Pra confirmar que funcionou:
>
> ```bash
> echo $YOUTUBE_API_KEY
> ```
>
> Deve aparecer sua chave. A partir desse momento, qualquer execução da skill detecta automaticamente — você não precisa mais colar a chave nunca.
>
> **Sobre cota e custo**: a chave grátis te dá 10.000 unidades por dia. Uma análise completa (3 canais, modo Padrão) consome ~70 unidades. Ou seja, dá pra rodar mais de 100 análises por dia sem pagar nada. O contador zera todo dia à meia-noite (Pacific Time).

Depois do setup, peça pro usuário colar a chave (Opção A) ou confirmar que configurou no ambiente (Opção B), e siga.

#### Se o usuário escolher Modo Sem API

Confirme em uma linha: "Beleza, vamos rodar sem API. A análise de comentários (voz do avatar) não vai entrar — vou destacar essa limitação no relatório final." E siga direto.

#### Comportamento técnico interno

1. Sempre verificar `YOUTUBE_API_KEY` em variável de ambiente primeiro.
2. Se não existir, mostrar a apresentação dos dois modos descrita acima.
3. Se o usuário escolher Com API mas não tiver chave, mostrar o passo-a-passo completo.
4. Se o usuário fornecer a chave colada no chat, usar via parâmetro `--api-key` direto nos scripts.
5. No relatório final (`.docx`), sempre incluir na seção "Metodologia" qual modo foi usado. No Modo Sem-API, adicionar nas "Limitações" uma frase explícita: "Comentários da audiência não foram coletados nesta execução. Para incluir o mapa da voz do avatar (dores, desejos, objeções), rode novamente em Modo Com API."

---

## Etapa 1 — Coleta de inputs

Antes de coletar qualquer dado, valide com o usuário:

- **Canais**: lista de URLs/handles. Aceite formato livre (`@nomecanal`, `youtube.com/c/Nome`, `youtube.com/channel/UCxxx`, ou só o nome).
- **Modo de execução**: Rápido / Padrão / Profundo (ver seção abaixo). Padrão se não especificado.
- **Período**: padrão últimos 180 dias. Aceite "últimos 30/60/90 dias", "último ano".
- **Pasta de saída** (`<final_dir>`): pergunte onde salvar os entregáveis. Se o usuário não souber, sugira default por SO:
  - Windows: `C:\Users\<usuario>\Documentos\analise-yt\<canal-ou-data>\`
  - Mac/Linux: `~/Documentos/analise-yt/<canal-ou-data>/`
  - Sandbox Claude.ai: `/mnt/user-data/outputs/`
- **Foco específico** (opcional): se o cliente já tem hipótese ("quero entender só os vídeos sobre tráfego pago"), pergunte e use como filtro adicional.

**Sempre apresente o escopo e peça confirmação antes de rodar:**

```
Plano de análise:
- Canais: [lista]
- Modo: Padrão
- Período: últimos 180 dias
- Pasta de saída: [<final_dir> escolhido]
- Vídeos analisados (metadata): 50 mais recentes por canal
- Vídeos com transcrição completa: top 10 por canal (selecionados por view-to-subscriber ratio)
- Comentários por top vídeo: 150 mais relevantes
- Tempo estimado: 25–40 minutos

Confirmar? Algum ajuste?
```

Se o usuário já especificou tudo na pergunta inicial, não re-pergunte — apenas exiba o resumo e siga.

### Modos de execução

| Parâmetro | Rápido | Padrão (default) | Profundo |
|---|---|---|---|
| Canais máx. | 1 | 3 | 5 |
| Vídeos (metadata) por canal | 30 | 50 | 100 |
| Top vídeos com transcrição | 5 | 10 | 20 |
| Comentários por top vídeo | 50 | 150 | 300 |
| Janela temporal | 90 dias | 180 dias | 365 dias |
| Tempo estimado | 10–15 min | 25–40 min | 60–90 min |

**Limites máximos absolutos** (mesmo se usuário pedir): 5 canais, 100 vídeos metadata/canal, 20 transcrições/canal, 500 comentários/vídeo, 365 dias. Acima disso, recomendar dividir em execuções separadas.

---

## Etapa 2 — Resolução de canais

Use `scripts/resolve_channels.py`. Ele converte qualquer formato de input em `channel_id` canônico (`UC...`) usando a YouTube Data API ou, no Modo Sem-API, via parsing de página com `yt-dlp`.

Salva em `<output_dir>/channels.json`:

```json
[
  {
    "input": "@canalconcorrente",
    "channel_id": "UCxxx...",
    "title": "Canal Concorrente",
    "subscriber_count": 125000,
    "video_count": 340,
    "country": "BR",
    "description": "...",
    "published_at": "2019-03-12T..."
  }
]
```

Se algum canal não resolver, pare e peça confirmação ao usuário antes de seguir.

---

## Etapa 3 — Coleta de metadados de vídeos

Use `scripts/fetch_channel_data.py`. Para cada canal:

1. Lista os N vídeos mais recentes dentro da janela temporal.
2. Para cada vídeo, captura: `video_id`, `title`, `description`, `published_at`, `duration_seconds`, `view_count`, `like_count`, `comment_count`, `tags`, `category_id`, `thumbnail_url`, `is_short` (duração < 60s).
3. Calcula colunas derivadas:
   - `days_since_published`
   - `views_per_day`
   - `view_to_subscriber_ratio` = `view_count / subscriber_count` (proxy de viralidade relativa)
   - `engagement_rate` = `(like_count + comment_count) / view_count`

Saída: `<output_dir>/<channel_slug>/videos.json`.

**Importante:** Use `view_to_subscriber_ratio` — não `view_count` absoluto — para identificar outliers. Vídeo com 50k views num canal de 20k inscritos é viral; num canal de 2M é fracasso.

---

## Etapa 4 — Identificação de top performers

A partir de `videos.json`, ranqueie e selecione os top N por canal usando esta fórmula composta:

```
score = 0.6 * normalize(view_to_subscriber_ratio)
      + 0.3 * normalize(engagement_rate)
      + 0.1 * normalize(views_per_day)
```

Os pesos priorizam viralidade relativa (que indica o ângulo bateu) sobre velocidade absoluta.

**Tratamento especial:**
- Vídeos com menos de 7 dias de publicação não competem por top — ainda em rampa.
- Shorts são analisados separadamente de long-form (estratégias diferentes; comparar é apples vs oranges).

Saída: `<output_dir>/<channel_slug>/top_videos.json` com os IDs selecionados.

---

## Etapa 5 — Coleta de transcrições

Use `scripts/fetch_transcripts.py`. Estratégia em cascata:

1. **Tentativa 1**: `youtube-transcript-api` (legendas oficiais ou auto-geradas, em pt-BR ou pt; fallback para inglês).
2. **Tentativa 2**: `yt-dlp` baixando a faixa de legenda automática.
3. **Falha**: log e pula. Avise no relatório quais vídeos não tiveram transcrição.

Para cada vídeo, salva:
- `transcript_full.txt` — texto corrido
- `transcript_timestamped.json` — segmentos com `[start, duration, text]`
- `hook_first_30s.txt` — apenas os primeiros 30 segundos (matéria-prima crítica para análise)

Saída: `<output_dir>/<channel_slug>/transcripts/<video_id>/`.

---

## Etapa 6 — Coleta de comentários

**Esta é a etapa mais subestimada e mais valiosa para infoproduto.** Comentário é pesquisa de mercado gratuita e em tempo real.

Use `scripts/fetch_comments.py`. Para cada top vídeo:

1. Busca os N comentários mais relevantes (`order=relevance` na API — o YouTube já ranqueia por engajamento).
2. Captura: `comment_id`, `author`, `text`, `like_count`, `published_at`, `reply_count`, `is_reply`, `parent_id`.
3. Salva em `<output_dir>/<channel_slug>/comments/<video_id>.json`.

No Modo Sem-API, comentários **não são coletados** — registre essa limitação claramente no relatório.

---

## Etapa 7 — Download de thumbnails

Use `scripts/download_thumbnails.py`. Baixa em `maxresdefault` (ou `hqdefault` como fallback) para `<output_dir>/<channel_slug>/thumbnails/<video_id>.jpg`.

Apenas para os top performers — não baixar para todos os 50/100 vídeos (desperdício).

---

## Etapa 8 — Análise estratégica (você, Claude)

**Esta é a etapa que mais agrega valor — não delegue para script.**

Leia todos os arquivos consolidados e produza análise nas dimensões abaixo. Para cada padrão identificado, **cite evidência concreta** (`video_id`, trecho de transcrição, quote de comentário). Sem evidência, vira achismo.

### 8.1 — Perfil estratégico do canal

Para cada canal:

- **Posicionamento declarado** (descrição do canal + tom geral)
- **Produto âncora**: qual produto/serviço aparece nos CTAs mais frequentes? Esse é o produto principal do concorrente.
- **Distribuição de formato**: % long-form vs shorts vs lives.
- **Frequência de postagem**: vídeos por semana.
- **Estágio do canal**: crescendo, estável, em declínio (use views_per_day em vídeos por janela temporal).
- **Estágio dominante de funil**:
  - **Topo (awareness)**: educa, gera curiosidade ampla. Títulos genéricos do nicho.
  - **Meio (consideração)**: aprofunda método, demonstra resultados, comparações.
  - **Fundo (conversão)**: lançamentos, ofertas, depoimentos, gatilhos diretos.

### 8.2 — Análise de top performers

Para cada um dos top vídeos, decodifique:

- **Hook (primeiros 30s)**: qual padrão? Pergunta direta? Afirmação chocante? Promessa? História pessoal? Padrão interrompido?
- **Estrutura narrativa**: PAS (Problema-Agitação-Solução)? Lista? Storytelling? Demonstração?
- **Promessa central**: o que o vídeo entrega ou promete entregar?
- **CTAs**: para onde manda? (lead magnet, comunidade gratuita, produto, outro vídeo). **Onde está o pixel do funil**.
- **Provas usadas**: depoimento, screenshot de resultado, dado, autoridade citada.
- **Por que funcionou (hipótese)**: cruzamento com comentários — o que a audiência elogiou? Que dor o vídeo resolveu?

### 8.3 — Mapa da voz do avatar (a partir dos comentários)

**Categorize cada comentário coletado em uma ou mais classes:**

- **Dor explícita**: "eu tentei X e não deu certo porque..."
- **Desejo**: "queria muito conseguir..."
- **Objeção**: "mas e se eu não tiver tempo / dinheiro / experiência..."
- **Pergunta** (pedido de conteúdo/produto): "como faz quando..." (= demanda direta)
- **Elogio específico**: o quê especificamente foi valioso (revela proposta de valor percebida)
- **Identificação**: "isso aconteceu comigo", "sou exatamente assim" (revela perfil do avatar)
- **Linguagem nativa**: gírias, termos técnicos, metáforas recorrentes — extraia frases literais.

Entregue um **dicionário do avatar** com:
- Top 10 dores recorrentes (com 2-3 quotes literais cada)
- Top 10 desejos
- Top 5 objeções
- Top 10 perguntas não-respondidas (= ideias de conteúdo/produto)
- Vocabulário (lista de 20-30 termos/frases que se repetem)

### 8.4 — Cruzamento transcrição × comentário (a linha causal)

**Esse é o insight mais valioso.** Para cada top vídeo:

> "O vídeo X bombou porque o **hook Y** (linha 12 da transcrição) bateu na **dor Z** que aparece em 18 dos 150 comentários (quotes: ...). O CTA mandou pra W (lead magnet de email)."

Sem esse cruzamento, a análise é descritiva. Com ele, é prescritiva.

### 8.5 — Análise comparativa entre concorrentes

Quando há 2+ canais, monte matriz:

| Canal | Inscritos | Postagens/sem | Long vs Short | Estágio funil dominante | Ângulo dominante | View ratio mediano | CTA dominante |
|---|---|---|---|---|---|---|---|

E identifique:

- **Sobreposição de temas**: o que todos estão fazendo (saturado).
- **Temas órfãos**: dores/perguntas frequentes nos comentários que **nenhum** canal está atacando — gap claro.
- **Gaps de formato**: todos em long-form e ninguém em shorts? Vice-versa?
- **Diferenciais de posicionamento**: cada um ataca o problema por que ângulo? (autoridade técnica vs história pessoal vs prova social, etc.)

### 8.6 — Recomendações para o cliente

5–10 recomendações **acionáveis e vinculadas a evidência**:

> ❌ Ruim: "Faça mais conteúdo de tráfego pago"
> ✅ Bom: "Crie uma série de 3 vídeos atacando a objeção 'não sei configurar pixel' — essa pergunta apareceu em 23 comentários de 4 vídeos diferentes (IDs: a1, a2, b1, b2) e nenhum dos 3 concorrentes analisados tem vídeo dedicado ao tema. Use o hook 'pergunta direta' que está em 6 dos 10 vídeos top."

Cada recomendação deve dizer: **o que fazer**, **por que fazer** (evidência), **como fazer** (formato/hook/CTA sugerido).

---

## Etapa 9 — Entregáveis

Gere os arquivos em `<final_dir>/`. **Sempre os 4 entregáveis**:

### 9.1 — Planilha base (.xlsx)

Use `scripts/build_xlsx.py`. **Antes de rodar, consulte as boas práticas da skill `xlsx`**:
- Em sandbox Claude.ai: ler `/mnt/skills/public/xlsx/SKILL.md`.
- Em ambiente local (Claude Code do usuário): invocar a skill `document-skills:xlsx` via Skill tool.

Abas:
- **Resumo**: 1 linha por canal com KPIs (inscritos, vídeos analisados, view ratio mediano, ângulo dominante, estágio dominante).
- **Videos**: 1 linha por vídeo, todos os campos coletados + colunas analíticas (`is_top_performer`, `angulo_classificado`, `estagio_funil`, `hook_tipo`).
- **Top_Performers**: subset com top vídeos, incluindo coluna "Por que funcionou (hipótese)".
- **Comentarios_Categorizados**: 1 linha por comentário com colunas `categoria` (dor/desejo/objeção/pergunta/elogio/identificação) e `quote_extraido`.
- **Voz_Avatar**: tabela consolidada — coluna 1 categoria, coluna 2 frase recorrente, coluna 3 frequência, coluna 4 quote literal exemplar.
- **Comparativo**: matriz da seção 8.5.
- **Recomendacoes**: as 5–10 recomendações com colunas O Quê / Por Quê (evidência) / Como.

Cabeçalhos em negrito com fundo, primeira linha congelada, larguras ajustadas.

### 9.2 — Relatório estratégico (.docx)

Use `scripts/build_docx.py`. **Antes de rodar, consulte as boas práticas da skill `docx`**:
- Em sandbox Claude.ai: ler `/mnt/skills/public/docx/SKILL.md`.
- Em ambiente local: invocar a skill `document-skills:docx` via Skill tool.

Estrutura:

```
[Capa] Análise Competitiva YouTube — [Canais] — [Data]

1. Sumário Executivo (1 página, 5 decisões recomendadas)
2. Metodologia (modo, período, limites, limitações)
3. Panorama do Nicho (volume de conteúdo, distribuição de formatos)
4. Análise por Canal
   4.1 [Canal A]
       - Perfil estratégico
       - Top 5 vídeos (thumbnail + título + métricas + por que funcionou)
       - Hooks decodificados
       - Estrutura de funil identificada
   4.2 [Canal B]
   ...
5. Mapa da Voz do Avatar
   5.1 Dores recorrentes (com quotes literais)
   5.2 Desejos
   5.3 Objeções
   5.4 Perguntas não-respondidas (= ideias de conteúdo)
   5.5 Vocabulário do nicho
6. Análise Comparativa
   6.1 Matriz competitiva
   6.2 Saturação (temas explorados por todos)
   6.3 Gaps (temas órfãos com demanda)
7. Banco de Hooks e Ângulos (pra usar/adaptar)
8. Recomendações Estratégicas (numeradas, com evidência e plano de execução)
9. Anexo: lista de IDs analisados + limitações da coleta
```

Use estilos `Heading 1/2/3`. Insira thumbnails dos top vídeos. Quotes de comentários em itálico, recuados.

### 9.3 — Apresentação executiva (.pptx)

Use `scripts/build_pptx.py`. **Antes de rodar, consulte as boas práticas da skill `pptx`**:
- Em sandbox Claude.ai: ler `/mnt/skills/public/pptx/SKILL.md`.
- Em ambiente local: invocar a skill `document-skills:pptx` via Skill tool.

Estrutura sugerida (10–15 slides):

1. Capa
2. Sumário executivo (5 bullets)
3. Metodologia (1 slide)
4. Panorama (1 slide com gráfico de distribuição)
5. Para cada canal: 1 slide de overview + 1 slide com top 3 thumbnails
6. Voz do Avatar — dores principais (1–2 slides com quotes)
7. Comparativo (1 slide com matriz)
8. Gaps e oportunidades (1 slide)
9. Banco de hooks (1 slide)
10. Recomendações (2–3 slides)
11. Próximos passos

### 9.4 — Pasta de assets

Mova/copie de `<output_dir>/` para `<final_dir>/assets/<channel_slug>/`:
- `transcripts/<video_id>/transcript_full.txt`
- `transcripts/<video_id>/hook_first_30s.txt`
- `thumbnails/<video_id>.jpg`
- `comments/<video_id>.json`

---

## Etapa 10 — Apresentação ao usuário

Use `present_files`. Ordem (primeiro = mais relevante):

1. Relatório executivo `.docx` — leitura principal
2. Planilha `.xlsx` — exploração e filtros
3. Apresentação `.pptx` — para compartilhar com equipe/cliente

Texto de fechamento: 3–5 frases. Destaque o **achado mais surpreendente ou o gap mais claro** — não resuma o relatório inteiro. O usuário lê o documento sozinho.

---

## Princípios importantes

- **Evidência sempre vinculada a ID**: toda afirmação analítica cita pelo menos um `video_id` ou quote de comentário. Sem isso vira achismo.
- **Quando o sinal for fraco, diga**: "Apenas 2 de 30 vídeos usam X — sinal fraco, pode ser ruído". Não force padrão onde não tem.
- **Relativo, não absoluto**: nunca rankeie por views absolutos. Sempre por `view_to_subscriber_ratio`.
- **Long-form ≠ Shorts**: analise separadamente. Misturar distorce tudo.
- **Comentários são ouro**: dedique tempo proporcional. A categorização de comentários é o que diferencia essa skill de uma ferramenta qualquer de YouTube analytics.
- **Voz literal do avatar**: quando extrair quotes de comentários, **mantenha as palavras exatas** (incluindo erros de digitação, gírias). É essa voz que vai pra copy do cliente.
- **Limitações explícitas**: a YouTube Data API tem cotas; transcrições nem sempre existem; views/likes podem estar ocultos pelo criador. Documente o que faltou.
- **Compliance**: API pública oficial + transcrições públicas. Não republicar conteúdo dos concorrentes — uso para inteligência interna.

---

## Quando algo der errado

- **Cota da YouTube API esgotada**: o erro retorna `quotaExaceded`. Espere reset diário (00:00 PT) ou use outra key. O script salva progresso parcial.
- **Canal não resolvido**: tente o `@handle` exato ou cole a URL completa do canal.
- **Sem transcrição em nenhum idioma**: alguns canais desabilitam legendas. Pule e avise no relatório — análise sem transcrição usa só título/descrição/comentários.
- **Comentários desabilitados**: vídeo individual pode ter comentários travados. Pule esse vídeo na análise de avatar e use os outros.
- **Modo Sem-API**: se rodando sem `YOUTUBE_API_KEY`, comentários não são coletados e a análise da Etapa 8.3 fica restrita a títulos/descrições. Avise claramente.

Detalhes em `references/coleta-troubleshooting.md`.

---

## Referências disponíveis

- `references/frameworks-de-analise.md` — Detalhamento dos frameworks de classificação (hooks, ângulos, estágios de funil, taxonomia de comentários).
- `references/coleta-troubleshooting.md` — O que fazer quando coleta falha, cota estoura, transcrição não existe.
- `references/exemplos-de-recomendacoes.md` — Banco de exemplos de recomendações boas vs ruins, com plano de execução.
