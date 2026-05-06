/**
 * extract-copy.js
 * Rodar na aba com a página original. Retorna estrutura JSON das seções.
 * O Claude usa isso como base pra gerar copy.md.
 */
(() => {
  // Tentar achar root Elementor, senão body
  const root = document.querySelector('[data-elementor-type]') || document.body;
  const sections = [...root.querySelectorAll(':scope > .elementor-section, :scope > section')];
  const scanList = sections.length >= 3 ? sections : [...root.children].filter(el => el.offsetHeight > 200);

  return scanList.map((sec, idx) => ({
    idx,
    height: sec.offsetHeight,
    headings: [...sec.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({
      tag: h.tagName,
      text: h.innerText.trim()
    })),
    paragraphs: [...sec.querySelectorAll('p')]
      .map(p => p.innerText.trim())
      .filter(t => t.length > 5),
    lists: [...sec.querySelectorAll('ul, ol')].map(ul =>
      [...ul.querySelectorAll('li')].map(li => li.innerText.trim()).filter(Boolean)
    ),
    iconBoxes: [...sec.querySelectorAll('.elementor-widget-icon-box')].map(ib => ({
      title: ib.querySelector('.elementor-icon-box-title')?.innerText.trim() || '',
      desc: ib.querySelector('.elementor-icon-box-description')?.innerText.trim() || '',
      iconImg: ib.querySelector('img')?.src?.split('/').pop().split('?')[0] || null
    })),
    toggles: [...sec.querySelectorAll('.elementor-toggle-item')].map(ti => ({
      q: ti.querySelector('.elementor-toggle-title')?.innerText.trim() || '',
      a: ti.querySelector('.elementor-tab-content')?.innerText.trim() || ''
    })),
    buttons: [...sec.querySelectorAll('.elementor-button, a[class*="button"], button')]
      .filter(b => b.innerText.trim())
      .map(b => ({ text: b.innerText.trim(), href: b.href || null })),
    images: [...sec.querySelectorAll('img')]
      .filter(i => i.src && !i.src.startsWith('data:'))
      .map(i => ({
        src: i.src.split('/').pop().split('?')[0],
        alt: i.alt || ''
      }))
  }));
})();
