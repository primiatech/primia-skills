# Formato intermediário (entre extratores e merge)

Cada extrator (`extract_from_url.py`, `extract_from_image.py`,
`extract_from_pdf.py`) produz um JSON nesse formato. O `merge_sources.py`
consome múltiplos desses e produz um único `merged.json`.

## Schema

```json
{
  "source": {
    "type": "url" | "pdf" | "image",
    "value": "string (url ou caminho absoluto)",
    "title": "string opcional (só url)",
    "filename": "string opcional (pdf/image)",
    "extraction_method": "static | playwright (só url)",
    "dimensions": {"width": int, "height": int} (só image),
    "embedded_images_found": int (só pdf)
  },
  "raw": {
    "colors": [
      {"value": "#rrggbb", "count": int, "from_text": bool (opcional, só pdf)}
    ],
    "font_families": ["string"],
    "font_sizes": [
      "16px" | {"value": "16px", "count": int}
    ],
    "font_weights": ["400", "bold", ...],
    "line_heights": ["1.5", "24px", ...],
    "spacings": [
      "16px" | {"value": "16px", "count": int}
    ],
    "radii": [
      "8px" | {"value": "8px", "count": int}
    ],
    "shadows": ["0 1px 2px rgba(0,0,0,0.1)"],
    "pantones": ["Pantone 200 C"] (opcional, só pdf)
  },
  "confidence": {
    "colors": "high | medium | low | none",
    "typography": "high | medium | low | none",
    "spacing": "high | medium | low | none",
    "radii": "high | medium | low | none"
  },
  "brand_assets": {
    "logo_candidates": [{"type": "img|svg", "src|html": "...", "from": "..."}],
    "source_image_path": "string (só image)",
    "embedded_images_count": int (só pdf)
  }
}
```

## Confiança por fonte

| Tipo  | Cores | Tipografia | Spacing | Radius |
|-------|-------|------------|---------|--------|
| URL (estática) | high | high | high | high |
| URL (Playwright) | high | high | high | high |
| PDF (com texto) | high | high (se especificada) | none | none |
| PDF (só visual) | medium | low | none | none |
| Imagem | high | none | none | none |

## Notas para mergers

- Cores podem aparecer com pequena variação entre fontes — comparar com
  threshold de distância (≤8 = mesma cor, 8-25 = conflito potencial).
- Quando `confidence` é `none` para um campo, simplesmente ignore esse
  campo dessa fonte. Não use defaults.
- `brand_assets.logo_candidates` deve ser preservado da fonte de maior
  prioridade na hierarquia.
