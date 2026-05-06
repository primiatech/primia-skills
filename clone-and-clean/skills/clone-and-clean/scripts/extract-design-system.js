/**
 * extract-design-system.js
 *
 * Rodar na aba do Chrome (via mcp__Claude_in_Chrome__javascript_tool) com a
 * página original aberta, renderizada e já scrollada até o fim.
 *
 * Saída: objeto JSON com todos os tokens extraídos do DOM real:
 *   - brand        (top cores de CTA/buttons/accent)
 *   - neutral      (escala de cinzas, texto, fundos)
 *   - gradients    (top background-images com linear-gradient)
 *   - typography   (families display/primary + scale h1..bodyLg)
 *   - radii        (valores distintos com contagem)
 *   - spacing      (sections padding/margin)
 *   - shadows      (valores distintos com contagem)
 *   - sections     (lista ordenada com bg + text + role por seção)
 *   - components   (btn-primary, cards, hero, vs-grid, marquee detectados)
 *
 * Esse JSON é consumido pelo Claude pra popular design-system/design-system.json
 * e, a partir dele, gerar o design-system.css do Passo 6.5.
 *
 * Uso (via MCP):
 *   javascript_tool { code: "<conteúdo deste arquivo>" }
 *   → retorna o objeto JSON que o Claude escreve em disco.
 */
(() => {
  // ───── helpers ─────
  const inc = (m, k) => m.set(k, (m.get(k) || 0) + 1);
  const topN = (m, n) =>
    [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n)
      .map(([value, count]) => ({ value, count }));
  const isTransparent = c =>
    !c || c === 'rgba(0, 0, 0, 0)' || c.includes('0, 0, 0, 0') || c === 'transparent';
  const toHex = (c) => {
    const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!m) return c;
    const h = n => (+n).toString(16).padStart(2, '0');
    return '#' + h(m[1]) + h(m[2]) + h(m[3]);
  };

  const all = [...document.querySelectorAll('*')];

  // ───── 1. Cores (color + backgroundColor + borderColor) ─────
  const colorMap = new Map();
  const bgMap = new Map();
  const borderMap = new Map();
  all.forEach(el => {
    const s = getComputedStyle(el);
    if (!isTransparent(s.color)) inc(colorMap, s.color);
    if (!isTransparent(s.backgroundColor)) inc(bgMap, s.backgroundColor);
    if (!isTransparent(s.borderColor)) inc(borderMap, s.borderColor);
  });

  // ───── 2. Fontes ─────
  const bodyFonts = new Map();
  ['p', 'span', 'li', 'body', 'a'].forEach(sel =>
    document.querySelectorAll(sel).forEach(el => {
      const f = getComputedStyle(el).fontFamily.split(',')[0].trim().replace(/['"]/g, '');
      if (f) inc(bodyFonts, f);
    })
  );
  const headingFonts = new Map();
  ['h1', 'h2', 'h3', 'h4'].forEach(sel =>
    document.querySelectorAll(sel).forEach(el => {
      const f = getComputedStyle(el).fontFamily.split(',')[0].trim().replace(/['"]/g, '');
      if (f) inc(headingFonts, f);
    })
  );

  // ───── 3. Escala tipográfica (por tag) ─────
  const sampleStyles = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const s = getComputedStyle(el);
    return {
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      lineHeight: s.lineHeight,
      letterSpacing: s.letterSpacing,
      textTransform: s.textTransform,
    };
  };
  const scale = {
    h1: sampleStyles('h1'),
    h2: sampleStyles('h2'),
    h3: sampleStyles('h3'),
    body: sampleStyles('body'),
    bodyLg: sampleStyles('p'),
    small: sampleStyles('small, .small, .text-small'),
  };

  // ───── 4. Radii ─────
  const radii = new Map();
  all.forEach(el => {
    const r = getComputedStyle(el).borderRadius;
    if (r && r !== '0px') inc(radii, r);
  });

  // ───── 5. Shadows ─────
  const shadows = new Map();
  all.forEach(el => {
    const sh = getComputedStyle(el).boxShadow;
    if (sh && sh !== 'none') inc(shadows, sh);
  });

  // ───── 6. Gradientes ─────
  const gradients = new Map();
  all.forEach(el => {
    const bg = getComputedStyle(el).backgroundImage;
    if (bg && bg.includes('gradient')) inc(gradients, bg);
  });

  // ───── 7. Sections (alternância) ─────
  const sectionSel = 'section, [class*="section"], [class*="e-con-full"]';
  const sections = [];
  document.querySelectorAll(sectionSel).forEach((el, i) => {
    const s = getComputedStyle(el);
    const bg = isTransparent(s.backgroundColor) ? null : s.backgroundColor;
    const bgImg = s.backgroundImage !== 'none' ? s.backgroundImage.slice(0, 80) + '…' : null;
    // Detectar "clima"
    let climate = 'neutral';
    if (bg) {
      const m = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (m) {
        const lum = (0.299 * +m[1] + 0.587 * +m[2] + 0.114 * +m[3]) / 255;
        climate = lum < 0.25 ? 'dark' : lum > 0.85 ? 'light' : 'tonal';
      }
    } else if (bgImg) climate = 'image';
    sections.push({
      index: i,
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      cls: el.className ? el.className.slice(0, 60) : null,
      bg,
      bgImage: bgImg,
      color: s.color,
      climate,
      padding: `${s.paddingTop} ${s.paddingRight} ${s.paddingBottom} ${s.paddingLeft}`,
      minHeight: s.minHeight,
    });
  });

  // ───── 8. Botões / componentes ─────
  const detectBtn = () => {
    const btns = [...document.querySelectorAll('a[class*="button"], button, .elementor-button, [role="button"]')];
    if (!btns.length) return null;
    // escolher o mais frequente visualmente (bg + color mais comum)
    const styles = new Map();
    btns.forEach(b => {
      const s = getComputedStyle(b);
      const key = `${toHex(s.backgroundColor)}|${toHex(s.color)}|${s.borderRadius}`;
      if (!styles.has(key)) styles.set(key, { count: 0, sample: s, el: b });
      styles.get(key).count++;
    });
    const [_, top] = [...styles.entries()].sort((a, b) => b[1].count - a[1].count)[0];
    const s = top.sample;
    return {
      background: s.backgroundColor,
      color: s.color,
      borderRadius: s.borderRadius,
      padding: s.padding,
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      textTransform: s.textTransform,
      letterSpacing: s.letterSpacing,
      count: top.count,
    };
  };

  const detectMarquee = () => {
    const m = document.querySelector('[class*="marquee"], .swiper-wrapper, [class*="ticker"]');
    if (!m) return null;
    const s = getComputedStyle(m);
    return {
      background: s.backgroundColor,
      color: s.color,
      fontFamily: s.fontFamily.split(',')[0].replace(/['"]/g, ''),
      fontSize: s.fontSize,
    };
  };

  const detectHero = () => {
    const h = document.querySelector('section:first-of-type, [class*="hero"]');
    if (!h) return null;
    const s = getComputedStyle(h);
    return {
      minHeight: s.minHeight,
      background: s.backgroundColor,
      backgroundImage: s.backgroundImage !== 'none' ? s.backgroundImage.slice(0, 120) : null,
      color: s.color,
      padding: s.padding,
    };
  };

  // ───── 9. Meta ─────
  const meta = {
    project: document.title || location.hostname,
    source: location.href,
    extractedAt: new Date().toISOString(),
    viewport: { w: window.innerWidth, h: window.innerHeight },
    method: 'getComputedStyle across all elements',
    totalElements: all.length,
  };

  // ───── saída ─────
  return {
    $schema: 'https://anthropic.com/cowork/design-tokens-v1',
    meta,
    brand: {
      topColors: topN(colorMap, 10).map(x => ({ ...x, hex: toHex(x.value) })),
      topBackgrounds: topN(bgMap, 10).map(x => ({ ...x, hex: toHex(x.value) })),
      topBorders: topN(borderMap, 10).map(x => ({ ...x, hex: toHex(x.value) })),
    },
    typography: {
      families: {
        display: topN(headingFonts, 3),
        primary: topN(bodyFonts, 3),
      },
      scale,
    },
    radii: topN(radii, 10),
    shadows: topN(shadows, 5),
    gradients: topN(gradients, 5),
    sections,
    components: {
      btnPrimary: detectBtn(),
      marquee: detectMarquee(),
      hero: detectHero(),
    },
  };
})();
