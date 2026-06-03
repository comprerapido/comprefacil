#!/usr/bin/env python3
"""Aplica melhorias SEO e cria dataset de homepage apenas com produtos publicados."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://comprerapido.github.io"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", text)


def load_products() -> list[dict]:
    merged = {}
    for rel in ["data/scored_products.json", "data/quality_products.json", "data/all_products.json"]:
        p = ROOT / rel
        if not p.exists():
            continue
        for item in json.loads(p.read_text(encoding="utf-8")):
            pid = str(item.get("id") or slugify(item.get("name") or item.get("title") or ""))
            merged.setdefault(pid, {}).update(item)
    return list(merged.values())


def internal_url(product: dict) -> str | None:
    pid = str(product.get("id") or "").lower()
    name = product.get("name") or product.get("title") or ""
    cat = product.get("custom_category_slug") or "outros"
    candidate = ROOT / "produtos" / cat / f"{slugify(name)}-{pid}" / "index.html"
    if candidate.exists():
        return "/" + candidate.parent.relative_to(ROOT).as_posix() + "/"
    matches = list((ROOT / "produtos").glob(f"*/*{pid}*/index.html"))
    if matches:
        return "/" + matches[0].parent.relative_to(ROOT).as_posix() + "/"
    return None


def add_home_faq() -> bool:
    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")
    faq_block = """
    <!-- ===== FAQ HOMEPAGE ===== -->
    <div class="section-header">
        <h2>Perguntas Frequentes</h2>
        <a href="/transparencia/" class="btn-ver-mais">Critérios de curadoria →</a>
    </div>
    <section class="articles-grid faq-grid" id="faq">
        <article class="article-card"><span>FAQ</span><h3>Como o Compre Rápido escolhe as ofertas?</h3><p>O site combina preço atual, desconto estimado, histórico local, categoria e critérios editoriais para priorizar ofertas com maior sinal de vantagem.</p></article>
        <article class="article-card"><span>FAQ</span><h3>Os preços podem mudar?</h3><p>Sim. Preço, estoque, frete e condições comerciais pertencem ao marketplace parceiro e devem ser confirmados antes da compra.</p></article>
        <article class="article-card"><span>FAQ</span><h3>O site vende os produtos diretamente?</h3><p>Não. O Compre Rápido publica análises, guias e links para lojas parceiras. A venda e entrega são responsabilidade do vendedor final.</p></article>
    </section>
"""
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": "Como o Compre Rápido escolhe as ofertas?", "acceptedAnswer": {"@type": "Answer", "text": "O site combina preço atual, desconto estimado, histórico local, categoria e critérios editoriais para priorizar ofertas com maior sinal de vantagem."}},
            {"@type": "Question", "name": "Os preços podem mudar?", "acceptedAnswer": {"@type": "Answer", "text": "Sim. Preço, estoque, frete e condições comerciais pertencem ao marketplace parceiro e devem ser confirmados antes da compra."}},
            {"@type": "Question", "name": "O site vende os produtos diretamente?", "acceptedAnswer": {"@type": "Answer", "text": "Não. O Compre Rápido publica análises, guias e links para lojas parceiras. A venda e entrega são responsabilidade do vendedor final."}},
        ],
    }
    changed = False
    if "<!-- ===== FAQ HOMEPAGE ===== -->" not in html:
        html = html.replace("\n\n    <!-- ===== REVIEWS RÁPIDOS ===== -->", "\n" + faq_block + "\n    <!-- ===== REVIEWS RÁPIDOS ===== -->", 1)
        changed = True
    if '"@type": "FAQPage"' not in html and "</head>" in html:
        html = html.replace("</head>", f'<script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False)}</script>\n</head>', 1)
        changed = True
    if changed:
        index.write_text(html, encoding="utf-8")
    return changed


def main() -> None:
    published = []
    for p in load_products():
        url = internal_url(p)
        if url:
            p = dict(p)
            p["internal_url"] = url
            published.append(p)
    published.sort(key=lambda p: int(float(p.get("custom_discount_pct") or 0)), reverse=True)
    out = ROOT / "data" / "homepage_products.json"
    out.write_text(json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8")

    app = ROOT / "assets" / "js" / "app.js"
    js = app.read_text(encoding="utf-8")
    js = js.replace("const DATA_URL = '/data/database/all_products.json';", "const DATA_URL = '/data/homepage_products.json';")
    app.write_text(js, encoding="utf-8")

    report = {"homepage_faq_added_or_present": add_home_faq(), "published_dataset_count": len(published), "dataset": "/data/homepage_products.json"}
    (ROOT / "seo_published_data_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
