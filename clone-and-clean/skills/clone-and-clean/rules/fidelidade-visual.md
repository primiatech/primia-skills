# Regra invinolável — fidelidade visual do clean vs original

## Por que essa regra existe

Na segunda execução da skill (Camila Vieira — Treinamento Posicione-se, 2026-04), o clean divergiu visualmente da original em **6 pontos simultâneos**:

1. Hero texto foi **centralizado** quando o original era alinhado à esquerda
2. Logo do header sumiu (ficou só texto)
3. Grid 2×2 de cards "o que você vai descobrir" virou **card único vertical**
4. Imagens das duas modelos ("Qual dessas mulheres é você") **sumiram**
5. Foto paisagem grande da mentora virou **thumbnail quadrado**
6. Formulário de lead que era **popup/modal** no original virou **inline**

O Hoberdan pediu reescrita imediata com a frase:

> "página que tem o texto na hero alinhado a esquerda devem permanecer assim, quando houver logo a logo deve ser replicada, tem que ser o mais próximo da realidade possível."

**Lição consolidada:** `clean` ≠ redesign. `clean` = **tradução** semântica + performática, preservando 100% da composição visual.

Essa regra existe em paralelo com `design-system.md` (que garante fidelidade **de tokens**) — esta aqui garante fidelidade **de composição e elementos**.

## Quando acionar

Sempre antes de escrever uma única linha do `clean/index.html` (Passo 7).
Depois de escrever cada seção, antes de passar pra próxima (loop de revisão).

## As 10 regras de fidelidade visual

### 1. Alinhamento de texto na hero
- Se o original tem texto alinhado à esquerda, o clean mantém alinhado à esquerda.
- Nunca centralizar porque "fica mais moderno".
- Idem pra direita.
- **Identifica no original**: olhe `text-align` do container de texto + posição relativa ao viewport.

### 2. Logo replicada
- Se o original tem logo (header, hero, footer — qualquer lugar), o clean replica essa logo na mesma posição.
- Não substitua por texto.
- Não omita mesmo "pra ficar minimal".
- **Como extrair**: baixa o arquivo SVG/PNG/WEBP da logo e referencia em `images/logo-*.{svg,webp,png}`.

### 3. Composição da hero
- Se o original é "texto em coluna esquerda + foto em coluna direita", o clean mantém 2 colunas.
- Se o original é "foto de fundo cobrindo toda a seção com texto sobreposto", o clean mantém assim.
- Não converta entre os dois padrões.
- **Como identificar**: screenshot + DOM inspection do viewport da dobra.

### 4. Elementos visuais intermediários
Todos devem ser preservados:
- Imagens entre cards (ilustrações, fotos de pessoas, mockups)
- Ornamentos/divisores (linhas, flores, detalhes decorativos)
- Ícones específicos (checks circulados ≠ números romanos ≠ emojis)
- Flechas, setas, indicadores

**Perder esses elementos descaracteriza a identidade.**

### 5. Estrutura de grids intacta
- 2×2 vira 2×2
- 2×3 vira 2×3
- Lista vertical vira lista vertical
- Grid horizontal vira grid horizontal
- Nunca colapsar grid em card único ("pra simplificar") nem expandir lista em grid ("pra preencher tela").
- **Exceção única**: responsivo mobile. `.grid-2 { grid-template-columns: 1fr 1fr }` pode virar `1fr` em `<768px`.

### 6. Tipo de formulário (popup vs inline)
- Se o original usa **popup/modal** pro lead (disparado por clique de CTA), o clean também usa popup/modal.
- Se o original tem **form inline** na seção, o clean mantém inline.
- Não embedar form inline onde o original tem popup.
- **Como identificar**: clique em cada CTA na original e veja se abre modal ou rola pra form inline.

### 7. Proporções de imagem
- Foto paisagem grande continua paisagem grande.
- Não encolher pra thumbnail quadrado.
- Foto vertical em bio não vira círculo.
- **Como preservar**: copiar aspect-ratio real da original via CSS (`aspect-ratio: 16/9` etc.).

### 8. Hero com foto integrada (asset único)
Quando a original usa **UM único asset** (tipicamente `bg-hero*.webp/jpg`) que já contém cenário + pessoa + iluminação integrados:

- Use esse asset como `background-image` da seção inteira com `background-size: cover`
- **Não tente separar** "foto da pessoa" em uma coluna e "fundo" em outra — isso perde a integração visual (luz, profundidade, auditório atrás, etc.)

```css
.hero.hero-2col {
  min-height: 100vh;
  background: var(--color-dark) url('images/bg-hero-desktop-2.webp') no-repeat center center;
  background-size: cover;
}
.hero.hero-2col::before {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(90deg, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.55) 30%, rgba(0,0,0,0.0) 55%);
}
```

### 9. Painel "único" com pessoa sobreposta
Quando o original mostra texto em 2 colunas **dentro de um único bloco cream/card contínuo** com a pessoa/modelo "em pé em cima" do bloco (transbordando o topo):

- ✅ Correto: UM `.vs-panel` com `.vs-panel-inner` em `grid-template-columns: 1fr 1fr` com gap central grande (ex: 12rem), e a imagem em `position: absolute; left: 50%; bottom: 0; transform: translateX(-50%)` transbordando o topo.
- ❌ Errado: 2 cards separados com imagem no gap (enxerga o fundo escuro entre os cards e quebra a ilusão de "um único bloco").

```css
.vs-panel {
  position: relative;
  max-width: 1200px;
  background: var(--brand-cream);
  border-radius: 28px;
  padding: 3rem 3.5rem;
}
.vs-panel-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12rem;
}
.vs-panel-photo {
  position: absolute;
  left: 50%; bottom: 0;
  transform: translateX(-50%);
  height: calc(100% + 80px);
}
```

### 10. Ícones no lugar de emojis nativos
Emojis como 📅 🕐 ✅ renderizam em **cor do sistema operacional** (preto/colorido default) e **nunca** batem com a paleta da marca. Substituir por SVG inline estilizado:

```html
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
     viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
  <line x1="16" y1="2" x2="16" y2="6"></line>
  <line x1="8" y1="2" x2="8" y2="6"></line>
  <line x1="3" y1="10" x2="21" y2="10"></line>
</svg>
```

Com cor via `stroke="currentColor"` controlado por `color: var(--brand-accent)` no elemento pai.

## Loop obrigatório de revisão visual

Após escrever cada seção do `clean/index.html`, antes de passar para a próxima:

1. Abrir screenshot da seção correspondente na original (ou re-capturar via DevTools)
2. Abrir a seção do clean renderizada localmente
3. Conferir item a item:
   - [ ] Alinhamento de texto (esquerda/centro/direita) idêntico
   - [ ] Logo presente se aplicável
   - [ ] Grid/estrutura de colunas idêntica
   - [ ] Imagens intermediárias presentes
   - [ ] Ornamentos/divisores presentes
   - [ ] Tipo de ícone correto (check vs número vs SVG vs emoji)
   - [ ] Proporção de imagens correta
   - [ ] Se hero com asset único: background-image aplicado na seção
   - [ ] Se painel contínuo com pessoa sobreposta: estrutura `.vs-panel` correta
   - [ ] Nenhum emoji nativo (só SVG ou texto)
4. Só avançar se 100% de match. Divergência estética é **sempre** regressão.

## Exceções permitidas (divergência legítima)

Clean pode divergir do original **somente** para correções técnicas silenciosas, nunca estéticas:

- Remover tracking pixels pra versão local de teste (depois reativar em produção)
- Substituir emoji por SVG (regra 10)
- Adicionar `aria-*`, `alt=""`, `loading="lazy"` (acessibilidade/performance)
- Normalizar paddings em múltiplos de 4/8px (regra `rules/clean-rewrite.md`)
- Trocar form provider de terceiros por endpoint próprio

**Qualquer divergência estética** (cor, alinhamento, grid, elemento sumindo/aparecendo) é **bug** e deve ser corrigida antes de finalizar.

## Validação no verify.py

Além das checagens existentes, o `verify.py` pode checar presença de assets críticos:

```python
critical_visuals = [
    "images/logo-*.{svg,webp,png}",      # logo replicada
    "images/bg-hero-*.webp",             # hero integrado
    "images/foto-pessoa-*.{webp,jpg}",   # modelos em painéis
]
# Grep no HTML: pelo menos 1 referência a cada padrão
```

Se o original tinha um SVG de logo mas o clean não referencia nenhum arquivo de logo → erro de fidelidade visual.
