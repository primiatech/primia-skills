# Banco de Exemplos — Recomendações

Este documento mostra **como fazer e como NÃO fazer** recomendações na seção 5.9 da análise. Use como referência ao redigir.

## Princípio fundamental

Toda recomendação tem 3 partes obrigatórias:

1. **Ação concreta** (o quê, especificamente)
2. **Evidência vinculada** (qual padrão observado nos concorrentes justifica)
3. **Indicação de prioridade** (Alta/Média/Baixa, com justificativa de tamanho)

Recomendações sem evidência vinculada são opinião — e o usuário não está pagando por opinião, está pagando por inteligência.

---

## Exemplos comparados

### Exemplo 1 — Hook de vídeo

❌ **Ruim:**
> Teste hooks mais fortes nos vídeos.

(Genérico, não acionável, sem evidência.)

✅ **Bom:**
> Teste hook de pergunta direta nos primeiros 3 segundos. **Evidência:** 7 dos 10 anúncios mais longevos analisados (IDs 1234567890, 0987654321, 1122334455, 5566778899, 9988776655, 4433221100, 6677889900) abrem com pergunta direta ao espectador. Nenhum dos 4 concorrentes evitou esse padrão. **Prioridade: Alta** — é o padrão de abertura mais consistente entre vencedores.

---

### Exemplo 2 — Oferta

❌ **Ruim:**
> Considere fazer descontos.

✅ **Bom:**
> Teste oferta de garantia de 7 dias em campanhas de fundo de funil. **Evidência:** 8 dos 12 anúncios em conversão direta de Hotmart e Eduzz mencionam "7 dias de garantia" (IDs A, B, C). Kiwify usa 30 dias, mas roda anúncios mais curtos (mediana 12 dias) — sugerindo garantia mais longa não compensa em CPM no nicho. **Prioridade: Média** — fácil de testar, baixo risco operacional.

---

### Exemplo 3 — Funil

❌ **Ruim:**
> Invista mais em topo de funil.

✅ **Bom:**
> Aloque 20-30% do budget em criativos de topo de funil com formato educativo curto (15-20s). **Evidência:** Hotmart dedica 35% do volume a topo (24 anúncios) com mediana de 67 dias — o maior portfólio "evergreen" entre concorrentes. Eduzz e Kiwify estão concentrados em fundo (>80% do volume), o que sugere dependência de remarketing e aquisição paga cara. **Prioridade: Alta** — preenche gap estrutural na operação atual.

---

### Exemplo 4 — Formato

❌ **Ruim:**
> Use mais carrosséis.

✅ **Bom:**
> Substitua carrosséis estáticos por vídeos de 30-45s em fundo de funil. **Evidência:** dos 31 anúncios com `days_running ≥ 60` na análise, 26 são vídeos. Apenas 2 são carrosséis e ambos são de Hotmart, especificamente para produtos de baixo ticket (sub-R$200). **Prioridade: Média** — exige produção de criativo, mas com retorno previsível dado o padrão.

---

### Exemplo 5 — Quando você NÃO tem evidência forte

Não force. Se o sinal for fraco, diga.

✅ **Honesto:**
> **Hipótese a validar (não recomendação firme):** UGC com depoimentos pode estar funcionando. **Evidência limitada:** apenas 3 dos 100 anúncios analisados usam UGC explícito (IDs X, Y, Z), mas todos os 3 estão entre os 20 mais longevos. Sinal interessante porém ruidoso (n=3). **Sugestão:** rodar 1 teste piloto com UGC antes de comprometer budget significativo.

---

## Estrutura sugerida em JSON

Quando preencher o `analysis.json`, use este shape:

```json
{
  "recommendations": [
    {
      "titulo": "Teste hook de pergunta direta nos primeiros 3 segundos de vídeo",
      "evidencia": "7 dos 10 anúncios mais longevos abrem com pergunta direta (IDs: 1234, 5678, 9012). Nenhum concorrente evita esse padrão.",
      "prioridade": "Alta",
      "categoria": "Criativo / Hook",
      "esforco_estimado": "Baixo — mudança de roteiro",
      "risco": "Baixo"
    },
    {
      "titulo": "Aloque 20-30% do budget em topo de funil com vídeo educativo curto",
      "evidencia": "Hotmart dedica 35% do volume a topo de funil com mediana de 67 dias no ar. Concorrentes diretos estão concentrados em fundo (>80%).",
      "prioridade": "Alta",
      "categoria": "Mídia / Estratégia de funil",
      "esforco_estimado": "Médio — exige planejamento de mídia",
      "risco": "Médio"
    }
  ]
}
```

---

## Quantidade

Mire em **5-10 recomendações totais**, não mais. Recomendações demais diluem prioridade. Se identificar 30 oportunidades, escolha as 8 com maior assimetria (alto impacto, baixo esforço/risco).

## Ordenação

Liste em ordem de prioridade decrescente — Alta primeiro. Dentro do mesmo nível, ordene por menor esforço (quick wins primeiro).

## Linguagem

- Use **verbos de ação no imperativo**: "Teste", "Aloque", "Substitua", "Adicione"
- Evite **modal verbs fracos**: "poderia", "talvez", "considerar" (a menos que seja hipótese explícita)
- Numere com referência cruzada quando aplicável: "Combinando com a recomendação 3..."
