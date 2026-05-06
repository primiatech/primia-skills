# Decisões — {{PROJECT_NAME}}

Este documento explica cada decisão automatizada que a `primia-design`
tomou ao gerar este design system. Use como referência pra entender
o porquê de cada token e identificar pontos de divergência da intenção
original — você pode editar os JSONs em `tokens/` e regenerar.

## 1. Hierarquia de fontes

**Aplicada:** {{HIERARCHY_HUMAN}}
**Origem:** {{HIERARCHY_ORIGIN}}

{{HIERARCHY_NOTE}}

Quando duas fontes discordaram, a fonte mais alta na hierarquia venceu.
Conflitos detectados estão em `conflicts.md`.

## 2. Cor primary

**Escolhida:** `{{PRIMARY_COLOR}}`
**Critério:** cor mais saturada combinada com maior frequência na fonte
de maior prioridade. Cinzas (saturação < 20%) são automaticamente
descartados como candidatos a primary.

A escala 50-950 foi gerada mantendo o hue da cor base e ajustando
lightness — saturação reduz levemente nos extremos pra parecer natural.

## 3. Cor neutral (cinza)

{{NEUTRAL_NOTE}}

A escala neutral cobre todo o texto, fundos e bordas do design system.
Ela é a cor mais usada em qualquer interface — vale revisar se está com
o tom certo (warm/cool gray).

## 4. Cores semânticas

| Slot     | Status      | Valor escolhido     |
|----------|-------------|---------------------|
| success  | {{SUCCESS_STATUS}} | `{{SUCCESS_COLOR}}` |
| warning  | {{WARNING_STATUS}} | `{{WARNING_COLOR}}` |
| danger   | {{DANGER_STATUS}}  | `{{DANGER_COLOR}}`  |
| info     | {{INFO_STATUS}}    | `{{INFO_COLOR}}`    |

**Status "inferido":** a skill identificou uma cor da fonte cujo hue cai
no slot semântico (ex: verde com hue 80-160° → success).
**Status "default":** a skill não encontrou cor adequada e usou um
default razoável (paleta Tailwind). Considere revisar se a marca tem
preferência.

## 5. Tipografia

**Família body:** {{FONT_BODY}}
**Família display:** {{FONT_DISPLAY}}
**Família mono:** {{FONT_MONO}}

**Escala detectada:** {{TYPO_SCALE_NAME}} (ratio {{TYPO_SCALE_RATIO}})
**Erro de fit:** {{TYPO_FIT_ERROR}}

A skill testou 8 escalas modulares comuns e escolheu a que melhor
explica os tamanhos extraídos. Erro de fit baixo (< 0.05) significa
que a escala é precisa; alto (> 0.15) significa que os tamanhos não
seguem uma escala consistente — vale revisar.

## 6. Spacing

**Step base:** múltiplos de **{{SPACING_STEP}}px**

A skill testou escalas de 4px e 8px e escolheu a com menor erro
acumulado. Tokens "staples" (0, 4, 8, 12, 16, 24, 32, 48, 64) são
sempre incluídos, mesmo que não tenham aparecido na fonte.

## 7. Border-radius e shadows

{{RADIUS_NOTE}}
{{SHADOW_NOTE}}

## 8. Contraste WCAG

| Métrica          | Quantidade |
|------------------|------------|
| Total testado    | {{CONTRAST_TOTAL}} |
| Passa AA         | {{CONTRAST_AA}} |
| Passa AAA        | {{CONTRAST_AAA}} |
| Só texto grande  | {{CONTRAST_AA_LARGE}} |
| **Falham**       | {{CONTRAST_FAIL}} |

{{CONTRAST_WARNINGS}}

Se há pares falhando, considere ajustar manualmente nos JSONs em
`tokens/` ou usar combinações alternativas em produção.

## 9. Limitações desta extração

{{LIMITATIONS}}

## 10. Avisos da extração

{{EXTRACTION_WARNINGS}}

---

*Gerado por primia-design em {{DATE}}.*
