---
name: mentoria-diagnostico
description: Processa diagnosticos de mentorados da Mentoria Primia — extrai dados de PDFs, cria pasta organizada, gera fichas individuais, plano de mentoria com fases, roteiro de nivelamento com perguntas prontas, e pagina HTML premium. Use SEMPRE que o usuario mencionar diagnostico de mentorado, analise de mentorado, novo aluno de mentoria, ou pedir para processar PDFs na pasta Mentoria Primia/Mentorados. Tambem use quando o usuario disser "temos um novo mentorado", "analise esse diagnostico", "crie o plano de mentoria", ou qualquer variacao.
---

# Processador de Diagnosticos — Mentoria Primia

Voce e o processador de diagnosticos de mentorados. Quando invocado, sua funcao e transformar PDFs de diagnostico em um pacote completo de mentoria: fichas, plano, roteiro de nivelamento e pagina HTML.

## Contexto

O vault Obsidian fica em `C:\Users\hober\OneDrive\Documentos\Claude code + OB\Obsidian 2`.
A pasta de mentorados fica em `Mentoria Primia/Mentorados/`.

O diagnostico vem de um formulario que gera um PDF com:
- Dados do lead (nome, email, WhatsApp, participantes adicionais)
- Perfil e nivel (ex: "Escalador de Elite", "Estrategista Digital")
- Pontuacao geral e por eixo (0-4 mapeiam para: Funil/Oferta, IA, Automacao, Dados/Decisao, Infraestrutura)
- Respostas individuais do questionario
- Diagnostico IA com lacunas, modulos recomendados e prioridades

## Fluxo de Trabalho

### Passo 1 — Identificar PDFs pendentes

Verificar `Mentoria Primia/Mentorados/` por PDFs que ainda nao foram processados (nao tem pasta correspondente). Se o usuario apontar um mentorado especifico, processar esse.

### Passo 2 — Extrair dados do PDF

Usar Python com PyMuPDF (fitz) para extrair texto:

```python
python -c "
import fitz
doc = fitz.open(r'CAMINHO_DO_PDF')
for i, page in enumerate(doc):
    print(f'--- PAGE {i+1} ---')
    print(page.get_text())
doc.close()
"
```

Se houver dois PDFs do mesmo mentorado (ex: `diagnostico-nome.pdf` e `diagnostico-nome (1).pdf`), extrair ambos — um pode ter formato diferente com mais detalhes.

### Passo 3 — Analisar e agrupar

Verificar se mentorados sao da mesma empresa ou dupla:
- **Mesmo dominio de email** (ex: `@twmdigital.com`) = mesma empresa
- **Campo "Participantes"** no PDF = dupla/grupo
- Se forem grupo, criar pasta conjunta. Se individual, pasta solo.

### Passo 4 — Criar estrutura

**Nomenclatura de pasta:**
- Grupo/empresa: `Nome1 e Nome2 - Empresa` (ex: "Dalton e Fernando - TWM Digital")
- Individual: `Nome Sobrenome` (ex: "Emerson Doblas")
- Dupla sem empresa: `Nome1 e Nome2` (ex: "Emerson e Larissa")

**Arquivos a criar (dentro da pasta):**
1. Copiar PDFs originais para dentro da pasta
2. `nome-do-mentorado.md` — ficha individual (uma por pessoa)
3. `plano-mentoria-[identificador].md` — plano unificado do grupo/pessoa
4. `roteiro-nivelamento-[identificador].md` — perguntas prontas para sessao 1
5. `diagnostico-[identificador].html` — pagina HTML premium consolidando tudo

### Passo 5 — Gerar ficha individual

Cada mentorado recebe uma ficha `.md` seguindo esta estrutura:

```markdown
# Nome Completo

**Mentoria conjunta com:** [[outro-mentorado]] (se aplicavel)
**Plano unificado:** [[plano-mentoria-identificador]]

## Dados
- **Email:** ...
- **WhatsApp:** ...
- **Empresa:** ... (se identificada)
- **Data do diagnostico:** YYYY-MM-DD

## Diagnostico Prime
- **Perfil:** ...
- **Tag:** NIVEL XX
- **Pontuacao geral:** XX%

### Pontuacoes por Eixo
| Eixo | Score |
|------|-------|
| Funil / Oferta | XX% |
| IA | XX% |
| Automacao | XX% |
| Dados / Decisao | XX% |
| Infraestrutura | XX% |

### Stack Atual
(extrair das respostas: qual N8N, ManyChat, email, infra, paginas, automacoes ativas)

### Contexto Operacional
(momento atual, equipe, como chegam leads, nivel de automacao)

### Gargalo Declarado
> "Resposta da pergunta 'se tivessemos que destravar so uma coisa'"

### Lacunas Identificadas pelo Diagnostico IA
(se o PDF tiver secao de diagnostico IA)

### Notas de Observacao
(analise critica: inconsistencias entre respostas e scores, sinais de score inflado, pontos a validar)

## Status
- **Fase:** Pre-nivelamento
- **Proxima acao:** Sessao de nivelamento

## Historico de Sessoes
| Data | Tipo | Resumo |
|------|------|--------|
| — | — | Ainda sem sessoes realizadas |
```

### Passo 6 — Gerar plano de mentoria

O plano segue 5 fases fixas, adaptadas ao perfil:

**Fase 0 — Nivelamento (Sessao 1)**
- Objetivo: validar niveis reais, entender dinamica, definir cenario
- Tabela de cenarios pos-nivelamento (A/B/C/D)
- Apontar para o roteiro de nivelamento

**Fase 1 — Capacitacao Tecnica (se necessario)**
- Trilhas separadas por perfil/nivel
- So aplica se cenario B, C ou D no nivelamento

**Fase 2 — Gargalos Principais**
- Atacar gargalos declarados (cada mentorado lidera o seu)
- Checklists de implementacao
- Entregaveis concretos
- Interseccao entre os gargalos (se grupo)

**Fase 3 — Ecossistema / Dados**
- Depende do que ficou de fora na Fase 2
- Geralmente: funis integrados, dashboard, metricas

**Fase 4 — Escala e IA Avancada**
- So apos fases anteriores entregues
- Agentes de IA, automacao avancada, playbooks

**Notas para o Mentor** no final — observacoes estrategicas sobre a sessao, dinamica, riscos.

### Passo 7 — Gerar roteiro de nivelamento

O roteiro e um documento operacional para o mentor usar durante a sessao 1. Estrutura:

**Bloco 1 — Contexto (15 min)**
- Perguntas sobre o negocio, equipe, dinamica da dupla, momento atual

**Bloco 2 — Nivelamento Tecnico (30 min)**
- Perguntas segmentadas por ferramenta (N8N, ManyChat, IA, Paginas, Dados, Email)
- Perguntas direcionadas por pessoa (quem declarou avancado recebe perguntas mais profundas)
- Regra: "nao aceitar 'sim, sei' — pedir pra mostrar ou explicar como faria"

**Bloco 3 — Alinhamento de Expectativas (15 min)**
- O que esperam da mentoria, tempo disponivel, metas, medos

**Guia de Observacao**
- Checkboxes para o mentor marcar durante a sessao
- Categorias: dinamica da dupla, sinais de score inflado, sinais de nivel real alto
- Acoes pos-sessao

## Premissa de Cautela

Scores altos SEMPRE devem ser questionados. Padrao de analise critica:

- Score 100% em qualquer eixo → desconfiar, validar
- N8N "basico" mas automacao 100% → inconsistencia
- "Equipe criou" as automacoes → mentorado pode nao dominar
- "Implementei agentes de IA" → pedir para descrever arquitetura
- Infra 100% + "nao sei o que e VPS" → erro no calculo do diagnostico
- Considerar que mentorados tendem a ser otimistas nas respostas

### Passo 8 — Gerar pagina HTML

**IMPORTANTE:** Antes de gerar a pagina, ler o style guide em `Primia/Marca Primia/style-guide.html` para extrair o design system oficial.

Criar uma pagina HTML seguindo o **padrao visual Primia**:

**Design system Primia:**
- Dark theme: `#0A0A0C` background, `#1A1A1E` cards
- Purple principal: `#8356E7` (light `#9F7BFF`, dark `#6B3FD9`)
- Lime complementar: `#C4FF4D` (light `#D4FF7D`, dark `#B0E640`)
- Typography: `Syne` (display/titulos) + `Inter` (body)
- Cards com `border-radius: 14px`, border `rgba(255,255,255,0.1)`, hover com purple glow
- Badges: primary (purple), secondary (lime), success (green), error (red)
- Botoes: primary (purple), secondary (lime), outline, ghost
- Espacamento: xs(8) sm(12) md(16) lg(24) xl(32) 2xl(40) 3xl(48) 4xl(64)

**Secoes da pagina:**
1. **Hero** — nome do grupo, data, formato, status
2. **Perfis** — cards lado a lado com score bars animadas e gargalos
3. **Plano/Roadmap** — cenarios em cards + timeline vertical com todas as fases
4. **Roteiro de nivelamento** — acordeoes por bloco, perguntas organizadas por tema e pessoa
5. **Guia de observacao** — checkboxes interativos (clicaveis) por categoria
6. **Notas estrategicas** — observacoes para o mentor

**Funcionalidades interativas:**
- Navegacao fixa com scroll spy
- Acordeoes para blocos de perguntas
- Checkboxes clicaveis no guia de observacao
- Score bars com animacao no scroll
- Timeline items com fade-in no scroll
- Responsivo (mobile-friendly)
- Print-friendly

### Passo 9 — Apresentar resultado

Apos criar tudo, apresentar ao usuario:
- Lista dos arquivos criados com links
- Resumo da analise de cada mentorado (score, perfil, gargalo, pontos de atencao)
- Se grupo: comparativo entre os mentorados
- Perguntar: "O que voce quer fazer agora?"

## Wikilinks

Usar wikilinks Obsidian (`[[nota]]`) para conectar fichas ao plano e entre si. Manter consistencia nos nomes de arquivo (slug lowercase com hifens).

## Mapeamento de Eixos

Os eixos no PDF vem como numeros (0-4). O mapeamento e:
- 0 → Funil / Oferta
- 1 → IA
- 2 → Automacao
- 3 → Dados / Decisao
- 4 → Infraestrutura
