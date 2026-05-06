#!/usr/bin/env python3
"""
Extrai design tokens de um PDF.

PDFs de brand guidelines tipicamente combinam:
- Texto explícito com hex codes (ex: "Primary: #FF5733") — extração de alta confiança
- Especificações tipográficas em texto (ex: "Headlines: Inter Bold 32pt")
- Imagens embutidas com amostras de cor — extração via k-means igual extract_from_image
- Logos vetoriais (SVG embutido) — extraídos pra brand_assets

Estratégia:
1. Extrai texto de todas as páginas com pypdf
2. Faz parse de hex codes, RGB tuples, CMYK, e specs de fonte do texto
3. Extrai imagens embutidas e roda k-means em cada uma
4. Funde paletas (de texto têm prioridade, sempre)

Uso:
    python extract_from_pdf.py <pdf> [--output FILE]
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
import tempfile
import os


# ---------------------------------------------------------------------------
# Regex pra extração de specs em texto
# ---------------------------------------------------------------------------

HEX_TEXT_RE = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
RGB_TEXT_RE = re.compile(
    r'(?:RGB|rgb)\s*[:=]?\s*\(?\s*(\d{1,3})\s*[,/\s]\s*(\d{1,3})\s*[,/\s]\s*(\d{1,3})\s*\)?'
)
# CMYK aparece muito em brand guidelines impressas
CMYK_TEXT_RE = re.compile(
    r'(?:CMYK|cmyk)\s*[:=]?\s*\(?\s*(\d{1,3})\s*[,/\s]\s*(\d{1,3})\s*[,/\s]\s*(\d{1,3})\s*[,/\s]\s*(\d{1,3})\s*\)?'
)
# "Pantone 200 C" — não converte (depende de licença), mas registra no decisions
PANTONE_RE = re.compile(r'Pantone\s+([0-9A-Z\s-]+?)(?:\s+[CU])?\b', re.IGNORECASE)

# Specs tipográficas em texto livre
FONT_SPEC_RE = re.compile(
    r'([A-Z][A-Za-z0-9\s-]{2,30})\s+'                     # nome da fonte
    r'(?:(Bold|Regular|Medium|Light|Thin|Black|SemiBold|ExtraBold|Heavy)\s+)?'
    r'(\d{1,3})\s*(?:pt|px)',                              # tamanho
    re.IGNORECASE
)


def normalize_hex(hex_str: str) -> str:
    h = hex_str.lstrip('#').lower()
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return f"#{h}"


def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> tuple[int, int, int]:
    """Conversão CMYK→RGB usando fórmula sem perfil de cor (aproximada)."""
    c, m, y, k = c / 100, m / 100, y / 100, k / 100
    r = int(round(255 * (1 - c) * (1 - k)))
    g = int(round(255 * (1 - m) * (1 - k)))
    b = int(round(255 * (1 - y) * (1 - k)))
    return r, g, b


def extract_text_tokens(text: str) -> dict:
    """Extrai tokens declarados explicitamente no texto do PDF."""
    colors: list[str] = []
    pantones: list[str] = []
    fonts: list[dict] = []

    # Hex
    for match in HEX_TEXT_RE.findall(text):
        colors.append(normalize_hex(match))

    # RGB
    for r, g, b in RGB_TEXT_RE.findall(text):
        r, g, b = int(r), int(g), int(b)
        if all(0 <= v <= 255 for v in (r, g, b)):
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

    # CMYK
    for c, m, y, k in CMYK_TEXT_RE.findall(text):
        c, m, y, k = int(c), int(m), int(y), int(k)
        if all(0 <= v <= 100 for v in (c, m, y, k)):
            r, g, b = cmyk_to_rgb(c, m, y, k)
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

    # Pantone (registramos pra decisions.md, sem conversão)
    for match in PANTONE_RE.findall(text):
        pantones.append(f"Pantone {match.strip()}")

    # Specs tipográficas
    for name, weight, size in FONT_SPEC_RE.findall(text):
        name_clean = name.strip()
        # Filtros pra reduzir falso positivo (palavras comuns)
        if name_clean.lower() in {
            'page', 'section', 'chapter', 'figure', 'table',
            'note', 'see', 'use', 'the', 'all', 'this'
        }:
            continue
        fonts.append({
            "family": name_clean,
            "weight": weight.lower() if weight else "regular",
            "size": f"{size}px",
        })

    return {
        "colors": colors,
        "pantones": list(dict.fromkeys(pantones)),
        "fonts": fonts,
    }


# ---------------------------------------------------------------------------
# Extração de imagens embutidas
# ---------------------------------------------------------------------------

def extract_embedded_images(pdf_path: str, output_dir: str) -> list[str]:
    """
    Extrai imagens embutidas usando pypdf. Retorna lista de caminhos.
    Falhas silenciosas — imagens corrompidas/proprietárias são puladas.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        print("WARN: pypdf não instalado, pulando extração de imagens", file=sys.stderr)
        return []

    saved: list[str] = []
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            try:
                images = page.images
            except Exception:
                continue
            for j, image in enumerate(images):
                try:
                    out_path = os.path.join(output_dir, f"page{i+1}_img{j+1}_{image.name}")
                    with open(out_path, "wb") as f:
                        f.write(image.data)
                    saved.append(out_path)
                except Exception:
                    continue
    except Exception as e:
        print(f"WARN: erro ao iterar PDF: {e}", file=sys.stderr)

    return saved


def palette_from_image(image_path: str, n: int = 5) -> list[dict]:
    """Reaproveita a lógica de extract_from_image."""
    try:
        from PIL import Image
        import numpy as np
        from sklearn.cluster import KMeans
    except ImportError:
        return []

    try:
        img = Image.open(image_path).convert('RGB')
    except Exception:
        return []

    max_side = 150
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    arr = np.array(img).reshape(-1, 3)
    if len(arr) < n:
        return []

    try:
        kmeans = KMeans(n_clusters=n, n_init=10, random_state=42)
    except TypeError:
        kmeans = KMeans(n_clusters=n, random_state=42)

    try:
        kmeans.fit(arr)
    except Exception:
        return []

    counts = Counter(kmeans.labels_)
    total = sum(counts.values())
    palette = []
    for label, count in counts.most_common():
        r, g, b = kmeans.cluster_centers_[label]
        palette.append({
            "value": f"#{int(round(r)):02x}{int(round(g)):02x}{int(round(b)):02x}",
            "frequency": count / total,
        })
    return palette


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def extract(pdf_path: str) -> dict:
    """Pipeline completo. Retorna formato intermediário."""
    path = Path(pdf_path)
    if not path.exists():
        print(f"ERRO: arquivo não encontrado: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Texto
    try:
        from pypdf import PdfReader
    except ImportError:
        print("ERRO: pypdf não instalado. pip install pypdf", file=sys.stderr)
        sys.exit(2)

    text_full = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            try:
                text_full += page.extract_text() + "\n"
            except Exception:
                continue
    except Exception as e:
        print(f"WARN: erro ao ler PDF: {e}", file=sys.stderr)

    text_tokens = extract_text_tokens(text_full)

    # Imagens embutidas
    image_palettes: list[dict] = []
    image_paths: list[str] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        image_paths = extract_embedded_images(pdf_path, tmpdir)
        for img_path in image_paths:
            palette = palette_from_image(img_path, n=5)
            for p in palette:
                image_palettes.append(p)

    # Cores de texto têm prioridade; cores de imagem complementam
    text_colors = text_tokens["colors"]
    image_colors = [p["value"] for p in image_palettes]

    # Combinar mantendo a ordem (texto primeiro, depois imagem) + count
    all_colors = text_colors * 3 + image_colors  # peso 3x pra cores de texto
    color_counts = Counter(all_colors)

    # Tipografia: ranking por frequência declarada
    font_families = list(dict.fromkeys(f["family"] for f in text_tokens["fonts"]))
    font_sizes = list(dict.fromkeys(f["size"] for f in text_tokens["fonts"]))
    font_weights = list(dict.fromkeys(
        f["weight"] for f in text_tokens["fonts"] if f["weight"] != "regular"
    ))

    return {
        "source": {
            "type": "pdf",
            "value": str(path.absolute()),
            "filename": path.name,
            "embedded_images_found": len(image_paths),
        },
        "raw": {
            "colors": [
                {"value": c, "count": n, "from_text": c in text_colors}
                for c, n in color_counts.most_common()
            ],
            "font_families": font_families,
            "font_sizes": font_sizes,
            "font_weights": font_weights,
            "line_heights": [],
            "spacings": [],
            "radii": [],
            "shadows": [],
            "pantones": text_tokens["pantones"],
        },
        "confidence": {
            "colors": "high" if text_colors else "medium",
            "typography": "high" if text_tokens["fonts"] else "low",
            "spacing": "none",
            "radii": "none",
        },
        "brand_assets": {
            "embedded_images_count": len(image_paths),
            # As imagens embutidas viram brand_assets no merge se forem logos
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Extrai design tokens de PDF")
    parser.add_argument("pdf", help="Caminho do PDF")
    parser.add_argument("--output", "-o", help="Arquivo de saída (default: stdout)")
    args = parser.parse_args()

    result = extract(args.pdf)
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"OK: gravado em {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
