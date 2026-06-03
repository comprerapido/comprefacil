#!/usr/bin/env python3
"""Adiciona interligação editorial entre produtos, blog e guias.

A rotina atua sobre HTML estático já publicado, preservando conteúdo existente e criando
seções idempotentes de links relacionados para SEO e navegação.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
MARK_PRODUCT_ARTICLES = "<!-- CR_RELATED_ARTICLES -->"
MARK_ARTICLE_PRODUCTS = "<!-- CR_RELATED_PRODUCTS -->"

CATEGORY_LABELS = {
    "beleza": "Beleza e cuidados pessoais",
    "casa": "Casa",
    "celulares": "Celulares",
    "eletrodomesticos": "Eletrodomésticos",
    "esporte": "Esporte e bem-estar",
    "ferramentas": "Ferramentas",
    "games": "Games",
    "informatica": "Informática",
    "tecnologia": "Tecnologia",
    "tv-e-video": "TV e vídeo",
}


def title_of(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S) or re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if not m:
        return path.parent.name.replace("-", " ").title()
    return re.sub(r"\s+", " ", re.sub(r"<.*?>", "", m.group(1))).replace(" | Compre Rápido", "").strip()


def rel_url_from_index(path: Path) -> str:
    if path.name == "index.html":
        return "/" + path.parent.relative_to(ROOT).as_posix() + "/"
    return "/" + path.relative_to(ROOT).as_posix()


def product_pages() -> list[dict]:
    out = []
    for p in sorted((ROOT / "produtos").glob("*/*/index.html")):
        rel = p.relative_to(ROOT).as_posix()
        parts = rel.split("/")
        cat = parts[1] if len(parts) > 2 else "outros"
        html = p.read_text(encoding="utf-8", errors="ignore")
        price = re.search(r'<p class="price">(.*?)</p>', html, re.I | re.S)
        out.append({"path": p, "url": rel_url_from_index(p), "category": cat, "title": title_of(p), "price": price.group(1) if price else ""})
    return out


def article_pages() -> list[dict]:
    paths = []
    for base in [ROOT / "noticias" / "posts", ROOT / "guias"]:
        if base.exists():
            paths += [p for p in base.rglob("index.html") if p.parent != base]
            paths += [p for p in base.glob("*.html") if p.name != "index.html"]
    out = []
    for p in sorted(paths):
        rel = rel_url_from_index(p)
        text = rel.lower()
        cat = next((c for c in CATEGORY_LABELS if c in text), "")
        out.append({"path": p, "url": rel, "category": cat, "title": title_of(p)})
    return out


def add_blog_to_nav(html: str) -> str:
    if '/noticias/' in html and '>Blog<' in html:
        return html
    html = html.replace('<a href="/guias/">Guias</a><a href="/transparencia/">', '<a href="/guias/">Guias</a><a href="/noticias/">Blog</a><a href="/transparencia/">')
    html = html.replace('<a href="/guias/">📖 Guias</a>\n            <a href="/sobre/"', '<a href="/guias/">📖 Guias</a>\n            <a href="/noticias/">Blog</a>\n            <a href="/sobre/"')
    return html


def related_articles_block(product: dict, articles: list[dict]) -> str:
    category_articles = [a for a in articles if a["category"] == product["category"]]
    generic = [a for a in articles if a not in category_articles]
    selected = (category_articles + generic)[:4]
    if not selected:
        return ""
    links = "".join(f"<li><a href='{a['url']}'>{escape(a['title'])}</a></li>" for a in selected)
    return f"""
        {MARK_PRODUCT_ARTICLES}
        <section class="card"><h2>Artigos relacionados</h2><p>Continue pesquisando com guias editoriais e tendências conectadas a esta categoria.</p><ul>{links}</ul></section>
        <!-- /CR_RELATED_ARTICLES -->"""


def related_products_block(article: dict, products: list[dict]) -> str:
    selected = [p for p in products if p["category"] == article["category"]] if article["category"] else []
    if len(selected) < 4:
        selected = selected + [p for p in products if p not in selected]
    selected = selected[:6]
    cards = "".join(f"<li><a href='{p['url']}'>{escape(p['title'])}</a>{' — ' + escape(p['price']) if p['price'] else ''}</li>" for p in selected)
    return f"""
        {MARK_ARTICLE_PRODUCTS}
        <section class="card"><h2>Produtos relacionados</h2><p>Veja análises e ofertas publicadas que complementam este conteúdo editorial.</p><ul>{cards}</ul></section>
        <!-- /CR_RELATED_PRODUCTS -->"""


def replace_marked(html: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(html):
        return pattern.sub(block, html)
    return html


def main() -> None:
    products = product_pages()
    articles = article_pages()
    product_updates = 0
    article_updates = 0

    for item in products:
        path = item["path"]
        html = add_blog_to_nav(path.read_text(encoding="utf-8", errors="ignore"))
        block = related_articles_block(item, articles)
        if MARK_PRODUCT_ARTICLES in html:
            html = replace_marked(html, MARK_PRODUCT_ARTICLES, "<!-- /CR_RELATED_ARTICLES -->", block)
        elif block:
            html = html.replace('<section class="card"><h2>Transparência editorial</h2>', block + '\n        <section class="card"><h2>Transparência editorial</h2>', 1)
        path.write_text(html, encoding="utf-8")
        product_updates += 1

    for item in articles:
        path = item["path"]
        html = add_blog_to_nav(path.read_text(encoding="utf-8", errors="ignore"))
        block = related_products_block(item, products)
        if MARK_ARTICLE_PRODUCTS in html:
            html = replace_marked(html, MARK_ARTICLE_PRODUCTS, "<!-- /CR_RELATED_PRODUCTS -->", block)
        elif "</main>" in html:
            html = html.replace("</main>", block + "\n</main>", 1)
        else:
            html = html.replace("</body>", block + "\n</body>", 1)
        path.write_text(html, encoding="utf-8")
        article_updates += 1

    report = {"product_pages_updated": product_updates, "article_pages_updated": article_updates, "product_pages_detected": len(products), "article_pages_detected": len(articles)}
    (ROOT / "crosslink_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
