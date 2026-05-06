# Frameworks de Análise Estratégica

Detalhamento das classificações usadas na Etapa 5. Use este documento quando estiver classificando anúncios para garantir consistência.

## 1. Ângulos de comunicação

Cada anúncio tem **um ângulo dominante** (raramente dois). Classifique pelo PRIMEIRO movimento da copy/vídeo.

### Dor (Pain)
**Sinal:** começa identificando um problema do cliente.
**Exemplos de abertura:**
- "Cansado de [problema]?"
- "Você já passou por isso..."
- "Sabe quando você [situação chata]?"
- "Ninguém te conta sobre [obstáculo]"

### Desejo / Aspiração
**Sinal:** pinta um cenário ideal/transformação.
**Exemplos:**
- "Imagine acordar e..."
- "E se você pudesse [resultado desejado]?"
- "[Pessoa] conseguiu [transformação] em [tempo]"

### Prova social
**Sinal:** depoimento real, números agregados, validação de terceiros.
**Exemplos:**
- "Mais de 50 mil alunos já..."
- "Veja o que [nome] tem a dizer:"
- Vídeo começando com cliente falando direto pra câmera (UGC)

### Autoridade
**Sinal:** expertise, credenciais, mídia, certificações.
**Exemplos:**
- "Eu, [nome], formado em [coisa], descobri..."
- "Como visto em [Globo, Forbes, etc]"
- "Método aprovado por [instituição]"

### Novidade
**Sinal:** algo é novo, recém-lançado, recém-descoberto.
**Exemplos:**
- "NOVO: o método que..."
- "Lançamento: [produto]"
- "A descoberta que está mudando [setor]"

### Curiosidade
**Sinal:** pergunta ou afirmação que cria gap de informação.
**Exemplos:**
- "Você sabia que..."
- "O segredo que [autoridade] não quer que você saiba"
- "99% das pessoas erram nisso"

### Comparação
**Sinal:** posiciona contra alternativa.
**Exemplos:**
- "Diferente de [concorrente categoria]..."
- "Cansado de [solução comum que não funciona]?"
- "Enquanto outros [coisa ruim], nós [coisa boa]"

### Storytelling pessoal
**Sinal:** narrativa de jornada, geralmente em primeira pessoa.
**Exemplos:**
- "Há 3 anos, eu estava..."
- "Quando descobri isso, minha vida mudou..."
- Vídeo começando com a história do criador

---

## 2. Estágios de funil

### Topo (Awareness)
**Objetivo:** introduzir marca/categoria a quem ainda não busca a solução.
**Sinais:**
- CTA leve: "Saiba mais", "Ver mais", "Curtir página"
- Sem oferta direta, sem preço
- Tom educativo / inspiracional
- Conteúdo de utilidade (dica, fato curioso)

### Meio (Consideração)
**Objetivo:** ajudar quem já sabe que tem o problema a avaliar soluções.
**Sinais:**
- CTA médio: "Ver detalhes", "Conhecer o método", "Acessar"
- Apresenta o produto/serviço
- Pode ter preço, mas não é o foco
- Comparações, demonstrações, casos de uso

### Fundo (Conversão)
**Objetivo:** converter quem já está decidido.
**Sinais:**
- CTA forte: "Compre agora", "Inscreva-se", "Garanta sua vaga"
- Oferta direta com preço
- Urgência ("últimas vagas", "só hoje")
- Garantias e bônus
- Remarketing reconhecível ("Você esqueceu seu carrinho")

**Caso ambíguo:** se o anúncio é puramente de marca/branding (sem CTA claro de produto), classifique como Topo.

---

## 3. Frameworks de copy

### AIDA (Atenção → Interesse → Desejo → Ação)
- **A**: hook que para o scroll
- **I**: contexto que prende
- **D**: amplifica desejo pelo resultado
- **A**: CTA explícito
**Marcador típico:** estrutura linear de quatro blocos.

### PAS (Problema → Agitação → Solução)
- **P**: nomeia a dor
- **A**: amplifica/intensifica a dor (consequências)
- **S**: apresenta o produto como solução
**Marcador típico:** copy curta com tom emocional crescente.

### Antes/Depois/Ponte (BAB)
- **B**: descreve situação atual ruim
- **A**: descreve situação ideal
- **B**: ponte = o produto
**Marcador típico:** "Saia de [X] para [Y]"; comparações antes/depois.

### Lista de benefícios
- Bullet points dos resultados/features
- Sem narrativa, foco em valor entregue
**Marcador típico:** ✓ ✓ ✓ ou números no início de linhas.

### Storytelling pessoal
- Narrativa cronológica
- Primeira pessoa
- Jornada → descoberta → produto
**Marcador típico:** "Eu já fui [X]... até descobrir [produto]".

---

## 4. Critério de "anúncio campeão"

Um anúncio é candidato a campeão se atende **pelo menos 2** dos 4 critérios:

1. **Longevidade**: `days_running ≥ 30`
2. **Variações**: `variations_count ≥ 3` (concorrente está testando muito = está investindo)
3. **Distribuição ampla**: roda em FB + IG simultaneamente
4. **Ainda ativo**: `is_active == true` no momento do scraping

Anúncios que atendem os 4 critérios são campeões fortes — destaque na análise.

---

## 5. Sinais de saturação vs. oportunidade

**Saturação:** quando 60%+ dos concorrentes usam o mesmo ângulo + estágio.
- Implicação: difícil destacar usando esse padrão.
- Ação: testar ângulo subutilizado.

**Oportunidade:** quando um ângulo claramente eficaz em outras categorias está ausente do nicho analisado.
- Implicação: hipótese de teste com baixo risco competitivo.
- Ação: validar com criativo único antes de escalar.

---

## 6. Limites do que você pode afirmar

**Pode afirmar com confiança (sinais públicos diretos):**
- Volume de anúncios
- Tempo de veiculação
- Número de variações
- Plataformas onde rodam
- Conteúdo do criativo (copy, imagem, vídeo)
- Cadência de lançamento

**Não pode afirmar (a Meta NÃO expõe publicamente):**
- ROAS, CTR, CPC, CPA, conversões
- Volume de impressões (exceto política)
- Investimento em mídia (exceto política)
- Públicos-alvo configurados

**Pode inferir com cautela (sinal indireto, declare como hipótese):**
- "Provavelmente performando bem" (baseado em longevidade)
- "Hipótese de público-alvo: [X]" (baseado em linguagem/estética)
- "Aparente lançamento de produto" (baseado em pico de cadência)

Sempre que inferir, use linguagem de hipótese: "indica", "sugere", "é consistente com".
