#!/usr/bin/env python3
"""
Analisa um conjunto de tamanhos de fonte e detecta a escala modular
mais próxima. Atribui nomes semânticos (xs, sm, md, lg, xl, 2xl...).

Escalas modulares comuns em design systems:
- 1.067 (Minor Second)
- 1.125 (Major Second) — Bootstrap
- 1.2   (Minor Third)  — Material Design
- 1.25  (Major Third)  — Tailwind aproximado
- 1.333 (Perfect Fourth)
- 1.414 (Augmented Fourth)
- 1.5   (Perfect Fifth)
- 1.618 (Golden Ratio)

Uso:
    python analyze_typography.py --input merged.json --output typography.json
"""

import argparse
import json
import sys
from pathlib import Path


COMMON_SCALES = [
    ("minor-second", 1.067),
    ("major-second", 1.125),
    ("minor-third", 1.2),
    ("major-third", 1.25),
    ("perfect-fourth", 1.333),
    ("augmented-fourth", 1.414),
    ("perfect-fifth", 1.5),
    ("golden-ratio", 1.618),
]

SIZE_NAMES = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl"]


def parse_size(s: str) -> float:
    """Aceita '16px', '1rem', etc. Retorna em px."""
    s = s.strip().lower()
    if s.endswith("px"):
        return float(s[:-2])
    if s.endswith("rem") or s.endswith("em"):
        return float(s[:-3] if s.endswith("rem") else s[:-2]) * 16
    try:
        return float(s)
    except ValueError:
        return 0


def detect_base_and_scale(sizes_px: list[float]) -> dict:
    """
    Tenta achar a base (tamanho mais próximo de 16px = body) e
    a escala que melhor explica os outros tamanhos.
    """
    if not sizes_px:
        return {"base": 16, "scale_name": "major-third", "scale": 1.25}

    sizes_sorted = sorted(set(sizes_px))

    # Escolhe base como o tamanho mais próximo de 16
    base = min(sizes_sorted, key=lambda s: abs(s - 16))
    if base == 0:
        base = 16

    # Pra cada escala candidata, mede o erro total ao mapear cada tamanho
    # ao "step" mais próximo da escala (base * scale^n)
    best = None
    best_error = float("inf")
    for name, scale in COMMON_SCALES:
        total_error = 0
        for s in sizes_sorted:
            if s <= 0:
                continue
            # Calcula em qual step da escala esse tamanho cairia
            import math
            n = round(math.log(s / base) / math.log(scale)) if base > 0 else 0
            ideal = base * (scale ** n)
            total_error += abs(s - ideal) / s  # erro relativo
        if total_error < best_error:
            best_error = total_error
            best = (name, scale)

    return {
        "base": base,
        "scale_name": best[0] if best else "major-third",
        "scale": best[1] if best else 1.25,
        "fit_error": round(best_error, 3) if best else None,
    }


def assign_size_names(sizes_px: list[float], base: float, scale: float) -> dict:
    """
    Mapeia cada tamanho a um nome (xs, sm, md=base, lg, xl...).
    """
    import math
    sizes_unique = sorted(set(sizes_px))
    if not sizes_unique:
        return {}

    # Para cada tamanho, calcula o step relativo à base
    steps = []
    for s in sizes_unique:
        if s <= 0 or base <= 0:
            continue
        n = round(math.log(s / base) / math.log(scale))
        steps.append((s, n))

    # md é o step 0; abaixo é xs/sm; acima é lg/xl/...
    by_step = {n: s for s, n in steps}
    base_index = SIZE_NAMES.index("md")

    result = {}
    for n, size_val in by_step.items():
        idx = base_index + n
        if 0 <= idx < len(SIZE_NAMES):
            name = SIZE_NAMES[idx]
        else:
            # Fora da nomenclatura padrão — usa step numérico
            name = f"step-{n}" if n != 0 else "md"
        result[name] = f"{int(round(size_val))}px"

    return result


def detect_font_roles(families: list[str]) -> dict:
    """
    Heurística pra atribuir famílias a papéis (display vs body).
    Geralmente a primeira fonte declarada é body, e qualquer fonte com
    "display", "serif" no nome ou que apareça depois é display.
    """
    if not families:
        return {"body": None, "display": None, "mono": None}

    body = families[0]
    display = None
    mono = None

    for f in families[1:]:
        f_lower = f.lower()
        if any(k in f_lower for k in ["mono", "code", "console", "courier"]):
            mono = mono or f
        elif any(k in f_lower for k in ["display", "headline", "serif"]):
            display = display or f
        elif display is None:
            display = f

    return {"body": body, "display": display or body, "mono": mono}


def main():
    parser = argparse.ArgumentParser(description="Analisa escala tipográfica")
    parser.add_argument("--input", required=True, help="merged.json do merge_sources")
    parser.add_argument("--output", required=True, help="typography.json final")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        merged = json.load(f)

    typo = merged.get("typography", {})
    sizes_raw = typo.get("sizes", [])
    sizes_px = [parse_size(s) for s in sizes_raw if parse_size(s) > 0]
    families = typo.get("families", [])
    weights = typo.get("weights", [])

    # Pesos: normaliza pra strings numéricas padrão
    WEIGHT_MAP = {
        "thin": "100", "extralight": "200", "light": "300",
        "normal": "400", "regular": "400", "medium": "500",
        "semibold": "600", "bold": "700", "extrabold": "800",
        "black": "900", "heavy": "900",
    }
    weights_normalized = []
    for w in weights:
        w_str = str(w).lower()
        weights_normalized.append(WEIGHT_MAP.get(w_str, w_str))
    # Remove duplicatas mantendo ordem
    weights_normalized = list(dict.fromkeys(weights_normalized))

    if not sizes_px:
        # Fallback: escala default sensata
        sizes_px = [12, 14, 16, 18, 20, 24, 30, 36, 48, 60]

    scale_info = detect_base_and_scale(sizes_px)
    named_sizes = assign_size_names(sizes_px, scale_info["base"], scale_info["scale"])
    roles = detect_font_roles(families)

    # Fallback stacks web-safe pra cada papel
    def fallback_stack(family: str | None, role: str) -> str:
        if not family:
            family = "system-ui"
        if role == "mono":
            return f'"{family}", ui-monospace, "SF Mono", Menlo, Consolas, monospace'
        if role == "display":
            return f'"{family}", system-ui, -apple-system, "Segoe UI", sans-serif'
        return f'"{family}", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

    output = {
        "scale": {
            "base": f"{int(scale_info['base'])}px",
            "ratio": scale_info["scale"],
            "name": scale_info["scale_name"],
            "fit_error": scale_info.get("fit_error"),
        },
        "sizes": named_sizes,
        "families": {
            "body": {
                "name": roles["body"],
                "stack": fallback_stack(roles["body"], "body"),
            },
            "display": {
                "name": roles["display"],
                "stack": fallback_stack(roles["display"], "display"),
            },
            "mono": {
                "name": roles["mono"],
                "stack": fallback_stack(roles["mono"], "mono"),
            },
        },
        "weights": weights_normalized or ["400", "500", "700"],
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"OK: tipografia em {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
