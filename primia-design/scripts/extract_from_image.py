#!/usr/bin/env python3
"""
Extrai paleta de cores de uma imagem usando k-means.

Cores são o único token confiável de extrair de imagem.
Tipografia, spacing e radius dependem de OCR/visão e são marcados
explicitamente como inferidos (e portanto baixa confiança) — esse
script registra isso no campo `confidence` do output.

Uso:
    python extract_from_image.py <imagem> [--colors N] [--output FILE]
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def extract_palette(image_path: str, n_colors: int = 8) -> list[dict]:
    """
    Extrai paleta dominante usando k-means.
    Retorna lista de dicts: {value: '#rrggbb', frequency: 0.0-1.0}
    ordenada por frequência decrescente.
    """
    try:
        from PIL import Image
        import numpy as np
        from sklearn.cluster import KMeans
    except ImportError as e:
        print(
            f"ERRO: dependência faltando ({e}).\n"
            "  pip install Pillow numpy scikit-learn",
            file=sys.stderr
        )
        sys.exit(2)

    img = Image.open(image_path).convert('RGB')

    # Reduzir a imagem acelera muito o k-means sem perder qualidade na paleta.
    # 200px no lado maior é suficiente.
    max_side = 200
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    arr = np.array(img).reshape(-1, 3)

    # k-means com n_init explícito (compat sklearn novo/antigo)
    try:
        kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    except TypeError:
        kmeans = KMeans(n_clusters=n_colors, random_state=42)

    kmeans.fit(arr)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    counts = Counter(labels)
    total = sum(counts.values())

    palette = []
    for label, count in counts.most_common():
        r, g, b = centers[label]
        hex_color = f"#{int(round(r)):02x}{int(round(g)):02x}{int(round(b)):02x}"
        palette.append({
            "value": hex_color,
            "frequency": count / total,
            "rgb": [int(round(r)), int(round(g)), int(round(b))],
        })

    return palette


def detect_dimensions(image_path: str) -> dict:
    """Retorna dimensões e relação de aspecto da imagem."""
    try:
        from PIL import Image
    except ImportError:
        return {}

    img = Image.open(image_path)
    w, h = img.size
    return {
        "width": w,
        "height": h,
        "aspect_ratio": round(w / h, 3) if h else None,
    }


def extract(image_path: str, n_colors: int = 8) -> dict:
    """Pipeline completo. Retorna o formato intermediário."""
    path = Path(image_path)
    if not path.exists():
        print(f"ERRO: arquivo não encontrado: {image_path}", file=sys.stderr)
        sys.exit(1)

    palette = extract_palette(image_path, n_colors=n_colors)
    dimensions = detect_dimensions(image_path)

    return {
        "source": {
            "type": "image",
            "value": str(path.absolute()),
            "filename": path.name,
            "dimensions": dimensions,
        },
        "raw": {
            "colors": [
                {"value": p["value"], "count": int(p["frequency"] * 1000),
                 "frequency": p["frequency"]}
                for p in palette
            ],
            # Imagens não dão extração confiável dos itens abaixo:
            "font_families": [],
            "font_sizes": [],
            "font_weights": [],
            "line_heights": [],
            "spacings": [],
            "radii": [],
            "shadows": [],
        },
        "confidence": {
            "colors": "high",
            "typography": "none",  # exigiria OCR + reconhecimento de fonte
            "spacing": "none",
            "radii": "none",
        },
        "brand_assets": {
            # A própria imagem pode ser um logo — sinalizamos pra o pipeline decidir
            "source_image_path": str(path.absolute()),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Extrai paleta de imagem")
    parser.add_argument("image", help="Caminho da imagem")
    parser.add_argument("--colors", "-n", type=int, default=8,
                        help="Número de cores na paleta (default: 8)")
    parser.add_argument("--output", "-o", help="Arquivo de saída (default: stdout)")
    args = parser.parse_args()

    result = extract(args.image, n_colors=args.colors)
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"OK: gravado em {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
