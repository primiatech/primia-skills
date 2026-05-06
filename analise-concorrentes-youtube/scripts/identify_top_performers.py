#!/usr/bin/env python3
"""
identify_top_performers.py

Identifica os top N vídeos de cada canal usando score composto:
    score = 0.6 * normalize(view_to_subscriber_ratio)
          + 0.3 * normalize(engagement_rate)
          + 0.1 * normalize(views_per_day)

Regras:
- Vídeos com < 7 dias publicados são EXCLUÍDOS (ainda em rampa)
- Long-form e Shorts são ranqueados separadamente (estratégias diferentes)

Saída: top_videos.json com IDs selecionados + score + categoria (long/short)

Uso:
    python identify_top_performers.py --output-dir output/ --top-n 10
"""
import argparse
import json
import sys
from pathlib import Path


def normalize(values):
    """Min-max normalize. Retorna lista mesma ordem."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def rank_videos(videos, top_n):
    """Aplica score composto e retorna top N."""
    if not videos:
        return []

    ratios = [v["view_to_subscriber_ratio"] for v in videos]
    engagements = [v["engagement_rate"] for v in videos]
    vpds = [v["views_per_day"] for v in videos]

    n_ratios = normalize(ratios)
    n_engagements = normalize(engagements)
    n_vpds = normalize(vpds)

    for i, v in enumerate(videos):
        v["composite_score"] = round(
            0.6 * n_ratios[i] + 0.3 * n_engagements[i] + 0.1 * n_vpds[i], 4
        )

    sorted_videos = sorted(videos, key=lambda x: x["composite_score"], reverse=True)
    return sorted_videos[:top_n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--min-days-published", type=int, default=7)
    args = parser.parse_args()

    base = Path(args.output_dir)
    channel_dirs = [d for d in base.iterdir() if d.is_dir() and (d / "videos.json").exists()]

    for ch_dir in channel_dirs:
        with open(ch_dir / "videos.json", "r", encoding="utf-8") as f:
            videos = json.load(f)

        # Filtra vídeos imaturos
        mature = [v for v in videos if v["days_since_published"] >= args.min_days_published]

        # Separa long vs short
        long_form = [v for v in mature if not v["is_short"]]
        shorts = [v for v in mature if v["is_short"]]

        top_long = rank_videos(long_form, args.top_n)
        # Para shorts, pega só metade do top_n (estratégia secundária)
        top_short = rank_videos(shorts, max(args.top_n // 2, 3))

        for v in top_long:
            v["format_category"] = "long_form"
        for v in top_short:
            v["format_category"] = "short"

        all_top = top_long + top_short

        out_file = ch_dir / "top_videos.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(all_top, f, ensure_ascii=False, indent=2)

        print(
            f"[{ch_dir.name}] Top {len(top_long)} long-form + {len(top_short)} shorts -> {out_file}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
