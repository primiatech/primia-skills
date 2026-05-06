#!/usr/bin/env python3
"""
Checa contraste WCAG entre pares relevantes da paleta.

Pares relevantes (não cartesianos — só os que de fato seriam usados em UI):
- Cada step de neutral contra white e black (descobre qual é texto)
- primary.500/600/700 contra white e contra primary.50/100 (texto em botão)
- semantic.500 contra white e contra semantic.50 (avisos coloridos)
- white contra black (sanity check)

Uso:
    python check_contrast.py --colors colors.json --output contrast.json
"""

import argparse
import json
import sys
from pathlib import Path


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def relative_luminance(hex_color: str) -> float:
    """Luminância relativa segundo WCAG 2.1."""
    r, g, b = hex_to_rgb(hex_color)
    def channel(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(c1: str, c2: str) -> float:
    """Razão de contraste WCAG (1.0 a 21.0)."""
    l1 = relative_luminance(c1)
    l2 = relative_luminance(c2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_level(ratio: float, large_text: bool = False) -> str:
    """
    AAA: ≥7:1 (normal) / ≥4.5:1 (large)
    AA:  ≥4.5:1 (normal) / ≥3:1 (large)
    """
    if large_text:
        if ratio >= 4.5:
            return "AAA"
        if ratio >= 3.0:
            return "AA"
        return "FAIL"
    if ratio >= 7.0:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3.0:
        return "AA-large"  # OK só pra texto grande
    return "FAIL"


def check_pair(fg: str, bg: str, label: str) -> dict:
    ratio = contrast_ratio(fg, bg)
    return {
        "label": label,
        "fg": fg,
        "bg": bg,
        "ratio": round(ratio, 2),
        "level": wcag_level(ratio),
        "level_large": wcag_level(ratio, large_text=True),
    }


def main():
    parser = argparse.ArgumentParser(description="Check de contraste WCAG")
    parser.add_argument("--colors", required=True, help="colors.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.colors, encoding="utf-8") as f:
        data = json.load(f)

    palette = data.get("palette", {})
    pairs = []

    white = palette.get("white", "#ffffff")
    black = palette.get("black", "#000000")

    # Sanity check
    pairs.append(check_pair(black, white, "black on white"))

    # Neutrals contra white e black — descobre o ponto de quebra de legibilidade
    if "neutral" in palette and isinstance(palette["neutral"], dict):
        for step, color in palette["neutral"].items():
            pairs.append(check_pair(color, white, f"neutral.{step} on white"))
            pairs.append(check_pair(color, black, f"neutral.{step} on black"))

    # Primary
    if "primary" in palette and isinstance(palette["primary"], dict):
        primary = palette["primary"]
        for step in ["500", "600", "700"]:
            if step in primary:
                pairs.append(check_pair(white, primary[step], f"white on primary.{step}"))
                if "50" in primary:
                    pairs.append(check_pair(primary[step], primary["50"],
                                             f"primary.{step} on primary.50"))
                if "100" in primary:
                    pairs.append(check_pair(primary[step], primary["100"],
                                             f"primary.{step} on primary.100"))

    # Semânticas
    for slot in ["success", "warning", "danger", "info"]:
        if slot in palette and isinstance(palette[slot], dict):
            scale = palette[slot]
            if "500" in scale:
                pairs.append(check_pair(white, scale["500"], f"white on {slot}.500"))
            if "600" in scale:
                pairs.append(check_pair(white, scale["600"], f"white on {slot}.600"))
            if "700" in scale and "50" in scale:
                pairs.append(check_pair(scale["700"], scale["50"],
                                         f"{slot}.700 on {slot}.50"))

    # Estatística geral
    failing = [p for p in pairs if p["level"] == "FAIL"]
    aa_large_only = [p for p in pairs if p["level"] == "AA-large"]
    passing_aa = [p for p in pairs if p["level"] in ("AA", "AAA")]

    output = {
        "summary": {
            "total_pairs": len(pairs),
            "passing_aa": len(passing_aa),
            "passing_aaa": sum(1 for p in pairs if p["level"] == "AAA"),
            "aa_large_only": len(aa_large_only),
            "failing": len(failing),
        },
        "warnings": [
            f"{p['label']}: contraste {p['ratio']} — falha WCAG AA"
            for p in failing
        ],
        "pairs": pairs,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"OK: contraste em {args.output}", file=sys.stderr)
    if failing:
        print(f"AVISO: {len(failing)} pares falhando WCAG AA", file=sys.stderr)


if __name__ == "__main__":
    main()
