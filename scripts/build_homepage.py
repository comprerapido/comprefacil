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
    logger.info("🏠 Iniciando construção da homepage premium...")
    
    if not os.path.exists(INPUT_FILE) or not os.path.exists(TEMPLATE_FILE):
        logger.error("Arquivos necessários não encontrados!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    if not products:
        logger.warning("Nenhum produto para exibir.")
        return

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Ordena por maior desconto
    products = sorted(products, key=lambda x: x.get("custom_discount_pct", 0), reverse=True)

    # Hero Section
    hero = products[0]
    hero_img = hero.get("image") or hero.get("thumbnail") or ""
    hero_html = f'''
    <div class="hero-product">
        <div class="hero-badge" style="background: #ef4444; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 10px; display: inline-block;">MENOR PREÇO DA HISTÓRIA ↑</div>
        <img src="{hero_img}" alt="{hero.get("title")}" style="background: white; padding: 15px; border-radius: 12px; width: 100%; max-width: 300px; display: block; margin: 0 auto;" onerror="this.src='https://placehold.co/400x400?text=Imagem+Indisponivel'">
        <div class="hero-price" style="font-size: 32px; font-weight: 800; margin-top: 15px;">R$ {format_price(hero.get("price"))}</div>
    </div>
    '''

    # Featured Grid
    grid_html = ""
    for p in products[1:9]:
        p_img = p.get("image") or p.get("thumbnail") or ""
        grid_html += f'''
        <div class="card" style="position: relative; background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0;">
            <span class="card-discount" style="position: absolute; top: 10px; right: 10px; background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">↓ {p.get("custom_discount_pct")}%</span>
            <div class="card-img" style="height: 160px; display: flex; align-items: center; justify-content: center; padding: 10px;">
                <img src="{p_img}" alt="{p.get("title")}" style="max-width: 100%; max-height: 100%; object-fit: contain;" onerror="this.src='https://placehold.co/400x400?text=Imagem+Indisponivel'">
            </div>
            <h3 style="font-size: 14px; margin: 10px 0; height: 40px; overflow: hidden;">{p.get("title")[:50]}...</h3>
            <div class="price-row">
                <span style="text-decoration: line-through; color: #94a3b8; font-size: 12px;">R$ {format_price(p.get("originalPrice"))}</span><br>
                <span style="font-size: 18px; font-weight: 800; color: #28a745;">R$ {format_price(p.get("price"))}</span>
            </div>
            <a href="{p.get("custom_affiliate_url")}" target="_blank" style="display: block; border: 1px solid #28a745; color: #28a745; text-align: center; padding: 8px; border-radius: 6px; margin-top: 15px; font-weight: bold; text-decoration: none;">Ver oferta</a>
        </div>
        '''

    # Table Rows
    table_html = ""
    for p in products[9:20]:
        table_html += f'''
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 15px; font-size: 13px;">{p.get("title")[:40]}...</td>
            <td style="padding: 15px; font-weight: bold;">R$ {format_price(p.get("price"))}</td>
            <td style="padding: 15px; color: #28a745; font-weight: bold;">{p.get("custom_discount_pct")}% OFF</td>
            <td style="padding: 15px;"><a href="{p.get("custom_affiliate_url")}" target="_blank" style="color: #28a745; font-weight: bold; text-decoration: none;">LOJA →</a></td>
        </tr>
        '''

    content = template.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", grid_html)
    content = content.replace("{{table_rows}}", table_html)
    content = content.replace("{{seo.title}}", "Radar Ninja — As Melhores Ofertas do Mercado Livre Hoje")
    content = content.replace("{{meta.description}}", "Economize com o Radar Ninja. Menor preço da história em celulares, games e mais.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info("✅ Homepage atualizada com sucesso.")

if __name__ == "__main__":
    build_homepage()
