import json
import os
import re
import unicodedata
from logger import logger

BASE_URL = "https://comprerapido.github.io/"
INPUT_FILE = "data/products/offers.json"
TEMPLATE_FILE = "templates/homepage.html"
OUTPUT_FILE = "index.html"

def format_price(value) -> str:
    return f"{float(value or 0):.2f}"

def build_homepage():
    logger.info("🏠 Iniciando construção da homepage dinâmica...")
    
    if not os.path.exists(INPUT_FILE):
        logger.error("Arquivo de ofertas não encontrado!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    if not products:
        logger.warning("Nenhum produto para exibir.")
        return

    # Ordena por maior desconto para os destaques
    products = sorted(products, key=lambda x: x.get("custom_discount_pct", 0), reverse=True)

    # Hero Section (Produto com maior desconto)
    hero = products[0]
    hero_name = hero.get("name") or hero.get("title")
    hero_img = hero.get("image") or hero.get("thumbnail")
    hero_price = hero.get("price", 0)
    hero_old = hero.get("originalPrice") or hero.get("original_price") or hero_price
    hero_discount = hero.get("custom_discount_pct", 0)
    hero_link = hero.get("custom_affiliate_url") or hero.get("permalink")

    hero_html = f"""
    <div class="hero-product">
        <div class="hero-badge">MENOR PREÇO DA HISTÓRIA ↑</div>
        <img src="{hero_img}" alt="{hero_name}" loading="lazy">
        <div class="hero-price">R$ {format_price(hero_price)}</div>
    </div>
    """

    # Featured Grid (Próximos 6 produtos)
    grid_html = ""
    for p in products[1:7]:
        p_name = p.get("name") or p.get("title")
        p_img = p.get("image") or p.get("thumbnail")
        p_price = p.get("price", 0)
        p_old = p.get("originalPrice") or p.get("original_price") or p_price
        p_discount = p.get("custom_discount_pct", 0)
        p_link = p.get("custom_affiliate_url") or p.get("permalink")
        p_cat = (p.get("custom_category_slug") or "OFERTA").upper()

        grid_html += f"""
        <div class="card">
            <span class="card-discount">↓ {p_discount}%</span>
            <div class="card-img">
                <img src="{p_img}" alt="{p_name}" loading="lazy">
            </div>
            <div class="card-cat">{p_cat}</div>
            <h3 class="card-title">{p_name[:60]}...</h3>
            <div class="card-price-row">
                <span class="card-old">R$ {format_price(p_old)}</span>
                <span class="card-price">R$ {format_price(p_price)}</span>
            </div>
            <a href="{p_link}" class="card-btn" target="_blank">Ver oferta</a>
        </div>
        """

    # Table Rows (Restante dos produtos)
    table_html = ""
    for p in products[7:27]:
        p_name = p.get("name") or p.get("title")
        p_img = p.get("image") or p.get("thumbnail")
        p_price = p.get("price", 0)
        p_old = p.get("originalPrice") or p.get("original_price") or p_price
        p_discount = p.get("custom_discount_pct", 0)
        p_link = p.get("custom_affiliate_url") or p.get("permalink")

        table_html += f"""
        <tr>
            <td>
                <div class="td-product">
                    <img src="{p_img}" alt="{p_name}" loading="lazy">
                    <span>{p_name[:50]}...</span>
                </div>
            </td>
            <td class="td-price">R$ {format_price(p_price)}</td>
            <td class="td-old">R$ {format_price(p_old)}</td>
            <td class="td-discount">{p_discount}% OFF</td>
            <td><a href="{p_link}" class="btn-sm" target="_blank">Ver Oferta</a></td>
        </tr>
        """

    if not os.path.exists(TEMPLATE_FILE):
        logger.error("Template não encontrado!")
        return

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", grid_html)
    content = content.replace("{{table_rows}}", table_html)
    content = content.replace("{{seo.title}}", "Radar Ninja — As Melhores Ofertas do Mercado Livre Hoje")
    content = content.replace("{{meta.description}}", "Economize com o Radar Ninja. Menor preço da história em celulares, games e mais.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"✅ Homepage atualizada com {len(products)} produtos.")

if __name__ == "__main__":
    build_homepage()
