#!/usr/bin/env python3
"""
Gera styleguide.html — página visual mostrando tudo que está nos tokens
+ componentes base usando esses tokens.

Recebe os tokens já processados e renderiza HTML estático autocontido
(sem dependências externas, exceto Google Fonts pra família primária se for web font).

Uso:
    python generate_styleguide.py --colors colors.json --typography typography.json \
        --spacing spacing.json --contrast contrast.json --output styleguide.html
"""

import argparse
import json
import sys
from pathlib import Path
from html import escape


# Lista de fontes que sabemos estar no Google Fonts (lista curta, expandir conforme necessário)
GOOGLE_FONTS = {
    "Inter", "Roboto", "Open Sans", "Lato", "Montserrat", "Poppins",
    "Source Sans Pro", "Source Sans 3", "Raleway", "Nunito", "Playfair Display",
    "Merriweather", "PT Sans", "Ubuntu", "Oswald", "Roboto Slab", "DM Sans",
    "Work Sans", "Manrope", "Plus Jakarta Sans", "Space Grotesk", "Outfit",
    "Roboto Mono", "Source Code Pro", "Fira Code", "JetBrains Mono", "IBM Plex Sans",
    "IBM Plex Mono", "Noto Sans", "Karla", "Mulish", "Rubik",
}


def google_fonts_link(families: dict) -> str:
    """Monta link do Google Fonts pras famílias que estão lá."""
    names = []
    for role, data in families.items():
        name = data.get("name")
        if name and name in GOOGLE_FONTS:
            names.append(name.replace(" ", "+") + ":wght@300;400;500;600;700")
    if not names:
        return ""
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link href="https://fonts.googleapis.com/css2?family='
        f'{"&family=".join(names)}&display=swap" rel="stylesheet">'
    )


def render_swatches(palette: dict) -> str:
    """Renderiza grid de swatches por escala."""
    sections = []
    for name, value in palette.items():
        if isinstance(value, dict):
            # escala
            swatches = []
            for step, color in value.items():
                # Decide cor do label baseado em luminância simples
                r, g, b = (int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
                luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                text_color = "#000" if luma > 0.55 else "#fff"
                swatches.append(
                    f'<div class="swatch" style="background:{color};color:{text_color}">'
                    f'<span class="swatch-step">{escape(step)}</span>'
                    f'<span class="swatch-hex">{escape(color)}</span></div>'
                )
            sections.append(
                f'<div class="palette-row"><h3>{escape(name)}</h3>'
                f'<div class="swatches">{"".join(swatches)}</div></div>'
            )
        else:
            # cor única
            r, g, b = (int(value.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            text_color = "#000" if luma > 0.55 else "#fff"
            sections.append(
                f'<div class="palette-row"><h3>{escape(name)}</h3>'
                f'<div class="swatches"><div class="swatch" '
                f'style="background:{value};color:{text_color}">'
                f'<span class="swatch-hex">{escape(value)}</span></div></div></div>'
            )
    return "\n".join(sections)


def render_typography(typography: dict) -> str:
    families = typography.get("families", {})
    sizes = typography.get("sizes", {})
    weights = typography.get("weights", [])

    # Famílias
    fam_html = []
    for role, data in families.items():
        if data.get("name"):
            fam_html.append(
                f'<div class="family-card">'
                f'<div class="family-role">{escape(role)}</div>'
                f'<div class="family-name" style="font-family:{data["stack"]}">'
                f'{escape(data["name"] or "")}</div>'
                f'<div class="family-sample" style="font-family:{data["stack"]}">'
                f'The quick brown fox jumps over the lazy dog</div>'
                f'<code>{escape(data["stack"])}</code>'
                f'</div>'
            )

    # Sizes — renderiza em escala visual
    body_stack = families.get("body", {}).get("stack", "system-ui")
    size_html = []
    # Ordena tokens xs,sm,md,lg,xl,2xl... ou step-N
    SIZE_ORDER = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl"]
    sorted_sizes = sorted(
        sizes.items(),
        key=lambda kv: SIZE_ORDER.index(kv[0]) if kv[0] in SIZE_ORDER else 999
    )
    for name, value in sorted_sizes:
        size_html.append(
            f'<div class="size-row">'
            f'<span class="size-label">{escape(name)} / {escape(value)}</span>'
            f'<span class="size-sample" style="font-size:{value};font-family:{body_stack}">'
            f'Aa Bb Cc 123</span>'
            f'</div>'
        )

    # Weights
    weight_html = []
    for w in weights:
        weight_html.append(
            f'<div class="weight-row">'
            f'<span class="weight-label">{escape(w)}</span>'
            f'<span class="weight-sample" '
            f'style="font-weight:{w};font-family:{body_stack}">'
            f'Tipografia em peso {escape(w)}</span>'
            f'</div>'
        )

    return f"""
    <h2>Famílias</h2>
    <div class="families">{"".join(fam_html)}</div>
    <h2>Escala de tamanhos</h2>
    <div class="sizes">{"".join(size_html)}</div>
    <h2>Pesos</h2>
    <div class="weights">{"".join(weight_html)}</div>
    """


def render_spacing(spacing: dict) -> str:
    scale = spacing.get("spacing", {}).get("scale", {})
    rows = []
    for name, value in scale.items():
        # Extrai px pra desenhar a barra
        px = int(value.replace("px", "")) if value.endswith("px") else 0
        rows.append(
            f'<div class="space-row">'
            f'<span class="space-label">{escape(name)} / {escape(value)}</span>'
            f'<div class="space-bar" style="width:{min(px, 256)}px"></div>'
            f'</div>'
        )
    return "<div class=\"spacings\">" + "".join(rows) + "</div>"


def render_radius(spacing: dict) -> str:
    radii = spacing.get("radius", {})
    items = []
    for name, value in radii.items():
        items.append(
            f'<div class="radius-card">'
            f'<div class="radius-shape" style="border-radius:{value}"></div>'
            f'<div class="radius-label">{escape(name)}<br/><code>{escape(value)}</code></div>'
            f'</div>'
        )
    return '<div class="radii">' + "".join(items) + "</div>"


def render_shadows(spacing: dict) -> str:
    shadows = spacing.get("shadow", {})
    items = []
    for name, value in shadows.items():
        items.append(
            f'<div class="shadow-card" style="box-shadow:{value}">'
            f'<div class="shadow-label">{escape(name)}</div>'
            f'</div>'
        )
    return '<div class="shadows">' + "".join(items) + "</div>"


def render_contrast(contrast: dict) -> str:
    summary = contrast.get("summary", {})
    pairs = contrast.get("pairs", [])

    rows = []
    for p in pairs:
        level_class = p["level"].lower().replace("-", "_")
        rows.append(
            f'<tr class="level-{level_class}">'
            f'<td><span class="contrast-sample" '
            f'style="background:{p["bg"]};color:{p["fg"]}">Aa</span></td>'
            f'<td>{escape(p["label"])}</td>'
            f'<td><code>{escape(p["fg"])}</code> / <code>{escape(p["bg"])}</code></td>'
            f'<td>{p["ratio"]}</td>'
            f'<td><strong>{escape(p["level"])}</strong></td>'
            f'</tr>'
        )

    summary_html = (
        f'<p><strong>{summary.get("total_pairs", 0)}</strong> pares testados — '
        f'<span class="ok">{summary.get("passing_aa", 0)} passam AA</span>, '
        f'<span class="warn">{summary.get("aa_large_only", 0)} só AA-large</span>, '
        f'<span class="bad">{summary.get("failing", 0)} falham</span></p>'
    )

    return f"""
    {summary_html}
    <table class="contrast-table">
      <thead><tr><th>Sample</th><th>Pair</th><th>Hex</th><th>Ratio</th><th>WCAG</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    """


def render_components() -> str:
    """Componentes base usando os tokens via CSS variables."""
    return """
    <h2>Botões</h2>
    <div class="component-row">
      <button class="btn btn-primary">Primary</button>
      <button class="btn btn-secondary">Secondary</button>
      <button class="btn btn-ghost">Ghost</button>
      <button class="btn btn-primary btn-sm">Small</button>
      <button class="btn btn-primary btn-lg">Large</button>
      <button class="btn btn-primary" disabled>Disabled</button>
    </div>

    <h2>Inputs</h2>
    <div class="component-row">
      <input class="input" placeholder="Input padrão" />
      <input class="input" placeholder="Disabled" disabled />
      <textarea class="input" rows="3" placeholder="Textarea"></textarea>
    </div>

    <h2>Cards</h2>
    <div class="component-row">
      <div class="card">
        <h3>Título do card</h3>
        <p>Conteúdo de exemplo dentro de um card. Usa background neutral.50,
        radius médio e shadow sm.</p>
        <button class="btn btn-primary btn-sm">Ação</button>
      </div>
      <div class="card card-elevated">
        <h3>Card elevado</h3>
        <p>Variante com shadow maior.</p>
      </div>
    </div>

    <h2>Badges</h2>
    <div class="component-row">
      <span class="badge badge-primary">Primary</span>
      <span class="badge badge-success">Success</span>
      <span class="badge badge-warning">Warning</span>
      <span class="badge badge-danger">Danger</span>
      <span class="badge badge-info">Info</span>
      <span class="badge badge-neutral">Neutral</span>
    </div>

    <h2>Alerts</h2>
    <div class="component-stack">
      <div class="alert alert-info">Informação útil pro usuário.</div>
      <div class="alert alert-success">Operação concluída com sucesso.</div>
      <div class="alert alert-warning">Atenção: revise antes de prosseguir.</div>
      <div class="alert alert-danger">Erro: algo deu errado.</div>
    </div>

    <h2>Headings</h2>
    <div class="headings">
      <h1>Heading 1 — display</h1>
      <h2>Heading 2 — display</h2>
      <h3>Heading 3</h3>
      <h4>Heading 4</h4>
      <h5>Heading 5</h5>
      <h6>Heading 6</h6>
      <p>Body text — Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
      <a href="#">Link de exemplo</a>
    </div>
    """


def styleguide_css() -> str:
    """CSS do próprio styleguide + dos componentes base usando as CSS vars geradas."""
    return """
    /* Layout do styleguide */
    body {
      margin: 0; padding: 0;
      font-family: var(--font-body, system-ui, sans-serif);
      color: var(--color-neutral-900, #111);
      background: var(--color-neutral-50, #fafafa);
      line-height: 1.5;
    }
    .container { max-width: 1200px; margin: 0 auto; padding: 48px 32px; }
    nav.toc {
      position: sticky; top: 0; background: rgba(255,255,255,0.95);
      backdrop-filter: blur(8px); padding: 16px 32px;
      border-bottom: 1px solid var(--color-neutral-200, #eee);
      display: flex; gap: 24px; flex-wrap: wrap; z-index: 10;
    }
    nav.toc a { color: var(--color-neutral-700, #333); text-decoration: none; font-size: 14px; }
    nav.toc a:hover { color: var(--color-primary-600, #06f); }
    h1 { font-family: var(--font-display, inherit); font-size: 48px; margin: 0 0 8px; }
    h2 { font-family: var(--font-display, inherit); font-size: 28px; margin: 48px 0 16px; }
    h3 { font-family: var(--font-display, inherit); font-size: 20px; margin: 24px 0 12px; }
    section { padding: 32px 0; border-bottom: 1px solid var(--color-neutral-200, #eee); }
    code { font-family: var(--font-mono, ui-monospace, monospace); font-size: 13px;
           background: var(--color-neutral-100, #f4f4f4); padding: 2px 6px; border-radius: 4px; }

    /* Swatches */
    .palette-row { margin-bottom: 32px; }
    .swatches { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 8px; }
    .swatch { padding: 16px 12px; border-radius: 8px; min-height: 80px;
              display: flex; flex-direction: column; justify-content: space-between;
              font-size: 12px; font-family: var(--font-mono, monospace); }
    .swatch-step { font-weight: 700; }
    .swatch-hex { opacity: 0.85; }

    /* Typography */
    .families { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
    .family-card { padding: 20px; background: white; border-radius: 12px;
                   box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .family-role { font-size: 12px; text-transform: uppercase; opacity: 0.6;
                   letter-spacing: 0.05em; margin-bottom: 4px; }
    .family-name { font-size: 28px; margin-bottom: 8px; }
    .family-sample { font-size: 16px; margin-bottom: 12px; opacity: 0.85; }
    .size-row { display: flex; align-items: baseline; gap: 24px; padding: 12px 0;
                border-bottom: 1px solid var(--color-neutral-100, #f4f4f4); }
    .size-label { width: 140px; font-family: var(--font-mono, monospace);
                  font-size: 12px; opacity: 0.6; }
    .weight-row { display: flex; align-items: baseline; gap: 24px; padding: 8px 0; }
    .weight-label { width: 80px; font-family: var(--font-mono, monospace);
                    font-size: 12px; opacity: 0.6; }

    /* Spacing */
    .space-row { display: flex; align-items: center; gap: 16px; padding: 6px 0; }
    .space-label { width: 140px; font-family: var(--font-mono, monospace);
                   font-size: 12px; opacity: 0.6; }
    .space-bar { height: 16px; background: var(--color-primary-400, #06f);
                 border-radius: 2px; min-width: 1px; }

    /* Radius */
    .radii { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 16px; }
    .radius-card { text-align: center; }
    .radius-shape { width: 80px; height: 80px; background: var(--color-primary-500, #06f);
                    margin: 0 auto 8px; }
    .radius-label { font-size: 12px; font-family: var(--font-mono, monospace); }

    /* Shadows */
    .shadows { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 24px; padding: 24px; }
    .shadow-card { background: white; padding: 24px; border-radius: 12px; text-align: center; min-height: 80px; }

    /* Contrast */
    .contrast-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .contrast-table th, .contrast-table td { padding: 8px 12px; text-align: left;
                                              border-bottom: 1px solid var(--color-neutral-100, #f4f4f4); }
    .contrast-sample { display: inline-block; padding: 4px 10px; border-radius: 4px;
                       font-weight: 600; }
    .level-aaa td:last-child { color: #15803d; }
    .level-aa td:last-child { color: #166534; }
    .level-aa_large td:last-child { color: #ca8a04; }
    .level-fail td:last-child { color: #b91c1c; }
    .ok { color: #15803d; } .warn { color: #ca8a04; } .bad { color: #b91c1c; }

    /* Componentes */
    .component-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-start; padding: 16px 0; }
    .component-stack { display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }

    .btn {
      font-family: var(--font-body, inherit);
      font-weight: 500;
      font-size: var(--text-md, 16px);
      padding: 10px 18px;
      border-radius: var(--radius-md, 8px);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .btn-primary {
      background: var(--color-primary-500, #06f);
      color: white;
      border-color: var(--color-primary-500, #06f);
    }
    .btn-primary:hover:not(:disabled) { background: var(--color-primary-600, #05c); }
    .btn-secondary {
      background: var(--color-neutral-100, #f4f4f4);
      color: var(--color-neutral-900, #111);
      border-color: var(--color-neutral-200, #e5e5e5);
    }
    .btn-ghost {
      background: transparent;
      color: var(--color-primary-600, #05c);
    }
    .btn-ghost:hover:not(:disabled) { background: var(--color-primary-50, #f0f7ff); }
    .btn-sm { font-size: var(--text-sm, 14px); padding: 6px 12px; }
    .btn-lg { font-size: var(--text-lg, 18px); padding: 14px 24px; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }

    .input {
      font-family: var(--font-body, inherit);
      font-size: var(--text-md, 16px);
      padding: 10px 14px;
      border: 1px solid var(--color-neutral-300, #ddd);
      border-radius: var(--radius-md, 8px);
      background: white;
      width: 220px;
    }
    .input:focus {
      outline: none;
      border-color: var(--color-primary-500, #06f);
      box-shadow: 0 0 0 3px var(--color-primary-100, #dbeafe);
    }
    .input:disabled { background: var(--color-neutral-100, #f4f4f4); opacity: 0.7; }

    .card {
      background: white;
      padding: 24px;
      border-radius: var(--radius-lg, 12px);
      box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
      max-width: 320px;
    }
    .card-elevated { box-shadow: var(--shadow-lg, 0 10px 15px rgba(0,0,0,0.1)); }
    .card h3 { margin-top: 0; }

    .badge {
      display: inline-block;
      padding: 2px 10px;
      border-radius: var(--radius-full, 9999px);
      font-size: var(--text-sm, 14px);
      font-weight: 500;
    }
    .badge-primary  { background: var(--color-primary-100, #dbeafe); color: var(--color-primary-700, #1d4ed8); }
    .badge-success  { background: var(--color-success-100, #dcfce7); color: var(--color-success-700, #15803d); }
    .badge-warning  { background: var(--color-warning-100, #fef3c7); color: var(--color-warning-700, #b45309); }
    .badge-danger   { background: var(--color-danger-100,  #fee2e2); color: var(--color-danger-700,  #b91c1c); }
    .badge-info     { background: var(--color-info-100,    #dbeafe); color: var(--color-info-700,    #1d4ed8); }
    .badge-neutral  { background: var(--color-neutral-200, #e5e5e5); color: var(--color-neutral-800, #1f1f1f); }

    .alert {
      padding: 12px 16px;
      border-radius: var(--radius-md, 8px);
      border-left: 3px solid;
      max-width: 600px;
    }
    .alert-info    { background: var(--color-info-50, #eff6ff);    border-color: var(--color-info-500, #3b82f6); color: var(--color-info-900, #1e3a8a); }
    .alert-success { background: var(--color-success-50, #f0fdf4); border-color: var(--color-success-500, #22c55e); color: var(--color-success-900, #14532d); }
    .alert-warning { background: var(--color-warning-50, #fffbeb); border-color: var(--color-warning-500, #f59e0b); color: var(--color-warning-900, #78350f); }
    .alert-danger  { background: var(--color-danger-50, #fef2f2);  border-color: var(--color-danger-500, #ef4444); color: var(--color-danger-900, #7f1d1d); }

    .headings { background: white; padding: 24px; border-radius: 12px; }
    .headings h1, .headings h2, .headings h3, .headings h4, .headings h5, .headings h6 {
      margin: 12px 0;
    }
    .headings a { color: var(--color-primary-600, #05c); }
    """


def main():
    parser = argparse.ArgumentParser(description="Gera styleguide.html")
    parser.add_argument("--colors", required=True)
    parser.add_argument("--typography", required=True)
    parser.add_argument("--spacing", required=True)
    parser.add_argument("--contrast", required=True)
    parser.add_argument("--tokens-css", required=True,
                        help="Caminho do tokens.css gerado (será incluído inline)")
    parser.add_argument("--project-name", default="Design System")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.colors, encoding="utf-8") as f:
        colors = json.load(f)
    with open(args.typography, encoding="utf-8") as f:
        typography = json.load(f)
    with open(args.spacing, encoding="utf-8") as f:
        spacing = json.load(f)
    with open(args.contrast, encoding="utf-8") as f:
        contrast = json.load(f)
    with open(args.tokens_css, encoding="utf-8") as f:
        tokens_css = f.read()

    gfonts = google_fonts_link(typography.get("families", {}))

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(args.project_name)} — Style Guide</title>
{gfonts}
<style>
{tokens_css}
{styleguide_css()}
</style>
</head>
<body>
<nav class="toc">
  <strong>{escape(args.project_name)}</strong>
  <a href="#colors">Cores</a>
  <a href="#typography">Tipografia</a>
  <a href="#spacing">Spacing</a>
  <a href="#radius">Radius</a>
  <a href="#shadows">Shadows</a>
  <a href="#contrast">Contraste</a>
  <a href="#components">Componentes</a>
</nav>
<main class="container">
  <h1>{escape(args.project_name)}</h1>
  <p>Style guide gerado por <code>primia-design</code>.</p>

  <section id="colors">
    <h2>Cores</h2>
    {render_swatches(colors.get("palette", {}))}
  </section>

  <section id="typography">
    <h2>Tipografia</h2>
    {render_typography(typography)}
  </section>

  <section id="spacing">
    <h2>Spacing</h2>
    <p>Escala baseada em múltiplos de <code>{spacing.get("spacing", {}).get("step", 4)}px</code>.</p>
    {render_spacing(spacing)}
  </section>

  <section id="radius">
    <h2>Border Radius</h2>
    {render_radius(spacing)}
  </section>

  <section id="shadows">
    <h2>Shadows</h2>
    {render_shadows(spacing)}
  </section>

  <section id="contrast">
    <h2>Contraste WCAG</h2>
    {render_contrast(contrast)}
  </section>

  <section id="components">
    <h2>Componentes base</h2>
    <p>Componentes HTML/CSS prontos usando os tokens deste design system. Consulte
    a pasta <code>components/</code> pro código fonte de cada um.</p>
    {render_components()}
  </section>
</main>
</body>
</html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK: styleguide em {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
