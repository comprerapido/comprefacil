import json
import os
import random
from datetime import datetime
from logger import logger

def generate_blog_posts():
    db_path = "data/database/all_products.json"
    if not os.path.exists(db_path):
        logger.error(f"Erro: Banco de dados não encontrado em {db_path}")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # Pegar os produtos mais recentes e com melhores descontos
    products = sorted(products, key=lambda x: x.get('custom_discount_pct', 0), reverse=True)[:12]
    
    os.makedirs("noticias/posts", exist_ok=True)
    posts_meta = []
    
    for product in products:
        slug = product['name'].lower().replace(" ", "-").replace("\"", "").replace("'", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        
        # Selos dinâmicos
        badges = [
            ('<span class="badge-history">🏆 MENOR PREÇO DA HISTÓRIA</span>', 'Menor Preço da História'),
            ('<span class="badge badge-down">🔥 BAIXOU AGORA</span>', 'Baixou Agora'),
            ('<span class="badge badge-best">⭐ MAIS VENDIDO</span>', 'Mais Vendido'),
            ('<span class="badge badge-new">✨ NOVIDADE NO SITE</span>', 'Novidade')
        ]
        # Priorizar Menor Preço da História para os top descontos
        if product.get('custom_discount_pct', 0) > 40:
            badge_html, badge_text = badges[0]
        else:
            badge_html, badge_text = random.choice(badges[1:])
        
        post_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Review: {product['name']} - Compra Rápido</title>
    <link rel="stylesheet" href="../../assets/main.css">
</head>
<body>
    <header><h1>Compra Rápido</h1></header>
    <nav>
        <a href="/">Início</a>
        <a href="/categorias/tv">TV e Vídeo</a>
        <a href="/categorias/games">Games</a>
        <a href="/categorias/celular">Smartphones</a>
        <a href="/categorias/moda">Moda</a>
        <a href="/noticias">📰 Blog</a>
    </nav>
    <main>
        <article class="blog-post">
            <div style="text-align:center; margin-bottom: 20px;">{badge_html}</div>
            <h1>{product['name']} - Vale a pena?</h1>
            <div class="meta">Postado em {datetime.now().strftime('%d/%m/%Y')} • 📂 {product['custom_category_slug'].upper()}</div>
            <img src="{product['image']}" alt="{product['name']}" style="display:block; margin: 0 auto; max-width: 300px;">
            <div style="background:#f0f9ff; padding:20px; border-radius:10px; margin: 20px 0; border-left: 5px solid #00ccff;">
                <h3 style="margin-top:0;">💥 Oferta Imperdível!</h3>
                <p>O <strong>{product['name']}</strong> atingiu hoje o valor de <strong>R$ {product['price']:.2f}</strong>. Isso representa um desconto real de <strong>{product['custom_discount_pct']}%</strong> em relação ao preço original de R$ {product['originalPrice']:.2f}.</p>
                <div style="text-align:center; margin-top:15px;">
                    <a href="{product['custom_affiliate_url']}" class="buy-button" target="_blank">VER PREÇO NO MERCADO LIVRE</a>
                </div>
            </div>
            <h2>Análise Técnica</h2>
            <p>Nossa equipe detectou que este produto é uma das maiores <strong>novidades</strong> da semana na categoria de {product['custom_category_slug']}. Se você busca qualidade e o <strong>menor preço</strong>, esta é a oportunidade ideal.</p>
        </article>
    </main>
    <footer><p>&copy; 2026 Compra Rápido</p></footer>
</body>
</html>"""
        
        post_path = f"noticias/posts/{slug}.html"
        with open(post_path, "w", encoding="utf-8") as f:
            f.write(post_content)
            
        posts_meta.append({
            "title": product['name'],
            "slug": slug,
            "category": product['custom_category_slug'],
            "date": datetime.now().strftime('%d/%m/%Y'),
            "image": product['image'],
            "badge": badge_html
        })
        
    # Atualizar index do blog
    blog_index = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog - Compra Rápido</title>
    <link rel="stylesheet" href="../assets/main.css">
</head>
<body>
    <header><h1>Compra Rápido</h1></header>
    <nav>
        <a href="/">Início</a>
        <a href="/categorias/tv">TV e Vídeo</a>
        <a href="/categorias/games">Games</a>
        <a href="/categorias/celular">Smartphones</a>
        <a href="/categorias/moda">Moda</a>
        <a href="/noticias">📰 Blog</a>
    </nav>
    <main>
        <h2>📰 Novidades e Menores Preços</h2>
        <div class="blog-list">
            {''.join([f'''
            <div class="blog-card">
                <div style="padding:10px; text-align:center;">{p['badge']}</div>
                <img src="{p['image']}" alt="{p['title']}">
                <div class="blog-card-content">
                    <h3><a href="/noticias/posts/{p['slug']}.html">{p['title']}</a></h3>
                    <div class="blog-meta">📅 {p['date']} • 📂 {p['category'].upper()}</div>
                    <a href="/noticias/posts/{p['slug']}.html" class="btn">Ver Análise</a>
                </div>
            </div>
            ''' for p in posts_meta])}
        </div>
    </main>
    <footer><p>&copy; 2026 Compra Rápido</p></footer>
</body>
</html>"""
    with open("noticias/index.html", "w", encoding="utf-8") as f:
        f.write(blog_index)

if __name__ == "__main__":
    generate_blog_posts()
