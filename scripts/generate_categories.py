import os
import json
import unicodedata
from logger import logger

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace(" ", "-")
    return "".join(c for c in text if c.isalnum() or c == "-")

def generate_categories():
    logger.info("🎨 Iniciando geração de categorias premium...")
    
    db_path = "data/products/offers.json"
    template_path = "templates/category_template.html"
    config_path = "data/ROBO4_CONFIG.json"
    
    if not os.path.exists(db_path) or not os.path.exists(template_path) or not os.path.exists(config_path):
        logger.error("Arquivos necessários não encontrados!")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    categories_config = {cat["id"]: cat["nome"] for cat in config["categorias"]}

    for cat_slug, cat_name in categories_config.items():
        # Filtra produtos pela categoria correta
        cat_products = [p for p in products if p.get("custom_category_slug") in [cat_slug, cat_slug + "s"]]
        
        products_html = ""
        if not cat_products:
            products_html = "<p style='grid-column: 1/-1; text-align: center; padding: 50px;'>Em breve novas ofertas para esta categoria!</p>"
        else:
            for p in cat_products:
                p_name = p.get("name") or p.get("title") or ""
                discount = p.get("custom_discount_pct", 0)
                price = p.get("price", 0)
                old_price = p.get("originalPrice") or p.get("original_price") or price
                image = p.get("image") or p.get("thumbnail") or ""
                # Usa o link de afiliado pronto do dado
                affiliate_url = p.get("custom_affiliate_url") or p.get("permalink")
                
                products_html += f'''
                <div class="product-card">
                    <span class="badge">↓ {discount}% OFF</span>
                    <div class="product-img">
                        <img src="{image}" alt="{p_name}" loading="lazy">
                    </div>
                    <div class="product-info">
                        <span class="category-tag">{cat_name.upper()}</span>
                        <h3>{p_name[:60]}...</h3>
                        <div class="price">
                            <span class="old-price">R$ {old_price:.2f}</span>
                            <span class="current-price">R$ {price:.2f}</span>
                        </div>
                        <a href="{affiliate_url}" class="btn" target="_blank">Ver Oferta no ML</a>
                    </div>
                </div>
                '''

        content = template.replace("{{category.name}}", cat_name)
        content = content.replace("{{category.products}}", products_html)
        content = content.replace("{{seo.title}}", f"Melhores Ofertas de {cat_name} | Radar Ninja")
        content = content.replace("{{meta.description}}", f"Confira as melhores ofertas de {cat_name} garimpadas pelo Radar Ninja.")
        content = content.replace("{{canonical.url}}", f"https://comprerapido.github.io/categorias/{cat_slug}/")

        os.makedirs(f"categorias/{cat_slug}", exist_ok=True)
        with open(f"categorias/{cat_slug}/index.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"✓ Categoria {cat_name} gerada com {len(cat_products)} produtos.")

if __name__ == "__main__":
    generate_categories()
