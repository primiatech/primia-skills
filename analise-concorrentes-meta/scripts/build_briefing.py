#!/usr/bin/env python3
"""
build_briefing.py — Gera briefings criativos em Markdown.

Entregáveis 6.5 da skill: insumo de produção pra copywriter / aluno criar
anúncios próprios baseados nos padrões vencedores identificados.

Gera:
  - briefings/<concorrente>.md (1 por concorrente — replicar vencedor)
  - briefings/_consolidado.md (mistura insights de todos)

Uso:
    python build_briefing.py \
        --enriched output/concorrente1/enriched_ads.json \
                   output/concorrente2/enriched_ads.json \
        --analysis output/analysis.json \
        --output-dir /mnt/user-data/outputs/briefings

O `analysis.json` deve ter, em cada `by_competitor[slug]`, um campo `briefing`:
{
    "avatar": "Mulheres 30-45, classe B, mães...",
    "dor_principal": "Falta de tempo pra cuidar da saúde",
    "angulo_vencedor": "PROVA_SOCIAL",
    "hook_recomendado": "Você sabia que 9 em cada 10...",
    "estrutura_video_30s": [
        {"tempo": "0-3s", "acao": "Hook impactante: pergunta provocativa"},
        {"tempo": "3-10s", "acao": "Apresenta o problema"},
        ...
    ],
    "copy_feed": "Texto pronto de 100-150 palavras...",
    "cta_recomendada": {"tipo": "SHOP_NOW", "justificativa": "..."},
    "oferta_sugerida": "Estrutura sugerida da oferta",
    "evitar": ["Não copiar tom", "Não usar depoimentos específicos"],
    "evidencia": ["12345", "67890", "11111"]
}

E, no nível raiz, um campo `briefing_consolidado` com a mesma estrutura mas
representando o anúncio "perfeito" que mistura o melhor de cada concorrente.
"""

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

# Versão sincronizada — fonte única para rodapés gerados.
# Mantenha igual ao frontmatter do SKILL.md (campo metadata.version).
VERSION = "1.2.0"

# Caminho do template parametrizado
TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets" / "briefing-template.md"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def render_estrutura_blocks(estrutura: list) -> dict:
    """Quebra a estrutura de vídeo em 4 blocos (hook, problema, solução, CTA).

    Retorna um dict com chaves STRUCTURE_HOOK / STRUCTURE_PROBLEM /
    STRUCTURE_SOLUTION / STRUCTURE_CTA. Se a estrutura tiver menos de 4 blocos,
    distribui o que tem e completa com placeholder.
    """
    fallback = "_(a definir)_"
    keys = ["STRUCTURE_HOOK", "STRUCTURE_PROBLEM", "STRUCTURE_SOLUTION", "STRUCTURE_CTA"]
    out = {k: fallback for k in keys}
    if not estrutura:
        return out
    for i, bloco in enumerate(estrutura[:4]):
        out[keys[i]] = bloco.get("acao", fallback)
    return out


def render_evitar(evitar: list) -> str:
    if not evitar:
        return "_(nenhuma observação específica)_"
    return "\n".join(f"- {item}" for item in evitar)


def render_evidencia(evidencia: list, ads_index: dict) -> str:
    """Renderiza lista de IDs com contexto (dias no ar)."""
    if not evidencia:
        return "_(sem evidências vinculadas)_"
    lines = []
    for ad_id in evidencia:
        ad = ads_index.get(str(ad_id))
        if ad:
            days = ad.get("days_running", "?")
            lines.append(f"- `ad_archive_id: {ad_id}` ({days} dias no ar)")
        else:
            lines.append(f"- `ad_archive_id: {ad_id}`")
    return "\n".join(lines)


CHECKLIST_FIXO = """- [ ] O avatar acima bate com o seu cliente real?
- [ ] Você adaptou o hook com a voz da sua marca?
- [ ] A oferta sugerida cabe na sua margem?
- [ ] O CTA está alinhado com seu funil atual?
- [ ] Você revisou os IDs de evidência pra confirmar contexto?"""


def load_template() -> str:
    """Carrega o template parametrizado de briefing.

    Se o arquivo não existir (instalação corrompida), usa um fallback embutido
    com a mesma estrutura — assim o pipeline não derruba.
    """
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH.read_text(encoding="utf-8")
    return _FALLBACK_TEMPLATE


# Fallback caso o assets/briefing-template.md não esteja disponível.
_FALLBACK_TEMPLATE = """# Briefing Criativo — {{TARGET}}

> **{{TYPE}}**
> Gerado em {{DATE}} · {{AUTHOR_LINE}}

## Avatar identificado
{{AVATAR}}

## Dor principal explorada
{{PAIN}}

## Ângulo vencedor a replicar
**{{ANGLE_NAME}}**
> {{ANGLE_NOTE}}

## Hook recomendado (vídeo)
> "{{HOOK}}"

{{HOOK_NOTE}}

## Estrutura sugerida (vídeo 30s)
- 0-3s: {{STRUCTURE_HOOK}}
- 3-10s: {{STRUCTURE_PROBLEM}}
- 10-22s: {{STRUCTURE_SOLUTION}}
- 22-30s: {{STRUCTURE_CTA}}

## Copy de feed
```
{{COPY_FEED}}
```

## CTA recomendada
**`{{CTA_NAME}}`**
{{CTA_RATIONALE}}

## Oferta sugerida
{{OFFER}}

## O que NÃO copiar
{{NOT_TO_COPY}}

## Evidência
{{EVIDENCE}}

## Checklist antes de produzir
{{CHECKLIST}}

---
_Briefing gerado pela skill `analise-concorrentes-meta` v{{VERSION}} · Mentoria Primia._
"""


def render_briefing(
    target: str,
    tipo: str,
    briefing: dict,
    ads_index: dict,
    autor: str = "Hoberdan Silva — Mentoria Primia",
) -> str:
    """Renderiza um briefing completo em markdown a partir do template."""

    template = load_template()

    # Defensivo: se algum campo veio vazio, sinaliza claramente
    avatar = briefing.get("avatar") or "_(não definido — preencher antes de produzir)_"
    dor = briefing.get("dor_principal") or "_(não definida)_"
    angulo = briefing.get("angulo_vencedor") or "_(não definido)_"
    angulo_note = briefing.get("angulo_nota") or (
        "Esse é o ângulo predominante nos anúncios mais longevos analisados — "
        "sinal forte de que ressoa com o avatar do nicho."
    )
    hook = briefing.get("hook_recomendado") or "_(não definido)_"
    hook_note = briefing.get("hook_nota") or (
        "Adapte com a voz da sua marca. **Não copie literalmente** — a similaridade "
        "alta com criativos do concorrente reduz performance no leilão da Meta e "
        "arrisca strike por similaridade."
    )
    copy_feed = briefing.get("copy_feed") or "_(não definido)_"

    cta = briefing.get("cta_recomendada", {})
    cta_tipo = cta.get("tipo", "_(não definido)_")
    cta_just = cta.get("justificativa", "")

    oferta = briefing.get("oferta_sugerida") or "_(não definida)_"

    structure_blocks = render_estrutura_blocks(briefing.get("estrutura_video_30s", []))
    evitar_md = render_evitar(briefing.get("evitar", []))
    evidencia_md = render_evidencia(briefing.get("evidencia", []), ads_index)

    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")

    placeholders = {
        "TARGET": target,
        "TYPE": tipo,
        "DATE": timestamp,
        "AUTHOR_LINE": autor,
        "AVATAR": avatar,
        "PAIN": dor,
        "ANGLE_NAME": angulo,
        "ANGLE_NOTE": angulo_note,
        "HOOK": hook,
        "HOOK_NOTE": hook_note,
        "STRUCTURE_HOOK": structure_blocks["STRUCTURE_HOOK"],
        "STRUCTURE_PROBLEM": structure_blocks["STRUCTURE_PROBLEM"],
        "STRUCTURE_SOLUTION": structure_blocks["STRUCTURE_SOLUTION"],
        "STRUCTURE_CTA": structure_blocks["STRUCTURE_CTA"],
        "COPY_FEED": copy_feed,
        "CTA_NAME": cta_tipo,
        "CTA_RATIONALE": cta_just,
        "OFFER": oferta,
        "NOT_TO_COPY": evitar_md,
        "EVIDENCE": evidencia_md,
        "CHECKLIST": CHECKLIST_FIXO,
        "VERSION": VERSION,
    }

    out = template
    for key, value in placeholders.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out


def build_ads_index(enriched_files: list) -> dict:
    """Cria índice global ad_archive_id → dados do ad, pra resolver evidências."""
    index = {}
    for path in enriched_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for ad in data.get("ads", []):
            ad_id = str(ad.get("ad_archive_id", ""))
            if ad_id:
                index[ad_id] = ad
    return index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enriched", nargs="+", required=True,
                        help="Caminhos dos enriched_ads.json")
    parser.add_argument("--analysis", required=True,
                        help="Caminho do analysis.json com briefings preenchidos")
    parser.add_argument("--output-dir", required=True,
                        help="Diretório onde salvar os .md")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Carrega análise
    with open(args.analysis, encoding="utf-8") as f:
        analysis = json.load(f)

    # Índice global de ads pra resolver evidências
    ads_index = build_ads_index(args.enriched)

    # 1. Um briefing por concorrente
    by_competitor = analysis.get("by_competitor", {})
    if not by_competitor:
        print("[!] Nenhum concorrente em analysis.by_competitor — pulando briefings individuais")

    arquivos_gerados = []
    for slug, comp_data in by_competitor.items():
        briefing = comp_data.get("briefing")
        if not briefing:
            print(f"[!] Concorrente '{slug}' sem campo `briefing` — pulando")
            continue

        nome = comp_data.get("nome") or slug
        md = render_briefing(
            target=nome,
            tipo="Por concorrente",
            briefing=briefing,
            ads_index=ads_index,
        )

        out_path = output_dir / f"{slugify(nome)}.md"
        out_path.write_text(md, encoding="utf-8")
        arquivos_gerados.append(out_path)
        print(f"[✓] Briefing individual: {out_path}")

    # 2. Briefing consolidado
    briefing_consolidado = analysis.get("briefing_consolidado")
    if briefing_consolidado:
        nomes = [c.get("nome", slug) for slug, c in by_competitor.items()]
        target_consolidado = f"Anúncio consolidado misturando o melhor de: {', '.join(nomes)}"
        md = render_briefing(
            target=target_consolidado,
            tipo="Consolidado",
            briefing=briefing_consolidado,
            ads_index=ads_index,
        )
        out_path = output_dir / "_consolidado.md"
        out_path.write_text(md, encoding="utf-8")
        arquivos_gerados.append(out_path)
        print(f"[✓] Briefing consolidado: {out_path}")
    else:
        print("[!] Sem campo `briefing_consolidado` no analysis.json — pulando consolidado")

    print(f"\n[✓] {len(arquivos_gerados)} briefing(s) gerado(s) em {output_dir}")


if __name__ == "__main__":
    main()
