# Primia Skills

Coleção de skills do Claude Code criadas por **Hoberdan Silva** para os alunos da **Mentoria Primia**.

Cada pasta deste repositório é uma skill independente, com seu próprio `SKILL.md`, `README.md` de instalação, scripts e referências.

---

## Skills disponíveis

| Skill | O que faz | Versão |
|---|---|---|
| [`analise-concorrentes-youtube`](./analise-concorrentes-youtube/) | Inteligência competitiva no YouTube voltada pra infoprodutos. Coleta metadados, transcrições e comentários, e entrega `.xlsx` + `.docx` + `.pptx` + assets. | 1.1.0 |

---

## Como instalar uma skill

Cada skill tem dois formatos disponíveis:

1. **Pasta extraída** (ex: `analise-concorrentes-youtube/`) — copie direto pra `~/.claude/skills/` (Mac/Linux) ou `%USERPROFILE%\.claude\skills\` (Windows).
2. **Arquivo `.skill`** (ex: `analise-concorrentes-youtube.skill`) — é um zip renomeado. Extraia em `~/.claude/skills/`.

O `README.md` dentro de cada skill tem o passo a passo completo, incluindo instalação de Python, configuração de virtualenv, dependências e variáveis de ambiente quando necessárias.

---

## Suporte

Uso interno e educacional dos alunos da Mentoria Primia. Para suporte, dúvidas ou sugestões, fale com o Hoberdan.