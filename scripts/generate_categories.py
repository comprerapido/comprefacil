import os
import json
import unicodedata
from logger import logger

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

    # Mapeamento para garantir que tanto "celular" quanto "celulares" funcionem para a mesma pasta física
    CAT_SLUG_MAP = {
        "celular": "celulares",
        "games": "games",
        "tv": "tv-e-video",
        "moda": "moda"
    }

    categories_config = {cat["id"]: cat["nome"] for cat in config["categorias"]}

    for cat_id, cat_name in categories_config.items():
        target_slug = CAT_SLUG_MAP.get(cat_id, cat_id)
        
        # Filtra produtos aceitando o ID original ou o Slug de destino
        cat_products = [p for p in products if p.get("custom_category_slug") in [cat_id, target_slug]]
        
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
                affiliate_url = p.get("custom_affiliate_url") or p.get("permalink")
                
                products_html += f'''
                <div class="product-card">
                    <span class="badge">↓ {discount}% OFF</span>
                    <div class="product-img">
                        <img src="{image}" alt="{p_name}" loading="lazy" onerror="this.src='https://placehold.co/400x400?text=Imagem+Indisponivel'">
                    </div>
                    <div class="product-info">
                        <span class="category-tag">{cat_name.upper()}</span>
                        <h3 style="font-size: 14px; height: 40px; overflow: hidden; margin: 10px 0;">{p_name[:60]}...</h3>
                        <div class="price" style="margin-bottom: 10px;">
                            <span class="old-price" style="text-decoration: line-through; color: #94a3b8; font-size: 12px;">R$ {old_price:.2f}</span><br>
                            <span class="current-price" style="font-size: 20px; font-weight: 800; color: #28a745;">R$ {price:.2f}</span>
                        </div>
                        <a href="{affiliate_url}" class="btn" target="_blank" style="display: block; background: #28a745; color: white; text-align: center; padding: 10px; border-radius: 6px; font-weight: bold;">Ver Oferta no ML</a>
                    </div>
                </div>
                '''

        content = template.replace("{{category.name}}", cat_name)
        content = content.replace("{{category.products}}", products_html)
        content = content.replace("{{seo.title}}", f"Melhores Ofertas de {cat_name} | Radar Ninja")
        content = content.replace("{{meta.description}}", f"Confira as melhores ofertas de {cat_name} garimpadas pelo Radar Ninja.")
        
        # Criar a pasta com o slug de destino (ex: celulares)
        os.makedirs(f"categorias/{target_slug}", exist_ok=True)
        with open(f"categorias/{target_slug}/index.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        # Criar redirecionamento ou cópia para o slug alternativo se for diferente (ex: celular -> celulares)
        if target_slug != cat_id:
            os.makedirs(f"categorias/{cat_id}", exist_ok=True)
            with open(f"categorias/{cat_id}/index.html", "w", encoding="utf-8") as f:
                f.write(content)

        logger.info(f"✓ Categoria {cat_name} gerada em /categorias/{target_slug}/")

if __name__ == "__main__":
    generate_categories()
