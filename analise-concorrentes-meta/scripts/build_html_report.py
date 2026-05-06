#!/usr/bin/env python3
"""
build_html_report.py — Gera dashboard HTML interativo offline.

Entregável 6.6 da skill. Produz uma pasta auto-contida que abre em qualquer
navegador, sem necessidade de servidor ou internet:

    relatorio_html/
    ├── index.html              # Dashboard principal
    ├── concorrente_<slug>.html # Página por concorrente
    ├── assets/
    │   ├── styles.css
    │   ├── chart.umd.min.js    # Chart.js empacotado
    │   ├── app.js
    │   └── data.json           # Dados pra alimentar charts
    └── creativos/              # Cópias dos criativos referenciados

Uso:
    python build_html_report.py \
        --enriched output/concorrente1/enriched_ads.json \
                   output/concorrente2/enriched_ads.json \
        --analysis output/analysis.json \
        --creatives-dir output/criativos \
        --output-dir /mnt/user-data/outputs/relatorio_html

Design tokens (Mentoria Primia):
    Primary:    #0F172A (slate-900)
    Accent:     #F59E0B (amber-500)
    Background: #FAFAF9 (stone-50)
    Surface:    #FFFFFF
    Text:       #1E293B (slate-800)
    Muted:      #64748B (slate-500)
    Success:    #059669 (emerald-600)
    Danger:     #DC2626 (red-600)
"""

import argparse
import json
import re
import shutil
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

# Versão sincronizada — fonte única para rodapés gerados.
# Mantenha igual ao frontmatter do SKILL.md (campo metadata.version).
VERSION = "1.2.0"

CHART_JS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
# Cache do Chart.js no diretório temporário do SO (cross-platform)
CHART_JS_CACHE = Path(tempfile.gettempdir()) / "_skill_chart_cache.js"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def fetch_chartjs() -> str:
    """Baixa Chart.js (com cache em /tmp pra não rebaixar a cada execução)."""
    if CHART_JS_CACHE.exists() and CHART_JS_CACHE.stat().st_size > 100_000:
        return CHART_JS_CACHE.read_text()
    print("[i] Baixando Chart.js (uma vez só, fica em cache)...")
    try:
        with urlopen(CHART_JS_URL, timeout=30) as r:
            content = r.read().decode()
        CHART_JS_CACHE.write_text(content)
        return content
    except Exception as e:
        print(f"[!] Falha ao baixar Chart.js: {e}")
        print("[!] HTML será gerado mas gráficos não funcionarão sem internet.")
        return "/* Chart.js indisponível — rode com internet pra gerar */"


# --------------------------------------------------------------------------- #
# CSS — paleta editorial / minimal-luxury (não genérica)
# --------------------------------------------------------------------------- #

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,700;9..144,900&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary: #0F172A;
  --accent: #F59E0B;
  --accent-soft: #FEF3C7;
  --bg: #FAFAF9;
  --surface: #FFFFFF;
  --text: #1E293B;
  --muted: #64748B;
  --border: #E2E8F0;
  --success: #059669;
  --danger: #DC2626;
  --info: #2563EB;
  --shadow-sm: 0 1px 2px rgba(15,23,42,.04), 0 1px 3px rgba(15,23,42,.06);
  --shadow-md: 0 4px 6px rgba(15,23,42,.05), 0 10px 15px rgba(15,23,42,.08);
  --shadow-lg: 0 20px 25px rgba(15,23,42,.10), 0 10px 10px rgba(15,23,42,.04);
  --radius: 8px;
  --radius-lg: 16px;
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html { scroll-behavior: smooth; }

body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  font-feature-settings: 'cv11', 'ss01';
  -webkit-font-smoothing: antialiased;
}

/* === LAYOUT === */
.container { max-width: 1280px; margin: 0 auto; padding: 0 24px; }
.section { padding: 64px 0; }
.section + .section { border-top: 1px solid var(--border); }

/* === NAV === */
.nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(250, 250, 249, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}
.nav-inner {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; max-width: 1280px; margin: 0 auto;
}
.brand {
  font-family: var(--font-display);
  font-weight: 900; font-size: 1.25rem;
  font-style: italic;
  letter-spacing: -0.02em;
}
.brand .accent { color: var(--accent); }
.nav-links { display: flex; gap: 24px; font-size: 0.875rem; font-weight: 500; }
.nav-links a {
  color: var(--muted); text-decoration: none;
  transition: color 150ms;
}
.nav-links a:hover { color: var(--primary); }

/* === HERO === */
.hero {
  padding: 96px 0 64px;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute;
  top: -100px; right: -100px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, var(--accent-soft) 0%, transparent 70%);
  opacity: 0.6;
  pointer-events: none;
}
.eyebrow {
  font-family: var(--font-mono);
  font-size: 0.75rem; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.15em;
  color: var(--accent);
  margin-bottom: 24px;
}
.hero h1 {
  font-family: var(--font-display);
  font-weight: 900; font-style: italic;
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  line-height: 1.05; letter-spacing: -0.03em;
  color: var(--primary);
  max-width: 900px;
  margin-bottom: 24px;
}
.hero h1 em {
  font-style: normal;
  background: linear-gradient(120deg, var(--accent) 0%, #DC2626 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero p {
  font-size: 1.125rem; color: var(--muted);
  max-width: 640px; margin-bottom: 32px;
}
.meta-bar {
  display: flex; gap: 32px; flex-wrap: wrap;
  font-family: var(--font-mono); font-size: 0.8125rem;
  color: var(--muted);
}
.meta-bar div strong { color: var(--primary); font-weight: 600; }

/* === STATS === */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-top: 48px;
}
.stat {
  background: var(--surface);
  padding: 32px;
}
.stat-label {
  font-family: var(--font-mono); font-size: 0.6875rem;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--muted); margin-bottom: 12px;
}
.stat-value {
  font-family: var(--font-display);
  font-weight: 700; font-size: 2.5rem;
  line-height: 1; letter-spacing: -0.02em;
  color: var(--primary);
}
.stat-value.accent { color: var(--accent); }
.stat-sub {
  margin-top: 8px;
  font-size: 0.8125rem;
  color: var(--muted);
}

/* === SECTION HEADERS === */
.section-header { margin-bottom: 48px; max-width: 720px; }
.section-header .eyebrow { margin-bottom: 12px; }
.section-header h2 {
  font-family: var(--font-display);
  font-weight: 700; font-style: italic;
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  line-height: 1.15; letter-spacing: -0.02em;
  color: var(--primary);
  margin-bottom: 12px;
}
.section-header p {
  font-size: 1.0625rem; color: var(--muted);
}

/* === CARDS === */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 200ms;
}
.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.card-body { padding: 32px; }

/* === GRID 2/3 COL === */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
@media (max-width: 768px) {
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}

/* === COMPETITOR CARDS === */
.competitor-card {
  display: block;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px;
  text-decoration: none;
  color: inherit;
  transition: all 200ms;
  position: relative;
  overflow: hidden;
}
.competitor-card::after {
  content: '→';
  position: absolute;
  top: 32px; right: 32px;
  font-size: 1.5rem;
  color: var(--muted);
  transition: transform 200ms, color 200ms;
}
.competitor-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}
.competitor-card:hover::after {
  transform: translateX(4px);
  color: var(--accent);
}
.competitor-card h3 {
  font-family: var(--font-display);
  font-weight: 700; font-size: 1.5rem;
  margin-bottom: 8px;
}
.competitor-card .stats-row {
  display: flex; gap: 24px; margin-top: 24px;
  font-family: var(--font-mono); font-size: 0.8125rem;
  color: var(--muted);
}
.competitor-card .stats-row strong {
  display: block; font-family: var(--font-display);
  font-size: 1.5rem; color: var(--primary);
  font-weight: 700;
  margin-bottom: 2px;
}

/* === CHARTS === */
.chart-container {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px;
}
.chart-container h3 {
  font-family: var(--font-display);
  font-weight: 700; font-size: 1.25rem;
  margin-bottom: 24px;
  letter-spacing: -0.01em;
}
.chart-wrap { position: relative; height: 320px; }
.chart-wrap.tall { height: 480px; }

/* === TOP CRIATIVOS === */
.creatives-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
.creative {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: all 200ms;
}
.creative:hover { box-shadow: var(--shadow-md); }
.creative-media {
  width: 100%;
  aspect-ratio: 1 / 1;
  background: var(--bg);
  object-fit: cover;
  display: block;
}
.creative-media-placeholder {
  width: 100%; aspect-ratio: 1 / 1;
  background: linear-gradient(135deg, var(--bg) 0%, #F1F5F9 100%);
  display: flex; align-items: center; justify-content: center;
  color: var(--muted);
  font-family: var(--font-mono); font-size: 0.75rem;
}
.creative-body { padding: 16px; }
.creative-meta {
  display: flex; justify-content: space-between;
  font-family: var(--font-mono); font-size: 0.75rem;
  color: var(--muted); margin-bottom: 8px;
}
.creative-meta .days {
  background: var(--accent-soft);
  color: #92400E;
  padding: 2px 8px; border-radius: 4px;
  font-weight: 500;
}
.creative-copy {
  font-size: 0.875rem; line-height: 1.5;
  color: var(--text);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.creative-tag {
  display: inline-block;
  font-family: var(--font-mono); font-size: 0.6875rem;
  text-transform: uppercase; letter-spacing: 0.05em;
  background: var(--bg);
  color: var(--muted);
  padding: 2px 8px; border-radius: 4px;
  margin-top: 8px;
}

/* === RECOMENDAÇÕES === */
.rec-list { display: flex; flex-direction: column; gap: 16px; }
.rec {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 20px; align-items: start;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  padding: 24px;
}
.rec-num {
  font-family: var(--font-display);
  font-weight: 900; font-size: 2rem;
  color: var(--accent);
  line-height: 1;
}
.rec-body h4 {
  font-family: var(--font-display);
  font-weight: 700; font-size: 1.125rem;
  margin-bottom: 8px;
}
.rec-body p {
  color: var(--muted); font-size: 0.9375rem;
}
.rec-body .evidence {
  margin-top: 12px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--muted);
}
.priority {
  font-family: var(--font-mono); font-size: 0.6875rem;
  text-transform: uppercase; letter-spacing: 0.1em;
  padding: 4px 10px; border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
}
.priority.alta { background: #FEE2E2; color: #991B1B; }
.priority.media { background: var(--accent-soft); color: #92400E; }
.priority.baixa { background: #DBEAFE; color: #1E40AF; }

/* === FOOTER === */
.footer {
  margin-top: 96px;
  padding: 48px 0;
  border-top: 1px solid var(--border);
  background: var(--primary);
  color: white;
}
.footer .container {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 16px;
}
.footer p { font-size: 0.875rem; opacity: 0.7; }
.footer .brand { color: white; }
.footer .brand .accent { color: var(--accent); }

/* === COMPETITOR PAGE === */
.back-link {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 0.875rem; color: var(--muted);
  text-decoration: none;
  margin-bottom: 32px;
  font-family: var(--font-mono);
}
.back-link:hover { color: var(--primary); }

.competitor-hero h1 {
  font-family: var(--font-display);
  font-weight: 900; font-style: italic;
  font-size: clamp(2rem, 5vw, 3.5rem);
  line-height: 1.05; letter-spacing: -0.03em;
  color: var(--primary);
  margin-bottom: 16px;
}

/* === ADS TABLE === */
.ads-filters {
  display: flex; gap: 12px; flex-wrap: wrap;
  margin-bottom: 24px;
}
.filter-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: var(--radius);
  font-size: 0.8125rem; font-family: var(--font-mono);
  cursor: pointer;
  transition: all 150ms;
}
.filter-btn:hover { border-color: var(--primary); }
.filter-btn.active {
  background: var(--primary); color: white; border-color: var(--primary);
}

.ads-table {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.875rem;
}
.ads-table thead th {
  text-align: left;
  padding: 16px;
  font-family: var(--font-mono); font-size: 0.6875rem;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--muted);
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  font-weight: 500;
}
.ads-table tbody td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
.ads-table tbody tr:last-child td { border-bottom: none; }
.ads-table tbody tr:hover { background: var(--bg); }
.ads-table .ad-id {
  font-family: var(--font-mono); font-size: 0.75rem;
  color: var(--muted);
}
.ads-table .ad-copy {
  max-width: 360px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.badge {
  display: inline-block;
  font-family: var(--font-mono); font-size: 0.6875rem;
  padding: 2px 8px; border-radius: 4px;
  background: var(--bg); color: var(--muted);
}
.badge.active { background: #D1FAE5; color: #065F46; }
.badge.inactive { background: #FEE2E2; color: #991B1B; }

/* === ANIMATIONS === */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.hero h1, .hero p, .stats-grid {
  animation: fadeUp 600ms ease-out backwards;
}
.hero p { animation-delay: 100ms; }
.stats-grid { animation-delay: 200ms; }

/* === PRINT === */
@media print {
  .nav { display: none; }
  .footer { background: white; color: var(--primary); }
}
"""


# --------------------------------------------------------------------------- #
# JS — toggles e charts
# --------------------------------------------------------------------------- #

APP_JS = r"""
// === Carrega dados e inicializa charts ===
async function loadData() {
  const r = await fetch('assets/data.json');
  return r.json();
}

const PALETTE = {
  primary: '#0F172A',
  accent: '#F59E0B',
  accent2: '#DC2626',
  emerald: '#059669',
  blue: '#2563EB',
  purple: '#7C3AED',
  pink: '#DB2777',
  teal: '#0D9488',
  muted: '#94A3B8',
};
const COLORS = [PALETTE.accent, PALETTE.primary, PALETTE.emerald, PALETTE.blue, PALETTE.accent2, PALETTE.purple, PALETTE.teal, PALETTE.pink];

function setChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.color = '#64748B';
  Chart.defaults.borderColor = '#E2E8F0';
}

// === INDEX ===
async function initIndex() {
  setChartDefaults();
  const data = await loadData();
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js não carregado');
    return;
  }

  // 1. Volume por concorrente
  const volEl = document.getElementById('chart-volume');
  if (volEl && data.volume_per_competitor) {
    new Chart(volEl, {
      type: 'bar',
      data: {
        labels: data.volume_per_competitor.labels,
        datasets: [{
          data: data.volume_per_competitor.values,
          backgroundColor: COLORS,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // 2. Distribuição de formatos
  const fmtEl = document.getElementById('chart-formats');
  if (fmtEl && data.format_distribution) {
    new Chart(fmtEl, {
      type: 'doughnut',
      data: {
        labels: data.format_distribution.labels,
        datasets: [{
          data: data.format_distribution.values,
          backgroundColor: COLORS,
          borderWidth: 2,
          borderColor: '#FFFFFF',
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { position: 'right', labels: { padding: 16, boxWidth: 12 } }
        }
      }
    });
  }

  // 3. Top longevos cross-concorrente
  const topEl = document.getElementById('chart-top-longevos');
  if (topEl && data.top_longevos) {
    new Chart(topEl, {
      type: 'bar',
      data: {
        labels: data.top_longevos.labels,
        datasets: [{
          data: data.top_longevos.values,
          backgroundColor: data.top_longevos.colors || PALETTE.accent,
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: '#F1F5F9' }, title: { display: true, text: 'Dias no ar' } },
          y: { grid: { display: false }, ticks: { font: { size: 11 } } }
        }
      }
    });
  }

  // 4. Heatmap ângulos × concorrentes (usando bar empilhado)
  const angEl = document.getElementById('chart-angles');
  if (angEl && data.angles_matrix) {
    const datasets = data.angles_matrix.angles.map((angle, i) => ({
      label: angle,
      data: data.angles_matrix.competitors.map(c => data.angles_matrix.values[c]?.[angle] || 0),
      backgroundColor: COLORS[i % COLORS.length],
    }));
    new Chart(angEl, {
      type: 'bar',
      data: { labels: data.angles_matrix.competitors, datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { padding: 12, boxWidth: 12, font: { size: 11 } } } },
        scales: {
          x: { stacked: true, grid: { display: false } },
          y: { stacked: true, grid: { color: '#F1F5F9' }, title: { display: true, text: '% do portfólio' } }
        }
      }
    });
  }
}

// === COMPETITOR PAGE ===
async function initCompetitor(slug) {
  setChartDefaults();
  const data = await loadData();
  if (typeof Chart === 'undefined') return;
  const comp = data.competitors[slug];
  if (!comp) return;

  // Cadência
  const cadEl = document.getElementById('chart-cadence');
  if (cadEl && comp.cadence) {
    new Chart(cadEl, {
      type: 'line',
      data: {
        labels: comp.cadence.labels,
        datasets: [{
          label: 'Novos anúncios por semana',
          data: comp.cadence.values,
          borderColor: PALETTE.accent,
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true, tension: 0.3, borderWidth: 2,
          pointBackgroundColor: PALETTE.accent,
          pointRadius: 4,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // Ângulos do concorrente
  const angEl = document.getElementById('chart-angles-comp');
  if (angEl && comp.angles) {
    new Chart(angEl, {
      type: 'bar',
      data: {
        labels: comp.angles.labels,
        datasets: [{
          data: comp.angles.values,
          backgroundColor: PALETTE.primary,
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: '#F1F5F9' }, title: { display: true, text: '% dos ads' } },
          y: { grid: { display: false } }
        }
      }
    });
  }

  // Funil
  const funEl = document.getElementById('chart-funnel');
  if (funEl && comp.funnel) {
    new Chart(funEl, {
      type: 'doughnut',
      data: {
        labels: comp.funnel.labels,
        datasets: [{
          data: comp.funnel.values,
          backgroundColor: [PALETTE.blue, PALETTE.accent, PALETTE.emerald],
          borderWidth: 2, borderColor: '#FFFFFF',
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '65%',
        plugins: { legend: { position: 'bottom', labels: { padding: 12, boxWidth: 12 } } }
      }
    });
  }

  // Filtros da tabela
  setupAdsFilters();
}

function setupAdsFilters() {
  const buttons = document.querySelectorAll('.filter-btn');
  const rows = document.querySelectorAll('.ads-table tbody tr');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      const value = btn.dataset.value;
      // Toggle active
      document.querySelectorAll(`.filter-btn[data-filter="${filter}"]`).forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      // Apply
      const activeFilters = {};
      document.querySelectorAll('.filter-btn.active').forEach(b => {
        activeFilters[b.dataset.filter] = b.dataset.value;
      });
      rows.forEach(row => {
        let show = true;
        for (const [k, v] of Object.entries(activeFilters)) {
          if (v === 'all') continue;
          if ((row.dataset[k] || '').toLowerCase() !== v.toLowerCase()) {
            show = false; break;
          }
        }
        row.style.display = show ? '' : 'none';
      });
    });
  });
}
"""


# --------------------------------------------------------------------------- #
# Helpers de extração de dados pra charts
# --------------------------------------------------------------------------- #

def get_competitor_name(comp_data: dict, slug: str, fallback_ads: list = None) -> str:
    """Tenta pegar o nome a partir de várias fontes."""
    if comp_data.get("nome"):
        return comp_data["nome"]
    if fallback_ads:
        for ad in fallback_ads:
            if ad.get("page_name"):
                return ad["page_name"]
    return slug.replace("-", " ").title()


def build_volume_data(all_competitors: dict) -> dict:
    """Volume de ads por concorrente."""
    return {
        "labels": [c["nome"] for c in all_competitors.values()],
        "values": [len(c["ads"]) for c in all_competitors.values()],
    }


def build_format_distribution(all_competitors: dict) -> dict:
    """Distribuição de formatos (vídeo/imagem/carrossel) globalmente."""
    formats = {}
    for c in all_competitors.values():
        for ad in c["ads"]:
            ct = ad.get("creative_type", "outro") or "outro"
            formats[ct] = formats.get(ct, 0) + 1
    return {
        "labels": list(formats.keys()),
        "values": list(formats.values()),
    }


def build_top_longevos(all_competitors: dict, top_n: int = 10) -> dict:
    """Top N anúncios mais longevos cross-concorrente."""
    all_ads = []
    color_map = {}
    palette = ["#F59E0B", "#0F172A", "#059669", "#2563EB", "#DC2626", "#7C3AED"]
    for i, (slug, c) in enumerate(all_competitors.items()):
        color_map[slug] = palette[i % len(palette)]
        for ad in c["ads"]:
            days = ad.get("days_running")
            if days is None:
                continue
            all_ads.append({
                "id": ad.get("ad_archive_id", "?"),
                "competitor_slug": slug,
                "competitor": c["nome"],
                "days": days,
                "snippet": (ad.get("body_text") or "")[:60],
            })
    all_ads.sort(key=lambda x: x["days"], reverse=True)
    top = all_ads[:top_n]
    return {
        "labels": [f"{a['competitor']} · {a['snippet'][:40]}…" for a in top],
        "values": [a["days"] for a in top],
        "colors": [color_map[a["competitor_slug"]] for a in top],
    }


def build_angles_matrix(analysis: dict, all_competitors: dict) -> dict:
    """Matriz de ângulos × concorrentes em %."""
    by_comp = analysis.get("by_competitor", {})
    angles_set = set()
    for comp_slug, comp_analysis in by_comp.items():
        for angle, _ in (comp_analysis.get("angles") or {}).items():
            angles_set.add(angle)

    angles = sorted(angles_set)
    if not angles:
        return None

    competitors = []
    values = {}
    for slug in all_competitors.keys():
        comp_name = all_competitors[slug]["nome"]
        competitors.append(comp_name)
        comp_angles = (by_comp.get(slug) or {}).get("angles") or {}
        total = sum(comp_angles.values()) or 1
        values[comp_name] = {a: round(comp_angles.get(a, 0) / total * 100, 1) for a in angles}

    return {"angles": angles, "competitors": competitors, "values": values}


def build_competitor_charts(comp_data: dict, ads: list) -> dict:
    """Charts individuais de um concorrente."""
    out = {}

    # Cadência: ads agrupados por semana de início
    from collections import Counter
    week_counts = Counter()
    for ad in ads:
        sd = ad.get("start_date")
        if not sd:
            continue
        try:
            d = datetime.fromisoformat(sd[:10])
            year, week, _ = d.isocalendar()
            key = f"{year}-W{week:02d}"
            week_counts[key] += 1
        except Exception:
            pass

    if week_counts:
        sorted_weeks = sorted(week_counts.items())
        out["cadence"] = {
            "labels": [w[0] for w in sorted_weeks],
            "values": [w[1] for w in sorted_weeks],
        }

    # Ângulos
    angles = comp_data.get("angles") or {}
    if angles:
        total = sum(angles.values()) or 1
        sorted_a = sorted(angles.items(), key=lambda x: -x[1])
        out["angles"] = {
            "labels": [a[0] for a in sorted_a],
            "values": [round(a[1] / total * 100, 1) for a in sorted_a],
        }

    # Funil
    funnel = comp_data.get("funnel") or {}
    if funnel:
        sorted_f = sorted(funnel.items(), key=lambda x: -x[1])
        out["funnel"] = {
            "labels": [f[0] for f in sorted_f],
            "values": list(f[1] for f in sorted_f),
        }

    return out


def build_competitor_data_payload(all_competitors: dict, analysis: dict) -> dict:
    """Monta o data.json final."""
    by_comp = analysis.get("by_competitor", {})

    competitors_payload = {}
    for slug, c in all_competitors.items():
        comp_analysis = by_comp.get(slug, {})
        charts = build_competitor_charts(comp_analysis, c["ads"])
        competitors_payload[slug] = {
            "nome": c["nome"],
            "total_ads": len(c["ads"]),
            "active_ads": sum(1 for a in c["ads"] if a.get("is_active") in (True, "true", "ativo", "Ativo")),
            **charts,
        }

    payload = {
        "generated_at": datetime.now().isoformat(),
        "volume_per_competitor": build_volume_data(all_competitors),
        "format_distribution": build_format_distribution(all_competitors),
        "top_longevos": build_top_longevos(all_competitors),
        "angles_matrix": build_angles_matrix(analysis, all_competitors),
        "competitors": competitors_payload,
    }
    return payload


# --------------------------------------------------------------------------- #
# Templates HTML
# --------------------------------------------------------------------------- #

NAV_HTML = '''
<nav class="nav">
  <div class="nav-inner">
    <a href="index.html" class="brand">Análise <span class="accent">.</span> Mentoria Primia</a>
    <div class="nav-links">
      <a href="index.html#panorama">Panorama</a>
      <a href="index.html#concorrentes">Concorrentes</a>
      <a href="index.html#recomendacoes">Recomendações</a>
    </div>
  </div>
</nav>
'''

FOOTER_HTML = '''
<footer class="footer">
  <div class="container">
    <div class="brand">Análise <span class="accent">.</span> Mentoria Primia</div>
    <p>Gerado em {date} · Skill <code>analise-concorrentes-meta</code> v{version} · Hoberdan Silva</p>
  </div>
</footer>
'''


def render_index(all_competitors: dict, analysis: dict, summary_meta: dict) -> str:
    """Renderiza index.html — o dashboard principal."""
    total_ads = sum(len(c["ads"]) for c in all_competitors.values())
    total_active = sum(
        sum(1 for a in c["ads"] if a.get("is_active") in (True, "true", "ativo", "Ativo"))
        for c in all_competitors.values()
    )
    n_competitors = len(all_competitors)

    # Stat: mediana de dias no ar
    all_days = [a.get("days_running") for c in all_competitors.values() for a in c["ads"] if a.get("days_running") is not None]
    if all_days:
        all_days.sort()
        median_days = all_days[len(all_days) // 2]
    else:
        median_days = "—"

    # Sumário executivo
    exec_summary = analysis.get("executive_summary") or []
    exec_html = "".join(
        f'<div class="card"><div class="card-body"><p>{item}</p></div></div>'
        for item in exec_summary[:5]
    ) if exec_summary else '<p class="muted">Sumário executivo será adicionado por Claude no analysis.json (campo <code>executive_summary</code>).</p>'

    # Cards de concorrentes
    competitor_cards = ""
    by_comp = analysis.get("by_competitor", {})
    for slug, c in all_competitors.items():
        ca = by_comp.get(slug, {})
        active = sum(1 for a in c["ads"] if a.get("is_active") in (True, "true", "ativo", "Ativo"))
        med = "—"
        days_list = [a.get("days_running") for a in c["ads"] if a.get("days_running") is not None]
        if days_list:
            days_list.sort()
            med = days_list[len(days_list) // 2]

        top_angle = "—"
        if ca.get("angles"):
            top_angle = max(ca["angles"].items(), key=lambda x: x[1])[0]

        competitor_cards += f'''
        <a href="concorrente_{slug}.html" class="competitor-card">
          <h3>{c["nome"]}</h3>
          <p style="color: var(--muted); font-size: 0.9375rem;">Ângulo dominante: <strong>{top_angle}</strong></p>
          <div class="stats-row">
            <div><strong>{len(c["ads"])}</strong>Total ads</div>
            <div><strong>{active}</strong>Ativos</div>
            <div><strong>{med}</strong>Dias mediana</div>
          </div>
        </a>'''

    # Recomendações
    recs = analysis.get("recommendations", [])
    recs_html = ""
    for i, r in enumerate(recs[:10], 1):
        prio = (r.get("prioridade") or "média").lower()
        prio_class = "alta" if "alta" in prio else "baixa" if "baixa" in prio else "media"
        evidence = r.get("evidencia") or ""
        recs_html += f'''
        <div class="rec">
          <div class="rec-num">{i:02d}</div>
          <div class="rec-body">
            <h4>{r.get("titulo", "")}</h4>
            <p>{r.get("descricao") or r.get("evidencia") or ""}</p>
            {f'<div class="evidence">Evidência: {evidence}</div>' if evidence and r.get("descricao") else ""}
          </div>
          <div class="priority {prio_class}">{prio}</div>
        </div>'''
    if not recs_html:
        recs_html = '<p class="muted">Recomendações serão preenchidas por Claude no analysis.json.</p>'

    nomes_str = ", ".join(c["nome"] for c in all_competitors.values())

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Análise de Concorrentes — Mentoria Primia</title>
<link rel="stylesheet" href="assets/styles.css">
<script src="assets/chart.umd.min.js" defer></script>
<script src="assets/app.js" defer></script>
</head>
<body>

{NAV_HTML}

<header class="hero">
  <div class="container">
    <div class="eyebrow">Inteligência competitiva · Meta Ad Library</div>
    <h1>Análise de <em>concorrentes</em> publicitários</h1>
    <p>{nomes_str} · {summary_meta.get("country", "BR")} · {summary_meta.get("period", "últimos 90 dias")}</p>
    <div class="meta-bar">
      <div><strong>{n_competitors}</strong> concorrentes</div>
      <div><strong>{total_ads}</strong> anúncios coletados</div>
      <div><strong>{total_active}</strong> ativos hoje</div>
      <div><strong>{median_days}</strong> dias mediana no ar</div>
    </div>
  </div>
</header>

<section class="section" id="resumo">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">01 · Sumário</div>
      <h2>O que foi <em>encontrado</em></h2>
      <p>Os achados mais importantes da análise, em ordem de relevância estratégica.</p>
    </div>
    <div class="grid-3">
      {exec_html}
    </div>
  </div>
</section>

<section class="section" id="panorama">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">02 · Panorama</div>
      <h2>Visão <em>comparativa</em></h2>
      <p>Como cada concorrente se posiciona em volume, formato e ângulos de comunicação.</p>
    </div>
    <div class="grid-2">
      <div class="chart-container">
        <h3>Volume de anúncios por concorrente</h3>
        <div class="chart-wrap"><canvas id="chart-volume"></canvas></div>
      </div>
      <div class="chart-container">
        <h3>Distribuição de formatos</h3>
        <div class="chart-wrap"><canvas id="chart-formats"></canvas></div>
      </div>
    </div>
    <div style="margin-top: 32px;">
      <div class="chart-container">
        <h3>Top 10 anúncios mais longevos (cross-concorrente)</h3>
        <div class="chart-wrap tall"><canvas id="chart-top-longevos"></canvas></div>
      </div>
    </div>
    <div style="margin-top: 32px;">
      <div class="chart-container">
        <h3>Mapa de ângulos por concorrente</h3>
        <div class="chart-wrap"><canvas id="chart-angles"></canvas></div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="concorrentes">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">03 · Detalhamento</div>
      <h2>Por <em>concorrente</em></h2>
      <p>Clique para ver perfil completo, top criativos, cadência e tabela detalhada.</p>
    </div>
    <div class="grid-2">
      {competitor_cards}
    </div>
  </div>
</section>

<section class="section" id="recomendacoes">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">04 · Ação</div>
      <h2>Recomendações <em>estratégicas</em></h2>
      <p>O que fazer com essa inteligência. Priorizado por impacto × evidência.</p>
    </div>
    <div class="rec-list">
      {recs_html}
    </div>
  </div>
</section>

{FOOTER_HTML.format(date=datetime.now().strftime("%d/%m/%Y"), version=VERSION)}

<script>document.addEventListener('DOMContentLoaded', initIndex);</script>
</body>
</html>'''
    return html


def find_creative_for_ad(ad: dict, creatives_dir: Path, competitor_slug: str) -> str | None:
    """Tenta encontrar o caminho relativo do criativo."""
    if not creatives_dir or not creatives_dir.exists():
        return None
    ad_id = ad.get("ad_archive_id")
    if not ad_id:
        return None
    candidates = list(creatives_dir.glob(f"{competitor_slug}/{ad_id}_*"))
    if not candidates:
        return None
    images = [c for c in candidates if c.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
    if images:
        return f"creativos/{competitor_slug}/{images[0].name}"
    return f"creativos/{competitor_slug}/{candidates[0].name}"


def render_competitor(slug: str, comp_data: dict, ads: list, comp_analysis: dict,
                      creatives_dir: Path) -> str:
    """Renderiza concorrente_<slug>.html."""
    nome = comp_data["nome"]

    # Stats
    total = len(ads)
    active = sum(1 for a in ads if a.get("is_active") in (True, "true", "ativo", "Ativo"))
    days_list = sorted([a.get("days_running") for a in ads if a.get("days_running") is not None])
    median = days_list[len(days_list) // 2] if days_list else "—"
    longest = max(days_list) if days_list else "—"

    # Top 6 criativos por dias_running
    top_ads = sorted(
        [a for a in ads if a.get("days_running") is not None],
        key=lambda x: x["days_running"], reverse=True
    )[:6]

    creatives_html = ""
    for ad in top_ads:
        media_path = find_creative_for_ad(ad, creatives_dir, slug)
        media_html = (
            f'<img src="{media_path}" alt="" class="creative-media" loading="lazy">'
            if media_path
            else f'<div class="creative-media-placeholder">SEM PREVIEW</div>'
        )
        copy = (ad.get("body_text") or "")[:200]
        days = ad.get("days_running", "—")
        ad_id = ad.get("ad_archive_id", "?")
        ct = (ad.get("creative_type") or "—").upper()

        creatives_html += f'''
        <div class="creative">
          {media_html}
          <div class="creative-body">
            <div class="creative-meta">
              <span>#{ad_id}</span>
              <span class="days">{days} dias</span>
            </div>
            <div class="creative-copy">{copy}</div>
            <span class="creative-tag">{ct}</span>
          </div>
        </div>'''

    if not creatives_html:
        creatives_html = '<p class="muted">Nenhum anúncio com data de início conhecida.</p>'

    # Tabela de TODOS os ads
    ads_rows = ""
    for ad in sorted(ads, key=lambda x: x.get("days_running") or 0, reverse=True):
        is_active_v = ad.get("is_active") in (True, "true", "ativo", "Ativo")
        ads_rows += f'''
        <tr data-status="{'ativo' if is_active_v else 'inativo'}" data-formato="{(ad.get('creative_type') or '').lower()}">
          <td><span class="ad-id">{ad.get("ad_archive_id", "?")}</span></td>
          <td><span class="badge {'active' if is_active_v else 'inactive'}">{'ATIVO' if is_active_v else 'INATIVO'}</span></td>
          <td>{ad.get("days_running", "—")}</td>
          <td><span class="badge">{(ad.get("creative_type") or "—").upper()}</span></td>
          <td><div class="ad-copy">{(ad.get("body_text") or "")[:200]}</div></td>
        </tr>'''

    # Briefing link (se existir)
    briefing_link = ""
    if comp_analysis.get("briefing"):
        briefing_link = f'''
        <div class="card" style="margin-top: 32px;">
          <div class="card-body">
            <div class="eyebrow">Insumo de produção</div>
            <h3 style="font-family: var(--font-display); font-size: 1.5rem; margin: 8px 0 12px;">Briefing criativo disponível</h3>
            <p style="color: var(--muted);">Veja o briefing pronto pra produção em <code>briefings/{slug}.md</code> — gerado pela mesma análise.</p>
          </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{nome} — Análise Mentoria Primia</title>
<link rel="stylesheet" href="assets/styles.css">
<script src="assets/chart.umd.min.js" defer></script>
<script src="assets/app.js" defer></script>
</head>
<body>

{NAV_HTML}

<section class="section competitor-hero">
  <div class="container">
    <a href="index.html" class="back-link">← voltar ao panorama</a>
    <div class="eyebrow">Concorrente · Detalhamento</div>
    <h1>{nome}</h1>
    <div class="stats-grid" style="margin-top: 32px;">
      <div class="stat">
        <div class="stat-label">Total de anúncios</div>
        <div class="stat-value">{total}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Ativos hoje</div>
        <div class="stat-value accent">{active}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Mediana de dias no ar</div>
        <div class="stat-value">{median}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Mais longevo</div>
        <div class="stat-value">{longest}</div>
        <div class="stat-sub">dias</div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">Top criativos</div>
      <h2>Anúncios <em>campeões</em></h2>
      <p>Os 6 mais longevos. Tempo de veiculação é o maior proxy de performance disponível na biblioteca.</p>
    </div>
    <div class="creatives-grid">
      {creatives_html}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">Padrões</div>
      <h2>Cadência, <em>ângulos</em> e funil</h2>
    </div>
    <div class="chart-container" style="margin-bottom: 32px;">
      <h3>Cadência de lançamento (ads novos por semana)</h3>
      <div class="chart-wrap"><canvas id="chart-cadence"></canvas></div>
    </div>
    <div class="grid-2">
      <div class="chart-container">
        <h3>Ângulos de comunicação</h3>
        <div class="chart-wrap"><canvas id="chart-angles-comp"></canvas></div>
      </div>
      <div class="chart-container">
        <h3>Distribuição de funil</h3>
        <div class="chart-wrap"><canvas id="chart-funnel"></canvas></div>
      </div>
    </div>
    {briefing_link}
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-header">
      <div class="eyebrow">Base completa</div>
      <h2>Todos os <em>anúncios</em></h2>
      <p>Filtre por status e formato. Os dados completos estão na planilha .xlsx.</p>
    </div>
    <div class="ads-filters">
      <button class="filter-btn active" data-filter="status" data-value="all">Todos status</button>
      <button class="filter-btn" data-filter="status" data-value="ativo">Apenas ativos</button>
      <button class="filter-btn" data-filter="status" data-value="inativo">Apenas inativos</button>
    </div>
    <table class="ads-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Status</th>
          <th>Dias</th>
          <th>Formato</th>
          <th>Copy</th>
        </tr>
      </thead>
      <tbody>
        {ads_rows}
      </tbody>
    </table>
  </div>
</section>

{FOOTER_HTML.format(date=datetime.now().strftime("%d/%m/%Y"), version=VERSION)}

<script>document.addEventListener('DOMContentLoaded', () => initCompetitor("{slug}"));</script>
</body>
</html>'''
    return html


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enriched", nargs="+", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--creatives-dir", default=None,
                        help="Diretório fonte dos criativos (será copiado para output)")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--country", default="BR")
    parser.add_argument("--period", default="últimos 90 dias")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Carrega tudo
    all_competitors = {}
    for path in args.enriched:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        meta = data.get("metadata", {})
        slug = slugify(meta.get("advertiser") or meta.get("slug") or Path(path).parent.name)
        ads = data.get("ads", [])
        nome = meta.get("advertiser") or get_competitor_name({}, slug, ads)
        all_competitors[slug] = {"nome": nome, "ads": ads, "meta": meta}

    with open(args.analysis, encoding="utf-8") as f:
        analysis = json.load(f)

    # Escreve assets
    (assets_dir / "styles.css").write_text(CSS, encoding="utf-8")
    (assets_dir / "app.js").write_text(APP_JS, encoding="utf-8")
    (assets_dir / "chart.umd.min.js").write_text(fetch_chartjs(), encoding="utf-8")

    # data.json (alimenta os charts)
    data_payload = build_competitor_data_payload(all_competitors, analysis)
    (assets_dir / "data.json").write_text(
        json.dumps(data_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Copia criativos (se fornecido)
    if args.creatives_dir:
        src = Path(args.creatives_dir)
        if src.exists():
            dst = output_dir / "creativos"
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"[✓] Criativos copiados para {dst}")
        else:
            print(f"[!] Diretório de criativos não existe: {src}")

    # Escreve index.html
    summary_meta = {"country": args.country, "period": args.period}
    (output_dir / "index.html").write_text(
        render_index(all_competitors, analysis, summary_meta), encoding="utf-8"
    )

    # Escreve uma página por concorrente
    by_comp = analysis.get("by_competitor", {})
    creatives_dir_p = Path(args.creatives_dir) if args.creatives_dir else None
    for slug, c in all_competitors.items():
        comp_analysis = by_comp.get(slug, {})
        page_html = render_competitor(slug, c, c["ads"], comp_analysis, creatives_dir_p)
        (output_dir / f"concorrente_{slug}.html").write_text(page_html, encoding="utf-8")
        print(f"[✓] Página de concorrente: concorrente_{slug}.html")

    print(f"\n[✓] Relatório HTML completo em: {output_dir}")
    print(f"    Abra {output_dir / 'index.html'} no navegador.")


if __name__ == "__main__":
    main()
