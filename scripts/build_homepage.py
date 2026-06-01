import json
import os
import requests
import base64
from logger import logger

INPUT_FILE = "data/products/offers.json"
TEMPLATE_FILE = "templates/homepage.html"
OUTPUT_FILE = "index.html"

def get_as_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode('utf-8')
            mime = response.headers.get('Content-Type', 'image/jpeg')
            return f"data:{mime};base64,{encoded}"
    except:
        pass
    return url

def format_price(value) -> str:
    try:
        return f"{float(value or 0):.2f}"
    except:
        return "0.00"

def build_homepage():
    logger.info("🏠 Construindo homepage com imagens embutidas...")
    
    if not os.path.exists(INPUT_FILE) or not os.path.exists(TEMPLATE_FILE):
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    products = sorted(products, key=lambda x: x.get("custom_discount_pct", 0), reverse=True)

    # Hero Section - Converter para Base64 para garantir exibição
    hero = products[0]
    hero_img = get_as_base64(hero.get("image"))
    
    hero_html = f'''
    <div class="hero-product">
        <div class="hero-badge" style="background: #ef4444; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 10px; display: inline-block;">MENOR PREÇO DA HISTÓRIA ↑</div>
        <img src="{hero_img}" alt="{hero.get("title")}" style="background: white; padding: 15px; border-radius: 12px; width: 100%; max-width: 300px; display: block; margin: 0 auto;">
        <div class="hero-price" style="font-size: 32px; font-weight: 800; margin-top: 15px;">R$ {format_price(hero.get("price"))}</div>
    </div>
    '''

    # Featured Grid
    grid_html = ""
    for p in products[1:9]:
        p_img = get_as_base64(p.get("image"))
        grid_html += f'''
        <div class="card" style="background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div class="card-img" style="height: 160px; display: flex; align-items: center; justify-content: center;">
                <img src="{p_img}" alt="{p.get("title")}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
            </div>
            <h3 style="font-size: 14px; margin: 10px 0; height: 40px; overflow: hidden;">{p.get("title")[:50]}...</h3>
            <div class="price-row">
                <span style="font-size: 18px; font-weight: 800; color: #28a745;">R$ {format_price(p.get("price"))}</span>
            </div>
            <a href="{p.get("custom_affiliate_url")}" target="_blank" style="display: block; background: #28a745; color: white; text-align: center; padding: 8px; border-radius: 6px; margin-top: 15px; font-weight: bold; text-decoration: none;">Ver oferta</a>
        </div>
        '''

    content = template.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", grid_html)
    content = content.replace("{{table_rows}}", "") # Limpar tabela por enquanto
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info("✅ Homepage pronta.")

if __name__ == "__main__":
    build_homepage()
