# Análise de Concorrentes — YouTube

> **Skill desenvolvida por Hoberdan Silva para os alunos da Mentoria Primia.**
> Versão 1.1.0 — Maio/2026

Skill que faz inteligência competitiva no YouTube voltada pra criação de infoprodutos. Não é "lista os vídeos do canal" — é traduzir dados em decisão de posicionamento, conteúdo e oferta. Entrega 4 arquivos: planilha completa, relatório estratégico, apresentação executiva e pasta de assets brutos.

---

## Índice rápido

- [O que essa skill faz](#o-que-essa-skill-faz)
- [Como instalar (passo a passo)](#como-instalar-passo-a-passo)
- [Configurar a YouTube API (recomendado)](#configurar-a-youtube-api-recomendado)
- [Como usar](#como-usar)
- [Resolução de problemas](#resolução-de-problemas)
- [Estrutura dos arquivos da skill](#estrutura-dos-arquivos-da-skill)

---

## O que essa skill faz

Ela analisa de 1 a 5 canais concorrentes do YouTube e gera **4 entregáveis profissionais**:

1. **Planilha `.xlsx`** — base de dados completa, com 7 abas (resumo, vídeos, top performers, comentários categorizados, voz do avatar, comparativo, recomendações).
2. **Relatório `.docx`** — documento estratégico estruturado (perfil de cada canal, mapa da voz do avatar com quotes literais, análise comparativa, banco de hooks, recomendações com plano de execução).
3. **Apresentação `.pptx`** — versão visual com top performers e principais achados, pronta pra compartilhar.
4. **Pasta de assets** — transcrições brutas, thumbnails, comentários em JSON pra consulta posterior.

**Diferencial vs. outras ferramentas de YouTube analytics:** essa skill foca em traduzir dados em decisão de copy e posicionamento. Os comentários da audiência são categorizados em dores, desejos, objeções, perguntas órfãs e vocabulário nativo — exatamente o que vai pra headline, página de vendas e VSL do cliente.

**3 modos de execução**, escolha conforme a profundidade necessária:

| Modo | Canais | Vídeos analisados | Tempo estimado |
|---|---|---|---|
| Rápido | 1 | 30 | 10–15 min |
| Padrão (default) | 3 | 50 cada | 25–40 min |
| Profundo | 5 | 100 cada | 60–90 min |

---

## Como instalar (passo a passo)

### Pré-requisitos

Você precisa de:

1. **Python 3.10 ou superior** instalado no computador
2. **Claude Code** instalado e configurado
3. (Opcional, mas recomendado) **Chave da YouTube Data API** — instruções na próxima seção

### Verificar se você tem Python

Abra o terminal:
- **Windows**: PowerShell (busque "PowerShell" no menu iniciar)
- **Mac**: Terminal (Cmd+Space → "Terminal")
- **Linux**: já sabe

Digite:

```bash
python --version
```

Se aparecer `Python 3.10.x` ou maior, você está pronto. Se aparecer "comando não encontrado" ou versão menor que 3.10, instale primeiro do site oficial: https://www.python.org/downloads/

> **Windows:** durante a instalação, MARQUE a caixinha "Add Python to PATH". Isso evita 90% dos problemas posteriores. Se mesmo assim `python` não funcionar, tente `py --version` (launcher oficial do Windows que sempre encontra o Python instalado).

### Passo 1 — Extrair a skill

O arquivo `analise-concorrentes-youtube.skill` é um zip renomeado. Você precisa extrair ele dentro de uma pasta específica que o Claude Code reconhece.

**Onde extrair (escolha um dos dois):**

- **Pasta global** (recomendado — vai funcionar em qualquer projeto seu):
  - Windows: `C:\Users\SeuUsuario\.claude\skills\`
  - Mac/Linux: `~/.claude/skills/`

- **Pasta do projeto** (skill específica deste projeto):
  - `<seu-projeto>/.claude/skills/`

**Como extrair:**

#### Windows (PowerShell)

```powershell
# 1. Cria a pasta se não existir
mkdir $env:USERPROFILE\.claude\skills -Force

# 2. Extrai o .skill nela (ajuste o caminho do arquivo)
Expand-Archive -Path "C:\caminho\para\analise-concorrentes-youtube.skill" -DestinationPath "$env:USERPROFILE\.claude\skills\" -Force
```

#### Mac/Linux

```bash
# 1. Cria a pasta se não existir
mkdir -p ~/.claude/skills/

# 2. Extrai o .skill nela (ajuste o caminho do arquivo)
unzip ~/Downloads/analise-concorrentes-youtube.skill -d ~/.claude/skills/
```

#### Alternativa visual (qualquer OS)

1. Renomeie o arquivo `analise-concorrentes-youtube.skill` pra `analise-concorrentes-youtube.zip`
2. Clique com botão direito → "Extrair tudo"
3. Mova a pasta extraída pra `~/.claude/skills/` (Mac/Linux) ou `C:\Users\SeuUsuario\.claude\skills\` (Windows)
4. Renomeie o arquivo de volta pra `.skill` (ou apague o zip)

### Passo 2 — Verificar se ficou certo

Abra o terminal e digite:

```bash
# Mac/Linux
ls ~/.claude/skills/analise-concorrentes-youtube/

# Windows
dir %USERPROFILE%\.claude\skills\analise-concorrentes-youtube\
```

Você deve ver:
```
SKILL.md
README.md
scripts/
references/
```

### Passo 3 — Instalar dependências Python

Ainda no terminal, navegue até a pasta da skill:

```bash
# Mac/Linux
cd ~/.claude/skills/analise-concorrentes-youtube/

# Windows
cd %USERPROFILE%\.claude\skills\analise-concorrentes-youtube\
```

Crie um virtualenv (recomendado — isola as dependências do resto do sistema):

```bash
# Cria
python -m venv .venv

# Ativa
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

Instale as dependências (lista canônica em `scripts/requirements.txt`):

```bash
pip install -r scripts/requirements.txt
```

Pronto. Skill instalada. **Lembre-se:** sempre que for usar a skill em uma sessão nova de terminal, ative o virtualenv antes (`source .venv/bin/activate` ou `.venv\Scripts\activate`).

---

## Configurar a YouTube API (recomendado)

A skill funciona de dois jeitos:

- **Com API** (recomendado): análise completa, incluindo o mapa da voz do avatar (dores, desejos, objeções, perguntas órfãs, vocabulário nativo).
- **Sem API**: análise de hooks, ângulos e funil funciona normalmente, mas **não coleta comentários** — perde a parte mais valiosa pra copy.

A API é **gratuita**, não pede cartão de crédito, e dá pra rodar mais de 100 análises por dia sem pagar nada.

### Passo a passo (10 minutos, uma única vez)

1. **Acesse** https://console.cloud.google.com/ e faça login com sua conta Google (a mesma do Gmail serve).

2. **Crie um projeto novo**: no topo da tela, clique no seletor de projeto → "Novo projeto" → dê um nome qualquer (ex: `analise-youtube`) → "Criar". Aguarde alguns segundos até aparecer selecionado no topo.

3. **Ative a YouTube Data API v3**: no menu lateral (☰), vá em **APIs e serviços → Biblioteca**. Na barra de busca, digite `YouTube Data API v3` → clique no resultado → clique no botão azul **"Ativar"**.

4. **Crie a chave**: no menu lateral, vá em **APIs e serviços → Credenciais** → **"+ Criar credenciais"** → **"Chave de API"**. Uma janelinha aparece com a chave (formato `AIza...`). **Copie essa chave**.

5. **(Opcional, recomendado) Restrinja a chave**: clique em "Restringir chave" → em "Restrições da API" escolha "Restringir chave" → marque apenas "YouTube Data API v3" → "Salvar". Isso evita uso indevido se a chave vazar.

6. **Configure no seu sistema**:

#### Windows (PowerShell, permanente)

```powershell
# Configura a variável permanentemente para o seu usuário
[Environment]::SetEnvironmentVariable("YOUTUBE_API_KEY", "AIza...sua-chave-aqui...", "User")
```

Feche e reabra o terminal pra a variável ficar disponível.

#### Mac/Linux

Adicione no final do `~/.zshrc` (Mac padrão) ou `~/.bashrc` (Linux):

```bash
export YOUTUBE_API_KEY="AIza...sua-chave-aqui..."
```

Depois rode `source ~/.zshrc` (ou `~/.bashrc`) ou abra um terminal novo.

#### Verificar que funcionou

```bash
# Mac/Linux
echo $YOUTUBE_API_KEY

# Windows
echo $env:YOUTUBE_API_KEY
```

Deve aparecer sua chave. Pronto — a skill detecta automaticamente toda vez que rodar.

### Compartilhar a chave com o time

Se você está configurando pra um time inteiro, **uma única chave pode ser usada por várias pessoas**. Configure você uma vez, salve num gerenciador de senhas compartilhado (1Password, Bitwarden, etc.), e cada pessoa do time configura a mesma chave no computador dela. A cota de 10.000 unidades/dia é compartilhada, mas dá conta de ~140 análises diárias.

---

## Como usar

Dentro do Claude Code, comece uma conversa com algo como:

```
Quero fazer uma análise de concorrentes do canal @nomedoconcorrente
```

Ou:

```
Espia o canal https://www.youtube.com/@criadorx
```

A skill é acionada automaticamente. O Claude vai:

1. Apresentar os dois modos (Com API / Sem API) e perguntar qual usar
2. Confirmar canais, modo de profundidade (Rápido/Padrão/Profundo) e janela temporal
3. Mostrar tempo estimado e pedir confirmação
4. Coletar tudo, analisar e gerar os 4 entregáveis

### Exemplos de prompts que ativam a skill

- "Analise o canal @hormozi"
- "Compara esses 3 canais: @canal1, @canal2, @canal3"
- "Quero entender o que [criador X] está postando ultimamente"
- "Faz um audit do canal https://youtube.com/@nomedele"
- "Mapeia os ângulos vencedores do [nicho/criador]"
- "Quero descobrir as dores do avatar do canal X"

### Onde os entregáveis ficam salvos

O Claude vai perguntar onde você quer salvar antes de rodar. Sugestões:
- **Windows**: `C:\Users\SeuUsuario\Documentos\analise-yt\`
- **Mac/Linux**: `~/Documentos/analise-yt/` ou `~/Downloads/analise-yt/`

Dentro dessa pasta, você vai encontrar os 3 arquivos (`.xlsx`, `.docx`, `.pptx`) + uma subpasta `assets/` com transcrições e thumbnails.

---

## Resolução de problemas

### "Comando python não encontrado" (Windows)

Reinstale o Python e marque a caixinha "Add Python to PATH" durante a instalação.

### "pip install" falha com erro de permissão

Você esqueceu de ativar o virtualenv. Volta pro Passo 3 e ativa antes de rodar `pip install`.

### "ModuleNotFoundError" ao rodar a skill

Suas dependências não foram instaladas. Verifique se o virtualenv está ativo e rode o `pip install` novamente.

### "quotaExceeded" durante a coleta

A cota diária da API estourou (raro — só acontece se você rodou muitas análises seguidas). Espere o reset à meia-noite Pacific Time (~04:00 ou 05:00 BRT) ou crie outra chave em outro projeto Google Cloud.

### Comentários vêm vazios em alguns vídeos

Normal. Acontece quando o criador desabilitou comentários naquele vídeo específico. A skill pula e segue.

### A skill não está sendo acionada quando peço

- Verifique se a pasta `analise-concorrentes-youtube/` está dentro de `~/.claude/skills/` (Mac/Linux) ou `%USERPROFILE%\.claude\skills\` (Windows)
- Verifique se o arquivo `SKILL.md` existe dentro dessa pasta
- Reinicie o Claude Code

### Preciso de ajuda mais detalhada

Veja os 3 arquivos de referência dentro da pasta `references/` da skill:
- `frameworks-de-analise.md` — taxonomias usadas (hooks, ângulos, funil, comentários)
- `coleta-troubleshooting.md` — problemas técnicos comuns
- `exemplos-de-recomendacoes.md` — calibração de qualidade dos outputs

---

## Estrutura dos arquivos da skill

```
analise-concorrentes-youtube/
├── SKILL.md                    # Manifesto principal (instruções pro Claude)
├── README.md                   # Este arquivo (instruções pra você)
├── scripts/
│   ├── requirements.txt           # Lista canônica de dependências Python
│   ├── resolve_channels.py        # Resolve URL/handle em channel_id
│   ├── fetch_channel_data.py      # Coleta metadados dos vídeos
│   ├── identify_top_performers.py # Ranqueia top vídeos
│   ├── fetch_transcripts.py       # Coleta transcrições
│   ├── fetch_comments.py          # Coleta comentários
│   ├── download_thumbnails.py     # Baixa thumbnails
│   ├── build_xlsx.py              # Gera planilha
│   ├── build_docx.py              # Gera relatório
│   └── build_pptx.py              # Gera apresentação
└── references/
    ├── frameworks-de-analise.md      # Taxonomias de classificação
    ├── coleta-troubleshooting.md     # Soluções pra erros comuns
    └── exemplos-de-recomendacoes.md  # Calibração de qualidade
```

---

## Suporte

Esta skill é de uso interno e educacional dos alunos da Mentoria Primia. Para suporte, dúvidas ou sugestões de melhoria, fale com o Hoberdan.
