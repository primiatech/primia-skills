#!/usr/bin/env python3
"""
Classifica cores extraídas em paleta semântica:
- primary: cor mais saturada e frequente
- neutral: tons cinza/quase-cinza, gerados em escala 50-900
- semantic (success/warning/danger/info): inferidos por hue + fallback default

Para cada cor classificada como primary/secondary, gera uma escala 50-900
através de manipulação HSL (clarear/escurecer mantendo hue+chroma).

Uso:
    python analyze_colors.py --input merged.json --output colors.json
"""

import argparse
import colorsys
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Conversões
# ---------------------------------------------------------------------------

def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"


def hex_to_hsl(h: str) -> tuple[float, float, float]:
    r, g, b = hex_to_rgb(h)
    h_val, l, s = colorsys.rgb_to_hls(r, g, b)
    return h_val * 360, s, l  # retorna (hue 0-360, sat 0-1, light 0-1)


def hsl_to_hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return rgb_to_hex(r, g, b)


# ---------------------------------------------------------------------------
# Classificação
# ---------------------------------------------------------------------------

def is_neutral(hex_color: str, sat_threshold: float = 0.15) -> bool:
    """Cores quase sem saturação são neutros (grays)."""
    _, s, _ = hex_to_hsl(hex_color)
    return s < sat_threshold


def hue_to_semantic(h: float) -> str | None:
    """Mapeia hue pra slot semântico mais próximo."""
    # Faixas aproximadas em graus
    if 0 <= h < 20 or 340 <= h <= 360:
        return "danger"     # vermelho
    if 20 <= h < 50:
        return "warning"    # laranja/amarelo
    if 80 <= h < 160:
        return "success"    # verde
    if 180 <= h < 250:
        return "info"       # azul/ciano
    return None  # tons fora dos slots semânticos clássicos


def pick_primary(colors: list[dict]) -> dict | None:
    """
    A cor primária é a mais 'expressiva' — alta saturação combinada com
    contagem alta. Cinza saturado-zero é descartado.
    """
    candidates = []
    for c in colors:
        value = c["value"]
        count = c.get("total_count") or c.get("count", 1)
        h, s, l = hex_to_hsl(value)
        if s < 0.2:
            continue  # neutro, não pode ser primary
        # score: saturação * sqrt(count). Saturação domina, mas frequência desempata.
        import math
        score = s * math.sqrt(count)
        candidates.append((score, value, h, s, l))

    if not candidates:
        return None

    candidates.sort(reverse=True, key=lambda x: x[0])
    _, value, h, s, l = candidates[0]
    return {"value": value, "h": h, "s": s, "l": l}


def generate_color_scale(base_hex: str, name: str = "color") -> dict:
    """
    Gera escala 50-900 a partir de uma cor base.
    Mantém hue, ajusta light. Saturação reduz nos extremos.
    """
    base_h, base_s, base_l = hex_to_hsl(base_hex)

    # Steps target lightness — calibrado pra parecer com Tailwind/Material
    targets = {
        "50":  0.97,
        "100": 0.93,
        "200": 0.86,
        "300": 0.74,
        "400": 0.62,
        "500": 0.50,  # base
        "600": 0.42,
        "700": 0.34,
        "800": 0.26,
        "900": 0.18,
        "950": 0.10,
    }

    # A cor base original será atribuída ao step com lightness mais próximo
    # (não força ela ser exatamente 500)
    closest_step = min(targets.keys(), key=lambda k: abs(targets[k] - base_l))

    scale = {}
    for step, target_l in targets.items():
        if step == closest_step:
            # Preserva a cor original neste step
            scale[step] = base_hex
            continue
        # Reduz saturação levemente em extremos pra parecer natural
        if target_l > 0.85 or target_l < 0.20:
            sat = base_s * 0.8
        else:
            sat = base_s
        scale[step] = hsl_to_hex(base_h, sat, target_l)

    return scale


def generate_neutral_scale(reference_hex: str | None = None) -> dict:
    """
    Gera escala neutra. Se houver referência (ex: cinza extraído da fonte),
    usa o hue dela pra criar 'cool gray' ou 'warm gray'.
    """
    if reference_hex:
        h, s, _ = hex_to_hsl(reference_hex)
        # Mantém um pouco do hue, mas reduz saturação pra ficar quase-cinza
        sat = min(s, 0.06)
    else:
        h, sat = 220, 0.04  # default: cool gray

    targets = {
        "50":  0.98,
        "100": 0.95,
        "200": 0.89,
        "300": 0.78,
        "400": 0.62,
        "500": 0.46,
        "600": 0.36,
        "700": 0.27,
        "800": 0.18,
        "900": 0.10,
        "950": 0.04,
    }
    return {step: hsl_to_hex(h, sat, l) for step, l in targets.items()}


# Cores semânticas default (usadas como fallback quando não conseguimos inferir)
SEMANTIC_DEFAULTS = {
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger":  "#ef4444",
    "info":    "#3b82f6",
}


def main():
    parser = argparse.ArgumentParser(description="Analisa cores e gera paleta semântica")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        merged = json.load(f)

    raw_colors = merged.get("colors", [])

    # 1. Primary
    primary = pick_primary(raw_colors)

    # 2. Neutral reference: cor mais frequente que é "neutra"
    neutral_ref = None
    for c in raw_colors:
        if is_neutral(c["value"]):
            neutral_ref = c["value"]
            break

    # 3. Cores semânticas: pra cada slot, pega a cor extraída cujo hue mais bate
    semantic_assignments: dict[str, str | None] = {
        "success": None, "warning": None, "danger": None, "info": None
    }
    for c in raw_colors:
        if is_neutral(c["value"]):
            continue
        if primary and c["value"] == primary["value"]:
            continue
        h, s, l = hex_to_hsl(c["value"])
        slot = hue_to_semantic(h)
        if slot and not semantic_assignments[slot] and s > 0.3:
            semantic_assignments[slot] = c["value"]

    # 4. Monta output
    palette = {}

    if primary:
        palette["primary"] = generate_color_scale(primary["value"])

    palette["neutral"] = generate_neutral_scale(neutral_ref)

    for slot, value in semantic_assignments.items():
        if value:
            palette[slot] = generate_color_scale(value)
        else:
            palette[slot] = generate_color_scale(SEMANTIC_DEFAULTS[slot])

    # 5. Cores extras: cores extraídas que não viraram nenhum slot mas
    # são saturadas e frequentes — guardamos como 'accent' / 'extra-N'
    used_values = set()
    if primary:
        used_values.add(primary["value"])
    used_values.update(v for v in semantic_assignments.values() if v)

    extras = []
    for c in raw_colors:
        if c["value"] in used_values:
            continue
        if is_neutral(c["value"]):
            continue
        extras.append(c["value"])
        if len(extras) >= 2:
            break

    for i, val in enumerate(extras):
        slot_name = "accent" if i == 0 else f"accent-{i+1}"
        palette[slot_name] = generate_color_scale(val)

    # 6. Cores absolutas
    palette["white"] = "#ffffff"
    palette["black"] = "#000000"

    output = {
        "palette": palette,
        "primary_source": primary["value"] if primary else None,
        "semantic_inferred": {
            slot: (value is not None)
            for slot, value in semantic_assignments.items()
        },
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"OK: cores em {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
