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

## Suporte

Uso interno e educacional dos alunos da Mentoria Primia. Para suporte, dúvidas ou sugestões, fale com o Hoberdan.