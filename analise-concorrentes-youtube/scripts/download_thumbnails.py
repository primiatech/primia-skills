#!/usr/bin/env python3
"""
download_thumbnails.py

Baixa thumbnails dos top performers em melhor resolução disponível.
Tenta maxresdefault primeiro, depois hqdefault como fallback.

Uso:
    python download_thumbnails.py --output-dir output/
"""
import argparse
import json
import sys
from pathlib import Path

import requests

THUMB_URLS = [
    "https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
    "https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
    "https://i.ytimg.com/vi/{vid}/mqdefault.jpg",
]


def download_thumb(video_id, out_path, original_url=None):
    """Tenta baixar thumb em ordem de qualidade."""
    candidates = []
    if original_url:
        candidates.append(original_url)
    candidates.extend([t.format(vid=video_id) for t in THUMB_URLS])

    for url in candidates:
        try:
            r = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AnaliseYTSkill/1.0)"
            })
            if r.status_code == 200 and len(r.content) > 1000:
                out_path.write_bytes(r.content)
                return True
        except Exception:
            continue
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    base = Path(args.output_dir)
    channel_dirs = [d for d in base.iterdir() if d.is_dir() and (d / "top_videos.json").exists()]

    success = 0
    failed = 0
    for ch_dir in channel_dirs:
        with open(ch_dir / "top_videos.json", "r", encoding="utf-8") as f:
            top_videos = json.load(f)

        thumb_dir = ch_dir / "thumbnails"
        thumb_dir.mkdir(exist_ok=True)

        print(f"\n[Canal] {ch_dir.name} — {len(top_videos)} thumbnails", file=sys.stderr)

        for v in top_videos:
            vid = v["video_id"]
            out_file = thumb_dir / f"{vid}.jpg"
            if out_file.exists():
                success += 1
                continue

            if download_thumb(vid, out_file, v.get("thumbnail_url")):
                print(f"  {vid}: OK", file=sys.stderr)
                success += 1
            else:
                print(f"  {vid}: FALHOU", file=sys.stderr)
                failed += 1

    print(f"\nThumbnails: {success} OK, {failed} falharam", file=sys.stderr)


if __name__ == "__main__":
    main()
