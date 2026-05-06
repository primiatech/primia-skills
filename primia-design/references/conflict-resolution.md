# Parsing de hierarquia a partir do prompt do usuário

O usuário declara hierarquia em linguagem natural. A skill traduz pra
ordem de prioridade (string separada por vírgulas) que o `merge_sources.py`
aceita via `--hierarchy`.

## Default

Se o usuário **não** declarar hierarquia explicitamente, use:
```
pdf,url,image
```

Justificativa: PDFs de brand guidelines geralmente são a fonte canônica.
URLs já implementadas refletem a marca em uso (segunda fonte de verdade).
Imagens são as menos precisas.

## Frases que indicam hierarquia explícita

| Frase do usuário | Hierarquia |
|---|---|
| "PDF é fonte da verdade" | `pdf,url,image` |
| "use o site como referência principal" | `url,pdf,image` |
| "ignore o PDF, foca no site" | `url,image` (PDF excluído) |
| "a imagem que mandei é o briefing" | `image,pdf,url` |
| "use o linear.app como referência principal e meu PDF como suporte" | `url,pdf` |
| "o PDF tem prioridade sobre tudo" | `pdf,url,image` |
| "tudo igual" | tratar como default, mas sinalizar conflitos sem ganhador |

## Regra prática

1. Procure por frases tipo "X é fonte da verdade", "use X como principal",
   "X tem prioridade".
2. Se houver, monte a hierarquia colocando X primeiro, depois os outros
   na ordem default (pdf > url > image).
3. Se não houver, aplique default silenciosamente.
4. **Nunca pergunte** a hierarquia se ela não foi declarada — a decisão da
   skill é "default silencioso". Só registra no `decisions.md` qual hierarquia
   foi usada.

## Exemplo de decisão registrada

No `decisions.md` final:
```markdown
## Hierarquia de fontes

Hierarquia aplicada: PDF > URL > Imagem.
Origem: default silencioso (usuário não declarou).
Conflitos detectados: 2 (ver conflicts.md).
```

ou

```markdown
## Hierarquia de fontes

Hierarquia aplicada: URL > PDF > Imagem.
Origem: usuário declarou no prompt ("use o linear.app como referência principal").
Conflitos detectados: 0.
```
