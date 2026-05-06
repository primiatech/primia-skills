#!/usr/bin/env python3
"""
verify.py — valida uma pasta clean/ ou deploy-ready/

Checa:
1. Todos os paths locais referenciados no HTML existem em disco
2. Pixels/trackers esperados estão mantidos
3. TODOs documentados (WhatsApp, canonical, endpoints de API)
4. Sem referências residuais ao domínio original (exceto feeds RSS)

Uso:
    python3 verify.py --target /caminho/clean \
        --expected-pixels GTM-XXX 123456789 G-ABCD \
        [--original-domain crisschumann.com]
"""
import argparse
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument("--expected-pixels", nargs="*", default=[])
    ap.add_argument("--original-domain", default=None)
    args = ap.parse_args()

    target = args.target.resolve()
    html_path = target / "index.html"
    if not html_path.exists():
        print(f"ERRO: {html_path} não existe", file=sys.stderr)
        sys.exit(2)

    html = html_path.read_text(encoding="utf-8")
    errors = []
    warnings = []

    # 1. Paths locais
    local_paths = set()
    for m in re.finditer(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', html):
        v = m.group(1).strip().split("?")[0].split("#")[0]
        if v and not v.startswith(("http://", "https://", "//", "data:", "javascript:", "mailto:", "tel:", "#")):
            local_paths.add(v)
    for m in re.finditer(r'url\((["\']?)([^)"\']+)\1\)', html):
        v = m.group(2).strip().split("?")[0]
        if v and not v.startswith(("http", "data:", "//")):
            local_paths.add(v)

    missing = [p for p in local_paths if not (target / p).exists()]
    present = [p for p in local_paths if (target / p).exists()]
    print(f"[1] Paths locais: {len(present)}/{len(local_paths)} presentes")
    if missing:
        for m in missing:
            # Permite placeholders TODO
            if m.startswith("TODO_") or m == "#":
                continue
            errors.append(f"  ✗ Path faltando: {m}")

    # 2. Pixels
    print(f"[2] Pixels esperados:")
    for pixel in args.expected_pixels:
        if pixel in html:
            print(f"    ✓ {pixel}")
        else:
            errors.append(f"  ✗ Pixel ausente: {pixel}")

    # 3. TODOs
    todos = re.findall(r"TODO[_\w-]*", html)
    print(f"[3] TODOs no código: {len(todos)}")
    for t in set(todos):
        print(f"    • {t} ({todos.count(t)}×)")

    # 4. Referências ao domínio original
    if args.original_domain:
        d = args.original_domain
        refs = re.findall(rf'(?:src|href)\s*=\s*["\']https?://(?:www\.)?{re.escape(d)}[^"\']*', html)
        # Permitir feeds RSS
        bad_refs = [r for r in refs if "feed" not in r.lower()]
        print(f"[4] Refs ao domínio {d}: {len(refs)} total, {len(bad_refs)} fora de feeds")
        for r in bad_refs[:10]:
            warnings.append(f"  ⚠ Ref residual: {r[:120]}")

    print("\n=== Resultado ===")
    if errors:
        print(f"ERROS: {len(errors)}")
        for e in errors:
            print(e)
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for w in warnings:
            print(w)
    if not errors:
        print("✓ OK — pasta validada")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
