---
name: voz-creator
description: Use sempre que o usuário pedir para extrair, destilar, mapear ou capturar o tom de voz / voz / forma de falar / jeito de escrever de um creator, expert, palestrante, podcaster, mentor ou figura pública a partir de transcrições prontas (.txt), gerando um documento-régua reutilizável para copywriters, editores e roteiristas. Triggers: "extrai a voz de X", "destila o tom de fala de X", "mapeia como X fala", "voz-creator de X", "/voz-creator", "preciso da régua de voz de X", "vamos extrair como X se comunica", "tom de voz de X". Use mesmo que o usuário não diga explicitamente "voz-creator" — se ele aponta uma pasta com transcrições e fala em destilar/mapear/capturar tom, voz, jeito de falar ou estilo de comunicação, ATIVE esta skill.
---

# Voz-Creator · Destilação de tom de voz a partir de transcrições

## Quando usar

Usuário tem transcrições prontas (.txt) de um creator/expert/palestrante e quer um **documento-régua de voz** que sirva de base para copywriters, editores de vídeo, designers e roteiristas escreverem materiais que soem como aquela pessoa.

## Quando NÃO usar

- Usuário tem só áudio/vídeo sem transcrição → use `transcribe` primeiro, depois retorna aqui
- Usuário quer engenharia reversa de páginas, aulas ou livros → use `primia-reverse`
- Usuário quer escrever um único reel/post mantendo voz já conhecida → escreva direto, não precisa destilar

## O que esta skill produz

| Arquivo | Conteúdo | Onde |
|---|---|---|
| `voz-[creator].md` | Documento-régua em 14 seções: perfil, posicionamento, vocabulário, estruturas narrativas, metáforas, gatilhos, temas, camada espiritual, don'ts, mecânicas, biblioteca de citações, checklist copywriter, template preenchível, perguntas em aberto | raiz do projeto do usuário |
| `voz-[creator].html` | Versão visual navegável (dark Primia) | raiz do projeto |
| `Voz-[Creator]/transcricoes/ficha-*.md` | Uma ficha por transcrição (insumo intermediário) | subpasta do projeto |

`[creator]` é o nome do creator em slug-lowercase (`voz-dulce`, `voz-bruno-vaz`, `voz-andrea-vermont`).

## Workflow em 5 passos

### Passo 1 — Briefing inicial

Pergunte (ou capte do contexto se já dito):

1. **Nome do creator** (ex: "Dulce Mariano", "Bruno Vaz")
2. **Caminho da pasta com as transcrições .txt**
3. **(Opcional) Contexto sobre o creator** — quem é, o que faz, para que vai usar a régua. Se o usuário não souber dizer, prossiga sem.

### Passo 2 — Validar elegibilidade

Antes de disparar agentes:

- Conte os arquivos `.txt` na pasta. Se houver **menos de 3**, avise: "Tem só X transcrições. A régua tende a ficar genérica com pouco material. Consegue trazer mais? Posso seguir mesmo assim se quiser."
- Conte palavras totais (`wc -w`). Se houver **menos de ~15.000 palavras**, faça o mesmo aviso. Não bloqueia — só sinaliza.
- Verifique se já existe `voz-[creator].md` na pasta. Se sim, pergunte: "Já existe régua dele aqui. Sobrescrevo, faço versão 2 (`voz-[creator]-v2.md`) ou paro?"

### Passo 3 — Disparar N agentes paralelos (1 por transcrição)

**Crítico: dispare TODOS os agentes em uma única mensagem com múltiplos `Agent` calls em paralelo.** Isso é o que faz a skill ser eficiente.

Cada agente recebe:

- O caminho do arquivo `.txt` específico
- O contexto do creator (passado do briefing)
- O caminho onde salvar a ficha: `[caminho-do-projeto]/Voz-[Creator]/transcricoes/ficha-[nome-do-arquivo].md`
- O template `templates/ficha-individual.md` (lê este arquivo do skill antes de mandar — passe o conteúdo dele no prompt do agente, não só o caminho, porque o agente roda fora do contexto do skill)

Use `subagent_type: general-purpose` para todos.

Mande no prompt do agente, em ordem:

1. **Contexto** — quem é o creator, para que serve a análise
2. **Tarefa** — ler o `.txt` inteiro (use Read paginado se >2000 linhas), produzir UMA ficha estruturada
3. **Template a seguir** — copie o conteúdo de `templates/ficha-individual.md` no prompt
4. **Onde salvar** — caminho exato do `.md` de saída
5. **Regras críticas:**
   - Citações **literais** (mín 15) entre aspas em blockquote — não parafrasear
   - Vocabulário-assinatura mín 30 termos com contexto
   - Se algo não aparece no material, marcar "ausente nesta peça" — nunca inventar
   - Preservar gírias, regionalismos, marcadores orais como ele(a) fala
6. **Resposta esperada** — relato curto (≤120 palavras): tom geral em 1 frase + 3 insights úteis para copy + 1 pergunta de interpretação se houver

### Passo 4 — Disparar 1 agente consolidador

Após TODAS as fichas individuais saírem prontas (todos os agentes da Fase 3 completaram), dispare 1 agente consolidador.

Esse agente:

1. Lê todas as fichas em `Voz-[Creator]/transcricoes/`
2. Cruza padrões — o que se repete entre as fichas é **núcleo** (método replicável); o que aparece só uma vez é **pele** (conteúdo daquela peça)
3. Produz `voz-[creator].md` seguindo o template `templates/voz-consolidada.md`
4. Produz `voz-[creator].html` seguindo o template `templates/voz-consolidada.html`

Passe no prompt do consolidador:

- Lista dos caminhos de todas as fichas
- Caminho onde salvar os 2 arquivos finais
- O conteúdo dos 2 templates (`voz-consolidada.md` e `voz-consolidada.html`)
- Contexto do creator
- Regras críticas:
  - Marque cada citação com origem (`ep01`, `ep02`, etc.)
  - Se as fichas divergem em algum ponto, trate como pluralidade ("nas fichas X e Y aparece Z, na W aparece W")
  - Não invente dados — se algo não está nas fichas, marca "a investigar"
  - O template HTML é o tema visual — preencha o conteúdo respeitando os tokens CSS
  - Antes de finalizar, aplique os 3 testes do método (descritos no template)
- Resposta esperada — relato curto: 3 aprendizados mais importantes + 3 perguntas em aberto + caminhos dos arquivos gerados

### Passo 5 — Apresentar resultado ao usuário

Após o consolidador terminar, apresente ao usuário:

- Caminhos dos 2 arquivos gerados (com links em markdown clicáveis se possível)
- Síntese de 1 frase do tom do creator
- 3 insights mais úteis para próximos passos
- Perguntas em aberto que precisam de validação humana antes de usar a régua

Pergunte: "Quer que eu use essa régua agora para algum copy específico (anúncios, página, slides, e-mail), ou só finalizar aqui?"

## Templates

Os 3 templates são insumos críticos. Sempre leia eles antes de instruir agentes:

- `templates/ficha-individual.md` — estrutura obrigatória das fichas individuais
- `templates/voz-consolidada.md` — estrutura obrigatória do documento-régua final
- `templates/voz-consolidada.html` — esqueleto visual para o consolidador preencher

Não delegue a estrutura aos agentes — eles seguem o template.

## Anti-patterns (não cometa)

- **Não rode agentes em série** quando podem rodar em paralelo. 3 transcrições = 3 agentes simultâneos, uma única mensagem.
- **Não delegue a transcrição** — esta skill assume que o `.txt` já existe. Se vier áudio/vídeo, redirecione para `transcribe`.
- **Não esterilize a voz** — se o creator usa "caramba", "graças a Deus", regionalismo, é exatamente isso que vai pra régua. Limpar = perder o que importa.
- **Não confunda voz com método** — voz é o COMO ele fala (vocabulário, ritmo, gatilhos). Método é o QUE ele ensina. Esta skill foca no como.
- **Não invente perfil etário, religião ou ideologia** se as transcrições não dizem. Marque "a investigar".
- **Não sobrescreva voz-[creator].md sem perguntar** se já existir.
- **Não pule o consolidador** mesmo que tenha só 1 ficha — o consolidador faz a curadoria final em 14 seções com checklist e template, que a ficha solta não tem.

## Validação interna do consolidador (3 testes)

Antes de declarar pronto, o consolidador deve ter aplicado:

1. **Generalização** — a régua funciona se eu tentar escrever um copy de tema completamente diferente do que o creator falou nas transcrições?
2. **Subtração** — se eu remover X do documento, ele ainda permite escrever no tom dele? (Se sim, X era pele, pode sair. Se não, X é núcleo.)
3. **Execução pelo leigo** — alguém que nunca ouviu o creator consegue escrever um copy razoável seguindo só o checklist + template?

Os 3 testes ficam documentados no fim do `.md` consolidado.
