#!/usr/bin/env python3
"""
enrich_creatives.py — Enriquece os anúncios com transcrição (Whisper), OCR (Tesseract) e pHash.

Uso:
    python enrich_creatives.py --input /home/claude/output/concorrente/raw_ads.json
        [--whisper-model small|tiny|base|medium]
        [--skip-whisper] [--skip-ocr]

Saída: gera enriched_ads.json ao lado do raw_ads.json.

Estratégia:
- Whisper: transcreve vídeos. Se não estiver instalado, pula sem falhar.
- Tesseract: OCR em imagens. Se não estiver instalado, pula sem falhar.
- pHash: hash perceptual para detectar duplicatas/variações. Sempre tenta.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Imports condicionais
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


def transcribe_video(model, video_path: Path) -> str | None:
    """Transcreve vídeo com Whisper. Retorna texto ou None se falhar."""
    try:
        result = model.transcribe(str(video_path), language="pt", fp16=False, verbose=False)
        return result["text"].strip()
    except Exception as e:
        print(f"    [x] Whisper falhou em {video_path.name}: {e}")
        return None


def ocr_image(image_path: Path) -> str | None:
    """Extrai texto de imagem via Tesseract."""
    if not (TESSERACT_AVAILABLE and PIL_AVAILABLE):
        return None
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="por+eng")
        return text.strip() or None
    except Exception as e:
        print(f"    [x] OCR falhou em {image_path.name}: {e}")
        return None


def phash_image(image_path: Path) -> str | None:
    """Calcula pHash perceptual."""
    if not (IMAGEHASH_AVAILABLE and PIL_AVAILABLE):
        return None
    try:
        return str(imagehash.phash(Image.open(image_path)))
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Caminho do raw_ads.json")
    parser.add_argument("--whisper-model", default="small",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--skip-whisper", action="store_true")
    parser.add_argument("--skip-ocr", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERRO: {input_path} não encontrado")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    # Carrega Whisper uma vez
    whisper_model = None
    if WHISPER_AVAILABLE and not args.skip_whisper:
        try:
            print(f"[*] Carregando Whisper ({args.whisper_model})...")
            whisper_model = whisper.load_model(args.whisper_model)
        except Exception as e:
            print(f"[!] Whisper não pôde ser carregado: {e}")
            whisper_model = None
    elif args.skip_whisper:
        print("[*] Whisper pulado (--skip-whisper)")
    else:
        print("[!] Whisper não instalado — pulando transcrições")

    if not (TESSERACT_AVAILABLE and PIL_AVAILABLE) or args.skip_ocr:
        print("[!] OCR pulado (Tesseract não instalado ou --skip-ocr)")

    ads = data.get("ads", [])
    print(f"[*] Enriquecendo {len(ads)} anúncios...")

    capabilities = {
        "whisper": whisper_model is not None,
        "ocr": TESSERACT_AVAILABLE and PIL_AVAILABLE and not args.skip_ocr,
        "phash": IMAGEHASH_AVAILABLE and PIL_AVAILABLE,
    }

    for i, ad in enumerate(ads, 1):
        print(f"[{i}/{len(ads)}] {ad.get('ad_archive_id', '?')}")
        ad.setdefault("transcript", None)
        ad.setdefault("ocr_text", None)
        ad.setdefault("phash", [])

        for lf in ad.get("local_files", []):
            path = Path(lf["path"])
            if not path.exists():
                continue

            if lf["type"] == "video" and whisper_model:
                if ad.get("transcript") is None:
                    print(f"    transcrevendo {path.name}...")
                    ad["transcript"] = transcribe_video(whisper_model, path)

            elif lf["type"] == "image":
                if capabilities["ocr"] and not ad.get("ocr_text"):
                    txt = ocr_image(path)
                    if txt:
                        ad["ocr_text"] = txt

                if capabilities["phash"]:
                    h = phash_image(path)
                    if h:
                        ad["phash"].append({"file": lf["filename"], "hash": h})

    # Salva resultado
    output_path = input_path.parent / "enriched_ads.json"
    data["metadata"]["enrichment_capabilities"] = capabilities
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Resultado salvo em {output_path}")
    print(f"[✓] Capabilities ativas: {capabilities}")


if __name__ == "__main__":
    main()
