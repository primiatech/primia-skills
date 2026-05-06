/**
 * browser-capture.js
 *
 * Código pra rodar dentro de uma aba Chrome via a extensão "Claude in Chrome"
 * (mcp__Claude_in_Chrome__javascript_tool). Captura HTML renderizado, imagens,
 * CSS/JS externos, screenshot full-page e empacota num ZIP que é baixado
 * automaticamente.
 *
 * Uso: Claude cola o código inteiro na aba com a página-alvo aberta.
 *
 * Requisitos:
 *   - Biblioteca JSZip carregada (via CDN injetada antes — ver snippet load-jszip.js)
 *   - html2canvas opcional pra screenshot (carregado sob demanda)
 *
 * Saída: um .zip disparado como download com:
 *   - index.html      (HTML com tags wp-json/xmlrpc/etc já limpas)
 *   - assets/css/*    (todos CSS baixados)
 *   - assets/js/*     (JS não-tracker)
 *   - assets/fonts/*  (fontes referenciadas)
 *   - images/*        (todas imagens visíveis + lightbox)
 *   - screenshot.jpg  (full-page)
 *   - manifest.json   (url-original → arquivo-local)
 */

async function captureFullPage({ slug, siteOrigin }) {
  // 1. Rolar a página até o fim pra forçar lazy-load
  window.scrollTo({ top: 0 });
  const scrollStep = window.innerHeight * 0.8;
  const total = document.body.scrollHeight;
  for (let y = 0; y < total; y += scrollStep) {
    window.scrollTo({ top: y });
    await new Promise(r => setTimeout(r, 350));
  }
  window.scrollTo({ top: 0 });
  await new Promise(r => setTimeout(r, 500));

  // 2. Forçar data-src → src pra imagens com lazyload custom
  document.querySelectorAll('img[data-src]').forEach(i => {
    if (i.dataset.src && !i.src.includes(i.dataset.src)) i.src = i.dataset.src;
  });

  const zip = new JSZip();
  const manifest = { capturedAt: new Date().toISOString(), source: location.href, urlMap: {} };

  // 3. Coletar URLs via performance API + DOM scan
  const urls = new Set();
  performance.getEntriesByType('resource').forEach(r => {
    if (r.name && !r.name.startsWith('data:') && r.initiatorType !== 'beacon') urls.add(r.name);
  });

  // Também pegar de dentro de style tags
  document.querySelectorAll('style, link[rel="stylesheet"]').forEach(s => {
    try {
      const text = s.innerText || '';
      const re = /url\((["']?)([^)"']+)\1\)/g;
      let m;
      while ((m = re.exec(text)) !== null) {
        const u = m[2];
        if (u && !u.startsWith('data:')) urls.add(new URL(u, location.href).href);
      }
    } catch (e) { /* cross-origin */ }
  });

  // 4. Baixar cada URL e empacotar no ZIP
  let ok = 0, fail = 0;
  for (const url of urls) {
    try {
      const res = await fetch(url, { credentials: 'omit' });
      if (!res.ok) { fail++; continue; }
      const blob = await res.blob();
      const localPath = categorize(url);
      zip.file(localPath, blob);
      manifest.urlMap[url] = localPath;
      ok++;
    } catch (e) {
      fail++;
    }
  }

  // 5. Screenshot full-page (opcional — requer html2canvas)
  if (window.html2canvas) {
    try {
      const canvas = await html2canvas(document.body, {
        height: document.body.scrollHeight,
        windowHeight: document.body.scrollHeight,
        useCORS: true, allowTaint: true, logging: false, scale: 1
      });
      const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg', 0.82));
      zip.file('screenshot-fullpage.jpg', blob);
    } catch (e) { console.warn('Screenshot falhou:', e); }
  }

  // 6. HTML com paths reescritos pra locais
  let html = document.documentElement.outerHTML;
  for (const [src, local] of Object.entries(manifest.urlMap)) {
    // Escape regex chars
    const esc = src.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    html = html.replace(new RegExp(esc, 'g'), local);
  }
  zip.file('index.html', `<!doctype html>\n${html}`);
  zip.file('manifest.json', JSON.stringify(manifest, null, 2));

  // 7. Baixar o ZIP
  const blob = await zip.generateAsync({ type: 'blob' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${slug || 'capture'}.zip`;
  document.body.appendChild(a); a.click(); a.remove();

  return { ok, fail, totalUrls: urls.size };
}

function categorize(url) {
  const u = new URL(url);
  const fname = u.pathname.split('/').pop() || 'index';
  const ext = (fname.match(/\.[^.]+$/) || [''])[0].toLowerCase();
  if (['.css'].includes(ext)) return `assets/css/${fname}`;
  if (['.js', '.mjs'].includes(ext)) return `assets/js/${fname}`;
  if (['.woff2', '.woff', '.ttf', '.otf', '.eot'].includes(ext)) return `assets/fonts/${fname}`;
  if (['.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.svg', '.ico'].includes(ext)) return `images/${fname}`;
  return `other/${fname}`;
}

// Exportar pra uso via eval/MCP
window.captureFullPage = captureFullPage;
