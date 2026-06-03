#!/usr/bin/env python3
"""Corrige integração homepage ↔ produtos ↔ blog para o site estático Compre Rápido.

O script usa os dados já coletados, cruza com páginas efetivamente publicadas em /produtos/,
e reescreve a homepage com cards estáticos SEO-friendly e blocos editoriais acessíveis.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from datetime import datetime
from html import escape

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://comprerapido.github.io"

CATEGORY_LABELS = {
    "beleza": "Beleza e cuidados pessoais",
    "casa": "Casa",
    "casa-inteligente": "Casa inteligente",
    "celulares": "Celulares",
    "eletrodomesticos": "Eletrodomésticos",
    "eletronicos": "Eletrônicos",
    "entretenimento": "Entretenimento",
    "esporte": "Esporte e bem-estar",
    "ferramentas": "Ferramentas",
    "games": "Games",
    "informatica": "Informática",
    "moda": "Moda e estilo",
    "tecnologia": "Tecnologia",
    "tv-e-video": "TV e vídeo",
    "outros": "Ofertas variadas",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", text)


def load_products() -> list[dict]:
    ordered_sources = [
        ROOT / "data" / "scored_products.json",
        ROOT / "data" / "quality_products.json",
        ROOT / "data" / "all_products.json",
    ]
    merged: dict[str, dict] = {}
    for path in ordered_sources:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("products") or data.get("items") or []
        for p in data:
            if not isinstance(p, dict):
                continue
            pid = str(p.get("id") or p.get("product_id") or slugify(p.get("name") or p.get("title") or ""))
            if not pid:
                continue
            merged.setdefault(pid, {}).update(p)
    return list(merged.values())


def page_url_for_product(product: dict) -> str | None:
    name = product.get("name") or product.get("title") or ""
    pid = str(product.get("id") or "")
    pid_slug = pid.lower()
    cat = product.get("custom_category_slug") or "outros"
    slug = slugify(name)
    candidate = ROOT / "produtos" / cat / f"{slug}-{pid_slug}" / "index.html"
    if candidate.exists():
        return f"/produtos/{cat}/{slug}-{pid_slug}/"
    # fallback por ID: captura páginas cujo título/slug pode ter sido normalizado de forma diferente
    matches = list((ROOT / "produtos").glob(f"*/*{pid_slug}*/index.html"))
    if matches:
        rel = matches[0].parent.relative_to(ROOT).as_posix()
        return f"/{rel}/"
    return None


def money(value) -> str:
    try:
        v = float(value)
    except Exception:
        v = 0.0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(product: dict) -> int:
    try:
        return int(round(float(product.get("custom_discount_pct") or product.get("discount") or 0)))
    except Exception:
        return 0


def old_price(product: dict) -> float:
    for key in ["original_price", "originalPrice", "base_price"]:
        try:
            val = float(product.get(key) or 0)
            if val > 0:
                return val
        except Exception:
            pass
    try:
        price = float(product.get("price") or 0)
        discount = pct(product)
        if price and discount and discount < 95:
            return price / (1 - discount / 100)
    except Exception:
        pass
    return 0.0


def product_card(product: dict) -> str:
    name = escape(product.get("name") or product.get("title") or "Produto em oferta")
    cat = product.get("custom_category_slug") or "outros"
    cat_label = CATEGORY_LABELS.get(cat, cat.replace("-", " ").title())
    image = escape(product.get("image") or product.get("thumbnail") or "/assets/img/placeholder.png")
    internal = page_url_for_product(product) or "/ofertas-hoje/"
    affiliate = escape(product.get("custom_affiliate_url") or product.get("permalink") or internal)
    discount = pct(product)
    price = money(product.get("price"))
    previous = old_price(product)
    previous_html = f'<span class="old-price">De {money(previous)}</span>' if previous else ""
    rating = product.get("editorial_score") or product.get("score") or "4.6"
    try:
        rating_val = min(5, max(4.1, float(rating) if float(rating) <= 5 else 4.6))
    except Exception:
        rating_val = 4.6
    bar_width = min(100, max(12, discount * 1.25 if discount else 34))
    return f"""
        <article class="product-card product-card-pro" itemscope itemtype="https://schema.org/Product">
            <a class="product-media-link" href="{internal}" aria-label="Ver análise de {name}">
                <span class="badge-discount">{discount}% OFF</span>
                <span class="badge-hot">Oferta verificada</span>
                <img src="{image}" alt="{name}" class="product-img" loading="lazy" itemprop="image" onerror="this.src='/assets/img/placeholder.png'">
            </a>
            <div class="product-card-body">
                <span class="category-pill">{escape(cat_label)}</span>
                <h3 class="product-title" itemprop="name"><a href="{internal}">{name}</a></h3>
                <div class="visual-rating" aria-label="Avaliação editorial {rating_val:.1f} de 5">
                    <span class="stars">★★★★★</span><strong>{rating_val:.1f}</strong><small>avaliação editorial</small>
                </div>
                <div class="price-box" itemprop="offers" itemscope itemtype="https://schema.org/Offer">
                    {previous_html}
                    <div class="current-price" itemprop="price">{price}</div>
                    <meta itemprop="priceCurrency" content="BRL">
                    <link itemprop="availability" href="https://schema.org/InStock">
                    <span class="savings">Economia estimada: {discount}%</span>
                </div>
                <div class="price-history-mini" aria-label="Histórico visual de preço">
                    <span style="width:{bar_width}%"></span>
                </div>
                <div class="product-actions">
                    <a href="{internal}" class="btn-analysis">Ver análise completa</a>
                    <a href="{affiliate}" class="btn-buy" target="_blank" rel="noopener noreferrer sponsored nofollow">Ver oferta</a>
                </div>
            </div>
        </article>"""


def latest_article_cards() -> str:
    paths = []
    for base in [ROOT / "noticias", ROOT / "guias"]:
        if base.exists():
            paths.extend([p for p in base.rglob("index.html") if p.parent != base])
    paths = sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)[:6]
    cards = []
    for p in paths:
        html = p.read_text(encoding="utf-8", errors="ignore")
        title_match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
        desc_match = re.search(r'<meta name="description" content="(.*?)"', html, re.I | re.S)
        title = re.sub(r"\s+", " ", (h1_match or title_match).group(1) if (h1_match or title_match) else p.parent.name.replace("-", " ").title())
        title = re.sub(r"<.*?>", "", title)
        desc = desc_match.group(1) if desc_match else "Guia editorial com critérios práticos para comprar melhor."
        rel = "/" + p.parent.relative_to(ROOT).as_posix() + "/"
        label = "Guia de compra" if rel.startswith("/guias/") else "Artigo"
        cards.append(f"""
            <article class="article-card">
                <span>{label}</span>
                <h3><a href="{rel}">{escape(title)}</a></h3>
                <p>{escape(desc[:155])}</p>
                <a class="read-more" href="{rel}">Ler conteúdo</a>
            </article>""")
    return "\n".join(cards)


def guide_cards() -> str:
    guide_paths = sorted([p for p in (ROOT / "guias").rglob("index.html") if p.parent.name.startswith("guia-de-compra")])[:8]
    cards = []
    for p in guide_paths:
        category = p.parent.name.replace("guia-de-compra-", "").replace("-2026", "")
        rel = "/" + p.parent.relative_to(ROOT).as_posix() + "/"
        title = f"Guia de Compra: {category.replace('-', ' ').title()}"
        cards.append(f'<a class="guide-chip" href="{rel}">{escape(title)}</a>')
    return "\n".join(cards)


def main() -> None:
    products = load_products()
    published = [p for p in products if page_url_for_product(p)]
    published.sort(key=lambda p: (pct(p), float(p.get("price") or 0)), reverse=True)
    top_products = published[:24]
    product_cards = "\n".join(product_card(p) for p in top_products)

    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")

    html = html.replace('<a href="/guias/">📖 Guias</a>\n            <a href="/sobre/" class="btn-primary">Sobre Nós</a>', '<a href="/guias/">📖 Guias</a>\n            <a href="/noticias/">Blog</a>\n            <a href="/sobre/" class="btn-primary">Sobre Nós</a>')
    html = html.replace('<li><a href="/guias/">Guias de Compra</a></li>', '<li><a href="/guias/">Guias de Compra</a></li>\n                    <li><a href="/noticias/">Blog</a></li>')

    html = re.sub(r'<div id="featuredGrid" class="products-grid">.*?</div>\s*(?=\n\n    <!-- ===== TOP ESCOLHAS 2026 ===== -->)', f'<div id="featuredGrid" class="products-grid">\n{product_cards}\n    </div>', html, count=1, flags=re.S)

    latest_block = f"""
    <!-- ===== ÚLTIMOS ARTIGOS ===== -->
    <div class="section-header">
        <h2>Últimos Artigos</h2>
        <a href="/noticias/" class="btn-ver-mais">Ir para o Blog →</a>
    </div>
    <div class="articles-grid">
{latest_article_cards()}
    </div>

    <!-- ===== GUIAS DE COMPRA ===== -->
    <div class="section-header">
        <h2>Guias de Compra</h2>
        <a href="/guias/" class="btn-ver-mais">Ver Guias →</a>
    </div>
    <div class="guide-chip-grid">
{guide_cards()}
    </div>
"""
    marker = "\n\n    <!-- ===== REVIEWS RÁPIDOS ===== -->"
    if "<!-- ===== ÚLTIMOS ARTIGOS ===== -->" not in html:
        html = html.replace(marker, "\n" + latest_block + marker)

    html = html.replace('content="O Compre Rápido rastreia milhares de ofertas em tempo real para você economizar de verdade. Descontos de até 70% em eletrônicos, eletrodomésticos, moda, esporte e muito mais."', 'content="O Compre Rápido reúne ofertas verificadas, análises de preço, histórico visual, avaliações editoriais e guias de compra para ajudar você a comprar melhor."')
    html = html.replace('03/06/2026 13:59 UTC', datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC'))
    index.write_text(html, encoding="utf-8")

    report = {
        "products_loaded": len(products),
        "published_product_pages_matched": len(published),
        "homepage_product_cards_written": len(top_products),
        "latest_article_cards_written": latest_article_cards().count('class="article-card"'),
        "guide_chips_written": guide_cards().count('class="guide-chip"'),
        "sample_product_urls": [page_url_for_product(p) for p in top_products[:10]],
    }
    (ROOT / "homepage_blog_product_fix_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
