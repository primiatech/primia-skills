#!/usr/bin/env python3
"""
fetch_channel_data.py

Coleta lista de vídeos de um canal dentro da janela temporal especificada,
junto com estatísticas (views, likes, comentários, duração).

Calcula colunas derivadas: days_since_published, views_per_day,
view_to_subscriber_ratio, engagement_rate.

Uso:
    python fetch_channel_data.py --channel-json channels.json --output-dir output/ \
           --max-videos 50 --window-days 180 [--api-key KEY]
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def iso_duration_to_seconds(iso):
    """Converte PT1H2M3S -> 3723 segundos."""
    if not iso:
        return 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not match:
        return 0
    h, m, s = (int(x) if x else 0 for x in match.groups())
    return h * 3600 + m * 60 + s


def fetch_via_api(channel, max_videos, window_days, api_key):
    """Coleta via YouTube Data API v3."""
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    youtube = build("youtube", "v3", developerKey=api_key)
    channel_id = channel["channel_id"]
    subscriber_count = channel.get("subscriber_count") or 1  # evita div por zero

    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    # Pega o uploads playlist do canal
    try:
        resp = youtube.channels().list(
            part="contentDetails", id=channel_id
        ).execute()
        items = resp.get("items", [])
        if not items:
            return []
        uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except HttpError as e:
        print(f"  [erro API canal]: {e}", file=sys.stderr)
        return []

    # Itera a playlist de uploads (mais recentes primeiro)
    video_ids = []
    page_token = None
    while len(video_ids) < max_videos:
        try:
            resp = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist,
                maxResults=min(50, max_videos - len(video_ids)),
                pageToken=page_token,
            ).execute()
        except HttpError as e:
            print(f"  [erro API playlist]: {e}", file=sys.stderr)
            break

        for item in resp.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            published_at = item["contentDetails"].get("videoPublishedAt")
            if not published_at:
                continue
            pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            if pub_dt < cutoff:
                page_token = None
                break
            video_ids.append(video_id)
        else:
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
            continue
        break

    # Busca estatísticas dos vídeos (em lotes de 50)
    videos = []
    now = datetime.now(timezone.utc)
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        try:
            resp = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch),
            ).execute()
        except HttpError as e:
            print(f"  [erro API videos]: {e}", file=sys.stderr)
            continue

        for v in resp.get("items", []):
            snippet = v.get("snippet", {})
            stats = v.get("statistics", {})
            content = v.get("contentDetails", {})

            published_at = snippet.get("publishedAt", "")
            try:
                pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                days_since = max((now - pub_dt).days, 1)
            except Exception:
                days_since = 1

            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))
            comment_count = int(stats.get("commentCount", 0))
            duration_sec = iso_duration_to_seconds(content.get("duration"))

            views_per_day = round(view_count / days_since, 2)
            view_to_sub = round(view_count / subscriber_count, 4)
            engagement = round((like_count + comment_count) / view_count, 4) if view_count > 0 else 0

            thumbnails = snippet.get("thumbnails", {})
            thumb_url = (
                thumbnails.get("maxres", {}).get("url")
                or thumbnails.get("high", {}).get("url")
                or thumbnails.get("default", {}).get("url")
            )

            videos.append({
                "video_id": v["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "published_at": published_at,
                "days_since_published": days_since,
                "duration_seconds": duration_sec,
                "is_short": duration_sec < 60,
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count,
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId"),
                "thumbnail_url": thumb_url,
                "channel_id": channel_id,
                "channel_title": channel.get("title"),
                "views_per_day": views_per_day,
                "view_to_subscriber_ratio": view_to_sub,
                "engagement_rate": engagement,
            })

    return videos


def fetch_via_ytdlp(channel, max_videos, window_days):
    """Fallback sem API key — usa yt-dlp."""
    try:
        import yt_dlp
    except ImportError:
        print("  [erro]: yt-dlp não instalado", file=sys.stderr)
        return []

    channel_id = channel["channel_id"]
    subscriber_count = channel.get("subscriber_count") or 1
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    now = datetime.now(timezone.utc)

    url = f"https://www.youtube.com/channel/{channel_id}/videos"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "playlistend": max_videos,
    }

    videos_basic = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        videos_basic = info.get("entries", []) or []
    except Exception as e:
        print(f"  [erro yt-dlp listing]: {e}", file=sys.stderr)
        return []

    # Hidrata cada vídeo (tem que ser um a um, mais lento)
    videos = []
    ydl_opts_full = {"quiet": True, "no_warnings": True, "skip_download": True}

    for entry in videos_basic[:max_videos]:
        if not entry:
            continue
        video_id = entry.get("id")
        if not video_id:
            continue

        try:
            with yt_dlp.YoutubeDL(ydl_opts_full) as ydl:
                v = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        except Exception:
            continue

        upload_date = v.get("upload_date")  # YYYYMMDD
        if not upload_date:
            continue
        try:
            pub_dt = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if pub_dt < cutoff:
            continue
        days_since = max((now - pub_dt).days, 1)

        view_count = v.get("view_count") or 0
        like_count = v.get("like_count") or 0
        comment_count = v.get("comment_count") or 0
        duration_sec = v.get("duration") or 0

        views_per_day = round(view_count / days_since, 2)
        view_to_sub = round(view_count / subscriber_count, 4)
        engagement = round((like_count + comment_count) / view_count, 4) if view_count > 0 else 0

        videos.append({
            "video_id": video_id,
            "title": v.get("title", ""),
            "description": v.get("description", "") or "",
            "published_at": pub_dt.isoformat(),
            "days_since_published": days_since,
            "duration_seconds": duration_sec,
            "is_short": duration_sec < 60,
            "view_count": view_count,
            "like_count": like_count,
            "comment_count": comment_count,
            "tags": v.get("tags") or [],
            "category_id": None,
            "thumbnail_url": v.get("thumbnail"),
            "channel_id": channel_id,
            "channel_title": channel.get("title"),
            "views_per_day": views_per_day,
            "view_to_subscriber_ratio": view_to_sub,
            "engagement_rate": engagement,
        })

    return videos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-videos", type=int, default=50)
    parser.add_argument("--window-days", type=int, default=180)
    parser.add_argument("--api-key", default=os.getenv("YOUTUBE_API_KEY"))
    args = parser.parse_args()

    with open(args.channels_json, "r", encoding="utf-8") as f:
        channels = json.load(f)

    use_api = bool(args.api_key)

    for channel in channels:
        slug = channel["slug"]
        out_dir = Path(args.output_dir) / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[Canal] {channel['title']} ({slug})", file=sys.stderr)

        if use_api:
            videos = fetch_via_api(channel, args.max_videos, args.window_days, args.api_key)
        else:
            videos = fetch_via_ytdlp(channel, args.max_videos, args.window_days)

        out_file = out_dir / "videos.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)

        print(f"  {len(videos)} vídeos coletados -> {out_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
