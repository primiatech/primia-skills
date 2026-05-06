#!/usr/bin/env python3
"""
rewrite-css.py — reescreve todos os url() e @import dos CSS baixados pra paths locais.

Uso:
    python3 rewrite-css.py \
        --capture-dir /caminho/para/pasta-descompactada \
        --manifest manifest.json \
        [--verbose]

A pasta-descompactada deve conter:
    assets/css/*.css
    assets/fonts/*.woff2
    images/*
    manifest.json  (mapa {url_original: path_local})

Estatísticas no final: total de url() encontrados, rewrites aplicados, referências não-resolvidas.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-dir", required=True, type=Path)
    ap.add_argument("--manifest", default="manifest.json")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    base = args.capture_dir.resolve()
    mpath = base / args.manifest
    if not mpath.exists():
        print(f"Manifest não encontrado: {mpath}", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    url_map = manifest.get("urlMap", {})
    source_origin = manifest.get("source", "")
    origin = urlparse(source_origin)
    origin_root = f"{origin.scheme}://{origin.netloc}" if origin.netloc else ""

    stats = {"files": 0, "urls": 0, "rewrites": 0, "unresolved": []}

    for css_file in base.glob("assets/css/*.css"):
        stats["files"] += 1
        text = css_file.read_text(encoding="utf-8", errors="ignore")
        original_url = None
        for url, local in url_map.items():
            if local == f"assets/css/{css_file.name}":
                original_url = url
                break

        def resolve_and_rewrite(match):
            stats["urls"] += 1
            raw = match.group(2).strip()
            if raw.startswith("data:") or raw.startswith("#"):
                return match.group(0)
            # Resolver path relativo usando URL original do CSS como base
            full = urljoin(original_url or source_origin, raw)
            # Tentar achar no manifest
            local = url_map.get(full)
            if not local:
                # Tentar achar só pelo nome do arquivo
                fname = Path(urlparse(full).path).name
                for u, l in url_map.items():
                    if l.endswith(f"/{fname}"):
                        local = l
                        break
            if not local:
                stats["unresolved"].append({"css": css_file.name, "url": raw})
                return match.group(0)
            # Reescrever relativo ao arquivo CSS (assets/css/*.css → ../../path/local)
            depth = 2  # assets/css/ → precisa de ../../
            rel = ("../" * depth) + local
            stats["rewrites"] += 1
            return f"url({rel})"

        new_text = re.sub(r'url\((["\']?)([^)"\']+)\1\)', resolve_and_rewrite, text)
        if new_text != text:
            css_file.write_text(new_text, encoding="utf-8")
            if args.verbose:
                print(f"Reescrito: {css_file.name}")

    print(f"CSS files: {stats['files']}")
    print(f"url() encontrados: {stats['urls']}")
    print(f"Rewrites aplicados: {stats['rewrites']}")
    print(f"Não resolvidos: {len(stats['unresolved'])}")
    if stats["unresolved"] and args.verbose:
        for u in stats["unresolved"][:20]:
            print(f"  ! {u['css']}: {u['url']}")


if __name__ == "__main__":
    main()
