---
name: primia-reverse
description: Sistema Primia de engenharia reversa de referencias e producao de conteudo metodologico. Use quando o usuario pedir para destilar metodo de um creator/aula/livro (modo Engenharia Reversa) OU quando pedir para gerar reel/carrossel/roteiro/conteudo seguindo o Metodo Primia (modo Producao). Triggers: "engenharia reversa de X", "destilar metodo de X", "extrair sistema de X", "cria reel/carrossel/roteiro sobre X no metodo primia", "produz conteudo no padrao primia", "primia reverse", "/primia-reverse".
user_invocable: true
---

# Primia Reverse

Sistema unificado de **engenharia reversa de referencias** e **producao de conteudo** baseado no Metodo Primia. Uma skill, dois modos — porque sao partes do mesmo sistema.

## Contexto vivo

- **Repo:** https://github.com/berdantx/Referencias-primia (privado)
- **Pagina apresentacao:** https://referencias-primia-andrea.vercel.app
- **Pasta do vault:** `Primia/Referências/` (Obsidian local)
- **Caso-base original:** Andrea Vermont — imersao Tradutor de Almas (3 aulas)

Todo material novo gerado por essa skill deve ser salvo no padrao do repo: markdown estruturado + opcionalmente pagina HTML no padrao Primia dark.

---

## Quando usar (triggers)

### Modo 1 — Engenharia Reversa
- "Faz engenharia reversa de [creator/aula/livro/imersao]"
- "Destila o metodo de [referencia]"
- "Extrai o sistema de [conteudo]"
- "Vamos analisar [material] no padrao primia"
- Usuario aponta uma pasta com transcricoes/material de uma referencia

### Modo 2 — Producao de Conteudo
- "Cria um reel sobre [tema] no metodo primia"
- "Gera carrossel/roteiro sobre [tema]"
- "Produz conteudo no padrao primia sobre X"
- "Aplica o metodo a [tema/publico]"

### Identificar o modo
Se o usuario menciona uma **referencia externa** (creator, livro, curso), e modo 1.
Se o usuario menciona um **tema/formato** sem referencia externa, e modo 2.
Em duvida, pergunte.

---

## MODO 1 — ENGENHARIA REVERSA

### Antes de comecar: validar elegibilidade

A referencia precisa atender **pelo menos 3 dos 5 criterios**:

1. **Volume** — 2-3 pecas completas disponiveis (nao recortes)
2. **Consistencia** — mesmo padrao se repete entre pecas
3. **Resultado observavel** — depoimentos de transformacao concreta
4. **Densidade pedagogica** — conceitos nomeados, exercicios, estrutura
5. **Aplicabilidade** — funciona alem do creator original

Se falha em 3+: avisar o usuario que pode nao valer a engenharia reversa.

### Briefing inicial (perguntar antes de comecar)

1. **Por que essa referencia?** (o que chamou atencao)
2. **Para que destilar?** (uso pessoal? produto? treinar time?)
3. **O que NAO levar?** (filtro consciente — ex: "nao quero a camada espiritual")
4. **Quantidade de material:** quantas pecas, quanto tempo cada uma?

### As 5 fases

#### Fase 1 — Imersao bruta
- Ler/ouvir todo o material sem tentar destilar
- Anotar so o que atravessou, surpreendeu, repetiu
- NAO estruturar ainda
- Output: 10-20 notas soltas

#### Fase 2 — Ficha individual (uma por peca)

Estrutura obrigatoria de cada ficha:

```markdown
# Ficha — [nome da peca]

> **Tema central (1 frase):** ...

**Formato:** [duracao, tipo]
**Estrutura pedagogica:** [arco]

## Mapa cronologico
[blocos com tempo aprox + conteudo]

## CORPO TEMATICO

### Conceitos-chave
[cada conceito nomeado, 1-2 paragrafos]

### Frameworks/modelos
[estruturas nomeadas, se houver]

### Exemplos e historias
[pessoais do creator + casos]

### Frases de impacto
[citacoes literais — usar > blockquote]

### Objecoes antecipadas
[tabela: objecao | resposta]

### Prescricoes/exercicios
[passos acionaveis]

### Mecanicas pedagogicas
[padroes de COMO ele ensina, nao o que]

## Pontos de conexao
[a preencher apos ler todas as pecas]

## Meta-observacoes
[insights para uso em conteudo proprio]
```

**Regra critica:** separar **o que** (conteudo do creator) de **como** (mecanicas pedagogicas). O *como* e onde mora o metodo replicavel.

#### Fase 3 — Identificacao de padroes (transversal)
Apos todas as fichas:
- O que se **repete** entre pecas → metodo
- O que e **sempre diferente** → conteudo, nao metodo
- O que aparece **uma vez mas funciona** → candidato a principio (validar)

3 perguntas guia:
- Qual a arquitetura recorrente?
- Quais principios operacionais repetidos?
- O que e opcional vs inegociavel?

#### Fase 4 — Destilacao (documento metodo)

Estrutura obrigatoria do documento metodo destilado:

```markdown
# [Nome do Metodo] — Sistema [...]

## PARTE 1 — NUCLEO INEGOCIAVEL
1.1 A arquitetura em N atos
1.2 Os N principios operacionais
1.3 Criterios operacionais (regras, metricas, anti-patterns)

## PARTE 2 — KIT DE MONTAGEM
[templates preenchiveis com exemplos da referencia]

## PARTE 3 — CRITERIOS DE ADAPTACAO
3.1 O que e nucleo (nunca muda)
3.2 O que adapta por tema
3.3 O que adapta por formato
3.4 O que e opcional

## PARTE 4 — EXEMPLO APLICADO (ficticio, tema diferente do original)

## PARTE 5 — PASSO A PASSO DE APLICACAO
```

Regras:
1. **Nomear tudo** (atos, principios, frameworks)
2. **Separar nucleo de pele** (nucleo sobrevive a troca de tema; pele e o que muda)
3. **Toda regra tem teste** (como verificar se foi aplicada)
4. **Todo conceito tem exemplo da referencia original**
5. **Anti-patterns explicitos**

#### Fase 5 — Validacao (3 testes)

1. **Teste de generalizacao:** escrever 1 aplicacao ficticia em tema completamente diferente. Funciona? Esta destilado.
2. **Teste de subtracao:** remover cada principio. Se metodo sobrevive sem, era pele. Se quebra, e nucleo.
3. **Teste do leigo:** alguem que nao conhece a referencia consegue aplicar?

So liberar quando passa nos 3.

### Entregaveis do Modo 1

Para cada engenharia reversa, gerar:
1. **N fichas individuais** (`ficha-[nome].md`) — uma por peca
2. **1 documento de metodo destilado** (`metodo-[nome].md`)
3. **1 pagina HTML opcional** (visual, padrao Primia dark) com biblioteca navegavel
4. **Salvar em** `Primia/Referências/[nome-da-referencia]/`

### Anti-patterns Modo 1

- Confundir fa com analista (paixao contamina destilacao)
- Copiar em vez de destilar (reproduzir frases ≠ extrair metodo)
- Generalizar demais (forcar padrao onde so ha similaridade)
- Generalizar de menos (descricao nao e metodo)
- Comecar pela estrutura (template antes de ler material)
- Parar na primeira versao (validacao e onde fica pronto)
- Nao filtrar o que nao quer levar

---

## MODO 2 — PRODUCAO DE CONTEUDO

### O Metodo Primia em 1 frase

Sistema de transformacao em **3 atos** sustentado por **5 principios operacionais**, agnostico de tema/publico/formato.

### Os 3 atos (ordem inegociavel)

| Ato | Funcao |
|---|---|
| **1. Diagnostico** | Destruir o falso. Mostrar que o publico vive uma versao adaptada/performada/editada de si. Nomear a ferida. |
| **2. Reconstrucao** | Construir o verdadeiro. Nova leitura, nova pratica, nova relacao com o problema. |
| **3. Integracao** | Atravessar para a vida. Acao concreta de segunda-feira. |

**Por que inegociavel:** invertendo, vira coaching raso. O peso da reconstrucao vem de ter atravessado o diagnostico.

### Os 5 principios operacionais

1. **Narrativa pessoal como cola** — nunca pedir vulnerabilidade sem entrar primeiro
2. **Metafora cultural forte por conceito** — cada ideia abstrata ganha corpo via referencia externa (mito, filme, arte, natureza)
3. **Associacao livre → vivencia** — todo conceito vira exercicio (frase, gesto, acao)
4. **Objecoes antecipadas** — para cada ideia forte, uma objecao respondida dentro do conteudo
5. **Acao para segunda-feira** — toda peca fecha com "o que voce faz diferente amanha?", pequena e verificavel

### Briefing antes de produzir (perguntar)

| Item | Pergunta |
|---|---|
| Tema | Qual o tema? |
| Publico | Para quem? (especifico) |
| Formato | Reel? Carrossel? Roteiro longo? Email? Outro? |
| Promessa mensuravel | O que o publico **consegue fazer** ao fim que nao conseguia antes? (1 frase mensuravel) |
| Voz/tom | Neutro-profissional? Voz especifica? |

Se o usuario nao definir promessa mensuravel, ajude a definir antes de produzir.

### Estrutura do entregavel

Toda peca produzida deve ter este formato (markdown):

```markdown
# Exemplo — [Formato]: "[Frase-sintese / titulo]"

> **Tema:** ...
> **Formato:** ...
> **Objetivo didatico:** ...

## Briefing
| Item | Definicao |
|---|---|
| Promessa mensuravel | ... |
| Publico | ... |
| Ferida nomeada | ... |
| Reconstrucao central | ... |
| Acao de segunda-feira | ... |

## ROTEIRO ANOTADO

[bloco do roteiro literal]

📌 **[Principio N — nome]**
[explicacao de onde foi aplicado e por que]

📌 **[Ato N — funcao]**
[como esse trecho cumpre o ato]

[continuar para todos os blocos...]

## CHECKLIST DE QUALIDADE
✅ 3 atos presentes
✅ Narrativa pessoal entra primeiro
✅ Metafora cultural ancora conceito
✅ Vivencia ativa (Principio 3)
✅ Objecao antecipada (Principio 4)
✅ Acao de segunda-feira (Principio 5)
✅ Promessa mensuravel cumprida

## NOTAS DE PRODUCAO
[B-roll, tom, design, etc.]
```

### Regras de adaptacao por formato

| Formato | Adaptacoes |
|---|---|
| **Reel 60-90s** | Diagnostico no gancho (primeiros 8s); reconstrucao em 1-2 frases; integracao na ultima frase. Sem aquecimento. |
| **Carrossel 6-10 slides** | Capa = interrupcao de padrao (nao titulo descritivo). 3 atos distribuidos: diagnostico nos primeiros 40-50%, reconstrucao no meio, integracao no fim com fechamento circular. |
| **Roteiro longo 15-20min** | Promessa mensuravel anunciada cedo. Multiplos exemplos/historias. Conceito nomeado com autoridade externa. Multiplas objecoes. Pacing controlado em blocos. |
| **Post de texto** | Hook = ferida nomeada. 1 metafora central. Exercicio mental durante a leitura. Acao especifica no fim. |
| **Email** | Assunto = objecao antecipada. Corpo segue 3 atos. PS com acao concreta. |

### Anti-patterns Modo 2 (NUNCA fazer)

- Comecar pela reconstrucao (sem diagnostico vira motivacional vazio)
- Conceito sem exercicio (vira palestra)
- Metafora sem conceito nomeado por tras (vira poesia)
- Promessa vaga ("transforme sua vida")
- Sem narrativa pessoal ancorando
- Sem acao de segunda-feira
- Catarse sem integracao para a vida
- Copia literal de outro creator

---

## REGRAS GERAIS (ambos os modos)

### Onde salvar

- **Modo 1 (engenharia reversa):** `Primia/Referências/[nome-referencia]/`
- **Modo 2 (producao):** `Primia/Conteudos/[tema]/[formato]-[titulo].md` ou onde usuario indicar
- Se o usuario quiser publicar no repo: `Referencias-primia` (privado, com deploy publico na Vercel)

### Padrao visual (paginas HTML opcionais)

Quando gerar HTML, usar **padrao Primia dark** (skill `landing-primia`):
- CSS variables: `--color-bg-dark: #0b0b0f`, `--color-primary: #8356E7`, `--color-accent: #C4FF4D`
- Fonte: Inter (Google Fonts)
- Cards `.card` com border `--color-border` e hover sutil
- Sem background claro
- Modal pra abrir markdown via `marked.js` se houver docs

### Quando o usuario pedir a "ponte completa"

Se o usuario disser algo como "faz tudo: engenharia reversa + metodo + exemplos + pagina":
1. Modo 1 completo (fichas + metodo destilado)
2. Modo 2 completo (3 exemplos anotados em 3 formatos diferentes)
3. Pagina HTML de apresentacao linkando tudo
4. Commit no repo + deploy Vercel se autorizado

### Briefing de risco antes de acoes externas

Antes de:
- Criar repo GitHub novo
- Push pra remoto
- Deploy Vercel publico
- Tornar algo publico

Sempre confirmar com o usuario: o que sobe, em qual repo, publico ou privado, qual subdominio.

---

## REFERENCIAS

- **Documento Engenharia Reversa Primia (meta-metodo completo):** https://referencias-primia-andrea.vercel.app/engenharia-reversa-primia.md
- **Documento Metodo Primia Sistema (sistema replicavel):** https://referencias-primia-andrea.vercel.app/metodo-primia-sistema.md
- **Pagina apresentacao do metodo:** https://referencias-primia-andrea.vercel.app
- **3 exemplos anotados:** https://referencias-primia-andrea.vercel.app/exemplos/
- **Caso-base original (Andrea Vermont):** `Primia/Referências/Andrea Vermont/`

Quando em duvida sobre como aplicar algo, ler esses documentos serve de referencia canonica.

---

## CHECKLIST FINAL (qualquer entregavel)

Antes de finalizar qualquer output desta skill:

✅ Markdown bem estruturado (headings, listas, tabelas)
✅ Frases-virada destacadas (blockquote)
✅ Anotacoes didaticas se for exemplo de aplicacao (📌 nos pontos-chave)
✅ Salvo no caminho correto (`Primia/Referências/` ou `Primia/Conteudos/`)
✅ Avisar o usuario onde foi salvo e por que
✅ Se publicar online: confirmar repo + visibilidade antes de push/deploy
