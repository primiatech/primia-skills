#!/usr/bin/env python3
"""
scrape_ad_library.py — Scraper da Meta Ad Library via Playwright (interface pública).

Uso:
    python scrape_ad_library.py \
        --advertiser "Nome do Concorrente" \
        --country BR \
        --active-status all \
        --ad-type all \
        --limit 100 \
        --output-dir /home/claude/output/concorrente-slug

Saída: <output-dir>/raw_ads.json com lista de anúncios estruturados.

Estratégia:
- Acessa a URL de busca pública (sem login).
- Usa scroll programático até atingir limite ou esgotar resultados.
- Múltiplos seletores de fallback (a Meta muda layout com frequência).
- Em caso de CAPTCHA/bloqueio, salva progresso parcial e sai limpo.
"""

import argparse
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("ERRO: playwright não instalado. Rode: pip install playwright && playwright install chromium")
    sys.exit(1)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def slugify(text: str) -> str:
    """Converte texto em slug seguro para nome de arquivo/pasta."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def parse_date_br(text: str):
    """Tenta parsear datas em PT-BR no formato 'D de mês de YYYY' ou 'D mês YYYY'."""
    if not text:
        return None
    months = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
        "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
        "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
        "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
    }
    text = text.lower().strip()
    m = re.search(r"(\d{1,2})\s*(?:de\s+)?(\w+)\s*(?:de\s+)?(\d{4})", text)
    if m:
        day, month_name, year = m.groups()
        month = months.get(month_name)
        if month:
            try:
                return datetime(int(year), month, int(day), tzinfo=timezone.utc).date().isoformat()
            except ValueError:
                return None
    return None


def days_between(start_iso: str, end_iso: str | None) -> int | None:
    """Calcula diferença em dias entre datas ISO. Se end_iso for None, usa hoje."""
    if not start_iso:
        return None
    try:
        start = datetime.fromisoformat(start_iso).date()
        end = datetime.fromisoformat(end_iso).date() if end_iso else datetime.now(timezone.utc).date()
        return (end - start).days
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Scraping
# --------------------------------------------------------------------------- #

def build_search_url(advertiser: str, country: str, active_status: str, ad_type: str) -> str:
    """Monta a URL de busca pública da Ad Library."""
    base = "https://www.facebook.com/ads/library/"
    params = {
        "active_status": active_status,
        "ad_type": ad_type,
        "country": country,
        "q": advertiser,
        "search_type": "keyword_unordered",
        "media_type": "all",
    }
    qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    return f"{base}?{qs}"


def dismiss_cookies(page):
    """Tenta fechar banners de cookie/login. Tolerante a falha."""
    selectors = [
        'div[role="button"][aria-label*="ecusar"]',
        'div[role="button"][aria-label*="Recusar"]',
        'div[role="button"][aria-label*="ssential"]',
        'button[data-cookiebanner="accept_button"]',
        'div[aria-label="Fechar"]',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                el.click(timeout=2000)
                page.wait_for_timeout(500)
        except Exception:
            pass


def detect_block(page) -> bool:
    """Detecta se a página foi bloqueada (CAPTCHA, login obrigatório)."""
    indicators = [
        "captcha", "verificação de segurança", "security check",
        "entrar no facebook", "log in to facebook", "você foi bloqueado",
    ]
    try:
        body = page.inner_text("body", timeout=3000).lower()
        return any(ind in body for ind in indicators)
    except Exception:
        return False


def scroll_and_collect(page, limit: int, max_idle_rounds: int = 5) -> int:
    """
    Faz scroll progressivo até atingir limite ou esgotar resultados.
    Retorna o número aproximado de cards visíveis.
    """
    last_count = 0
    idle_rounds = 0
    scroll_count = 0

    while True:
        cards = page.query_selector_all('div[role="article"], div[data-pagelet*="AdLibrary"]')
        current = len(cards)

        if current >= limit:
            return current

        if current == last_count:
            idle_rounds += 1
            if idle_rounds >= max_idle_rounds:
                return current
        else:
            idle_rounds = 0
            last_count = current

        page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
        page.wait_for_timeout(2000)
        scroll_count += 1

        # safety: máximo 100 scrolls
        if scroll_count > 100:
            return current


def extract_ads(page) -> list[dict]:
    """
    Extrai dados estruturados dos cards de anúncio visíveis na página.
    Usa parsing baseado em estrutura visível + atributos.
    """
    js = r"""
    () => {
        const cards = document.querySelectorAll('div[role="article"], div[data-pagelet*="AdLibrary"] > div > div > div');
        const out = [];

        cards.forEach((card) => {
            try {
                const text = card.innerText || '';
                if (text.length < 30) return;

                // ID do anúncio (Library ID: XXXXXXX)
                const idMatch = text.match(/(?:Library ID|Identificação na biblioteca|ID da biblioteca):\s*(\d+)/i);
                const adId = idMatch ? idMatch[1] : null;

                // Status: Ativo / Inativo
                const isActive = /Ativ[oa]|Active/i.test(text.split('\n')[0] || '');

                // Datas: "Veiculado a partir de DATA" ou "Veiculado de DATA até DATA"
                let startDate = null, endDate = null;
                const dateRangeMatch = text.match(/(?:Veiculado de|Started running on|Ran from)\s+([^\n]+?)(?:\s+(?:até|to|-)\s+([^\n]+?))?(?:\n|$)/i);
                if (dateRangeMatch) {
                    startDate = dateRangeMatch[1] ? dateRangeMatch[1].trim() : null;
                    endDate = dateRangeMatch[2] ? dateRangeMatch[2].trim() : null;
                }
                const startOnlyMatch = text.match(/(?:Veiculado a partir de|Started running on)\s+([^\n]+?)(?:\n|$)/i);
                if (startOnlyMatch && !startDate) {
                    startDate = startOnlyMatch[1].trim();
                }

                // Plataformas (procura ícones / texto)
                const platforms = [];
                if (/Facebook/i.test(text)) platforms.push('facebook');
                if (/Instagram/i.test(text)) platforms.push('instagram');
                if (/Messenger/i.test(text)) platforms.push('messenger');
                if (/Audience Network/i.test(text)) platforms.push('audience_network');
                if (/Threads/i.test(text)) platforms.push('threads');

                // Variations
                const varMatch = text.match(/(\d+)\s+(?:versões deste an[uú]ncio|ad versions|versions)/i);
                const variationsCount = varMatch ? parseInt(varMatch[1]) : 1;

                // Page name (geralmente o primeiro link forte ou heading)
                const pageNameEl = card.querySelector('a[role="link"] strong, a[role="link"] span[dir="auto"]');
                const pageName = pageNameEl ? pageNameEl.innerText.trim() : null;

                // Body text: pega o maior bloco de texto após as metadata
                const allParagraphs = Array.from(card.querySelectorAll('div[dir="auto"] span, div[dir="auto"]'))
                    .map(p => p.innerText.trim())
                    .filter(t => t.length > 30);
                const bodyText = allParagraphs.sort((a, b) => b.length - a.length)[0] || null;

                // Headline e link de destino
                const linkEl = card.querySelector('a[href*="l.facebook.com/l.php"], a[href^="https://"][role="link"][target="_blank"]');
                let linkUrl = linkEl ? linkEl.href : null;
                // Limpa redirect do Facebook
                if (linkUrl && linkUrl.includes('l.facebook.com/l.php')) {
                    try {
                        const u = new URL(linkUrl);
                        linkUrl = u.searchParams.get('u') || linkUrl;
                    } catch (e) {}
                }

                // CTA (procura por botões conhecidos)
                const ctaPatterns = ['Saiba mais', 'Compre agora', 'Cadastre-se', 'Inscreva-se',
                                     'Baixar', 'Reservar', 'Assinar', 'Entrar em contato',
                                     'Learn more', 'Shop now', 'Sign up', 'Download', 'Book now'];
                let cta = null;
                for (const p of ctaPatterns) {
                    if (text.includes(p)) { cta = p; break; }
                }

                // Mídia: imagens e vídeos
                const mediaUrls = [];
                card.querySelectorAll('img').forEach(img => {
                    if (img.src && img.src.startsWith('http') &&
                        !img.src.includes('emoji') && !img.src.includes('static') &&
                        img.naturalWidth > 100) {
                        mediaUrls.push({ type: 'image', url: img.src });
                    }
                });
                card.querySelectorAll('video').forEach(v => {
                    if (v.src) mediaUrls.push({ type: 'video', url: v.src });
                    if (v.poster) mediaUrls.push({ type: 'image', url: v.poster, role: 'thumbnail' });
                });

                // Tipo de criativo
                let creativeType = 'image';
                if (mediaUrls.some(m => m.type === 'video')) creativeType = 'video';
                else if (mediaUrls.filter(m => m.type === 'image').length > 1) creativeType = 'carousel';

                if (adId || bodyText) {
                    out.push({
                        ad_archive_id: adId,
                        page_name: pageName,
                        is_active: isActive,
                        start_date_raw: startDate,
                        end_date_raw: endDate,
                        platforms: platforms,
                        variations_count: variationsCount,
                        body_text: bodyText,
                        cta_type: cta,
                        link_url: linkUrl,
                        creative_type: creativeType,
                        media_urls: mediaUrls,
                        raw_text: text.substring(0, 2000)
                    });
                }
            } catch (err) {
                // ignora erros em cards individuais
            }
        });

        return out;
    }
    """
    return page.evaluate(js)


def post_process(ads: list[dict], advertiser: str) -> list[dict]:
    """Pós-processa os anúncios: parse de datas, dedup, cálculo de days_running."""
    processed = []
    seen_ids = set()

    for ad in ads:
        ad_id = ad.get("ad_archive_id")
        if ad_id and ad_id in seen_ids:
            continue
        if ad_id:
            seen_ids.add(ad_id)

        start_iso = parse_date_br(ad.get("start_date_raw") or "")
        end_iso = parse_date_br(ad.get("end_date_raw") or "")
        days = days_between(start_iso, end_iso) if start_iso else None

        ad["start_date"] = start_iso
        ad["end_date"] = end_iso
        ad["days_running"] = days
        ad["scraped_advertiser_query"] = advertiser
        ad["scraped_at"] = datetime.now(timezone.utc).isoformat()

        processed.append(ad)

    return processed


def scrape(advertiser: str, country: str, active_status: str, ad_type: str,
           limit: int, output_dir: Path, headless: bool = True) -> dict:
    """Função principal. Retorna metadata da execução."""
    output_dir.mkdir(parents=True, exist_ok=True)
    url = build_search_url(advertiser, country, active_status, ad_type)
    print(f"[*] Acessando: {url}")

    result = {"advertiser": advertiser, "url": url, "ads_collected": 0, "blocked": False}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1366, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="pt-BR",
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)
            dismiss_cookies(page)
            page.wait_for_timeout(2000)

            if detect_block(page):
                print("[!] Bloqueio/CAPTCHA detectado. Salvando progresso parcial.")
                result["blocked"] = True
                browser.close()
                return result

            # Aguarda primeiro card aparecer
            try:
                page.wait_for_selector('div[role="article"]', timeout=15000)
            except PWTimeout:
                print("[!] Nenhum card encontrado em 15s — pode ser que o anunciante não tenha anúncios.")

            print(f"[*] Iniciando scroll para coletar até {limit} anúncios...")
            scroll_and_collect(page, limit)

            print("[*] Extraindo dados dos cards...")
            ads = extract_ads(page)
            print(f"[*] {len(ads)} cards brutos extraídos. Pós-processando...")

            processed = post_process(ads, advertiser)[:limit]

            output_file = output_dir / "raw_ads.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "advertiser": advertiser,
                        "country": country,
                        "active_status": active_status,
                        "ad_type": ad_type,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "url": url,
                        "total_ads": len(processed),
                    },
                    "ads": processed
                }, f, ensure_ascii=False, indent=2)

            result["ads_collected"] = len(processed)
            result["output_file"] = str(output_file)
            print(f"[✓] {len(processed)} anúncios salvos em {output_file}")

        except Exception as e:
            print(f"[!] Erro durante scraping: {e}")
            result["error"] = str(e)
        finally:
            browser.close()

    return result


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Scraper da Meta Ad Library")
    parser.add_argument("--advertiser", required=True, help="Nome do anunciante / página")
    parser.add_argument("--country", default="BR", help="Código do país (default: BR)")
    parser.add_argument("--active-status", default="all",
                        choices=["all", "active", "inactive"], help="Status do anúncio")
    parser.add_argument("--ad-type", default="all",
                        choices=["all", "political_and_issue_ads", "housing_ads",
                                 "employment_ads", "credit_ads"], help="Categoria")
    parser.add_argument("--limit", type=int, default=100, help="Máximo de anúncios")
    parser.add_argument("--output-dir", required=True, help="Pasta de saída")
    parser.add_argument("--no-headless", action="store_true",
                        help="Roda com browser visível (debug)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    result = scrape(
        advertiser=args.advertiser,
        country=args.country,
        active_status=args.active_status,
        ad_type=args.ad_type,
        limit=args.limit,
        output_dir=output_dir,
        headless=not args.no_headless,
    )

    print("\n" + "=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)

    if result.get("blocked") or result.get("ads_collected", 0) == 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
