---
name: mentoria-reuniao
description: Processa transcricoes e observacoes de reunioes de mentoria — extrai insights, atualiza fichas dos mentorados, atualiza plano de mentoria, define proximos passos e regenera pagina HTML premium. Use SEMPRE que o usuario subir transcricao de reuniao, arquivo de observacoes, anotacoes do Gemini, ou pedir para analisar uma sessao de mentoria. Tambem use quando disser "analise a reuniao", "subi a transcricao", "processe a sessao", "o que ficou definido na reuniao", ou qualquer variacao envolvendo pos-sessao de mentoria.
---

# Processador de Reunioes — Mentoria Primia

Voce processa reunioes de mentoria depois que acontecem. Sua funcao e extrair tudo de relevante de transcricoes e observacoes, atualizar as fichas e planos existentes, e regenerar a pagina HTML com o estado atual.

## Contexto

O vault Obsidian fica em `C:\Users\hober\OneDrive\Documentos\Claude code + OB\Obsidian 2`.
Os mentorados ficam em `Mentoria Primia/Mentorados/`, cada grupo em sua pasta.

A skill `mentoria-diagnostico` ja criou a estrutura inicial (fichas, plano, roteiro, HTML). Esta skill atualiza tudo apos cada sessao.

## Tipos de Arquivo de Entrada

Reunioes podem vir em varios formatos:

- **Transcricao .txt** — texto corrido com timestamps e falas identificadas por nome
- **Observacoes .pdf** — resumo gerado pelo Gemini/Meet com secoes: Resumo, Detalhes, Proximas Etapas
- **Audio transcrito** — colado direto na conversa pelo usuario
- **Notas manuais** — usuario descreve o que aconteceu

Os dois primeiros sao os mais comuns. Transcrições podem ser longas (40k+ tokens) — ler em partes.

## Fluxo de Trabalho

### Passo 1 — Identificar o mentorado e a pasta

Verificar na pasta `Mentoria Primia/Mentorados/` qual grupo corresponde a reuniao. O nome do arquivo geralmente contem os nomes dos mentorados. Se nao for claro, perguntar.

Ler os arquivos existentes na pasta para ter contexto do que ja existe:
- Fichas individuais (.md)
- Plano de mentoria (.md)
- Roteiro de nivelamento (.md)
- Pagina HTML anterior (.html)

### Passo 2 — Extrair conteudo

**Para .txt (transcricao):**
Ler em blocos de 200 linhas. Transcricoes sao longas — nao tentar ler tudo de uma vez.

**Para .pdf (observacoes):**
Usar PyMuPDF:
```python
python -c "
import fitz, sys
sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open(r'CAMINHO')
for i, page in enumerate(doc):
    print(f'--- PAGE {i+1} ---')
    print(page.get_text())
doc.close()
"
```

Ler AMBOS se existirem — o PDF de observacoes tem resumo estruturado, a transcricao tem detalhes e falas literais. Os dois se complementam.

### Passo 3 — Analisar e extrair insights

Extrair da reuniao:

**Informacoes fatuais:**
- O que foi apresentado/demonstrado
- Que ferramentas foram mencionadas/adotadas
- Que decisoes foram tomadas
- Que tarefas foram atribuidas (quem faz o que)
- Que prazos foram definidos
- Que materiais foram pedidos

**Informacoes sobre o negocio:**
- Nome do expert/produto/marca
- Tamanho da base de leads
- Plataformas e ferramentas que usam (vendas, CRM, email, paginas)
- Metricas mencionadas (conversao, faturamento, abertura de email)
- Dores do publico-alvo
- Lancamentos planejados

**Insights sobre os mentorados:**
- Quem engajou mais (fez perguntas, pediu detalhes)
- Quem mostrou perfil gestor vs. tecnico
- Frases literais reveladoras (citar entre aspas)
- Nivel real demonstrado durante a conversa
- O que os animou mais (indica prioridade real)

**Proximos passos:**
- O que ficou definido como tema da proxima sessao
- Tarefas pendentes por pessoa
- Materiais que precisam ser enviados/preparados

### Passo 4 — Atualizar fichas individuais

Adicionar uma secao `### Informacoes da Sessao X (Tipo)` em cada ficha com:
- Dados revelados na reuniao (ferramentas, metricas, expert, base)
- Comportamento observado (engajamento, perfil confirmado/alterado)
- Frases-chave entre aspas
- Interesses e prioridades demonstradas

Atualizar o bloco `## Status`:
- Fase atual (pos-onboarding, pos-nivelamento, em implementacao, etc.)
- Proxima acao concreta
- Foco da proxima sessao

Adicionar linha no `## Historico de Sessoes`:
- Data, tipo, resumo de 1-2 linhas

### Passo 5 — Atualizar plano de mentoria

Adicionar secao `## O que ficou definido na Sessao X`:

**Informacoes-chave reveladas:**
Lista de bullets com os dados mais importantes descobertos na reuniao.

**Tarefas pendentes (pre-sessao seguinte):**
Checklists com owner: `- [ ] **Nome:** Tarefa`
Separar por: mentorado 1, mentorado 2, mentor, ambos.

**Proxima sessao:**
- Tema/foco definido
- Passos concretos do que sera feito
- Referencia a modelos/exemplos se mencionados

Atualizar a tabela de `## Acompanhamento`:
- Marcar sessao realizada com data e resumo
- Adicionar proxima sessao pendente

Atualizar `## Notas para o Mentor` com insights estrategicos da reuniao.

### Passo 6 — Regenerar pagina HTML

A pagina HTML precisa refletir o estado ATUAL do mentorado. Nao e um snapshot do diagnostico — e um documento vivo.

**Atualizar/adicionar:**
- Status bar no topo com fase atual e indicador visual
- Hero com informacoes atualizadas (expert, base, deadline)
- Perfis com badge de confirmacao se perfil foi validado + insights da reuniao
- Secao de descobertas do onboarding/sessao (grid de findings)
- Board de tarefas interativo com checkboxes por pessoa (mentorado 1, mentorado 2, mentor)
- Proxima sessao detalhada com passos numerados
- Roadmap/timeline com sessao realizada marcada como concluida
- Historico de sessoes com badges de status (concluida/pendente)
- Notas estrategicas atualizadas

**Design system — usar padrao Primia:**

Antes de gerar/atualizar o HTML, ler o style guide em `Primia/Marca Primia/style-guide.html` para extrair o design system oficial.

- Dark theme: `#0A0A0C` background, `#1A1A1E` cards
- Purple principal: `#8356E7` (light `#9F7BFF`, dark `#6B3FD9`)
- Lime complementar: `#C4FF4D` (light `#D4FF7D`, dark `#B0E640`)
- Typography: `Syne` (display/titulos) + `Inter` (body)
- Cards com `border-radius: 14px`, border `rgba(255,255,255,0.1)`, hover com purple glow
- Badges: primary (purple), secondary (lime), success (green), error (red)
- Score bars animadas no scroll
- Timeline com scroll reveal
- Checkboxes clicaveis no board de tarefas e guia de observacao
- Navegacao fixa com scroll spy
- Responsivo e print-friendly

**Funcionalidades interativas:**
- Checkboxes que persistem estado visual ao clicar
- Acordeoes para conteudo longo
- Badges coloridas: verde (concluida), laranja (pendente)
- Task board com colunas por responsavel

### Passo 7 — Apresentar resultado

Apos atualizar tudo:
1. Listar arquivos atualizados com links
2. Resumo das descobertas mais importantes da reuniao
3. Lista de tarefas pendentes organizada por pessoa
4. O que mudou no plano (nova sessao, novas fases, timeline ajustada)
5. Perguntar: "O que voce quer fazer agora?"

## Principios

**Fidelidade:** Usar dados reais da reuniao, nao suposicoes. Citar frases literais quando reveladoras.

**Atualizacao, nao substituicao:** Adicionar informacoes as fichas existentes. Nao apagar o que ja estava la — acrescentar. O historico importa.

**Plano vivo:** O roadmap se adapta a realidade. Se a reuniao revelou que o caminho mudou (ex: diagnostico virou prioridade em vez de nivelamento tecnico), o plano deve refletir isso.

**Consistencia visual:** A pagina HTML de cada grupo de mentorados deve manter o mesmo design system. Atualizar conteudo, nao redesenhar.

**Tarefas rastreavels:** Toda tarefa mencionada na reuniao deve ter owner e aparecer no board de tarefas — tanto no .md quanto no HTML.
