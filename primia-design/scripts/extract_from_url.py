#!/usr/bin/env python3
"""
Extrai design tokens de uma URL.

Estratégia híbrida:
1. Tenta primeiro extração estática (requests + BeautifulSoup + tinycss2).
   Rápido, leve, suficiente pra sites com CSS server-rendered.
2. Se detectar SPA (React/Vue/Next/etc) ou se a extração estática vier
   pobre demais, cai pra Playwright headless e usa getComputedStyle()
   em elementos representativos.

Output: JSON em stdout no formato intermediário comum a todos os
extratores (ver references/intermediate-format.md).

Uso:
    python extract_from_url.py <url> [--force-playwright] [--output FILE]
"""

import argparse
import json
import re
import sys
from collections import Counter
from urllib.parse import urljoin, urlparse


# ---------------------------------------------------------------------------
# Detecção de SPA
# ---------------------------------------------------------------------------

SPA_MARKERS = [
    # tags/atributos que indicam SPA
    r'id="__next"',           # Next.js
    r'id="root"',              # CRA / Vite default
    r'id="app"',               # Vue
    r'data-reactroot',
    r'ng-version',             # Angular
    r'data-server-rendered',   # Nuxt SSR mas hidrata client
    # bundles típicos
    r'/_next/static/',
    r'/static/js/main\.',
    r'webpack',
]


def looks_like_spa(html: str) -> bool:
    """Heurística simples pra decidir se vale a pena ir de Playwright."""
    if not html:
        return False
    # corpo muito vazio é forte indicador de SPA não-renderizada
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
    if body_match:
        body = body_match.group(1)
        # remove scripts e tags vazias pra ver quanto conteúdo "real" sobrou
        body_clean = re.sub(r'<script.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body_clean = re.sub(r'<[^>]+>', '', body_clean).strip()
        if len(body_clean) < 200:
            return True

    return any(re.search(marker, html, re.IGNORECASE) for marker in SPA_MARKERS)


# ---------------------------------------------------------------------------
# Extração estática
# ---------------------------------------------------------------------------

def fetch_static(url: str, timeout: int = 15) -> tuple[str, list[str]]:
    """
    Baixa o HTML e todas as folhas de estilo linkadas/inline.
    Retorna (html, [css_strings]).
    """
    try:
        import requests
    except ImportError:
        print("ERRO: requests não instalado. pip install requests", file=sys.stderr)
        sys.exit(2)

    headers = {
        # User-Agent realista pra evitar bloqueio em alguns sites
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    html = response.text

    css_blobs: list[str] = []

    # CSS inline em <style>
    for match in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE):
        css_blobs.append(match.group(1))

    # CSS externo em <link rel="stylesheet">
    link_pattern = re.compile(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]*>',
        re.IGNORECASE
    )
    href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

    for link_tag in link_pattern.findall(html):
        href_match = href_pattern.search(link_tag)
        if not href_match:
            continue
        css_url = urljoin(url, href_match.group(1))
        try:
            css_resp = requests.get(css_url, headers=headers, timeout=timeout)
            if css_resp.status_code == 200:
                css_blobs.append(css_resp.text)
        except Exception:
            # CSS externo falhar não derruba a extração — só loga
            print(f"WARN: falhou ao baixar {css_url}", file=sys.stderr)

    return html, css_blobs


# ---------------------------------------------------------------------------
# Parsing CSS
# ---------------------------------------------------------------------------

HEX_COLOR_RE = re.compile(r'#(?:[0-9a-fA-F]{3,4}){1,2}\b')
RGB_COLOR_RE = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)')
HSL_COLOR_RE = re.compile(r'hsla?\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%(?:\s*,\s*([\d.]+))?\s*\)')

FONT_FAMILY_RE = re.compile(r'font-family\s*:\s*([^;}]+)', re.IGNORECASE)
FONT_SIZE_RE = re.compile(r'font-size\s*:\s*([\d.]+)(px|rem|em)', re.IGNORECASE)
FONT_WEIGHT_RE = re.compile(r'font-weight\s*:\s*(\d{3}|bold|normal|lighter|bolder)', re.IGNORECASE)
LINE_HEIGHT_RE = re.compile(r'line-height\s*:\s*([\d.]+)(px|rem|em|%)?', re.IGNORECASE)

PADDING_RE = re.compile(r'padding(?:-(?:top|right|bottom|left))?\s*:\s*([^;}]+)', re.IGNORECASE)
MARGIN_RE = re.compile(r'margin(?:-(?:top|right|bottom|left))?\s*:\s*([^;}]+)', re.IGNORECASE)
GAP_RE = re.compile(r'\bgap\s*:\s*([^;}]+)', re.IGNORECASE)

RADIUS_RE = re.compile(r'border-radius\s*:\s*([^;}]+)', re.IGNORECASE)
SHADOW_RE = re.compile(r'box-shadow\s*:\s*([^;}]+)', re.IGNORECASE)


def normalize_hex(hex_color: str) -> str:
    """Normaliza hex pra formato #rrggbb minúsculo."""
    h = hex_color.lstrip('#').lower()
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    elif len(h) == 4:
        # #rgba -> #rrggbbaa
        h = ''.join(c * 2 for c in h)
    return f"#{h[:6]}"  # ignora canal alpha — design tokens são opacos


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def hsl_to_hex(h: int, s: int, l: int) -> str:
    """Conversão HSL → hex. Inputs: h=0-360, s/l=0-100."""
    s_norm = s / 100
    l_norm = l / 100
    c = (1 - abs(2 * l_norm - 1)) * s_norm
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l_norm - c / 2

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return rgb_to_hex(
        int(round((r + m) * 255)),
        int(round((g + m) * 255)),
        int(round((b + m) * 255))
    )


def parse_css_blobs(css_blobs: list[str]) -> dict:
    """
    Extrai tokens crus de uma lista de strings CSS.
    Retorna dict com listas (com repetições — frequência importa pra ranking depois).
    """
    colors: list[str] = []
    font_families: list[str] = []
    font_sizes: list[str] = []
    font_weights: list[str] = []
    line_heights: list[str] = []
    spacings: list[str] = []
    radii: list[str] = []
    shadows: list[str] = []

    for css in css_blobs:
        # Cores hex
        for match in HEX_COLOR_RE.findall(css):
            colors.append(normalize_hex(match))

        # Cores rgb/rgba
        for r, g, b, a in RGB_COLOR_RE.findall(css):
            colors.append(rgb_to_hex(int(r), int(g), int(b)))

        # Cores hsl/hsla
        for h, s, l, a in HSL_COLOR_RE.findall(css):
            colors.append(hsl_to_hex(int(h), int(s), int(l)))

        # Tipografia
        for match in FONT_FAMILY_RE.findall(css):
            # pega só a primeira família declarada (a preferida)
            first = match.split(',')[0].strip().strip('"\'').strip()
            if first and len(first) < 60:
                font_families.append(first)

        for value, unit in FONT_SIZE_RE.findall(css):
            # normaliza pra px (assumindo root=16)
            v = float(value)
            if unit.lower() == 'rem' or unit.lower() == 'em':
                v = v * 16
            font_sizes.append(f"{int(round(v))}px")

        for match in FONT_WEIGHT_RE.findall(css):
            font_weights.append(match.lower())

        for value, unit in LINE_HEIGHT_RE.findall(css):
            if unit:
                line_heights.append(f"{value}{unit}")
            else:
                line_heights.append(value)

        # Spacing — só pega o primeiro valor (shorthand pode ter 4)
        for prop_re in (PADDING_RE, MARGIN_RE, GAP_RE):
            for match in prop_re.findall(css):
                first_val = match.strip().split()[0] if match.strip() else ''
                if re.match(r'^[\d.]+(px|rem|em)$', first_val):
                    v_match = re.match(r'^([\d.]+)(px|rem|em)$', first_val)
                    if v_match:
                        v = float(v_match.group(1))
                        unit = v_match.group(2)
                        if unit in ('rem', 'em'):
                            v = v * 16
                        spacings.append(f"{int(round(v))}px")

        # Border-radius
        for match in RADIUS_RE.findall(css):
            first_val = match.strip().split()[0]
            if re.match(r'^[\d.]+(px|rem|em|%)$', first_val):
                radii.append(first_val)

        # Box-shadow
        for match in SHADOW_RE.findall(css):
            shadow = match.strip().rstrip(';').strip()
            if shadow and shadow.lower() != 'none':
                shadows.append(shadow)

    return {
        "colors": colors,
        "font_families": font_families,
        "font_sizes": font_sizes,
        "font_weights": font_weights,
        "line_heights": line_heights,
        "spacings": spacings,
        "radii": radii,
        "shadows": shadows,
    }


# ---------------------------------------------------------------------------
# Extração via Playwright (fallback SPA)
# ---------------------------------------------------------------------------

PLAYWRIGHT_SCRIPT = """
() => {
    // Coleta CSS de todos os stylesheets carregados (incluindo os injetados via JS)
    const cssBlobs = [];
    for (const sheet of document.styleSheets) {
        try {
            const rules = sheet.cssRules || sheet.rules;
            if (!rules) continue;
            const parts = [];
            for (const rule of rules) {
                parts.push(rule.cssText);
            }
            cssBlobs.push(parts.join('\\n'));
        } catch (e) {
            // CORS pode bloquear acesso a stylesheets cross-origin — tudo bem, ignoramos
        }
    }

    // Coleta valores computados de elementos representativos
    const samples = [];
    const selectors = [
        'body', 'h1', 'h2', 'h3', 'h4', 'p', 'a',
        'button', 'input', 'textarea',
        'header', 'nav', 'main', 'footer', 'section', 'article',
        '.btn', '.button', '.card', '.container',
    ];
    for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (!el) continue;
        const cs = window.getComputedStyle(el);
        samples.push({
            selector: sel,
            color: cs.color,
            backgroundColor: cs.backgroundColor,
            fontFamily: cs.fontFamily,
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
            lineHeight: cs.lineHeight,
            padding: cs.padding,
            margin: cs.margin,
            borderRadius: cs.borderRadius,
            boxShadow: cs.boxShadow,
            borderColor: cs.borderColor,
        });
    }

    // Extrai logo se houver
    const logoCandidates = [];
    const logoSelectors = [
        'header img[alt*="logo" i]',
        'a[href="/"] img',
        'img[class*="logo" i]',
        '[class*="logo" i] img',
        'svg[class*="logo" i]',
    ];
    for (const sel of logoSelectors) {
        const els = document.querySelectorAll(sel);
        for (const el of els) {
            if (el.tagName === 'IMG' && el.src) {
                logoCandidates.push({type: 'img', src: el.src, alt: el.alt});
            } else if (el.tagName === 'SVG') {
                logoCandidates.push({type: 'svg', html: el.outerHTML});
            }
        }
    }

    return {
        cssBlobs,
        samples,
        logoCandidates: logoCandidates.slice(0, 5),
        title: document.title,
    };
}
"""


def fetch_with_playwright(url: str, timeout: int = 30) -> dict:
    """Renderiza a página com headless browser e extrai CSS + computed styles."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "playwright não instalado. "
            "Rode `pip install --break-system-packages playwright` "
            "e `python -m playwright install chromium` antes de extrair URLs SPA."
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
            # pequeno extra pra animações/lazy carregarem
            page.wait_for_timeout(1500)
            data = page.evaluate(PLAYWRIGHT_SCRIPT)
            return data
        finally:
            browser.close()


def samples_to_css_blob(samples: list[dict]) -> str:
    """Converte samples do Playwright pra string CSS pseudo pra reusar o parser."""
    parts = []
    for s in samples:
        sel = s.get('selector', '*')
        decls = []
        for prop, css_prop in [
            ('color', 'color'),
            ('backgroundColor', 'background-color'),
            ('fontFamily', 'font-family'),
            ('fontSize', 'font-size'),
            ('fontWeight', 'font-weight'),
            ('lineHeight', 'line-height'),
            ('padding', 'padding'),
            ('margin', 'margin'),
            ('borderRadius', 'border-radius'),
            ('boxShadow', 'box-shadow'),
            ('borderColor', 'border-color'),
        ]:
            v = s.get(prop)
            if v and v not in ('none', 'auto', 'normal', 'rgba(0, 0, 0, 0)'):
                decls.append(f"  {css_prop}: {v};")
        if decls:
            parts.append(f"{sel} {{\n" + "\n".join(decls) + "\n}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def extract(url: str, force_playwright: bool = False) -> dict:
    """Pipeline completo. Retorna o formato intermediário."""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    extraction_method = "static"
    samples_data = []
    logo_candidates = []
    page_title = ""

    css_blobs: list[str] = []
    html = ""

    if not force_playwright:
        try:
            html, css_blobs = fetch_static(url)
        except Exception as e:
            print(f"WARN: extração estática falhou: {e}", file=sys.stderr)
            html, css_blobs = "", []

    warnings: list[str] = []
    needs_playwright = force_playwright or looks_like_spa(html) or len(css_blobs) == 0

    if needs_playwright:
        print("INFO: tentando Playwright (SPA detectada ou forçado)", file=sys.stderr)
        try:
            pw_data = fetch_with_playwright(url)
            extraction_method = "playwright"
            css_blobs = pw_data.get('cssBlobs', [])
            samples_data = pw_data.get('samples', [])
            logo_candidates = pw_data.get('logoCandidates', [])
            page_title = pw_data.get('title', '')
            # adiciona os computed styles ao pool de CSS pra parsing
            css_blobs.append(samples_to_css_blob(samples_data))
        except ImportError as e:
            # Playwright não instalado — fallback gracioso pra extração estática.
            msg = (f"{e} Extração estática usada como fallback. "
                   "Pra sites SPA, resultados podem ser parciais.")
            print(f"WARN: {msg}", file=sys.stderr)
            warnings.append(msg)
            extraction_method = "static-fallback"
        except Exception as e:
            msg = f"Playwright falhou ({type(e).__name__}): {e}. Usando extração estática."
            print(f"WARN: {msg}", file=sys.stderr)
            warnings.append(msg)
            extraction_method = "static-fallback"
            if not css_blobs:
                # Nada extraído de jeito nenhum — ainda devolvemos JSON válido,
                # mas com alerta forte. Pipeline downstream pode lidar com fonte vazia.
                warnings.append(
                    "ATENÇÃO: nenhum CSS conseguiu ser extraído deste site. "
                    "Os outros (PDF/imagem) carregam o pipeline; se for a única fonte, "
                    "considere fornecer um print do site como imagem."
                )

    parsed_tokens = parse_css_blobs(css_blobs)

    # Conta frequências — útil pra ranking downstream
    color_counts = Counter(parsed_tokens["colors"])
    spacing_counts = Counter(parsed_tokens["spacings"])
    font_size_counts = Counter(parsed_tokens["font_sizes"])
    radius_counts = Counter(parsed_tokens["radii"])

    return {
        "source": {
            "type": "url",
            "value": url,
            "title": page_title,
            "extraction_method": extraction_method,
        },
        "warnings": warnings,
        "raw": {
            "colors": [{"value": c, "count": n} for c, n in color_counts.most_common()],
            "font_families": list(dict.fromkeys(parsed_tokens["font_families"])),
            "font_sizes": [{"value": s, "count": n} for s, n in font_size_counts.most_common()],
            "font_weights": list(dict.fromkeys(parsed_tokens["font_weights"])),
            "line_heights": list(dict.fromkeys(parsed_tokens["line_heights"])),
            "spacings": [{"value": s, "count": n} for s, n in spacing_counts.most_common()],
            "radii": [{"value": r, "count": n} for r, n in radius_counts.most_common()],
            "shadows": list(dict.fromkeys(parsed_tokens["shadows"])),
        },
        "brand_assets": {
            "logo_candidates": logo_candidates,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Extrai design tokens de URL")
    parser.add_argument("url", help="URL pra extrair")
    parser.add_argument("--force-playwright", action="store_true",
                        help="Força uso do Playwright mesmo se não for SPA")
    parser.add_argument("--output", "-o", help="Arquivo de saída (default: stdout)")
    args = parser.parse_args()

    result = extract(args.url, force_playwright=args.force_playwright)
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"OK: gravado em {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
