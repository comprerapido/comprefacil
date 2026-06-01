import json
import os
import re
import unicodedata
from urllib.parse import urlparse
from logger import logger

BASE_URL = "https://comprerapido.github.io/"
DEFAULT_INPUT = "data/products/offers.json"
DEFAULT_TEMPLATE = "templates/homepage.html"
DEFAULT_OUTPUT = "index.html"
CONFIG_PATH = "data/ROBO3_CONFIG.json"

def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    return re.sub(r"\s+", " ", value).strip()

def format_price(value) -> str:
    try:
        return f"{float(value or 0):.2f}"
    except:
        return "0.00"

def affiliate_url(product: dict) -> str:
    url = product.get("custom_affiliate_url") or product.get("permalink") or ""
    if not url:
        return "https://www.mercadolivre.com.br"
    # Garante o parâmetro de afiliado
    if "matt_tool=vendas0nline" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}matt_tool=vendas0nline"
    return url

def get_valid_image(product: dict) -> str:
    img = (product.get("image") or product.get("thumbnail") or "").split("?")[0]
    if not img or "http" not in img:
        return "https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp" # Fallback seguro
    return img.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg")

def build_homepage(input_path: str, template_path: str, output_path: str) -> None:
    logger.info("Gerando homepage Mestre com visual Radar de Preços...")

    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return

    products = []
    if os.path.exists(input_path):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as exc:
            logger.error(f"Erro ao carregar {input_path}: {exc}")

    # Filtrar produtos sem imagem ou link
    products = [p for p in products if p.get("permalink") and (p.get("image") or p.get("thumbnail"))]
    
    if not products:
        logger.warning("Nenhum produto válido encontrado.")
        return

    # Inverter para que o mais recente seja o primeiro (Ninja Choice)
    products = products[::-1]

    # 1. Hero Section (Ninja Choice)
    hero = products[0]
    hero_name = hero.get("name") or hero.get("title")
    hero_img = get_valid_image(hero)
    hero_price = hero.get("price", 0)
    hero_old = hero.get("originalPrice") or hero.get("original_price") or hero_price
    
    hero_html = f"""
    <div class="hero-product">
        <img src="{hero_img}" alt="{hero_name}">
        <div style="text-align: center;">
            <div style="color: var(--primary); font-size: 24px; font-weight: 800; margin-bottom: 5px;">R$ {format_price(hero_price)}</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 14px;">Menor preço da história! ↑</div>
        </div>
    </div>
    """

    # 2. Featured Grid (Top 8)
    featured_html = ""
    for p in products[1:9]:
        name = p.get("name") or p.get("title")
        img = get_valid_image(p)
        price = p.get("price", 0)
        old_price = p.get("originalPrice") or p.get("original_price") or price
        discount = p.get("custom_discount_pct", 0)
        cat = (p.get("custom_category_slug") or "Oferta").upper()
        
        featured_html += f"""
        <div class="card">
            <span class="card-discount">↓ {discount}%</span>
            <div class="card-img">
                <img src="{img}" alt="{name}" loading="lazy">
            </div>
            <div class="card-cat">{cat}</div>
            <h3 class="card-title">{name}</h3>
            <div class="card-prices">
                <span class="card-price">R$ {format_price(price)}</span>
                <span class="card-old">R$ {format_price(old_price)}</span>
            </div>
            <a href="{affiliate_url(p)}" class="card-btn" target="_blank" rel="noopener noreferrer">Ver oferta</a>
        </div>
        """

    # 3. Table Rows (Próximos 10)
    table_html = ""
    for p in products[9:19]:
        name = p.get("name") or p.get("title")
        img = get_valid_image(p)
        price = p.get("price", 0)
        discount = p.get("custom_discount_pct", 0)
        
        table_html += f"""
        <tr>
            <td>
                <div class="td-product">
                    <img src="{img}" alt="{name}">
                    <span>{name[:50]}...</span>
                </div>
            </td>
            <td class="td-price">R$ {format_price(price)}</td>
            <td class="td-price">R$ {format_price(price)}</td>
            <td class="td-discount">↓ {discount}%</td>
            <td><a href="{affiliate_url(p)}" class="btn-sm" target="_blank" rel="noopener noreferrer">Ver oferta</a></td>
        </tr>
        """

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", featured_html)
    content = content.replace("{{table_rows}}", table_html)
    content = content.replace("{{seo.title}}", "Radar Ninja — O Menor Preço da História")
    content = content.replace("{{meta.description}}", "Monitoramos os preços para você economizar de verdade.")
    content = content.replace("{{canonical.url}}", BASE_URL)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Homepage gerada com sucesso: {output_path}")

if __name__ == "__main__":
    build_homepage(DEFAULT_INPUT, DEFAULT_TEMPLATE, DEFAULT_OUTPUT)
