/**
 * load-jszip.js — snippet a colar na aba antes de browser-capture.js
 * Injeta JSZip e html2canvas via CDN (cdnjs), retorna Promise.
 */
(async () => {
  const load = (src) => new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = src;
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });
  if (!window.JSZip) await load('https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js');
  if (!window.html2canvas) await load('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js');
  return { jszip: !!window.JSZip, html2canvas: !!window.html2canvas };
})();
