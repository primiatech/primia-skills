#!/usr/bin/env python3
"""
download_creatives.py — Baixa imagens e vídeos dos anúncios coletados.

Uso:
    python download_creatives.py --input /home/claude/output/concorrente/raw_ads.json

Saída: cria pasta `creatives/` ao lado do raw_ads.json com os arquivos baixados.
       Atualiza o raw_ads.json adicionando `local_files` em cada anúncio.

Estratégia:
- Imagens via requests (rápido, leve).
- Vídeos via yt-dlp (mais robusto pra CDN da Meta, lida com URLs assinadas).
- Falhas individuais não param o processo.
- Skip se arquivo já existe (idempotente).
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERRO: requests não instalado. Rode: pip install requests")
    sys.exit(1)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://www.facebook.com/",
}


def guess_extension(url: str, default: str = "bin") -> str:
    """Tenta inferir extensão da URL."""
    path = urlparse(url).path.lower()
    for ext in ("jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"):
        if path.endswith(f".{ext}"):
            return ext
    return default


def download_image(url: str, dest: Path) -> bool:
    """Baixa imagem via requests."""
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest.stat().st_size > 0
    except Exception as e:
        print(f"    [x] Falha imagem: {e}")
        if dest.exists():
            dest.unlink()
        return False


def download_video(url: str, dest: Path) -> bool:
    """Baixa vídeo via yt-dlp se disponível, fallback para requests."""
    if dest.exists() and dest.stat().st_size > 0:
        return True

    # Tenta yt-dlp primeiro
    try:
        result = subprocess.run(
            ["yt-dlp", "-q", "--no-warnings", "-o", str(dest), url],
            capture_output=True, timeout=120, text=True
        )
        if result.returncode == 0 and dest.exists():
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: requests
    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        return dest.stat().st_size > 0
    except Exception as e:
        print(f"    [x] Falha vídeo: {e}")
        if dest.exists():
            dest.unlink()
        return False


def process_ad(ad: dict, creatives_dir: Path) -> list[dict]:
    """Baixa todas as mídias de um anúncio. Retorna lista de arquivos locais."""
    local_files = []
    ad_id = ad.get("ad_archive_id") or f"unknown-{abs(hash(ad.get('body_text', '')))}"

    for idx, media in enumerate(ad.get("media_urls", [])):
        url = media.get("url")
        mtype = media.get("type", "image")
        if not url:
            continue

        ext = guess_extension(url, default="mp4" if mtype == "video" else "jpg")
        filename = f"{ad_id}_{idx}.{ext}"
        dest = creatives_dir / filename

        success = (download_video(url, dest) if mtype == "video"
                   else download_image(url, dest))

        if success:
            local_files.append({
                "type": mtype,
                "path": str(dest),
                "filename": filename,
                "role": media.get("role"),
            })

    return local_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Caminho do raw_ads.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERRO: {input_path} não encontrado")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    creatives_dir = input_path.parent / "creatives"
    creatives_dir.mkdir(exist_ok=True)

    ads = data.get("ads", [])
    print(f"[*] Processando {len(ads)} anúncios...")

    total_files = 0
    for i, ad in enumerate(ads, 1):
        print(f"[{i}/{len(ads)}] {ad.get('ad_archive_id', '?')} "
              f"({len(ad.get('media_urls', []))} mídias)")
        local_files = process_ad(ad, creatives_dir)
        ad["local_files"] = local_files
        total_files += len(local_files)

    # Salva de volta
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] {total_files} arquivos baixados em {creatives_dir}")
    print(f"[✓] Metadata atualizada em {input_path}")


if __name__ == "__main__":
    main()
