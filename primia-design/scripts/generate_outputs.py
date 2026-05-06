#!/usr/bin/env python3
"""
Gera os 6 formatos de output a partir de:
- colors.json   (paleta semântica com escalas)
- typography.json (escala tipográfica + famílias)
- spacing.json    (spacing/radius/shadow)

Formatos gerados:
1. design-tokens.json    — W3C Design Tokens Format
2. tokens.css            — CSS variables :root
3. tokens.scss           — SCSS variables com $-prefix
4. tailwind.config.js    — extend do theme do Tailwind
5. figma-tokens.json     — formato Figma Tokens / Tokens Studio
6. (styleguide.html é gerado por generate_styleguide.py separadamente)

Uso:
    python generate_outputs.py --colors colors.json --typography typography.json \
        --spacing spacing.json --output-dir outputs/tokens/
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. W3C Design Tokens Format
# ---------------------------------------------------------------------------

def to_w3c_tokens(colors: dict, typography: dict, spacing: dict) -> dict:
    """Formato W3C Design Tokens Community Group (DTCG)."""
    tokens = {"$schema": "https://design-tokens.github.io/community-group/format/"}

    # Colors
    color_section = {}
    palette = colors.get("palette", {})
    for name, value in palette.items():
        if isinstance(value, dict):
            # escala 50-900
            color_section[name] = {
                step: {"$value": v, "$type": "color"}
                for step, v in value.items()
            }
        else:
            # cor única (white, black)
            color_section[name] = {"$value": value, "$type": "color"}
    tokens["color"] = color_section

    # Typography
    typo_section: dict = {}
    families = typography.get("families", {})
    typo_section["fontFamily"] = {
        role: {"$value": data["stack"], "$type": "fontFamily"}
        for role, data in families.items()
        if data.get("name")
    }
    typo_section["fontSize"] = {
        name: {"$value": value, "$type": "dimension"}
        for name, value in typography.get("sizes", {}).items()
    }
    typo_section["fontWeight"] = {
        f"weight-{w}": {"$value": w, "$type": "fontWeight"}
        for w in typography.get("weights", [])
    }
    tokens["typography"] = typo_section

    # Spacing
    tokens["spacing"] = {
        name: {"$value": value, "$type": "dimension"}
        for name, value in spacing.get("spacing", {}).get("scale", {}).items()
    }

    # Radius
    tokens["radius"] = {
        name: {"$value": value, "$type": "dimension"}
        for name, value in spacing.get("radius", {}).items()
    }

    # Shadow
    tokens["shadow"] = {
        name: {"$value": value, "$type": "shadow"}
        for name, value in spacing.get("shadow", {}).items()
    }

    return tokens


# ---------------------------------------------------------------------------
# 2. CSS variables
# ---------------------------------------------------------------------------

def to_css(colors: dict, typography: dict, spacing: dict) -> str:
    lines = [
        "/* Design Tokens — gerado por primia-design */",
        ":root {",
    ]

    # Colors
    palette = colors.get("palette", {})
    for name, value in palette.items():
        if isinstance(value, dict):
            for step, v in value.items():
                lines.append(f"  --color-{name}-{step}: {v};")
        else:
            lines.append(f"  --color-{name}: {value};")

    lines.append("")
    # Typography
    for role, data in typography.get("families", {}).items():
        if data.get("name"):
            lines.append(f"  --font-{role}: {data['stack']};")

    for name, value in typography.get("sizes", {}).items():
        lines.append(f"  --text-{name}: {value};")

    for w in typography.get("weights", []):
        lines.append(f"  --weight-{w}: {w};")

    lines.append("")
    # Spacing
    for name, value in spacing.get("spacing", {}).get("scale", {}).items():
        # nomes podem ter ponto (0.5) — viram sublinhado em CSS
        css_name = name.replace(".", "_")
        lines.append(f"  --space-{css_name}: {value};")

    lines.append("")
    # Radius
    for name, value in spacing.get("radius", {}).items():
        lines.append(f"  --radius-{name}: {value};")

    lines.append("")
    # Shadow
    for name, value in spacing.get("shadow", {}).items():
        lines.append(f"  --shadow-{name}: {value};")

    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 3. SCSS variables
# ---------------------------------------------------------------------------

def to_scss(colors: dict, typography: dict, spacing: dict) -> str:
    lines = ["// Design Tokens — gerado por primia-design", ""]

    # Colors
    palette = colors.get("palette", {})
    lines.append("// Colors")
    for name, value in palette.items():
        if isinstance(value, dict):
            for step, v in value.items():
                lines.append(f"$color-{name}-{step}: {v};")
        else:
            lines.append(f"$color-{name}: {value};")

    # Maps SCSS pra cada escala (útil pra @each)
    lines.append("")
    lines.append("// Color maps")
    for name, value in palette.items():
        if isinstance(value, dict):
            entries = ", ".join(f'"{step}": {v}' for step, v in value.items())
            lines.append(f"$color-{name}: ({entries});")

    lines.append("")
    lines.append("// Typography")
    for role, data in typography.get("families", {}).items():
        if data.get("name"):
            lines.append(f"$font-{role}: {data['stack']};")

    for name, value in typography.get("sizes", {}).items():
        lines.append(f"$text-{name}: {value};")

    lines.append("")
    lines.append("// Spacing")
    for name, value in spacing.get("spacing", {}).get("scale", {}).items():
        scss_name = name.replace(".", "_")
        lines.append(f"$space-{scss_name}: {value};")

    lines.append("")
    lines.append("// Radius")
    for name, value in spacing.get("radius", {}).items():
        lines.append(f"$radius-{name}: {value};")

    lines.append("")
    lines.append("// Shadow")
    for name, value in spacing.get("shadow", {}).items():
        lines.append(f'$shadow-{name}: {value};')

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 4. Tailwind config
# ---------------------------------------------------------------------------

def to_tailwind(colors: dict, typography: dict, spacing: dict) -> str:
    """Gera tailwind.config.js como módulo CommonJS."""
    palette = colors.get("palette", {})
    families = typography.get("families", {})
    sizes = typography.get("sizes", {})
    spacing_scale = spacing.get("spacing", {}).get("scale", {})
    radii = spacing.get("radius", {})
    shadows = spacing.get("shadow", {})

    # Constrói a estrutura como dict Python e serializa pra JS
    config = {
        "theme": {
            "extend": {
                "colors": {},
                "fontFamily": {},
                "fontSize": {},
                "spacing": {},
                "borderRadius": {},
                "boxShadow": {},
            }
        }
    }

    for name, value in palette.items():
        if isinstance(value, dict):
            config["theme"]["extend"]["colors"][name] = value
        else:
            config["theme"]["extend"]["colors"][name] = value

    for role, data in families.items():
        if data.get("name"):
            # tailwind quer arrays
            stack_array = [s.strip().strip('"').strip("'")
                           for s in data["stack"].split(",")]
            config["theme"]["extend"]["fontFamily"][role] = stack_array

    config["theme"]["extend"]["fontSize"] = sizes
    config["theme"]["extend"]["spacing"] = spacing_scale
    config["theme"]["extend"]["borderRadius"] = radii
    config["theme"]["extend"]["boxShadow"] = shadows

    body = json.dumps(config, indent=2, ensure_ascii=False)
    return (
        "/** @type {import('tailwindcss').Config} */\n"
        "// Gerado por primia-design\n"
        f"module.exports = {body};\n"
    )


# ---------------------------------------------------------------------------
# 5. Figma Tokens / Tokens Studio
# ---------------------------------------------------------------------------

def to_figma_tokens(colors: dict, typography: dict, spacing: dict) -> dict:
    """
    Formato do Tokens Studio for Figma plugin.
    Estrutura: {set_name: {category: {token: {value, type}}}}
    """
    set_data: dict = {}

    # Colors
    set_data["colors"] = {}
    for name, value in colors.get("palette", {}).items():
        if isinstance(value, dict):
            set_data["colors"][name] = {
                step: {"value": v, "type": "color"}
                for step, v in value.items()
            }
        else:
            set_data["colors"][name] = {"value": value, "type": "color"}

    # Typography
    set_data["typography"] = {}
    set_data["typography"]["fontFamilies"] = {}
    for role, data in typography.get("families", {}).items():
        if data.get("name"):
            set_data["typography"]["fontFamilies"][role] = {
                "value": data["name"], "type": "fontFamilies"
            }
    set_data["typography"]["fontSizes"] = {
        name: {"value": value, "type": "fontSizes"}
        for name, value in typography.get("sizes", {}).items()
    }
    set_data["typography"]["fontWeights"] = {
        f"weight-{w}": {"value": w, "type": "fontWeights"}
        for w in typography.get("weights", [])
    }

    # Spacing
    set_data["spacing"] = {
        name: {"value": value, "type": "spacing"}
        for name, value in spacing.get("spacing", {}).get("scale", {}).items()
    }

    # Radius
    set_data["borderRadius"] = {
        name: {"value": value, "type": "borderRadius"}
        for name, value in spacing.get("radius", {}).items()
    }

    # Shadow
    set_data["boxShadow"] = {
        name: {"value": value, "type": "boxShadow"}
        for name, value in spacing.get("shadow", {}).items()
    }

    return {
        "global": set_data,
        "$themes": [],
        "$metadata": {"tokenSetOrder": ["global"]},
    }


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Gera os 6 formatos de output")
    parser.add_argument("--colors", required=True)
    parser.add_argument("--typography", required=True)
    parser.add_argument("--spacing", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.colors, encoding="utf-8") as f:
        colors = json.load(f)
    with open(args.typography, encoding="utf-8") as f:
        typography = json.load(f)
    with open(args.spacing, encoding="utf-8") as f:
        spacing = json.load(f)

    # 1. W3C
    w3c = to_w3c_tokens(colors, typography, spacing)
    with open(out_dir / "design-tokens.json", "w", encoding="utf-8") as f:
        json.dump(w3c, f, indent=2, ensure_ascii=False)

    # 2. CSS
    with open(out_dir / "tokens.css", "w", encoding="utf-8") as f:
        f.write(to_css(colors, typography, spacing))

    # 3. SCSS
    with open(out_dir / "tokens.scss", "w", encoding="utf-8") as f:
        f.write(to_scss(colors, typography, spacing))

    # 4. Tailwind
    with open(out_dir / "tailwind.config.js", "w", encoding="utf-8") as f:
        f.write(to_tailwind(colors, typography, spacing))

    # 5. Figma Tokens
    with open(out_dir / "figma-tokens.json", "w", encoding="utf-8") as f:
        json.dump(to_figma_tokens(colors, typography, spacing),
                  f, indent=2, ensure_ascii=False)

    print(f"OK: 5 formatos gravados em {out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
