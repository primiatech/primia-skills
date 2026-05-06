/**
 * extract-palette.js
 * Rodar na aba com a página original aberta. Retorna JSON com:
 *   - top-10 cores mais usadas (mapeadas pra variáveis --brand-*)
 *   - fonte de body + fonte de heading dominantes
 *   - font-size/weight/line-height padrão de body, h1, h2, botão
 *   - border-radius dominante de botões
 *
 * O Claude usa isso pra popular clean-base.html.
 */
(() => {
  const colors = new Map();
  document.querySelectorAll('*').forEach(el => {
    const s = getComputedStyle(el);
    ['color', 'backgroundColor'].forEach(p => {
      const c = s[p];
      if (c && c !== 'rgba(0, 0, 0, 0)' && !c.includes('0, 0, 0, 0')) {
        colors.set(c, (colors.get(c) || 0) + 1);
      }
    });
  });

  const topColors = [...colors.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)
    .map(([c, n]) => ({ color: c, uses: n }));

  // Fontes
  const fontCount = new Map();
  document.querySelectorAll('p, span, li, body').forEach(el => {
    const f = getComputedStyle(el).fontFamily.split(',')[0].trim().replace(/['"]/g, '');
    fontCount.set(f, (fontCount.get(f) || 0) + 1);
  });
  const topBody = [...fontCount.entries()].sort((a, b) => b[1] - a[1])[0];

  const headingFonts = new Map();
  document.querySelectorAll('h1, h2, h3').forEach(el => {
    const f = getComputedStyle(el).fontFamily.split(',')[0].trim().replace(/['"]/g, '');
    headingFonts.set(f, (headingFonts.get(f) || 0) + 1);
  });
  const topHeading = [...headingFonts.entries()].sort((a, b) => b[1] - a[1])[0];

  // Estilo body
  const bs = getComputedStyle(document.body);
  const h1 = document.querySelector('h1');
  const h1s = h1 ? getComputedStyle(h1) : null;
  const h2 = document.querySelector('h2');
  const h2s = h2 ? getComputedStyle(h2) : null;
  const btn = document.querySelector('.elementor-button, button, a[class*="button"]');
  const btns = btn ? getComputedStyle(btn) : null;

  return {
    colors: topColors,
    fontBody: topBody ? topBody[0] : bs.fontFamily,
    fontHeading: topHeading ? topHeading[0] : 'Montserrat',
    sizes: {
      body: { size: bs.fontSize, weight: bs.fontWeight, lineHeight: bs.lineHeight },
      h1: h1s ? { size: h1s.fontSize, weight: h1s.fontWeight } : null,
      h2: h2s ? { size: h2s.fontSize, weight: h2s.fontWeight } : null,
      button: btns ? {
        size: btns.fontSize,
        weight: btns.fontWeight,
        bg: btns.backgroundColor,
        color: btns.color,
        borderRadius: btns.borderRadius,
        padding: btns.padding
      } : null
    }
  };
})();
