#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(rel, default=None):
    p = ROOT / rel
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

index = (ROOT / "index.html").read_text(encoding="utf-8", errors="ignore")
app = (ROOT / "assets/js/app.js").read_text(encoding="utf-8", errors="ignore")
product_pages = list((ROOT / "produtos").glob("*/*/index.html"))
article_html = []
for base in [ROOT / "noticias", ROOT / "guias"]:
    if base.exists():
        article_html.extend(base.rglob("*.html"))

sample_urls = list(dict.fromkeys(re.findall(r'href="(/produtos/[^\"]+)"', index)))[:10]
report = {
    "causa_raiz": "Os produtos eram gerados em /produtos/, mas partes do pipeline e do sitemap ainda tratavam /ofertas/ ou dependiam de renderização dinâmica; a homepage inicial não publicava cards estáticos suficientes com URLs internas válidas.",
    "produtos_coletados_all_products": len(load_json("data/all_products.json", [])),
    "produtos_qualificados": len(load_json("data/quality_products.json", [])),
    "paginas_produto_publicadas": len(product_pages),
    "produtos_no_dataset_da_homepage": len(load_json("data/homepage_products.json", [])),
    "cards_estaticos_homepage": index.count("product-card-pro"),
    "links_internos_produtos_homepage": len(re.findall(r'href="/produtos/[^\"]+"', index)),
    "blog_no_menu": 'href="/noticias/"' in index,
    "pagina_blog_existe": (ROOT / "noticias" / "index.html").exists(),
    "bloco_ultimos_artigos_homepage": "<!-- ===== ÚLTIMOS ARTIGOS ===== -->" in index,
    "bloco_guias_compra_homepage": "<!-- ===== GUIAS DE COMPRA ===== -->" in index,
    "faq_homepage_schema": "FAQPage" in index,
    "sitemap_produtos_urls": (ROOT / "sitemap-produtos.xml").read_text(encoding="utf-8", errors="ignore").count("<url>"),
    "produtos_com_artigos_relacionados": sum("CR_RELATED_ARTICLES" in p.read_text(encoding="utf-8", errors="ignore") for p in product_pages),
    "artigos_guias_com_produtos_relacionados": sum("CR_RELATED_PRODUCTS" in p.read_text(encoding="utf-8", errors="ignore") for p in article_html),
    "dataset_dinamico_app_js": re.search(r"const DATA_URL = '([^']+)'", app).group(1) if re.search(r"const DATA_URL = '([^']+)'", app) else None,
    "scripts_pos_publicacao_no_auto_robot": all(s in (ROOT / "scripts" / "auto_robot.py").read_text(encoding="utf-8") for s in ["fix_homepage_blog_product_integration.py", "enhance_blog_product_crosslinks.py", "apply_seo_and_published_data.py", "finalize_blog_and_sitemaps.py"]),
    "amostra_urls_produtos_homepage": sample_urls,
}
(ROOT / "final_ux_publication_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

md = ["# Auditoria final de publicação, blog, UX e SEO", ""]
md.append("## Diagnóstico")
md.append(report["causa_raiz"])
md.append("")
md.append("## Evidências")
for k, v in report.items():
    if k in {"causa_raiz", "amostra_urls_produtos_homepage"}:
        continue
    md.append(f"- **{k.replace('_',' ')}:** {v}")
md.append("")
md.append("## URLs de produtos publicadas na homepage")
for url in sample_urls:
    md.append(f"- {url}")
(ROOT / "final_ux_publication_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
