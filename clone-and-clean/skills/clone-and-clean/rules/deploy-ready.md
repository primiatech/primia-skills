# Regras para o artefato `deploy-ready/`

O `deploy-ready/` é uma **captura 1:1 da página original**, mas reconfigurada pra rodar 100% self-contained em hospedagem estática (Vercel, Netlify, Cloudflare Pages).

## 1. Pixels e analytics — MANTER ORIGINAIS por padrão

Manter os IDs de tracking originais:
- Meta Pixel
- GTM (Google Tag Manager)
- GA4 (Google Analytics 4)
- Google Ads / AW-*
- Microsoft Clarity
- LeadTracker
- Hotjar (se presente)
- PixelYourSite (gerenciador WP — só os IDs finais importam)

**Por quê:** a intenção do deploy-ready é servir como base fiel pra lançamentos novos. O usuário prefere trocar os IDs manualmente quando for reutilizar, ao invés de ter que recolocar do zero.

**Aviso obrigatório:** no `README.md` do deploy-ready, incluir um **checklist destacado** com todos os IDs mantidos e a orientação explícita de trocar antes de publicar (senão vai contaminar a conta do cliente original).

**Correção de loader GTM:** o rewriter de paths pode reescrever erroneamente `https://www.googletagmanager.com/gtm.js` pra um path local. Corrigir manualmente pra apontar pro Google de volta.

## 2. APIs dinâmicas externas — COMENTAR com TODO

Serviços como progress bar da grupofpx, sistemas de contagem de vendas externos, leadscore de terceiros:

```html
<!-- TODO: reconfigurar endpoint para novo lançamento
<script src="https://api.grupofpx.com/pb/main.js" data-token="..."></script>
-->
```

Manter o markup visual (div da progress bar, etc) mas comentar o script que busca os dados. Isso preserva a estrutura HTML/CSS pro template funcionar e evita disparo em ambiente errado.

## 3. WhatsApp e contatos do cliente original — PLACEHOLDER

Números de WhatsApp, telefones, emails que apontam pra contato direto do cliente original:

```html
<!-- antes -->
<a href="https://wa.me/5513974236404?text=Olá...">

<!-- depois -->
<a href="https://wa.me/TODO_WHATSAPP_NUMBER?text=Olá...">
```

Também normalizar textos pré-preenchidos pra genérico:

```
Olá. Gostaria de saber mais sobre a Imersão
```

## 4. CSS/JS/fontes hospedados no domínio original — BAIXAR TUDO

A página não pode depender do WordPress do cliente continuar no ar.
- Varrer todo CSS por `url(...)` e baixar referências
- Varrer HTML por `src`/`href` locais e baixar
- Reescrever paths pra locais
- Remover CDNs opcionais (Cloudflare Insights, Cloudflare Beacon, etc)

## 5. Limpezas WordPress obrigatórias

Remover do HTML:
- `<link rel="https://api.w.org/">`
- `<link rel="EditURI">`
- `<link rel="alternate" type="application/json" href=".../wp-json/...">` (mantém só o feed se houver)
- `<meta name="generator">` do WP/Elementor
- Referências a `xmlrpc.php`
- Referências a `wlwmanifest`
- `<script type="speculationrules">` (API experimental do Chrome)
- Links de admin (`wp-admin/admin-ajax.php` se forem apenas cosméticos)

## 6. Canonical URL

```html
<link rel="canonical" href="#" data-todo="substituir pelo domínio final">
```

## 7. Feeds RSS

Manter `<link rel="alternate" type="application/rss+xml">` como está (navegador ignora no render, e pode ser útil se o template virar CMS). Não é prioridade.

## 8. O que NÃO pode fazer no deploy-ready

- Não alterar layout visual
- Não otimizar CSS/HTML (isso é trabalho do `clean/`)
- Não mexer em copy
- Não mudar estrutura do DOM
- Não remover classes `elementor-*` (podem ser referenciadas por CSS)

O deploy-ready é **conservador**. A criatividade vai pro `clean/`.
