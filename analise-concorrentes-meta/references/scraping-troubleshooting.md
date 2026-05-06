# Scraping Troubleshooting — Meta Ad Library

A interface da Meta Ad Library muda com frequência. Este guia descreve como diagnosticar e adaptar quando o scraping para de funcionar.

## Sintomas comuns e soluções

### Sintoma: 0 anúncios retornados, mesmo o concorrente tendo anúncios ativos

**Diagnóstico:**

1. Abra manualmente: `https://www.facebook.com/ads/library/?country=BR&q=NOME_DO_ANUNCIANTE`
2. Verifique se aparecem anúncios. Se não aparecem, o problema não é seu scraper — o concorrente realmente não tem anúncios naquele país/categoria.
3. Se aparecem manualmente mas o scraper retorna 0, o seletor de cards mudou.

**Solução:**

Rode o scraper com `--no-headless` para ver o que está acontecendo. Quando os cards aparecerem, abra o DevTools (F12) e inspecione. O seletor atual é:

```javascript
'div[role="article"], div[data-pagelet*="AdLibrary"] > div > div > div'
```

Se o atributo `role="article"` não existir mais, procure outro padrão estável (geralmente algum `data-pagelet` com prefixo `AdLibrary`). Atualize a função `extract_ads()` em `scrape_ad_library.py`.

---

### Sintoma: CAPTCHA ou tela de login obrigatório

**Diagnóstico:** O detector `detect_block()` identifica isso e sai limpo. Veja se o stdout do scraper diz `"blocked": true`.

**Soluções:**

1. **Aguarde 30 minutos** e tente novamente. A Meta libera após cooldown.
2. **Use VPN** — bloqueios são por IP. Mudar de IP geralmente resolve.
3. **Reduza a frequência**: se está rodando vários concorrentes em sequência, adicione delay entre execuções:
   ```bash
   for c in concorrente1 concorrente2 concorrente3; do
       python scrape_ad_library.py --advertiser "$c" ...
       sleep 60
   done
   ```
4. **Mude user-agent**: edite `user_agent` no `context = browser.new_context(...)` para um valor mais recente.

---

### Sintoma: scroll não carrega mais anúncios (para no meio)

**Causa provável:** A Meta tem rate limit no carregamento via scroll. Após ~50-80 cards, pode parar de carregar.

**Solução:** O script tem `max_idle_rounds=5` — após 5 scrolls sem novos cards, ele desiste. Se quiser forçar mais, aumente para 10. Mas a partir de certo ponto, simplesmente não há mais anúncios para aquela query.

---

### Sintoma: dados parciais (faltam datas, plataformas, ou body_text)

**Diagnóstico:** A extração JS é tolerante a falhas — pega o que consegue, ignora o que não. Se um campo aparece null para muitos anúncios, o regex/seletor daquele campo quebrou.

**Solução:** Edite a função `extract_ads()` no script. Os campos são extraídos via regex sobre o texto visível do card — adapte os padrões. Por exemplo, se o texto agora diz "Em veiculação desde DATA" em vez de "Veiculado a partir de DATA", ajuste o regex.

---

### Sintoma: links de mídia (imagens/vídeos) retornam 403 ao baixar

**Causa:** A CDN da Meta usa URLs assinadas com TTL curto. Se demorar muito entre scraping e download, expira.

**Solução:**

1. Rode `download_creatives.py` IMEDIATAMENTE após o scraping (mesmo dia).
2. Para vídeos, `yt-dlp` é mais robusto que requests porque sabe lidar com m3u8 e URLs assinadas.
3. Se ainda falhar, o `download_creatives.py` continua o processo — você terá os metadados mesmo sem o arquivo.

---

### Sintoma: Playwright trava ou não inicia

**Causa comum:** dependências de sistema do Chromium ausentes no ambiente.

**Solução:**

```bash
playwright install chromium --with-deps
# ou
apt-get install -y libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
                   libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
                   libpango-1.0-0 libcairo2 libasound2
```

Se está em ambiente serverless/sandbox onde não dá pra instalar pacotes do sistema, use a flag `--no-sandbox` (já está no script).

---

## Quando tudo falhar

A Meta Ad Library tem uma **API oficial** (`Ad Library API`) que requer:
- Conta de desenvolvedor Meta
- Verificação de identidade
- Token de acesso de longa duração

Se o scraping ficar inviável, considere migrar para a API oficial — é mais estável, embora limitada a anúncios políticos/de issues em muitos países (anúncios comerciais brasileiros NÃO são acessíveis via API oficial em 2026).

Documentação: `https://www.facebook.com/ads/library/api/`
