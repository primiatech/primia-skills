#!/usr/bin/env python3
"""
fetch_comments.py

Coleta os comentários mais relevantes dos top vídeos.
O YouTube ordena por engajamento quando se passa order=relevance — os primeiros
comentários já capturam ~70-80% do sinal de dor/desejo/objeção.

Modo Sem-API: NÃO COLETA comentários (yt-dlp pode mas é muito instável e lento;
melhor avisar a limitação no relatório do que entregar dado ruim).

Uso:
    python fetch_comments.py --output-dir output/ --max-per-video 150 [--api-key KEY]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path


def fetch_comments_api(video_id, max_count, api_key):
    """Coleta via YouTube Data API."""
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    page_token = None

    while len(comments) < max_count:
        try:
            resp = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(100, max_count - len(comments)),
                order="relevance",
                textFormat="plainText",
                pageToken=page_token,
            ).execute()
        except HttpError as e:
            err_str = str(e)
            if "commentsDisabled" in err_str:
                print(f"    [comentários desabilitados]: {video_id}", file=sys.stderr)
                return []
            if "quotaExceeded" in err_str:
                print(f"    [QUOTA EXCEDIDA]", file=sys.stderr)
                raise
            print(f"    [erro API comentários {video_id}]: {e}", file=sys.stderr)
            return comments

        for item in resp.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comment_id = item["snippet"]["topLevelComment"]["id"]

            comments.append({
                "comment_id": comment_id,
                "author": top_comment.get("authorDisplayName"),
                "text": top_comment.get("textDisplay", ""),
                "like_count": top_comment.get("likeCount", 0),
                "published_at": top_comment.get("publishedAt"),
                "reply_count": item["snippet"].get("totalReplyCount", 0),
                "is_reply": False,
                "parent_id": None,
            })

            # Inclui até 3 replies relevantes (replies frequentemente têm objeções)
            replies = item.get("replies", {}).get("comments", [])[:3]
            for reply in replies:
                rs = reply.get("snippet", {})
                comments.append({
                    "comment_id": reply.get("id"),
                    "author": rs.get("authorDisplayName"),
                    "text": rs.get("textDisplay", ""),
                    "like_count": rs.get("likeCount", 0),
                    "published_at": rs.get("publishedAt"),
                    "reply_count": 0,
                    "is_reply": True,
                    "parent_id": comment_id,
                })

        page_token = resp.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.1)  # rate limiting cortesy

    return comments[:max_count]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-per-video", type=int, default=150)
    parser.add_argument("--api-key", default=os.getenv("YOUTUBE_API_KEY"))
    args = parser.parse_args()

    if not args.api_key:
        print("[AVISO] Sem API key — comentários NÃO serão coletados (Modo Sem-API)", file=sys.stderr)
        print("        Documente essa limitação no relatório.", file=sys.stderr)
        return

    base = Path(args.output_dir)
    channel_dirs = [d for d in base.iterdir() if d.is_dir() and (d / "top_videos.json").exists()]

    total_collected = 0
    quota_hit = False

    for ch_dir in channel_dirs:
        if quota_hit:
            break

        with open(ch_dir / "top_videos.json", "r", encoding="utf-8") as f:
            top_videos = json.load(f)

        comments_dir = ch_dir / "comments"
        comments_dir.mkdir(exist_ok=True)

        print(f"\n[Canal] {ch_dir.name} — {len(top_videos)} top vídeos", file=sys.stderr)

        for v in top_videos:
            vid = v["video_id"]
            out_file = comments_dir / f"{vid}.json"
            if out_file.exists():
                print(f"  {vid}: já existe, pulando", file=sys.stderr)
                continue

            try:
                comments = fetch_comments_api(vid, args.max_per_video, args.api_key)
            except Exception as e:
                if "quotaExceeded" in str(e):
                    quota_hit = True
                    print(f"  [PARANDO — cota da API esgotada]", file=sys.stderr)
                    break
                print(f"  {vid}: erro - {e}", file=sys.stderr)
                continue

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)

            print(f"  {vid}: {len(comments)} comentários", file=sys.stderr)
            total_collected += len(comments)

    print(f"\nTotal coletado: {total_collected} comentários", file=sys.stderr)
    if quota_hit:
        print("AVISO: cota da API esgotada — alguns vídeos ficaram sem comentários", file=sys.stderr)


if __name__ == "__main__":
    main()
