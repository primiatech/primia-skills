#!/usr/bin/env python3
"""
Funde múltiplas extrações intermediárias em um único conjunto de tokens.

Hierarquia: configurável via flag, default é "pdf,url,image".
Em caso de conflito, a fonte mais alta na hierarquia ganha.
TODAS as divergências são registradas em conflicts.md pra revisão.

Cores são comparadas com tolerância (delta-E aproximado via distância RGB)
porque é raro extrações de fontes diferentes baterem hex exato — #FF5733
do PDF e #FF5733 do site são "iguais", mas #FF5733 e #FF5832 também devem
ser considerados o mesmo token (a diferença é imperceptível e provavelmente
ruído de renderização ou compressão).

Uso:
    python merge_sources.py --inputs file1.json file2.json [--hierarchy pdf,url,image]
                            --output-tokens merged.json --output-conflicts conflicts.md
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Comparação de cores com tolerância
# ---------------------------------------------------------------------------

def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def color_distance(c1: str, c2: str) -> float:
    """Distância euclidiana em RGB. Suficiente pra detectar 'mesma cor'."""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


COLOR_SAME_THRESHOLD = 8.0    # praticamente idênticas — mesma cor
COLOR_CONFLICT_THRESHOLD = 25.0  # diferentes mas próximas — conflito real


# ---------------------------------------------------------------------------
# Pipeline de merge
# ---------------------------------------------------------------------------

def order_sources_by_hierarchy(sources: list[dict], hierarchy: list[str]) -> list[dict]:
    """Ordena fontes pela hierarquia. Fontes não declaradas vão pro fim."""
    rank = {t: i for i, t in enumerate(hierarchy)}
    return sorted(sources, key=lambda s: rank.get(s["source"]["type"], len(hierarchy)))


def merge_colors(sources: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Funde cores de várias fontes.
    Retorna (cores_finais, conflitos).
    cores_finais: lista [{value, count, sources}]
    conflitos: lista [{color_a, color_b, source_a, source_b, distance}]
    """
    # Acumulador: cada cor canônica guarda quem a contribuiu e a contagem total
    canonical: list[dict] = []  # {value, total_count, sources: [{type, count}]}
    conflicts: list[dict] = []

    for src in sources:
        src_type = src["source"]["type"]
        for color_entry in src.get("raw", {}).get("colors", []):
            value = color_entry["value"]
            count = color_entry.get("count", 1)

            # Procura uma cor canônica próxima
            matched = None
            closest_distance = float("inf")
            for canon in canonical:
                d = color_distance(value, canon["value"])
                if d < closest_distance:
                    closest_distance = d
                    if d < COLOR_SAME_THRESHOLD:
                        matched = canon
                        break

            if matched:
                matched["total_count"] += count
                matched["sources"].append({"type": src_type, "count": count, "value": value})
            else:
                # Verifica se a mais próxima cai na zona de conflito (próxima mas não igual)
                if (closest_distance < COLOR_CONFLICT_THRESHOLD
                        and closest_distance >= COLOR_SAME_THRESHOLD):
                    closest = min(canonical, key=lambda c: color_distance(value, c["value"]))
                    conflicts.append({
                        "kind": "near_color",
                        "color_a": closest["value"],
                        "color_b": value,
                        "source_a": closest["sources"][0]["type"],
                        "source_b": src_type,
                        "distance": round(closest_distance, 2),
                    })
                canonical.append({
                    "value": value,
                    "total_count": count,
                    "sources": [{"type": src_type, "count": count, "value": value}],
                })

    # Ordena por contagem (cores mais frequentes primeiro)
    canonical.sort(key=lambda c: -c["total_count"])
    return canonical, conflicts


def merge_typography(sources: list[dict]) -> tuple[dict, list[dict]]:
    """
    Funde tipografia. Tipografia raramente conflita (geralmente ou tem ou não tem).
    Quando conflita (ex: PDF diz Inter, site usa Roboto), registra como conflito
    e a primeira fonte na hierarquia ganha.
    """
    families_by_source: dict[str, list[str]] = {}
    sizes_by_source: dict[str, list[str]] = {}
    weights_by_source: dict[str, list[str]] = {}

    for src in sources:
        t = src["source"]["type"]
        raw = src.get("raw", {})
        families_by_source[t] = raw.get("font_families", [])
        sizes_by_source[t] = [
            (s["value"] if isinstance(s, dict) else s)
            for s in raw.get("font_sizes", [])
        ]
        weights_by_source[t] = raw.get("font_weights", [])

    conflicts: list[dict] = []

    # Famílias: a primeira fonte (na hierarquia) que tiver dado vence
    final_families: list[str] = []
    chosen_source = None
    for src in sources:
        t = src["source"]["type"]
        if families_by_source.get(t):
            if not final_families:
                final_families = families_by_source[t]
                chosen_source = t
            else:
                # Conflito potencial: outra fonte declarou algo diferente
                other = families_by_source[t]
                if set(other) - set(final_families):
                    conflicts.append({
                        "kind": "typography_family",
                        "winning_source": chosen_source,
                        "winning_value": final_families,
                        "losing_source": t,
                        "losing_value": other,
                    })

    # Sizes e weights: união (eles são uma escala, não um valor único)
    all_sizes: list[str] = []
    all_weights: list[str] = []
    for src in sources:
        t = src["source"]["type"]
        for s in sizes_by_source.get(t, []):
            if s not in all_sizes:
                all_sizes.append(s)
        for w in weights_by_source.get(t, []):
            if w not in all_weights:
                all_weights.append(w)

    return {
        "families": final_families,
        "sizes": all_sizes,
        "weights": all_weights,
    }, conflicts


def merge_simple_field(sources: list[dict], field: str) -> list:
    """Para campos onde queremos apenas união (spacings, radii, shadows)."""
    merged: list = []
    for src in sources:
        for v in src.get("raw", {}).get(field, []):
            value = v["value"] if isinstance(v, dict) else v
            if value not in merged:
                merged.append(value)
    return merged


def merge_brand_assets(sources: list[dict]) -> dict:
    """Coleta refs de logos/imagens que cada fonte indicou."""
    assets: dict = {
        "logo_candidates": [],
        "source_images": [],
        "embedded_image_counts": {},
    }
    for src in sources:
        t = src["source"]["type"]
        ba = src.get("brand_assets", {})
        for logo in ba.get("logo_candidates", []):
            assets["logo_candidates"].append({**logo, "from": t})
        if "source_image_path" in ba:
            assets["source_images"].append({
                "path": ba["source_image_path"],
                "from": t,
            })
        if "embedded_images_count" in ba:
            assets["embedded_image_counts"][t] = ba["embedded_images_count"]
    return assets


# ---------------------------------------------------------------------------
# Geração do conflicts.md
# ---------------------------------------------------------------------------

def render_conflicts_md(color_conflicts: list[dict],
                         typo_conflicts: list[dict],
                         hierarchy: list[str]) -> str:
    lines = ["# Conflitos entre fontes\n"]
    lines.append(
        f"Hierarquia aplicada: **{' > '.join(hierarchy)}**. "
        "Quando há conflito, a fonte mais à esquerda venceu.\n"
    )

    if not color_conflicts and not typo_conflicts:
        lines.append("\nNenhum conflito detectado entre as fontes fornecidas.\n")
        return "\n".join(lines)

    if color_conflicts:
        lines.append("\n## Cores próximas mas divergentes\n")
        lines.append(
            "Estas cores apareceram em fontes diferentes com pequenas variações. "
            "Pode ser ruído de renderização ou divergência real — vale revisar.\n"
        )
        lines.append("| Fonte A | Cor A | Fonte B | Cor B | Distância |")
        lines.append("|---|---|---|---|---|")
        for c in color_conflicts:
            lines.append(
                f"| {c['source_a']} | `{c['color_a']}` | "
                f"{c['source_b']} | `{c['color_b']}` | {c['distance']} |"
            )

    if typo_conflicts:
        lines.append("\n## Tipografia divergente\n")
        for c in typo_conflicts:
            lines.append(
                f"- **{c['kind']}**: `{c['winning_source']}` declarou "
                f"`{c['winning_value']}`, mas `{c['losing_source']}` declarou "
                f"`{c['losing_value']}`. Hierarquia escolheu `{c['winning_source']}`."
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Funde múltiplas extrações")
    parser.add_argument("--inputs", nargs="+", required=True,
                        help="Arquivos JSON de extração intermediária")
    parser.add_argument("--hierarchy", default="pdf,url,image",
                        help="Hierarquia de prioridade, separada por vírgulas")
    parser.add_argument("--output-tokens", required=True,
                        help="Arquivo de saída com tokens fundidos")
    parser.add_argument("--output-conflicts", required=True,
                        help="Arquivo .md com relatório de conflitos")
    args = parser.parse_args()

    hierarchy = [t.strip() for t in args.hierarchy.split(",")]

    sources = []
    for path in args.inputs:
        with open(path, encoding="utf-8") as f:
            sources.append(json.load(f))

    sources = order_sources_by_hierarchy(sources, hierarchy)

    colors, color_conflicts = merge_colors(sources)
    typography, typo_conflicts = merge_typography(sources)
    spacings = merge_simple_field(sources, "spacings")
    radii = merge_simple_field(sources, "radii")
    shadows = merge_simple_field(sources, "shadows")
    line_heights = merge_simple_field(sources, "line_heights")
    brand_assets = merge_brand_assets(sources)

    merged = {
        "hierarchy": hierarchy,
        "sources": [s["source"] for s in sources],
        "colors": colors,
        "typography": typography,
        "spacings": spacings,
        "radii": radii,
        "shadows": shadows,
        "line_heights": line_heights,
        "brand_assets": brand_assets,
    }

    Path(args.output_tokens).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_tokens, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    conflicts_md = render_conflicts_md(color_conflicts, typo_conflicts, hierarchy)
    with open(args.output_conflicts, "w", encoding="utf-8") as f:
        f.write(conflicts_md)

    print(f"OK: tokens em {args.output_tokens}", file=sys.stderr)
    print(f"OK: conflitos em {args.output_conflicts}", file=sys.stderr)


if __name__ == "__main__":
    main()
