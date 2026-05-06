# Primia Instagram Analyst

**Versão:** 1.1.0
**Autor:** Hoberdan Silva
**Audiência:** Alunos da Mentoria Primia + uso geral em Claude.ai

Skill que mapeia quem está comentando nos seus posts do Instagram, cruza cada perfil com o seu cliente ideal (ICP) e devolve uma planilha pronta pra você decidir quem abordar primeiro.

A coleta de dados acontece pelo Claude Cowork, que controla o seu Chrome como se fosse uma pessoa navegando. Você fica logado normalmente, a skill faz o trabalho.

---

## Índice rápido

1. [O que essa skill faz](#o-que-essa-skill-faz)
2. [Pré-requisitos](#pré-requisitos)
3. [Como instalar](#como-instalar)
4. [Como usar](#como-usar)
5. [Os 3 modos](#os-3-modos)
6. [Onde os outputs ficam salvos](#onde-os-outputs-ficam-salvos)
7. [Resolução de problemas](#resolução-de-problemas)
8. [Limites de uso recomendados](#limites-de-uso-recomendados)
9. [Estrutura dos arquivos](#estrutura-dos-arquivos)

---

## O que essa skill faz

Você manda a URL do seu perfil e descreve seu ICP. A skill abre o Chrome (pelo Cowork), entra no seu Instagram, lê os comentários dos seus últimos posts, visita o perfil de cada comentarista e avalia quem é cliente em potencial.

No final, você recebe uma planilha onde cada lead já vem categorizado por temperatura comercial. Sem precisar olhar perfil por perfil na mão.

A skill tem três modos (PESADO, LEVE-A, LEVE-B) — detalhes na seção [Os 3 modos](#os-3-modos).

Saídas possíveis:

- `.xlsx` com cores por categoria, hyperlinks pros perfis, freeze panes e autofiltro (PESADO e LEVE-B).
- Lista formatada direto no chat com DMs sugeridas (LEVE-A).

---

## Pré-requisitos

Você precisa de 4 coisas antes de instalar:

1. **Python 3.10 ou superior** instalado no seu computador.
   - Pra checar, abra o terminal (Mac/Linux) ou Prompt de Comando (Windows) e rode:
     ```bash
     python --version
     ```
   - Se aparecer "Python 3.10.x" ou maior, tá ok. Se aparecer 3.9 ou menor, atualize em [python.org/downloads](https://www.python.org/downloads/).
2. **Google Chrome** instalado.
3. **Claude Cowork** (a versão de desktop ou a extensão do Chrome). Sem o Cowork, a skill não roda.
4. **Conta do Instagram logada** no Chrome onde o Cowork está conectado.

---

## Como instalar

### Passo 1 — Extrair a skill na pasta do Claude

A skill fica numa pasta chamada `~/.claude/skills/` (Mac/Linux) ou `%USERPROFILE%\.claude\skills\` (Windows).

**Mac/Linux:**

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
unzip ~/Downloads/primia-instagram-analyst-v1.1.0.zip
```

**Windows (Prompt de Comando):**

```cmd
mkdir %USERPROFILE%\.claude\skills 2>nul
cd %USERPROFILE%\.claude\skills
tar -xf %USERPROFILE%\Downloads\primia-instagram-analyst-v1.1.0.zip
```

Depois disso, você deve ter uma pasta `primia-instagram-analyst/` dentro de `~/.claude/skills/`.

### Passo 2 — Criar virtualenv

Virtualenv é um Python isolado pra essa skill. Evita que dependências dela conflitem com outros projetos seus.

```bash
cd ~/.claude/skills/primia-instagram-analyst
python -m venv .venv
```

No Windows o caminho usa `\` no lugar de `/`, mas o comando é o mesmo.

### Passo 3 — Ativar virtualenv e instalar dependências

**Mac/Linux:**

```bash
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

**Windows:**

```cmd
.venv\Scripts\activate
pip install -r scripts\requirements.txt
```

Você sabe que o virtualenv está ativo quando aparece `(.venv)` no começo da linha do terminal.

### Passo 4 — Instalar Claude Cowork no Chrome

Baixa em [claude.ai/download](https://claude.ai/download) ou pela Chrome Web Store. Depois de instalar, confirma que o ícone do Cowork aparece na barra de extensões.

### Passo 5 — Logar no Instagram

Abre o Chrome, ativa o Cowork (clica no ícone se estiver cinza), entra em [instagram.com](https://www.instagram.com/) e loga na sua conta. Deixa essa aba aberta.

### Passo 6 — Sanity check

Confirma que a dependência foi instalada certinho. Com o virtualenv ativo:

```bash
python -c "import openpyxl; print('OK')"
```

Se aparecer `OK`, tá tudo pronto. Se der erro, volta no Passo 3 e confirma que o virtualenv está ativo (tem que ter `(.venv)` no começo da linha).

---

## Como usar

A skill é ativada por linguagem natural. Não tem comando. Você só fala com o Claude.

### Frases-gatilho que ativam a skill

Qualquer uma dessas funciona:

- "Analisar comentaristas do Instagram"
- "Mapear minha audiência ativa"
- "Quem está comentando nos meus posts"
- "Identificar leads no Instagram"
- "Auditoria de Instagram"
- "Leads quentes do Insta"
- "Rotina mensal de Instagram"

Você também pode colar a URL do seu perfil pedindo análise da audiência.

### Exemplo de prompt completo

```
Roda a auditoria mensal de Instagram pra mim.

Perfil: instagram.com/seuperfil
ICP: infoprodutores que vendem cursos ou mentorias, faturamento entre
10k e 100k por mês, geralmente entre 30 e 45 anos, com audiência
acima de 5k seguidores.

Modo PESADO.
```

A skill confirma em uma linha o que entendeu, abre o Chrome e começa. Você não precisa ficar olhando.

---

## Os 3 modos

| Modo | Quando usar | Posts | Saída | Tempo |
|---|---|---|---|---|
| **PESADO** | Auditoria mensal, visão estratégica | 30 | Planilha .xlsx com 11 colunas + aba Resumo (categorias: Fã Recorrente ICP, Diamante Oculto, Engajador Frequente, Observar, Descartar) | 30 min a 3 h |
| **LEVE-A** | Triagem semanal, ação rápida | 5 | Lista no chat com até 15 leads + DM sugerida pra cada um | 5 a 15 min |
| **LEVE-B** | Triagem semanal com histórico | 5 | Planilha .xlsx enxuta (6 colunas: username, link, ICP, temperatura, comentário, DM) | 5 a 15 min |

Se você não disser qual modo quer, a skill pergunta uma vez. Se não souber, vai de PESADO.

---

## Onde os outputs ficam salvos

No **sandbox Claude.ai**, a planilha aparece direto no chat pra você baixar.

No **uso local** (Claude Code ou Claude Desktop), os arquivos saem em:

- Mac/Linux: `~/.claude/outputs/primia-instagram-analyst/`
- Windows: `%USERPROFILE%\.claude\outputs\primia-instagram-analyst\`

O nome do arquivo segue o padrão `comentaristas_<data>.xlsx`. Cada execução gera um arquivo novo, sem sobrescrever o anterior, então você consegue comparar mês a mês.

---

## Resolução de problemas

### "Não consegui acessar o Chrome via Cowork"

Provavelmente uma dessas três:

1. O Cowork não está aberto. Abre ele.
2. O Chrome está fechado. Abre o Chrome.
3. A extensão do Cowork está desativada. Olha o ícone na barra do Chrome — se estiver cinza, clica e ativa.

### O Instagram pediu captcha ou mostrou "ação bloqueada"

Acontece quando o Instagram detecta movimento incomum. A skill já para sozinha quando isso acontece. O que fazer:

- Aguarda 24 a 48 horas antes de rodar de novo.
- Não tenta forçar.
- Se aparecer com frequência, espaça mais as execuções.

### A skill voltou com 0 comentaristas

Possíveis causas:

- O perfil analisado não teve comentários nos últimos posts (acontece com perfis novos ou pouco engajados).
- Os posts são reels promocionais ou collabs, que a skill pula por padrão.
- O Instagram não carregou os comentários (raro, mas acontece). Tenta de novo.

### `ModuleNotFoundError: No module named 'openpyxl'`

O virtualenv não está ativo, ou a dependência não foi instalada. Reativa o virtualenv (Mac/Linux: `source .venv/bin/activate` / Windows: `.venv\Scripts\activate`) e roda de novo `pip install -r scripts/requirements.txt`.

### "Como sei se o virtualenv está ativo?"

Tem que aparecer `(.venv)` no começo da linha do terminal. Se não aparece, ele não está ativo — roda o comando de ativação acima.

### A planilha saiu, mas algumas linhas têm "Não identificada" em Profissão

Normal. Quando a bio do perfil é vazia ou genérica, a skill marca assim e baixa a confiança da nota. Esses leads estão na planilha pra você reavaliar manualmente se quiser.

---

## Limites de uso recomendados

O Instagram tem detecção anti-automação. Mesmo com a skill calibrada pra agir como humano, vale segurar a mão:

- **PESADO:** no máximo 1 vez por mês.
- **LEVE-A ou LEVE-B:** no máximo 1 a 2 vezes por semana.

Se você rodar mais que isso, a chance de cair em captcha sobe. E se cair com frequência, o Instagram pode aplicar limite temporário em ações da sua conta. Não vale a pena.

Cadência sugerida pros mentorados:

- Toda segunda-feira de manhã: LEVE-A pra abordar 3-5 leads quentes da semana anterior.
- Primeira segunda do mês: PESADO pra ter visão consolidada.
- Depois de um post viral: LEVE-B pra arquivar quem apareceu, sem perder ninguém.

---

## Estrutura dos arquivos

```
primia-instagram-analyst/
├── SKILL.md              o cérebro: como a skill se comporta
├── README.md             este arquivo
├── .gitignore            ignora arquivos temporários
├── scripts/
│   ├── requirements.txt  lista de dependências Python
│   └── build_planilha.py gera o .xlsx final
└── references/
    ├── rubrica-icp.md    como atribuir nota 0-10 e categoria
    └── prompts-dm.md     templates de DM por categoria
```

Os arquivos em `references/` são lidos pelo Claude conforme necessário. Você não precisa abrir, mas pode editar se quiser ajustar a rubrica ao seu nicho.

---

*Material exclusivo para alunos da Mentoria Primia. Uso interno e educacional.*
