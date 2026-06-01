import json
import os
from logger import logger

INPUT_FILE = "data/products/offers.json"
TEMPLATE_FILE = "templates/homepage.html"
OUTPUT_FILE = "index.html"

def format_price(value) -> str:
    try:
        return f"{float(value or 0):.2f}"
    except:
        return "0.00"

def build_homepage():
    logger.info("🏠 Construindo homepage com imagens REAIS e estáveis...")
    
    if not os.path.exists(INPUT_FILE) or not os.path.exists(TEMPLATE_FILE):
        logger.error("Arquivos necessários não encontrados!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    if not products:
        logger.error("Nenhum produto encontrado no JSON!")
        return

    # Hero Section
    hero = products[0]
    hero_html = f'''
    <div class="hero-product">
        <div class="hero-badge" style="background: #ef4444; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 10px; display: inline-block;">MENOR PREÇO DA HISTÓRIA ↑</div>
        <img src="{hero.get("image")}" alt="{hero.get("title")}" style="background: white; padding: 15px; border-radius: 12px; width: 100%; max-width: 300px; display: block; margin: 0 auto;">
        <div class="hero-price" style="font-size: 32px; font-weight: 800; margin-top: 15px;">R$ {format_price(hero.get("price"))}</div>
    </div>
    '''

    # Featured Grid
    grid_html = ""
    for p in products:
        grid_html += f'''
        <div class="card" style="background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; position: relative; display: flex; flex-direction: column;">
            <div class="card-discount" style="position: absolute; top: 10px; right: 10px; background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">↓ {p.get("custom_discount_pct")}%</div>
            <div class="card-img" style="height: 160px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                <img src="{p.get("image")}" alt="{p.get("title")}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
            </div>
            <h3 style="font-size: 14px; margin: 0 0 10px 0; height: 40px; overflow: hidden; color: #1e293b;">{p.get("title")}</h3>
            <div class="price-row" style="margin-top: auto;">
                <span style="font-size: 18px; font-weight: 800; color: #059669;">R$ {format_price(p.get("price"))}</span>
            </div>
            <a href="{p.get("custom_affiliate_url")}" target="_blank" style="display: block; background: #059669; color: white; text-align: center; padding: 10px; border-radius: 8px; margin-top: 15px; font-weight: bold; text-decoration: none; font-size: 14px;">Ver oferta no Mercado Livre</a>
        </div>
        '''

    # Substituições Finais
    content = template
    content = content.replace("{{seo.title}}", "Radar Ninja — As Melhores Ofertas do Mercado Livre Hoje")
    content = content.replace("{{meta.description}}", "Economize com o Radar Ninja. Monitoramos os menores preços do Mercado Livre em celulares, games e muito mais.")
    content = content.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", grid_html)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info("✅ Homepage reconstruída com sucesso.")

if __name__ == "__main__":
    build_homepage()
