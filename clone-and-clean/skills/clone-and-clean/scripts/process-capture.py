#!/usr/bin/env python3
"""
process-capture.py — processa o ZIP baixado pelo Chrome e prepara o filesystem local.

Pipeline:
  1. Descompacta o ZIP gerado por browser-capture.js
  2. Lê manifest.json (mapa url → path local)
  3. Baixa assets faltantes via `curl` (HTTP fallback — caso o fetch no browser
     tenha falhado por CORS ou autenticação)
  4. Invoca rewrite-css.py pra corrigir url() e @import dos CSS
  5. Reescreve src/href do HTML pra paths locais usando o urlMap
  6. Gera um relatório final (total de arquivos, faltantes, tamanhos)

Uso:
    python3 process-capture.py \\
        --zip /caminho/para/capture.zip \\
        --out /caminho/para/pasta-destino \\
        [--skip-download] [--verbose]

Pré-requisitos:
    - Python 3.9+
    - curl disponível no PATH
    - rewrite-css.py no mesmo diretório deste script
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse


SCRIPT_DIR = Path(__file__).resolve().parent


def log(msg, verbose=False, always=True):
    if always or verbose:
        print(msg)


def unzip_capture(zip_path: Path, out_dir: Path, verbose=False):
    if not zip_path.exists():
        sys.exit(f"❌ ZIP não encontrado: {zip_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)
    log(f"✓ Descompactado em {out_dir}", verbose)


def load_manifest(capture_dir: Path):
    mpath = capture_dir / "manifest.json"
    if not mpath.exists():
        sys.exit(f"❌ manifest.json ausente em {capture_dir}. Foi gerado pelo browser-capture.js?")
    return json.loads(mpath.read_text(encoding="utf-8"))


def download_missing(capture_dir: Path, manifest: dict, verbose=False):
    """Baixa via curl os assets que estão no urlMap mas faltam no disco."""
    missing = []
    fixed = []
    for url, local in manifest.get("urlMap", {}).items():
        target = capture_dir / local
        if target.exists() and target.stat().st_size > 0:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["curl", "-sS", "-L", "-o", str(target), url],
                check=True, timeout=30,
                capture_output=True,
            )
            if target.stat().st_size > 0:
                fixed.append(local)
                if verbose:
                    log(f"  ↓ {local}", True)
            else:
                missing.append(local)
        except subprocess.CalledProcessError as e:
            missing.append(local)
            if verbose:
                log(f"  ✗ {local} ({e.returncode})", True)
        except subprocess.TimeoutExpired:
            missing.append(local)
    log(f"✓ Assets baixados via curl: {len(fixed)}")
    log(f"  Faltantes: {len(missing)}")
    if missing and verbose:
        for m in missing[:10]:
            log(f"  ! {m}", True)
    return fixed, missing


def rewrite_html(capture_dir: Path, manifest: dict, verbose=False):
    """Reescreve src/href/srcset no index.html pra paths locais."""
    html_path = capture_dir / "index.html"
    if not html_path.exists():
        sys.exit(f"❌ index.html ausente em {capture_dir}")
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    rewrites = 0
    for url, local in manifest.get("urlMap", {}).items():
        esc = re.escape(url)
        new_html, n = re.subn(esc, local, html)
        if n > 0:
            html = new_html
            rewrites += n
    html_path.write_text(html, encoding="utf-8")
    log(f"✓ HTML reescrito: {rewrites} ocorrências trocadas por paths locais")


def invoke_rewrite_css(capture_dir: Path, verbose=False):
    rewriter = SCRIPT_DIR / "rewrite-css.py"
    if not rewriter.exists():
        log("⚠️  rewrite-css.py não encontrado no mesmo diretório — pulando")
        return
    cmd = ["python3", str(rewriter), "--capture-dir", str(capture_dir)]
    if verbose:
        cmd.append("--verbose")
    subprocess.run(cmd, check=False)


def final_report(capture_dir: Path, manifest: dict):
    counts = {"css": 0, "js": 0, "images": 0, "fonts": 0, "other": 0}
    sizes = {"css": 0, "js": 0, "images": 0, "fonts": 0, "other": 0}
    for root in ("assets/css", "assets/js", "assets/fonts", "images", "other"):
        p = capture_dir / root
        if not p.exists():
            continue
        key = {
            "assets/css": "css",
            "assets/js": "js",
            "assets/fonts": "fonts",
            "images": "images",
            "other": "other",
        }[root]
        for f in p.iterdir():
            if f.is_file():
                counts[key] += 1
                sizes[key] += f.stat().st_size
    log("\n" + "─" * 60)
    log("RELATÓRIO FINAL")
    log("─" * 60)
    for k in ("css", "js", "fonts", "images", "other"):
        log(f"  {k:7s}: {counts[k]:4d} arquivo(s)  ({sizes[k]/1024:.1f} KB)")
    log(f"  TOTAL : {sum(counts.values())} arquivo(s)  ({sum(sizes.values())/1024:.1f} KB)")
    log(f"  source: {manifest.get('source', 'n/d')}")
    log(f"  capturedAt: {manifest.get('capturedAt', 'n/d')}")


def main():
    ap = argparse.ArgumentParser(description="Processa ZIP de captura e prepara filesystem local.")
    ap.add_argument("--zip", required=True, type=Path, help="ZIP gerado por browser-capture.js")
    ap.add_argument("--out", required=True, type=Path, help="Pasta destino (ex: clientes/X/Y/Z/)")
    ap.add_argument("--skip-download", action="store_true", help="Pular fallback de curl")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    unzip_capture(args.zip, args.out, args.verbose)
    manifest = load_manifest(args.out)

    if not args.skip_download:
        download_missing(args.out, manifest, args.verbose)

    rewrite_html(args.out, manifest, args.verbose)
    invoke_rewrite_css(args.out, args.verbose)
    final_report(args.out, manifest)
    print("\n✅ Processamento concluído.")


if __name__ == "__main__":
    main()
