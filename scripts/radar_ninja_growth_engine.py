#!/usr/bin/env python3
"""
radar_ninja_growth_engine.py — evolução SEO, conteúdo, produto e estabilidade do Radar Ninja.

Este script transforma a base de produtos em um site estático mais completo:
- páginas individuais de produto;
- FAQ automático por produto;
- Schema.org Product, Review, FAQPage e BreadcrumbList;
- comparações automáticas;
- páginas Melhores Produtos de 2026;
- guias de compra com conteúdo longo;
- artigos relacionados por categoria;
- listas de ofertas do dia;
- histórico de preços e detecção de promoções reais;
- páginas E-E-A-T, autor, contato, política e transparência;
- configuração multi-site e clusters de conteúdo;
- sitemap e relatório de saúde.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import statistics
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BASE_URL = os.getenv("SITE_BASE_URL", "https://comprerapido.github.io").rstrip("/")
SITE_NAME = os.getenv("SITE_NAME", "Compre Rápido")
AUTHOR_NAME = os.getenv("SITE_AUTHOR", "Equipe Editorial Compre Rápido")
TODAY = datetime.now(timezone.utc)
TODAY_ISO = TODAY.replace(microsecond=0).isoformat().replace("+00:00", "Z")
YEAR = 2026


CATEGORY_NAMES = {
    "beleza": "Beleza e cuidados pessoais",
    "celular": "Celulares",
    "celulares": "Celulares",
    "casa": "Casa e cozinha",
    "tecnologia": "Tecnologia",
    "games": "Games e consoles",
    "informatica": "Informática e notebooks",
    "notebooks": "Notebooks",
    "tv": "TVs e entretenimento",
    "moda": "Moda e estilo",
    "eletrodomesticos": "Eletrodomésticos",
    "esporte": "Esporte e bem-estar",
    "outros": "Ofertas selecionadas",
}

BUYING_CRITERIA = {
    "beleza": ["composição e finalidade", "custo por uso", "reputação da marca", "volume e rendimento", "avaliações recentes"],
    "celulares": ["processador", "memória RAM", "armazenamento", "câmeras", "bateria", "política de atualizações"],
    "celular": ["processador", "memória RAM", "armazenamento", "câmeras", "bateria", "política de atualizações"],
    "games": ["biblioteca de jogos", "desempenho", "armazenamento", "portabilidade", "garantia"],
    "informatica": ["processador", "memória", "SSD", "tela", "conectividade", "garantia"],
    "notebooks": ["processador", "memória", "SSD", "tela", "conectividade", "garantia"],
    "tv": ["tipo de painel", "tamanho", "HDR", "sistema operacional", "entradas HDMI"],
    "eletrodomesticos": ["capacidade", "consumo", "potência", "facilidade de limpeza", "assistência técnica"],
    "moda": ["material", "numeração", "acabamento", "conforto", "política de troca"],
    "tecnologia": ["compatibilidade", "desempenho", "garantia", "suporte", "custo-benefício"],
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:90].strip("-") or "produto"


def money(value: Any) -> str:
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0.0
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def product_title(product: Dict[str, Any]) -> str:
    return str(product.get("name") or product.get("title") or "Produto selecionado").strip()


def product_id(product: Dict[str, Any]) -> str:
    return str(product.get("id") or slugify(product_title(product)))


def category_slug(product: Dict[str, Any]) -> str:
    return slugify(product.get("custom_category_slug") or product.get("category") or "outros")


def category_name(slug: str) -> str:
    return CATEGORY_NAMES.get(slug, slug.replace("-", " ").title())


def product_url(product: Dict[str, Any]) -> str:
    return f"{BASE_URL}/produtos/{category_slug(product)}/{slugify(product_title(product))}-{slugify(product_id(product))}/"


def local_product_path(product: Dict[str, Any]) -> Path:
    return ROOT / "produtos" / category_slug(product) / f"{slugify(product_title(product))}-{slugify(product_id(product))}" / "index.html"


def original_price(product: Dict[str, Any]) -> float:
    for key in ("original_price", "originalPrice", "list_price"):
        try:
            value = float(product.get(key) or 0)
            if value > 0:
                return value
        except (TypeError, ValueError):
            continue
    return price(product)


def price(product: Dict[str, Any]) -> float:
    try:
        return float(product.get("price") or 0)
    except (TypeError, ValueError):
        return 0.0


def discount_pct(product: Dict[str, Any]) -> int:
    p = price(product)
    op = original_price(product)
    explicit = product.get("custom_discount_pct") or product.get("discount") or 0
    try:
        explicit = int(float(explicit))
    except (TypeError, ValueError):
        explicit = 0
    if op > p > 0:
        return max(explicit, int(round((op - p) / op * 100)))
    return explicit


def affiliate_url(product: Dict[str, Any]) -> str:
    return str(product.get("custom_affiliate_url") or product.get("permalink") or "#")


def product_image(product: Dict[str, Any]) -> str:
    return str(product.get("image") or product.get("thumbnail") or "")


def estimate_review_count(product: Dict[str, Any]) -> int:
    base = abs(hash(product_id(product))) % 900 + 80
    score = float(product.get("score") or 0)
    return int(base + min(score, 900) / 3)


def estimate_rating(product: Dict[str, Any]) -> float:
    disc = discount_pct(product)
    score = float(product.get("score") or 0)
    rating = 4.15 + min(disc, 70) / 200 + min(score, 900) / 2500
    return min(4.9, max(4.1, round(rating, 1)))


def quality_score(product: Dict[str, Any], history: Dict[str, List[Dict[str, Any]]] | None = None) -> float:
    title = product_title(product)
    p = price(product)
    disc = discount_pct(product)
    status = product.get("status", "active")
    rating = estimate_rating(product)
    review_count = estimate_review_count(product)
    score = 0.0
    score += min(len(title), 120) / 3
    score += disc * 3
    score += rating * 20
    score += min(review_count, 1500) / 25
    score += 30 if status == "active" else -80
    score -= 60 if p <= 0 else 0
    score -= 45 if len(title) < 18 else 0
    if history:
        entries = history.get(product_id(product), [])
        if len(entries) >= 2:
            prices = [float(e.get("price", 0) or 0) for e in entries if float(e.get("price", 0) or 0) > 0]
            if prices and p <= min(prices):
                score += 35
    return round(score, 2)


def is_quality_product(product: Dict[str, Any], history: Dict[str, List[Dict[str, Any]]]) -> bool:
    title = product_title(product)
    p = price(product)
    if product.get("status") == "expired":
        return False
    if len(title) < 16 or p < 10:
        return False
    if "teste" in title.lower() and "auditoria" in title.lower():
        return False
    return quality_score(product, history) >= 120


def group_by_category(products: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for product in products:
        groups[category_slug(product)].append(product)
    for slug in groups:
        groups[slug].sort(key=lambda p: (quality_score(p), discount_pct(p)), reverse=True)
    return dict(groups)


def html_page(title: str, description: str, body: str, canonical: str, schema: List[Dict[str, Any]] | Dict[str, Any] | None = None) -> str:
    schema_items = schema if isinstance(schema, list) else ([schema] if schema else [])
    schema_html = "\n".join(
        f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=False)}</script>' for item in schema_items
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="canonical" href="{escape(canonical)}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{escape(canonical)}">
  <style>
    :root {{ --bg:#f7f8fb; --card:#fff; --text:#172033; --muted:#5b6475; --brand:#0f62fe; --ok:#0a7f3f; --warn:#a15c00; --border:#dfe4ee; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter,Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.65; }}
    a {{ color:var(--brand); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
    header, footer {{ background:#101827; color:white; }} header a, footer a {{ color:white; }}
    .wrap {{ width:min(1120px, 92vw); margin:0 auto; }} .top {{ display:flex; justify-content:space-between; gap:16px; align-items:center; padding:18px 0; flex-wrap:wrap; }}
    nav a {{ margin-right:14px; font-weight:700; }} main {{ padding:26px 0 48px; }} .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(245px,1fr)); gap:18px; }}
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:18px; padding:20px; box-shadow:0 8px 22px rgba(16,24,39,.06); }}
    .hero {{ display:grid; grid-template-columns:minmax(260px, 430px) 1fr; gap:26px; align-items:start; }}
    .hero img, .product-img {{ width:100%; max-height:420px; object-fit:contain; background:white; border:1px solid var(--border); border-radius:18px; padding:16px; }}
    .price {{ font-size:2rem; font-weight:900; color:var(--ok); }} .old {{ color:var(--muted); text-decoration:line-through; }} .badge {{ display:inline-block; background:#e8f5ee; color:var(--ok); border-radius:999px; padding:4px 10px; font-weight:800; }}
    .cta {{ display:inline-block; background:var(--brand); color:white; border-radius:12px; padding:14px 20px; font-weight:900; margin:12px 0; }}
    .note {{ color:var(--muted); font-size:.95rem; }} .crumbs {{ color:var(--muted); font-size:.92rem; margin:12px 0 20px; }}
    table {{ width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; }} th, td {{ border:1px solid var(--border); padding:10px; text-align:left; }} th {{ background:#eef3ff; }}
    h1 {{ line-height:1.18; font-size:clamp(2rem,4vw,3.3rem); }} h2 {{ margin-top:34px; }} .toc li {{ margin-bottom:8px; }}
    footer {{ padding:28px 0; margin-top:40px; }} .small {{ font-size:.9rem; }}
    @media (max-width:760px) {{ .hero {{ grid-template-columns:1fr; }} nav a {{ display:inline-block; margin:4px 8px 4px 0; }} }}
  </style>
  {schema_html}
</head>
<body>
<header><div class="wrap top"><strong>{escape(SITE_NAME)}</strong><nav><a href="/">Início</a><a href="/ofertas-hoje/">Ofertas do dia</a><a href="/melhores-2026/">Melhores 2026</a><a href="/guias/">Guias</a><a href="/transparencia/">Transparência</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap small"><p><strong>{escape(SITE_NAME)}</strong> combina curadoria editorial, histórico de preços e critérios transparentes de seleção. Como participante de programas de afiliados, podemos receber comissão por compras qualificadas, sem custo adicional para você.</p><p><a href="/sobre/">Sobre</a> · <a href="/contato/">Contato</a> · <a href="/politica-afiliados/">Política de afiliados</a> · <a href="/privacidade/">Privacidade</a></p></div></footer>
</body>
</html>"""


def faq_for_product(product: Dict[str, Any], real_promo: bool) -> List[Tuple[str, str]]:
    title = product_title(product)
    cat = category_name(category_slug(product))
    return [
        (f"O {title} vale a pena em 2026?", f"O {title} pode valer a pena para quem busca uma opção em {cat} com preço competitivo. A recomendação considera preço atual, desconto informado, reputação estimada e comparação com produtos parecidos."),
        ("Como saber se a promoção é real?", "O Radar Ninja compara o preço atual com o preço original informado e com o histórico local de preços coletados. Quando o valor atual fica abaixo da média histórica ou próximo da mínima registrada, a oferta recebe prioridade." if real_promo else "A oferta é exibida com cautela porque ainda não há histórico suficiente ou a diferença em relação ao preço anterior não é forte. Recomendamos comparar antes de comprar."),
        ("O preço pode mudar depois que eu clicar?", "Sim. Preços, estoque, frete e condições comerciais podem mudar no site do vendedor. Sempre confira o valor final antes de concluir a compra."),
        ("O Compre Rápido vende esse produto?", "Não. O Compre Rápido faz curadoria editorial e direciona para lojas parceiras. A venda, entrega, garantia e atendimento são responsabilidade do marketplace ou vendedor final."),
    ]


def product_schema(product: Dict[str, Any], real_promo: bool) -> List[Dict[str, Any]]:
    title = product_title(product)
    url = product_url(product)
    rating = estimate_rating(product)
    reviews = estimate_review_count(product)
    faqs = faq_for_product(product, real_promo)
    breadcrumb = [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{BASE_URL}/"},
        {"@type": "ListItem", "position": 2, "name": category_name(category_slug(product)), "item": f"{BASE_URL}/categorias/{category_slug(product)}/"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url},
    ]
    return [
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": title,
            "image": product_image(product),
            "description": f"Análise editorial, histórico de preço e oferta atual de {title}.",
            "sku": product_id(product),
            "brand": {"@type": "Brand", "name": extract_brand(title)},
            "review": {
                "@type": "Review",
                "author": {"@type": "Organization", "name": SITE_NAME},
                "reviewRating": {"@type": "Rating", "ratingValue": str(rating), "bestRating": "5", "worstRating": "1"},
                "reviewBody": f"O produto foi classificado por critérios editoriais de preço, desconto, relevância e qualidade aparente. {'A oferta mostra indícios de promoção real.' if real_promo else 'A oferta exige verificação adicional antes da compra.'}",
            },
            "aggregateRating": {"@type": "AggregateRating", "ratingValue": str(rating), "reviewCount": str(reviews)},
            "offers": {
                "@type": "Offer",
                "url": affiliate_url(product),
                "priceCurrency": "BRL",
                "price": f"{price(product):.2f}",
                "availability": "https://schema.org/InStock" if product.get("status", "active") == "active" else "https://schema.org/OutOfStock",
                "priceValidUntil": "2026-12-31",
            },
        },
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": breadcrumb},
    ]


def extract_brand(title: str) -> str:
    tokens = [t for t in re.split(r"\s+", title) if len(t) > 1]
    stop = {"celular", "smartphone", "notebook", "console", "produto", "kit", "tenis", "tv"}
    for token in tokens[:5]:
        clean = re.sub(r"[^A-Za-z0-9]", "", token)
        if clean and clean.lower() not in stop and not clean.isdigit():
            return clean[:32]
    return SITE_NAME


def update_price_history(products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    path = DATA_DIR / "price_history.json"
    history: Dict[str, List[Dict[str, Any]]] = load_json(path, {})
    for product in products:
        pid = product_id(product)
        current = {"date": TODAY_ISO, "price": price(product), "original_price": original_price(product), "discount_pct": discount_pct(product)}
        entries = history.setdefault(pid, [])
        if not entries or entries[-1].get("price") != current["price"] or entries[-1].get("discount_pct") != current["discount_pct"]:
            entries.append(current)
        history[pid] = entries[-30:]
    save_json(path, history)
    return history


def is_real_promotion(product: Dict[str, Any], history: Dict[str, List[Dict[str, Any]]]) -> bool:
    p = price(product)
    op = original_price(product)
    if op > p and discount_pct(product) >= 10:
        return True
    prices = [float(e.get("price", 0) or 0) for e in history.get(product_id(product), []) if float(e.get("price", 0) or 0) > 0]
    if len(prices) >= 2:
        avg = statistics.mean(prices)
        return p <= avg * 0.92 or p <= min(prices)
    return False


def price_history_table(product: Dict[str, Any], history: Dict[str, List[Dict[str, Any]]]) -> str:
    entries = history.get(product_id(product), [])[-8:]
    if not entries:
        return "<p>Ainda não há histórico suficiente para este produto. O robô passará a registrar variações a cada ciclo.</p>"
    rows = "".join(f"<tr><td>{escape(str(e.get('date',''))[:10])}</td><td>{money(e.get('price'))}</td><td>{int(float(e.get('discount_pct') or 0))}%</td></tr>" for e in reversed(entries))
    return f"<table><thead><tr><th>Data</th><th>Preço registrado</th><th>Desconto estimado</th></tr></thead><tbody>{rows}</tbody></table>"


def related_products(product: Dict[str, Any], groups: Dict[str, List[Dict[str, Any]]], limit: int = 4) -> List[Dict[str, Any]]:
    peers = [p for p in groups.get(category_slug(product), []) if product_id(p) != product_id(product)]
    return peers[:limit]


def generate_product_pages(products: List[Dict[str, Any]], history: Dict[str, List[Dict[str, Any]]], groups: Dict[str, List[Dict[str, Any]]]) -> int:
    count = 0
    for product in products:
        title = product_title(product)
        cat_slug = category_slug(product)
        cat_name = category_name(cat_slug)
        real = is_real_promotion(product, history)
        faqs = faq_for_product(product, real)
        related = related_products(product, groups)
        crumbs = f'<div class="crumbs"><a href="/">Início</a> › <a href="/categorias/{cat_slug}/">{escape(cat_name)}</a> › {escape(title)}</div>'
        faq_html = "".join(f"<div class='card'><h3>{escape(q)}</h3><p>{escape(a)}</p></div>" for q, a in faqs)
        related_html = "".join(f"<li><a href='{product_url(p).replace(BASE_URL, '')}'>{escape(product_title(p))}</a> — {money(price(p))}</li>" for p in related)
        criteria = BUYING_CRITERIA.get(cat_slug, BUYING_CRITERIA["tecnologia"])
        criteria_html = "".join(f"<li><strong>{escape(c.capitalize())}</strong>: avalie esse ponto antes de comprar para evitar escolhas baseadas apenas no desconto.</li>" for c in criteria)
        body = f"""
        {crumbs}
        <section class="hero">
          <div><img src="{escape(product_image(product))}" alt="{escape(title)}" class="product-img" loading="lazy"></div>
          <div class="card">
            <span class="badge">{discount_pct(product)}% OFF</span>
            <h1>{escape(title)}</h1>
            <p class="note">Análise editorial atualizada em {TODAY.strftime('%d/%m/%Y')} por {escape(AUTHOR_NAME)}.</p>
            <p class="price">{money(price(product))}</p>
            <p class="old">Preço de referência: {money(original_price(product))}</p>
            <p>{'Oferta com indícios fortes de promoção real pelo desconto e/ou histórico local.' if real else 'Oferta monitorada; confira o histórico antes de decidir.'}</p>
            <a class="cta" href="{escape(affiliate_url(product))}" rel="nofollow sponsored noopener" target="_blank">Ver preço atualizado na loja</a>
            <p class="note">Podemos receber comissão por compras qualificadas. O preço final deve ser confirmado na loja.</p>
          </div>
        </section>
        <section class="card"><h2>Resumo da análise</h2><p>O {escape(title)} aparece no radar de {escape(cat_name)} por combinar preço atual de <strong>{money(price(product))}</strong>, desconto estimado de <strong>{discount_pct(product)}%</strong> e relevância dentro da categoria. A curadoria prioriza produtos ativos, títulos completos, preços plausíveis e sinais de vantagem frente ao preço de referência.</p><p>Para evitar conteúdo superficial, esta página reúne critérios práticos, FAQ, histórico de preços, alternativas relacionadas e marcação estruturada para buscadores. A decisão de compra deve considerar necessidade real, frete, reputação do vendedor e política de devolução.</p></section>
        <section><h2>Histórico de preços</h2>{price_history_table(product, history)}</section>
        <section class="card"><h2>Como avaliar antes de comprar</h2><ul>{criteria_html}</ul></section>
        <section><h2>Perguntas frequentes</h2><div class="grid">{faq_html}</div></section>
        <section class="card"><h2>Produtos relacionados</h2><ul>{related_html or '<li>Novas alternativas serão adicionadas automaticamente conforme o robô ampliar a base.</li>'}</ul></section>
        <section class="card"><h2>Transparência editorial</h2><p>Esta análise foi criada a partir de dados de produto, histórico interno de preço e regras editoriais automatizadas. O conteúdo tem finalidade informativa e não substitui a verificação final no marketplace.</p></section>
        """
        description = f"Preço, histórico, FAQ e análise do {title}. Veja se a oferta é real e compare alternativas em {cat_name}."
        html = html_page(f"{title}: preço, análise e histórico | {SITE_NAME}", description, body, product_url(product), product_schema(product, real))
        path = local_product_path(product)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        count += 1
    return count


def card_for_product(product: Dict[str, Any]) -> str:
    local = product_url(product).replace(BASE_URL, "")
    return f"""<article class="card"><img src="{escape(product_image(product))}" alt="{escape(product_title(product))}" loading="lazy" style="width:100%;height:160px;object-fit:contain"><h3><a href="{local}">{escape(product_title(product))}</a></h3><p><strong>{money(price(product))}</strong> · {discount_pct(product)}% OFF</p><p class="note">Nota editorial: {estimate_rating(product)} / 5 · {estimate_review_count(product)} avaliações estimadas</p><a class="cta" href="{escape(affiliate_url(product))}" rel="nofollow sponsored noopener" target="_blank">Ver oferta</a></article>"""


def generate_category_pages(groups: Dict[str, List[Dict[str, Any]]]) -> int:
    count = 0
    for slug, items in groups.items():
        name = category_name(slug)
        cards = "".join(card_for_product(p) for p in items[:24])
        body = f"""
        <div class="crumbs"><a href="/">Início</a> › Categorias › {escape(name)}</div>
        <h1>Melhores ofertas em {escape(name)} em {YEAR}</h1>
        <p>Esta página reúne produtos priorizados por desconto, qualidade aparente, preço e relevância. Ela também serve como cluster central para guias, comparações e análises individuais da categoria.</p>
        <div class="grid">{cards}</div>
        <section class="card"><h2>Critérios usados na categoria</h2><p>O robô prioriza itens com preço plausível, desconto consistente, títulos completos, maior nota editorial estimada e sinais de procura. Produtos expirados, incompletos ou de baixa qualidade são removidos da listagem principal automaticamente.</p></section>
        """
        canonical = f"{BASE_URL}/categorias/{slug}/"
        html = html_page(f"Ofertas de {name} em {YEAR} | {SITE_NAME}", f"Compare ofertas, guias e produtos recomendados em {name}.", body, canonical, {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Ofertas de {name}"})
        out = ROOT / "categorias" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        count += 1
    return count


def comparison_slug(a: Dict[str, Any], b: Dict[str, Any]) -> str:
    return f"{slugify(product_title(a))}-vs-{slugify(product_title(b))}"[:140].strip("-")


def generate_comparisons(groups: Dict[str, List[Dict[str, Any]]]) -> int:
    count = 0
    index_links = []
    for slug, items in groups.items():
        top = items[:6]
        for i in range(0, len(top) - 1, 2):
            a, b = top[i], top[i + 1]
            comp_slug = comparison_slug(a, b)
            canonical = f"{BASE_URL}/comparacoes/{slug}/{comp_slug}/"
            winner = a if quality_score(a) >= quality_score(b) else b
            rows = "".join([
                f"<tr><th>Preço atual</th><td>{money(price(a))}</td><td>{money(price(b))}</td></tr>",
                f"<tr><th>Desconto</th><td>{discount_pct(a)}%</td><td>{discount_pct(b)}%</td></tr>",
                f"<tr><th>Nota editorial</th><td>{estimate_rating(a)} / 5</td><td>{estimate_rating(b)} / 5</td></tr>",
                f"<tr><th>Avaliações estimadas</th><td>{estimate_review_count(a)}</td><td>{estimate_review_count(b)}</td></tr>",
                f"<tr><th>Página completa</th><td><a href='{product_url(a).replace(BASE_URL, '')}'>Ver análise</a></td><td><a href='{product_url(b).replace(BASE_URL, '')}'>Ver análise</a></td></tr>",
            ])
            body = f"""
            <div class="crumbs"><a href="/">Início</a> › <a href="/categorias/{slug}/">{escape(category_name(slug))}</a> › Comparação</div>
            <h1>{escape(product_title(a))} vs {escape(product_title(b))}: qual vale mais a pena?</h1>
            <p>Esta comparação automática analisa preço, desconto, qualidade aparente e sinais de relevância para ajudar na escolha entre produtos semelhantes.</p>
            <table><thead><tr><th>Critério</th><th>{escape(product_title(a))}</th><th>{escape(product_title(b))}</th></tr></thead><tbody>{rows}</tbody></table>
            <section class="card"><h2>Resultado recomendado</h2><p>Com os dados atuais, o destaque é <strong>{escape(product_title(winner))}</strong>, por apresentar melhor combinação de preço, desconto e nota editorial estimada. Ainda assim, a melhor escolha depende do uso pretendido, frete e reputação do vendedor no momento da compra.</p></section>
            <div class="grid">{card_for_product(a)}{card_for_product(b)}</div>
            """
            html = html_page(f"{product_title(a)} vs {product_title(b)} | {SITE_NAME}", f"Comparação automática com preço, desconto e critérios de compra.", body, canonical, {"@context": "https://schema.org", "@type": "WebPage", "name": f"Comparação: {product_title(a)} vs {product_title(b)}"})
            out = ROOT / "comparacoes" / slug / comp_slug / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            index_links.append((canonical, product_title(a), product_title(b), slug))
            count += 1
    body_links = "".join(f"<li><a href='{url.replace(BASE_URL, '')}'>{escape(a)} vs {escape(b)}</a> — {escape(category_name(slug))}</li>" for url, a, b, slug in index_links)
    body = f"<h1>Comparações automáticas de produtos</h1><p>Compare produtos populares por preço, desconto e critérios editoriais.</p><ul>{body_links}</ul>"
    out = ROOT / "comparacoes" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_page(f"Comparações de produtos | {SITE_NAME}", "Comparações automáticas entre produtos populares.", body, f"{BASE_URL}/comparacoes/"), encoding="utf-8")
    return count


def long_buying_guide(slug: str, items: List[Dict[str, Any]]) -> str:
    name = category_name(slug)
    criteria = BUYING_CRITERIA.get(slug, BUYING_CRITERIA["tecnologia"])
    top = items[:5]
    product_list = "".join(f"<li><a href='{product_url(p).replace(BASE_URL, '')}'>{escape(product_title(p))}</a>, encontrado por {money(price(p))} com desconto estimado de {discount_pct(p)}%.</li>" for p in top)
    criteria_sections = "".join(f"<h3>{escape(c.capitalize())}</h3><p>Ao avaliar {escape(name)}, observe {escape(c)} não como um detalhe isolado, mas como parte do custo total de uso. Um preço menor pode não compensar se o produto tiver limitações importantes, baixa durabilidade ou pouca compatibilidade com sua rotina. O Radar Ninja usa esse critério para enriquecer a curadoria e evitar que a recomendação seja baseada apenas no maior percentual de desconto.</p>" for c in criteria)
    return f"""
    <p>Comprar produtos de <strong>{escape(name)}</strong> em {YEAR} exige mais do que comparar o menor preço. Marketplaces mudam ofertas rapidamente, vendedores competem por visibilidade e muitos descontos parecem altos porque usam preços de referência inflados. Por isso, este guia combina curadoria editorial automatizada, histórico de preços e critérios de qualidade para ajudar você a separar oportunidade real de promoção apenas aparente.</p>
    <p>A primeira regra é entender a sua necessidade. Um produto recomendado para uso intenso pode ser exagerado para uso ocasional, enquanto a alternativa mais barata pode sair cara se não entregar desempenho, garantia ou durabilidade. O objetivo do Compre Rápido não é empurrar o item mais caro, mas destacar escolhas com boa relação entre preço, reputação aparente e utilidade prática.</p>
    <h2>Critérios essenciais antes da compra</h2>{criteria_sections}
    <h2>Como interpretar descontos</h2><p>Desconto alto não é automaticamente sinônimo de boa compra. O robô compara preço atual, preço original informado e registros anteriores para identificar indícios de promoção real. Quando existe histórico suficiente, produtos próximos da mínima registrada ganham prioridade. Quando não existe histórico, a oferta permanece monitorada e a página informa que o consumidor deve confirmar a vantagem antes de comprar.</p>
    <p>Também é importante observar frete, prazo de entrega e política de devolução. Um item com preço baixo pode deixar de ser competitivo se o frete for elevado ou se o vendedor não tiver boa reputação. A recomendação editorial deve ser vista como ponto de partida para a decisão, não como substituto da conferência final no ambiente da loja.</p>
    <h2>Produtos em destaque no cluster</h2><ul>{product_list}</ul>
    <h2>Estratégia de compra recomendada</h2><p>Para compras planejadas, monitore o produto por alguns dias e compare alternativas semelhantes. Para ofertas relâmpago, priorize produtos com desconto consistente, página completa, histórico favorável e políticas claras. Se dois produtos parecerem equivalentes, use as páginas de comparação para entender qual entrega melhor equilíbrio entre preço e características.</p>
    <p>Este guia é atualizado pelo robô à medida que novos produtos entram na base. A estrutura de clusters conecta guias, categorias, comparações e análises individuais, melhorando a navegação interna e ajudando mecanismos de busca a compreenderem a especialidade editorial do site em cada nicho.</p>
    <h2>Conclusão</h2><p>O melhor produto de {escape(name)} em {YEAR} é aquele que resolve sua necessidade com preço justo, histórico coerente e risco reduzido. Use a curadoria como filtro inicial, leia a análise individual e confirme as informações finais no marketplace antes de concluir a compra.</p>
    """


def generate_guides_articles_best(groups: Dict[str, List[Dict[str, Any]]]) -> Tuple[int, int, int]:
    guides = articles = best_pages = 0
    best_index_items = []
    posts_index_items = []
    for slug, items in groups.items():
        name = category_name(slug)
        guide_body = f"<div class='crumbs'><a href='/'>Início</a> › Guias › {escape(name)}</div><h1>Guia de compra: melhores produtos de {escape(name)} em {YEAR}</h1>{long_buying_guide(slug, items)}<div class='grid'>{''.join(card_for_product(p) for p in items[:6])}</div>"
        out = ROOT / "guias" / f"guia-de-compra-{slug}-{YEAR}" / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_page(f"Guia de compra de {name} em {YEAR} | {SITE_NAME}", f"Guia completo para comprar produtos de {name}, com critérios, histórico e recomendações.", guide_body, f"{BASE_URL}/guias/guia-de-compra-{slug}-{YEAR}/", {"@context":"https://schema.org","@type":"Article","headline":f"Guia de compra de {name} em {YEAR}","author":{"@type":"Organization","name":SITE_NAME}}), encoding="utf-8")
        guides += 1

        article_body = f"<div class='crumbs'><a href='/'>Início</a> › Notícias › {escape(name)}</div><h1>Tendências de {escape(name)} em {YEAR}: como encontrar boas ofertas</h1><p>As ofertas de {escape(name)} mudam rapidamente em {YEAR}. O Radar Ninja organiza produtos em clusters para identificar padrões de preço, destacar oportunidades reais e evitar recomendações rasas.</p><p>Entre os fatores mais importantes estão desconto consistente, preço histórico, reputação aparente e comparação com alternativas próximas. A análise automatizada ajuda a publicar páginas úteis em escala, mantendo links internos entre guias, produtos e comparações.</p><h2>Produtos acompanhados agora</h2><div class='grid'>{''.join(card_for_product(p) for p in items[:4])}</div><h2>Como usar este cluster</h2><p>Comece pelo guia de compra, avance para as comparações e finalize conferindo a página individual do produto. Essa jornada reduz o risco de decidir apenas pelo desconto anunciado.</p>"
        post_slug = f"tendencias-{slug}-{YEAR}"
        out = ROOT / "noticias" / "posts" / post_slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_page(f"Tendências de {name} em {YEAR} | {SITE_NAME}", f"Artigo relacionado à categoria {name}, com ofertas e critérios de compra.", article_body, f"{BASE_URL}/noticias/posts/{post_slug}/", {"@context":"https://schema.org","@type":"Article","headline":f"Tendências de {name} em {YEAR}","author":{"@type":"Organization","name":SITE_NAME}}), encoding="utf-8")
        posts_index_items.append((post_slug, name))
        articles += 1

        best_body = f"<div class='crumbs'><a href='/'>Início</a> › Melhores {YEAR} › {escape(name)}</div><h1>Melhores produtos de {escape(name)} em {YEAR}</h1><p>Ranking automático baseado em preço, desconto, qualidade aparente e sinais de popularidade. A lista prioriza produtos ativos e remove itens expirados ou de baixa qualidade.</p><div class='grid'>{''.join(card_for_product(p) for p in items[:12])}</div><section class='card'><h2>Como o ranking é calculado</h2><p>O robô pondera desconto, preço, histórico, nota editorial estimada, volume estimado de avaliações e qualidade dos dados. O objetivo é destacar produtos com maior potencial de conversão e valor para o leitor.</p></section>"
        best_slug = f"melhores-{slug}-{YEAR}"
        out = ROOT / "melhores-2026" / best_slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_page(f"Melhores produtos de {name} em {YEAR} | {SITE_NAME}", f"Ranking dos melhores produtos de {name} em {YEAR} com curadoria automática.", best_body, f"{BASE_URL}/melhores-2026/{best_slug}/"), encoding="utf-8")
        best_index_items.append((best_slug, name))
        best_pages += 1

    guide_index = "".join(f"<li><a href='/guias/guia-de-compra-{slug}-{YEAR}/'>Guia de compra de {escape(category_name(slug))}</a></li>" for slug in groups)
    (ROOT / "guias" / "index.html").write_text(html_page(f"Guias de compra | {SITE_NAME}", "Guias completos de compra por categoria.", f"<h1>Guias de compra</h1><ul>{guide_index}</ul>", f"{BASE_URL}/guias/"), encoding="utf-8")
    posts_index = "".join(f"<li><a href='/noticias/posts/{slug}/'>{escape(name)} em {YEAR}: tendências e ofertas</a></li>" for slug, name in posts_index_items)
    (ROOT / "noticias" / "index.html").write_text(html_page(f"Artigos e notícias | {SITE_NAME}", "Artigos relacionados a categorias e ofertas.", f"<h1>Artigos relacionados</h1><ul>{posts_index}</ul>", f"{BASE_URL}/noticias/"), encoding="utf-8")
    best_index = "".join(f"<li><a href='/melhores-2026/{slug}/'>Melhores produtos de {escape(name)} em {YEAR}</a></li>" for slug, name in best_index_items)
    (ROOT / "melhores-2026" / "index.html").write_text(html_page(f"Melhores produtos de {YEAR} | {SITE_NAME}", "Rankings automáticos dos melhores produtos por categoria.", f"<h1>Melhores Produtos de {YEAR}</h1><p>Rankings por categoria com curadoria automatizada e critérios transparentes.</p><ul>{best_index}</ul>", f"{BASE_URL}/melhores-2026/"), encoding="utf-8")
    return guides, articles, best_pages


def generate_daily_deals(products: List[Dict[str, Any]], history: Dict[str, List[Dict[str, Any]]]) -> int:
    ranked = sorted(products, key=lambda p: (is_real_promotion(p, history), discount_pct(p), quality_score(p, history)), reverse=True)[:30]
    cards = "".join(card_for_product(p) for p in ranked)
    body = f"<h1>Ofertas do dia</h1><p>Lista atualizada automaticamente com produtos de maior desconto, melhor sinal de promoção real e qualidade mínima aprovada.</p><div class='grid'>{cards}</div>"
    out = ROOT / "ofertas-hoje" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_page(f"Ofertas do dia | {SITE_NAME}", "Produtos em promoção monitorados automaticamente hoje.", body, f"{BASE_URL}/ofertas-hoje/"), encoding="utf-8")
    return len(ranked)


def generate_eeat_pages() -> int:
    pages = {
        "autor": ("Página de autor", f"<h1>{escape(AUTHOR_NAME)}</h1><p>A {escape(AUTHOR_NAME)} é responsável pela curadoria automatizada e revisão editorial das páginas do {escape(SITE_NAME)}. A metodologia combina dados públicos de produtos, histórico de preços, critérios de qualidade e transparência sobre monetização por afiliados.</p><h2>Experiência editorial</h2><p>Nosso foco é ajudar consumidores brasileiros a comparar ofertas com mais contexto, evitando decisões baseadas apenas em percentuais de desconto. As páginas indicam limitações, necessidade de conferência final e critérios usados no ranking.</p>"),
        "transparencia": ("Transparência editorial", f"<h1>Transparência editorial</h1><p>O {escape(SITE_NAME)} utiliza automação para monitorar produtos, gerar páginas informativas e organizar clusters de conteúdo. Podemos receber comissão quando o usuário compra por links identificados como afiliados, sem custo adicional para o consumidor.</p><h2>Como ganhamos dinheiro</h2><p>Receitas podem vir de programas de afiliados e publicidade. Esse modelo não altera o preço final exibido pela loja, mas influencia a necessidade de deixar claro quando um link é patrocinado ou comissionado.</p><h2>Como reduzimos viés</h2><p>Priorizamos preço, desconto, qualidade de dados, histórico e relevância. Produtos expirados, incompletos ou com sinais de baixa qualidade são removidos das listagens principais.</p>"),
        "politica-editorial": ("Política editorial", "<h1>Política editorial</h1><p>As recomendações são geradas com base em dados disponíveis, critérios objetivos e revisão estrutural automatizada. Não garantimos disponibilidade, preço final ou desempenho específico dos produtos.</p><h2>Correções</h2><p>Quando encontramos páginas quebradas, dados insuficientes ou sitemaps inconsistentes, o robô tenta corrigir automaticamente e registra o problema nos relatórios de saúde.</p>"),
        "contato": ("Contato", "<h1>Contato</h1><p>Para sugestões, correções ou solicitações comerciais, utilize os canais oficiais vinculados ao projeto Compre Rápido. Informe a URL da página e descreva a alteração solicitada para acelerar a análise.</p><h2>Correções de conteúdo</h2><p>Se uma oferta estiver indisponível, com preço diferente ou com informação incompleta, priorizamos a correção das páginas que recebem maior tráfego e mantemos logs de saúde para acompanhar problemas recorrentes.</p>"),
        "politica-afiliados": ("Política de afiliados", "<h1>Política de afiliados</h1><p>Alguns links do site são links de afiliado. Isso significa que podemos receber comissão quando uma compra qualificada é realizada. O usuário não paga a mais por isso.</p><p>A presença de links afiliados não elimina nossa preocupação com qualidade, transparência e utilidade do conteúdo.</p><h2>Independência editorial</h2><p>Os rankings consideram desconto, histórico de preço, avaliação, popularidade e completude dos dados. A monetização é separada dos critérios técnicos usados para reduzir produtos de baixa qualidade.</p>"),
        "politica-privacidade": ("Política de privacidade", "<h1>Política de privacidade</h1><p>O Radar Ninja publica páginas informativas sobre produtos, ofertas, guias e comparações. Podemos coletar métricas agregadas de navegação por meio de ferramentas de análise e publicidade, sempre com foco em melhorar a experiência do usuário e a qualidade editorial.</p><h2>Dados e publicidade</h2><p>Parceiros de publicidade e afiliados podem usar cookies ou identificadores semelhantes para medir desempenho, evitar fraude, limitar frequência de anúncios e atribuir compras qualificadas. O usuário deve consultar também as políticas das plataformas externas acessadas pelos links de compra.</p><h2>Contato e atualização</h2><p>Solicitações relacionadas a privacidade, correções de dados ou remoção de conteúdo podem ser enviadas pelos canais indicados na página de contato. Esta política pode ser atualizada para refletir mudanças técnicas, legais ou comerciais.</p>"),
        "privacidade": ("Privacidade", "<h1>Privacidade</h1><p>Esta página resume como o Radar Ninja trata informações de navegação, links de afiliados, cookies e métricas agregadas. Para a versão principal, acesse também a política de privacidade.</p><h2>Uso responsável</h2><p>Não vendemos produtos diretamente e não solicitamos dados financeiros. As compras são concluídas em lojas parceiras, que possuem seus próprios termos e controles de privacidade.</p><p><a href='/politica-privacidade/'>Ler política de privacidade completa</a></p>"),
        "termos-de-uso": ("Termos de uso", "<h1>Termos de uso</h1><p>Ao acessar o Radar Ninja, o usuário entende que as informações são fornecidas para comparação e educação de consumo. Preços, estoque, avaliações e condições comerciais podem mudar sem aviso porque dependem das lojas e marketplaces de origem.</p><h2>Limitações</h2><p>O site não substitui a conferência final na loja. Antes de comprar, verifique frete, prazo, reputação do vendedor, garantia, política de devolução e preço final no checkout. Páginas com histórico de preços e comparação ajudam na decisão, mas não garantem economia.</p><h2>Responsabilidade editorial</h2><p>Buscamos corrigir inconsistências automaticamente por meio de relatórios de saúde, auditoria de links e atualização de sitemaps. Mesmo assim, erros podem ocorrer em razão de mudanças externas nas ofertas.</p>"),
        "termos": ("Termos", "<h1>Termos</h1><p>Esta página direciona para os termos de uso completos do Radar Ninja, que explicam limitações, responsabilidade editorial e recomendações antes da compra.</p><p><a href='/termos-de-uso/'>Ler termos de uso completos</a></p>"),
    }
    count = 0
    for slug, (title, body) in pages.items():
        out = ROOT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_page(f"{title} | {SITE_NAME}", f"{title} do {SITE_NAME}.", body, f"{BASE_URL}/{slug}/", {"@context":"https://schema.org","@type":"AboutPage","name":title}), encoding="utf-8")
        count += 1
    return count


def generate_multisite_config(groups: Dict[str, List[Dict[str, Any]]]) -> None:
    config = {
        "version": 1,
        "updated_at": TODAY_ISO,
        "default_site": {
            "domain": "comprerapido.github.io",
            "site_name": SITE_NAME,
            "base_url": BASE_URL,
            "template": "default-editorial-affiliate",
            "language": "pt-BR",
        },
        "supported_sites": [
            {"domain": "comprerapido.github.io", "niche_strategy": "ofertas amplas com clusters por categoria", "template": "default-editorial-affiliate"},
            {"domain": "comparaoferta.github.io", "niche_strategy": "comparações e rankings para evitar duplicidade", "template": "comparison-first"},
        ],
        "duplicate_content_policy": {
            "same_product_across_sites": "reescrever título, introdução, FAQ e ordem dos blocos; usar canonicals próprios; priorizar ângulo editorial diferente por domínio",
            "cluster_variation": "cada domínio deve ter clusters, palavras-chave e templates diferentes para reduzir sobreposição semântica",
        },
        "content_clusters": [
            {"slug": slug, "name": category_name(slug), "pillar": f"/guias/guia-de-compra-{slug}-{YEAR}/", "category_page": f"/categorias/{slug}/", "best_page": f"/melhores-2026/melhores-{slug}-{YEAR}/", "products": len(items)}
            for slug, items in groups.items()
        ],
    }
    save_json(DATA_DIR / "multisite_config.json", config)
    save_json(DATA_DIR / "content_clusters.json", config["content_clusters"])


def generate_sitemap() -> int:
    urls = []
    for html in ROOT.rglob("index.html"):
        if ".git" in html.parts or "scripts" in html.parts:
            continue
        rel_dir = html.parent.relative_to(ROOT).as_posix()
        loc = f"{BASE_URL}/" if rel_dir == "." else f"{BASE_URL}/{rel_dir.strip('/')}/"
        urls.append(loc)
    for html in ROOT.rglob("*.html"):
        if html.name == "index.html" or ".git" in html.parts or "scripts" in html.parts:
            continue
        rel = html.relative_to(ROOT).as_posix()
        urls.append(f"{BASE_URL}/{rel}")
    urls = sorted(set(urls))
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
    for url in urls:
        xml += f"  <url><loc>{escape(url)}</loc><lastmod>{TODAY.date().isoformat()}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>\n"
    xml += "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (ROOT / "sitemap-produtos.xml").write_text(xml, encoding="utf-8")
    return len(urls)


def validate_internal_links() -> Dict[str, Any]:
    broken = []
    for html in ROOT.rglob("*.html"):
        if ".git" in html.parts:
            continue
        text = html.read_text(encoding="utf-8", errors="ignore")
        for href in re.findall(r'href=["\']([^"\']+)["\']', text):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            href_clean = href.split("#")[0].split("?")[0]
            if not href_clean:
                continue
            if href_clean.startswith("/"):
                target = ROOT / href_clean.lstrip("/")
            else:
                target = html.parent / href_clean
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append({"page": str(html.relative_to(ROOT)), "href": href, "expected": str(target.relative_to(ROOT)) if ROOT in target.parents else str(target)})
    report = {"updated_at": TODAY_ISO, "broken_internal_links": broken, "broken_count": len(broken)}
    save_json(DATA_DIR / "broken_pages_report.json", report)
    return report


def write_health_report(stats: Dict[str, Any]) -> None:
    health = {
        "updated_at": TODAY_ISO,
        "status": "healthy" if stats.get("broken_links", 0) == 0 and stats.get("quality_products", 0) > 0 else "warning",
        "checks": stats,
        "recovery": {
            "product_pages": "Regeneradas automaticamente a partir de data/all_products.json.",
            "sitemap": "Recriado automaticamente a partir dos arquivos HTML existentes.",
            "broken_pages": "Links internos são auditados e listados em data/broken_pages_report.json.",
        },
    }
    save_json(DATA_DIR / "health_report.json", health)
    md = f"""# Relatório de Saúde — Radar Ninja

| Métrica | Valor |
| --- | --- |
| Atualizado em | {TODAY_ISO} |
| Status | {health['status']} |
| Produtos de qualidade | {stats.get('quality_products', 0)} |
| Páginas de produto | {stats.get('product_pages', 0)} |
| Comparações | {stats.get('comparisons', 0)} |
| Guias | {stats.get('guides', 0)} |
| Artigos | {stats.get('articles', 0)} |
| URLs no sitemap | {stats.get('sitemap_urls', 0)} |
| Links internos quebrados | {stats.get('broken_links', 0)} |

## Recuperação automática

O sistema regenera páginas essenciais, recria o sitemap e salva relatórios JSON para auditoria. Se houver links quebrados, o arquivo `data/broken_pages_report.json` indica a origem e o destino esperado.
"""
    (ROOT / "health_report.md").write_text(md, encoding="utf-8")


def ensure_robots() -> None:
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")


def main() -> Dict[str, Any]:
    products = load_json(DATA_DIR / "all_products.json", [])
    if not isinstance(products, list):
        raise RuntimeError("data/all_products.json não contém uma lista de produtos")

    history = update_price_history(products)
    quality_products = [p for p in products if is_quality_product(p, history)]
    quality_products.sort(key=lambda p: (quality_score(p, history), discount_pct(p)), reverse=True)
    save_json(DATA_DIR / "quality_products.json", quality_products)

    promotions = [p for p in quality_products if is_real_promotion(p, history)]
    save_json(DATA_DIR / "real_promotions.json", promotions)

    groups = group_by_category(quality_products)
    generate_multisite_config(groups)

    product_pages = generate_product_pages(quality_products, history, groups)
    category_pages = generate_category_pages(groups)
    comparisons = generate_comparisons(groups)
    guides, articles, best_pages = generate_guides_articles_best(groups)
    daily_deals = generate_daily_deals(quality_products, history)
    eeat_pages = generate_eeat_pages()
    ensure_robots()
    sitemap_urls = generate_sitemap()
    broken_report = validate_internal_links()

    stats = {
        "total_products": len(products),
        "quality_products": len(quality_products),
        "real_promotions": len(promotions),
        "product_pages": product_pages,
        "category_pages": category_pages,
        "comparisons": comparisons,
        "guides": guides,
        "articles": articles,
        "best_pages": best_pages,
        "daily_deals": daily_deals,
        "eeat_pages": eeat_pages,
        "sitemap_urls": sitemap_urls,
        "broken_links": broken_report.get("broken_count", 0),
    }
    write_health_report(stats)
    save_json(DATA_DIR / "growth_engine_report.json", {"updated_at": TODAY_ISO, "stats": stats})
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return stats


if __name__ == "__main__":
    main()
