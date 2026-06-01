import os
import json
from logger import logger

CAT_SLUG_MAP = {
    "celular": "celulares",
    "games": "games",
    "tv": "tv-e-video",
    "moda": "moda"
}

def generate_categories():
    logger.info("🎨 Gerando categorias com imagens locais...")
    with open("data/products/offers.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    with open("templates/category_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    for cat_id, target_slug in CAT_SLUG_MAP.items():
        cat_products = [p for p in products if p.get("custom_category_slug") in [cat_id, target_slug]]
        
        html = ""
        for p in cat_products:
            p_img = p.get("image_local") or p.get("image")
            # Ajustar caminho para subpasta
            if p_img.startswith("/"):
                p_img = "../../" + p_img.lstrip("/")
                
            html += f'''
            <div class="product-card">
                <div class="product-img">
                    <img src="{p_img}" alt="{p["title"]}">
                </div>
                <h3>{p["title"]}</h3>
                <p class="price">R$ {p["price"]:.2f}</p>
                <a href="{p["custom_affiliate_url"]}" class="btn" target="_blank">VER OFERTA</a>
            </div>
            '''
        
        content = template.replace("{{category.name}}", target_slug.upper())
        content = content.replace("{{category.products}}", html)
        
        os.makedirs(f"categorias/{target_slug}", exist_ok=True)
        with open(f"categorias/{target_slug}/index.html", "w", encoding="utf-8") as f:
            f.write(content)
            
if __name__ == "__main__":
    generate_categories()
