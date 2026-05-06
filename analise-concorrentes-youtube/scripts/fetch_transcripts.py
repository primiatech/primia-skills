#!/usr/bin/env python3
"""
fetch_transcripts.py

Coleta transcrições dos top vídeos com estratégia em cascata:
1. youtube-transcript-api (legendas oficiais ou auto-geradas)
2. yt-dlp como fallback (baixa faixa de legenda)
3. Falha silenciosa: log e segue

Para cada vídeo, salva:
- transcript_full.txt (texto corrido)
- transcript_timestamped.json (segmentos com timestamps)
- hook_first_30s.txt (apenas primeiros 30 segundos — crítico pra análise)

Uso:
    python fetch_transcripts.py --output-dir output/
"""
import argparse
import json
import sys
from pathlib import Path


def try_transcript_api(video_id, languages=("pt-BR", "pt", "en")):
    """Estratégia 1: youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable,
        )
    except ImportError:
        return None

    try:
        # Tenta cada idioma na ordem
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        transcript = None
        # Tenta achar manualmente criada primeiro
        for lang in languages:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                break
            except Exception:
                continue
        # Senão, auto-gerada
        if transcript is None:
            for lang in languages:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    break
                except Exception:
                    continue

        if transcript is None:
            return None

        segments = transcript.fetch()
        return [
            {"start": s.start, "duration": s.duration, "text": s.text}
            for s in segments
        ]
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
        return None
    except Exception as e:
        print(f"    [erro transcript-api {video_id}]: {e}", file=sys.stderr)
        return None


def try_ytdlp(video_id, output_dir, languages=("pt-BR", "pt", "en")):
    """Estratégia 2: yt-dlp baixa subtitle file."""
    try:
        import yt_dlp
    except ImportError:
        return None

    sub_dir = output_dir / "_temp_subs"
    sub_dir.mkdir(exist_ok=True)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": list(languages),
        "subtitlesformat": "vtt",
        "outtmpl": str(sub_dir / "%(id)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
    except Exception as e:
        print(f"    [erro yt-dlp {video_id}]: {e}", file=sys.stderr)
        return None

    # Procura o arquivo .vtt resultante
    vtt_files = list(sub_dir.glob(f"{video_id}*.vtt"))
    if not vtt_files:
        return None

    # Parse simples de VTT
    segments = []
    try:
        with open(vtt_files[0], "r", encoding="utf-8") as f:
            content = f.read()

        # Remove cabeçalho VTT
        blocks = content.split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 2:
                continue
            # Procura linha de timestamp (formato: HH:MM:SS.sss --> HH:MM:SS.sss)
            ts_line = None
            text_lines = []
            for line in lines:
                if "-->" in line:
                    ts_line = line
                elif ts_line:
                    text_lines.append(line)
            if not ts_line or not text_lines:
                continue

            start_str = ts_line.split("-->")[0].strip()
            end_str = ts_line.split("-->")[1].strip().split()[0]

            def to_sec(s):
                parts = s.replace(",", ".").split(":")
                if len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                if len(parts) == 2:
                    return int(parts[0]) * 60 + float(parts[1])
                return 0.0

            start = to_sec(start_str)
            end = to_sec(end_str)
            text = " ".join(text_lines).strip()
            if text:
                segments.append({
                    "start": start,
                    "duration": end - start,
                    "text": text,
                })

        # Cleanup
        for f in vtt_files:
            f.unlink()
    except Exception as e:
        print(f"    [erro parse vtt {video_id}]: {e}", file=sys.stderr)
        return None

    return segments


def save_transcript(segments, out_dir):
    """Salva os 3 arquivos: full.txt, timestamped.json, hook_first_30s.txt."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Full text
    full_text = " ".join(s["text"] for s in segments).strip()
    (out_dir / "transcript_full.txt").write_text(full_text, encoding="utf-8")

    # Timestamped
    with open(out_dir / "transcript_timestamped.json", "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    # First 30s
    hook_segments = [s for s in segments if s["start"] < 30]
    hook_text = " ".join(s["text"] for s in hook_segments).strip()
    (out_dir / "hook_first_30s.txt").write_text(hook_text, encoding="utf-8")


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

        ts_root = ch_dir / "transcripts"
        ts_root.mkdir(exist_ok=True)

        print(f"\n[Canal] {ch_dir.name} — {len(top_videos)} top vídeos", file=sys.stderr)

        for v in top_videos:
            vid = v["video_id"]
            v_dir = ts_root / vid
            if (v_dir / "transcript_full.txt").exists():
                print(f"  {vid}: já existe, pulando", file=sys.stderr)
                success += 1
                continue

            print(f"  {vid}: tentando transcript-api...", file=sys.stderr)
            segments = try_transcript_api(vid)

            if not segments:
                print(f"  {vid}: tentando yt-dlp...", file=sys.stderr)
                segments = try_ytdlp(vid, ts_root)

            if segments:
                save_transcript(segments, v_dir)
                print(f"  {vid}: OK ({len(segments)} segmentos)", file=sys.stderr)
                success += 1
            else:
                print(f"  {vid}: SEM TRANSCRIÇÃO", file=sys.stderr)
                failed += 1

        # Cleanup do tmp
        tmp = ts_root / "_temp_subs"
        if tmp.exists():
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nTranscrições: {success} OK, {failed} falharam", file=sys.stderr)


if __name__ == "__main__":
    main()
