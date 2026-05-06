#!/usr/bin/env python3
"""
resolve_channels.py

Resolve diferentes formatos de input (URL, @handle, channel ID, nome) em channel_id canônico (UC...).

Estratégia:
1. Se input já é UC...: valida com API
2. Se @handle: usa search da API
3. Se URL: extrai e processa
4. Modo Sem-API: usa yt-dlp como fallback

Uso:
    python resolve_channels.py --inputs "@canal1" "youtube.com/@canal2" "UCxxx" --output channels.json [--api-key KEY]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_input(raw):
    """Normaliza input pra um identificador útil."""
    raw = raw.strip()

    # URL completa
    url_match = re.match(r"https?://(www\.)?youtube\.com/(.+)", raw)
    if url_match:
        rest = url_match.group(2)
        if rest.startswith("@"):
            return ("handle", rest.split("/")[0])
        if rest.startswith("channel/"):
            return ("channel_id", rest.split("/")[1].split("?")[0])
        if rest.startswith("c/") or rest.startswith("user/"):
            return ("legacy_url", raw)

    # Handle direto
    if raw.startswith("@"):
        return ("handle", raw)

    # Channel ID direto
    if re.match(r"^UC[\w-]{20,}$", raw):
        return ("channel_id", raw)

    # Nome livre
    return ("name", raw)


def resolve_with_api(input_kind, value, api_key):
    """Resolve usando YouTube Data API v3."""
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    youtube = build("youtube", "v3", developerKey=api_key)

    channel_id = None

    try:
        if input_kind == "channel_id":
            channel_id = value
        elif input_kind == "handle":
            handle = value.lstrip("@")
            resp = youtube.channels().list(
                part="id", forHandle=handle
            ).execute()
            items = resp.get("items", [])
            if items:
                channel_id = items[0]["id"]
            else:
                # Fallback via search
                resp = youtube.search().list(
                    part="snippet", q=handle, type="channel", maxResults=1
                ).execute()
                items = resp.get("items", [])
                if items:
                    channel_id = items[0]["snippet"]["channelId"]
        elif input_kind == "name":
            resp = youtube.search().list(
                part="snippet", q=value, type="channel", maxResults=1
            ).execute()
            items = resp.get("items", [])
            if items:
                channel_id = items[0]["snippet"]["channelId"]
        elif input_kind == "legacy_url":
            # URL antiga (/c/Nome ou /user/Nome) — buscar pelo nome
            name = value.rstrip("/").split("/")[-1]
            resp = youtube.search().list(
                part="snippet", q=name, type="channel", maxResults=1
            ).execute()
            items = resp.get("items", [])
            if items:
                channel_id = items[0]["snippet"]["channelId"]

        if not channel_id:
            return None

        # Hidrata dados completos
        resp = youtube.channels().list(
            part="snippet,statistics,brandingSettings",
            id=channel_id
        ).execute()
        items = resp.get("items", [])
        if not items:
            return None

        ch = items[0]
        snippet = ch.get("snippet", {})
        stats = ch.get("statistics", {})

        return {
            "channel_id": channel_id,
            "title": snippet.get("title"),
            "description": snippet.get("description", ""),
            "country": snippet.get("country"),
            "published_at": snippet.get("publishedAt"),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        }

    except HttpError as e:
        print(f"  [erro API]: {e}", file=sys.stderr)
        return None


def resolve_with_ytdlp(input_kind, value):
    """Fallback usando yt-dlp (sem API key)."""
    try:
        import yt_dlp
    except ImportError:
        print("  [erro]: yt-dlp não instalado", file=sys.stderr)
        return None

    if input_kind == "handle":
        url = f"https://www.youtube.com/{value}"
    elif input_kind == "channel_id":
        url = f"https://www.youtube.com/channel/{value}"
    elif input_kind == "legacy_url":
        url = value
    else:
        url = f"https://www.youtube.com/results?search_query={value}"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": 1,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        channel_id = info.get("channel_id") or info.get("uploader_id")
        if not channel_id:
            entries = info.get("entries", [])
            if entries:
                channel_id = entries[0].get("channel_id")

        if not channel_id:
            return None

        return {
            "channel_id": channel_id,
            "title": info.get("channel") or info.get("uploader"),
            "description": info.get("description", ""),
            "country": None,
            "published_at": None,
            "subscriber_count": info.get("channel_follower_count") or 0,
            "video_count": None,
            "view_count": None,
            "thumbnail_url": None,
        }
    except Exception as e:
        print(f"  [erro yt-dlp]: {e}", file=sys.stderr)
        return None


def slugify(text):
    if not text:
        return "canal"
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:50] or "canal"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--api-key", default=os.getenv("YOUTUBE_API_KEY"))
    args = parser.parse_args()

    use_api = bool(args.api_key)
    if not use_api:
        print("[aviso] Sem API key — usando yt-dlp (Modo Sem-API)", file=sys.stderr)

    results = []
    for raw in args.inputs:
        input_kind, value = parse_input(raw)
        print(f"Resolvendo: {raw}  ({input_kind})", file=sys.stderr)

        data = None
        if use_api:
            data = resolve_with_api(input_kind, value, args.api_key)
        if not data:
            data = resolve_with_ytdlp(input_kind, value)

        if data:
            data["input"] = raw
            data["slug"] = slugify(data.get("title"))
            results.append(data)
            print(f"  OK: {data['title']} ({data['channel_id']})", file=sys.stderr)
        else:
            print(f"  FALHOU: {raw}", file=sys.stderr)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{len(results)}/{len(args.inputs)} canais resolvidos -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
