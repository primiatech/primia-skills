#!/usr/bin/env python3
"""
Analisa valores de spacing/radius e mapeia pra uma escala consistente.

Decisões:
- Spacing: tenta encaixar numa escala de 4px (mais comum em design systems
  modernos) ou 8px. Decide qual tem menor erro acumulado.
- Radius: agrupa em buckets semânticos (none, sm, md, lg, full).

Uso:
    python analyze_spacing.py --input merged.json --output spacing.json
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


def parse_to_px(s: str) -> float:
    s = s.strip().lower()
    m = re.match(r'^([\d.]+)(px|rem|em|%)?$', s)
    if not m:
        return 0
    v = float(m.group(1))
    unit = m.group(2) or "px"
    if unit in ("rem", "em"):
        return v * 16
    if unit == "%":
        return v  # vai virar % no output
    return v


def is_percentage(s: str) -> bool:
    return s.strip().endswith("%")


# ---------------------------------------------------------------------------
# Spacing
# ---------------------------------------------------------------------------

SPACING_NAMES = {
    0: "0",
    2: "0.5",
    4: "1",
    6: "1.5",
    8: "2",
    10: "2.5",
    12: "3",
    14: "3.5",
    16: "4",
    20: "5",
    24: "6",
    28: "7",
    32: "8",
    36: "9",
    40: "10",
    48: "12",
    56: "14",
    64: "16",
    80: "20",
    96: "24",
    128: "32",
}


def snap_to_grid(value: float, step: int) -> int:
    """Arredonda pro múltiplo mais próximo do step."""
    return int(round(value / step) * step)


def detect_spacing_step(values_px: list[float]) -> int:
    """Decide entre escala de 4 ou 8 pelo menor erro."""
    if not values_px:
        return 4

    error_4 = sum(abs(v - snap_to_grid(v, 4)) for v in values_px if v > 0)
    error_8 = sum(abs(v - snap_to_grid(v, 8)) for v in values_px if v > 0)

    # Penaliza um pouco escala de 8 (cobre menos casos)
    return 4 if error_4 <= error_8 * 1.2 else 8


def build_spacing_scale(values_px: list[float], step: int) -> dict:
    """
    Constrói escala de spacing nomeada baseada nos valores observados,
    snapped pro step. Sempre garante os 'staples': 0, 1, 2, 4, 6, 8, 12, 16.
    """
    snapped = sorted(set(snap_to_grid(v, step) for v in values_px if v >= 0))

    # Garante valores fundamentais
    staples = [0, 4, 8, 12, 16, 24, 32, 48, 64]
    for s in staples:
        if s not in snapped:
            snapped.append(s)
    snapped = sorted(set(snapped))

    result = {}
    for v in snapped:
        if v in SPACING_NAMES:
            name = SPACING_NAMES[v]
        else:
            # nomeação por px se não cair num múltiplo conhecido
            name = f"px-{v}"
        result[name] = f"{v}px"

    return result


# ---------------------------------------------------------------------------
# Radius
# ---------------------------------------------------------------------------

def build_radius_scale(values: list[str]) -> dict:
    """
    Bucketiza radii em: none, xs, sm, md, lg, xl, 2xl, full.
    """
    px_values: list[float] = []
    has_full = False  # 50%, 9999px, etc.

    for v in values:
        if is_percentage(v):
            px = parse_to_px(v)
            if px >= 50:
                has_full = True
                continue
            # % menor que 50 cai como ~ "lg" (raro)
            continue
        px = parse_to_px(v)
        if px >= 999:
            has_full = True
            continue
        if px >= 0:
            px_values.append(px)

    px_unique = sorted(set(int(round(v)) for v in px_values))

    # Buckets baseados nos valores observados, com fallback pra defaults
    buckets = {"none": "0px"}

    if not px_unique:
        # Defaults sensatos
        buckets.update({
            "sm": "4px",
            "md": "8px",
            "lg": "12px",
            "xl": "16px",
            "2xl": "24px",
        })
    else:
        # Distribui os valores observados entre os buckets
        names = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl"]
        step = max(1, len(px_unique) // len(names))
        # Pega os mais frequentes/representativos
        for i, name in enumerate(names):
            idx = min(i * step, len(px_unique) - 1)
            buckets[name] = f"{px_unique[idx]}px"

    if has_full or any(v >= 32 for v in px_unique):
        buckets["full"] = "9999px"

    # Remove duplicatas de valor mantendo o nome menor
    seen_values = {}
    cleaned = {}
    for name, val in buckets.items():
        if val in seen_values:
            continue
        seen_values[val] = name
        cleaned[name] = val
    return cleaned


# ---------------------------------------------------------------------------
# Shadows
# ---------------------------------------------------------------------------

def build_shadow_scale(shadows: list[str]) -> dict:
    """
    Atribui nomes a shadows. Heurística: ordena por intensidade (offset y)
    e nomeia sm/md/lg/xl.
    """
    if not shadows:
        return {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
        }

    # Tenta extrair o offset Y como proxy de intensidade
    def shadow_intensity(s: str) -> float:
        m = re.search(r'(-?\d+)\s*px\s+(-?\d+)\s*px', s)
        if m:
            return abs(int(m.group(2)))
        return 0

    sorted_shadows = sorted(set(shadows), key=shadow_intensity)
    names = ["sm", "md", "lg", "xl", "2xl"]
    result = {}
    for i, sh in enumerate(sorted_shadows[:len(names)]):
        result[names[i]] = sh
    return result


def main():
    parser = argparse.ArgumentParser(description="Analisa spacing/radius/shadows")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        merged = json.load(f)

    spacings_raw = merged.get("spacings", [])
    radii_raw = merged.get("radii", [])
    shadows_raw = merged.get("shadows", [])

    spacings_px = [parse_to_px(s) for s in spacings_raw if parse_to_px(s) > 0]
    step = detect_spacing_step(spacings_px)
    spacing_scale = build_spacing_scale(spacings_px, step)

    radius_scale = build_radius_scale(radii_raw)
    shadow_scale = build_shadow_scale(shadows_raw)

    output = {
        "spacing": {
            "step": step,
            "scale": spacing_scale,
        },
        "radius": radius_scale,
        "shadow": shadow_scale,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"OK: spacing em {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
