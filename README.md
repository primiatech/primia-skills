# Primia Skills

Coleção de skills do Claude Code criadas por **Hoberdan Silva** para os alunos da **Mentoria Primia**.

Cada pasta deste repositório é uma skill independente, com seu próprio `SKILL.md`, `README.md` de instalação, scripts e referências.

---

## Skills disponíveis

| Skill | O que faz | Versão |
|---|---|---|
| [`analise-concorrentes-youtube`](./analise-concorrentes-youtube/) | Inteligência competitiva no YouTube voltada pra infoprodutos. Coleta metadados, transcrições e comentários, e entrega `.xlsx` + `.docx` + `.pptx` + assets. | 1.1.0 |
| [`primia-design`](./primia-design/) | Gera design system completo (tokens W3C, CSS vars, SCSS, Tailwind, Figma Tokens, styleguide HTML, 6 componentes) a partir de imagem, PDF e/ou URL. Funde múltiplas fontes com hierarquia configurável. | 1.1.0 |
| [`analise-concorrentes-meta`](./analise-concorrentes-meta/) | Inteligência competitiva publicitária na Biblioteca de Anúncios da Meta (Facebook + Instagram). Scraping + Whisper + OCR. Entrega `.xlsx` + `.docx` + `.pptx` + briefings criativos `.md` + dashboard HTML interativo + criativos baixados. | 1.2.0 |
| [`primia-instagram-analyst`](./primia-instagram-analyst/) | Mapeia comentaristas dos posts do **próprio perfil** do aluno no Instagram, cruza cada um com o ICP do negócio e devolve planilha categorizada por temperatura comercial (Fã Recorrente ICP, Diamante Oculto, Engajador Frequente, Observar, Descartar). Coleta via Claude Cowork no Chrome. 3 modos: PESADO mensal, LEVE-A semanal no chat, LEVE-B semanal em planilha enxuta. | 1.1.0 |
| [`primia-reverse`](./primia-reverse/) | Sistema unificado de engenharia reversa de referências (destila método de creator/aula/livro) e produção de conteúdo (gera reel/carrossel/roteiro no padrão Método Primia). Uma skill, 2 modos. | — |
| [`voz-creator`](./voz-creator/) | Extrai, destila e mapeia o tom de voz de um creator/expert/podcaster a partir de transcrições `.txt`, gerando documento-régua reutilizável pra copywriters, editores e roteiristas. | — |
| [`clone-redesign`](./clone-redesign/) | Clona e redesenha páginas web existentes a partir de URL ou screenshot. Recria a versão melhorada usando o design system do projeto. | — |
| [`mentoria-diagnostico`](./mentoria-diagnostico/) | Processa diagnósticos de novos mentorados — extrai dados de PDFs, cria pasta organizada, gera fichas individuais, plano de mentoria com fases, roteiro de nivelamento e página HTML premium. | — |
| [`mentoria-reuniao`](./mentoria-reuniao/) | Processa transcrições e observações de reuniões de mentoria — extrai insights, atualiza fichas dos mentorados, atualiza plano de mentoria, define próximos passos e regenera a página HTML. | — |

---

## Como instalar uma skill

Cada skill tem dois formatos disponíveis:

1. **Pasta extraída** (ex: `analise-concorrentes-youtube/`) — copie direto pra `~/.claude/skills/` (Mac/Linux) ou `%USERPROFILE%\.claude\skills\` (Windows).
2. **Arquivo `.skill`** (ex: `analise-concorrentes-youtube.skill`) — é um zip renomeado. Extraia em `~/.claude/skills/`.

As 4 skills do topo da tabela (com versão definida) são skills "pesadas" — têm scripts Python, dependências e setup. O `README.md` dentro de cada uma tem o passo a passo completo de instalação.

As 5 skills de baixo (sem versão) são skills "leves" — só têm `SKILL.md` (e templates, no caso de `voz-creator`). Não exigem instalação de dependência: basta copiar a pasta pra `~/.claude/skills/` e o Claude detecta automaticamente.

---

## Plugins recomendados (instalar via marketplace do Claude Code)

As skills deste repositório resolvem problemas específicos da Mentoria Primia. Pra completar o stack do mentorado no dia a dia, instale também esses plugins oficiais via marketplace.

**Como instalar:** dentro do Claude Code, rode o comando `/plugin install <plugin>@<marketplace>` com cada um da lista abaixo.

### Tier 1 — Essenciais (instalar antes de começar)

Esses são a base do stack. Sem eles, o Claude funciona, mas você perde produtividade óbvia.

```bash
/plugin install superpowers@claude-plugins-official
/plugin install document-skills@anthropic-agent-skills
/plugin install claude-api@anthropic-agent-skills
/plugin install frontend-design@claude-plugins-official
/plugin install figma@claude-plugins-official
/plugin install context7@claude-plugins-official
```

| Plugin | Pra que serve |
|---|---|
| `superpowers` | O "modo de pensar" do Claude. Adiciona brainstorming estruturado, planejamento antes de codar, debugging sistemático, TDD, code review. Maior alavanca de qualidade do stack. |
| `document-skills` | Manipulação completa de Word, Excel, PowerPoint e PDF. Qualquer entrega pra cliente que envolva documento usa essas skills. |
| `claude-api` | Toolkit Anthropic com brand-guidelines, theme-factory, internal-comms, mcp-builder, web-artifacts-builder, canvas-design e mais 10 skills. |
| `frontend-design` | Cria interfaces distintivas, foge do "design AI genérico". Componentes, páginas, landing pages com qualidade de produção. |
| `figma` | Implementa designs do Figma direto pra código. Lê designs, gera screens, mantém Code Connect. Vale ouro pra quem trabalha com designer. |
| `context7` | Documentação atualizada de qualquer biblioteca/framework (React, Next, Tailwind, Supabase, etc). **Essencial pra mentorado começando dev** — evita o Claude inventar API antiga. |

### Tier 2 — Quando precisar (instalar conforme demanda)

Esses não são pra todo mundo. Instala quando o projeto pedir.

```bash
# Quando for construir SaaS, área de membros ou app com banco
/plugin install supabase@claude-plugins-official

# Quando for testar landing/app local no browser via Claude
/plugin install webapp-testing@anthropic-agent-skills

# Quando começar a usar PRs e issues do GitHub no fluxo
/plugin install github@claude-plugins-official

# Pra criar suas próprias skills do jeito certo
/plugin install skill-creator@claude-plugins-official
```

### Como verificar o que está instalado

```bash
/plugin list
```

Mostra todos os plugins ativos. Cada plugin pode trazer múltiplas skills, comandos e agentes — o Claude detecta automaticamente.

### Atualizar plugins

```bash
/plugin update <plugin>@<marketplace>
```

Marketplaces atualizam com frequência. Vale rodar `/plugin update` esporadicamente nos plugins do Tier 1.

---

## Suporte

Uso interno e educacional dos alunos da Mentoria Primia. Para suporte, dúvidas ou sugestões, fale com o Hoberdan.