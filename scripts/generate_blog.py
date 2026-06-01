import json
import os
from datetime import datetime
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def generate_blog_post(product, category, post_index):
    """Gera um post de blog para um produto"""
    
    slug = slugify(product['title'])
    
    affiliate_link = product['permalink']
    if '?' in affiliate_link:
        affiliate_link += "&utm_source=comprerapido&utm_medium=blog"
    else:
        affiliate_link += "?utm_source=comprerapido&utm_medium=blog"
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Review: {product['title']} - Compra Rápido</title>
    <meta name="description" content="Review detalhado do {product['title']}. Confira características, preço e se vale a pena comprar.">
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header>
        <h1>Compra Rápido</h1>
    </header>
    
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
            <h1>Review: {product['title']}</h1>
            <p class="meta">Postado em {datetime.now().strftime('%d/%m/%Y')} na categoria {category['nome']}</p>
            
            <img src="{product['thumbnail']}" alt="{product['title']}">
            
            <p>Hoje vamos analisar o <strong>{product['title']}</strong>. Se você está procurando por ofertas em {category['nome']}, este produto é uma das melhores opções do mercado atualmente.</p>
            
            <h2>Principais Características</h2>
            <ul>
                <li><strong>Preço Competitivo:</strong> R$ {product['price']:.2f}</li>
                <li><strong>Categoria:</strong> {category['nome']}</li>
                <li><strong>Condição:</strong> {product['condition'].upper()}</li>
                <li><strong>Disponibilidade:</strong> Em estoque</li>
            </ul>
            
            <h2>Por que Comprar?</h2>
            <p>Nossa equipe de especialistas avaliou este item e recomenda a compra se você busca:</p>
            <ul>
                <li>Custo-benefício excelente</li>
                <li>Qualidade garantida</li>
                <li>Entrega rápida</li>
                <li>Melhor preço do mercado</li>
            </ul>
            
            <h2>Conclusão</h2>
            <p>Se você está buscando uma ótima oportunidade de compra em {category['nome']}, este produto é altamente recomendado. Não perca esta oferta!</p>
            
            <a href="{affiliate_link}" class="btn">Ver Oferta Completa no Mercado Livre</a>
        </article>
    </main>
    
    <footer>
        <p>&copy; 2026 Compra Rápido - O seu guia de compras inteligente.</p>
        <nav>
            <a href="/privacidade">Privacidade</a>
            <a href="/termos">Termos de Uso</a>
            <a href="/sobre">Quem Somos</a>
            <a href="/contato">Fale Conosco</a>
        </nav>
    </footer>
</body>
</html>
"""
    
    return slug, html

def generate_blog_index(all_posts):
    """Gera página de índice do blog"""
    
    posts_html = ""
    for post in all_posts:
        posts_html += f"""
        <div class="blog-card">
            <div class="blog-card-content">
                <h3><a href="/noticias/posts/{post['slug']}/">{post['title']}</a></h3>
                <p class="blog-meta">📅 {post['date']} • 📂 {post['category']}</p>
                <p class="blog-excerpt">{post['excerpt']}</p>
                <a href="/noticias/posts/{post['slug']}/" class="btn">Ler Mais</a>
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog - Compra Rápido</title>
    <meta name="description" content="Blog com reviews e análises de produtos do Mercado Livre">
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header>
        <h1>Compra Rápido</h1>
    </header>
    
    <nav>
        <a href="/">Início</a>
        <a href="/categorias/tv">TV e Vídeo</a>
        <a href="/categorias/games">Games</a>
        <a href="/categorias/celular">Smartphones</a>
        <a href="/categorias/moda">Moda</a>
        <a href="/noticias">📰 Blog</a>
    </nav>
    
    <main>
        <section class="intro">
            <h2>📰 Últimas Notícias e Reviews</h2>
            <p>Acompanhe nossas análises detalhadas dos melhores produtos do Mercado Livre</p>
        </section>
        
        <div class="blog-list">
            {posts_html}
        </div>
    </main>
    
    <footer>
        <p>&copy; 2026 Compra Rápido - O seu guia de compras inteligente.</p>
        <nav>
            <a href="/privacidade">Privacidade</a>
            <a href="/termos">Termos de Uso</a>
            <a href="/sobre">Quem Somos</a>
            <a href="/contato">Fale Conosco</a>
        </nav>
    </footer>
</body>
</html>
"""
    
    return html

def main():
    """Executa o script principal"""
    config_path = os.path.join(os.path.dirname(__file__), '../data/ROBO3_CONFIG.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    all_posts = []
    posts_dir = os.path.join(os.path.dirname(__file__), '../noticias/posts')
    
    # Limpar posts antigos para evitar 404 de links órfãos
    import shutil
    if os.path.exists(posts_dir):
        shutil.rmtree(posts_dir)
    os.makedirs(posts_dir, exist_ok=True)
    
    for cat in config['categorias']:
        products_file = os.path.join(os.path.dirname(__file__), f"../data/products_{cat['id']}.json")
        if not os.path.exists(products_file):
            continue
        
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        for idx, product in enumerate(products[:3]):
            slug, html = generate_blog_post(product, cat, idx)
            post_dir = os.path.join(posts_dir, slug)
            os.makedirs(post_dir, exist_ok=True)
            with open(os.path.join(post_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)
            
            all_posts.append({
                'slug': slug,
                'title': f"Review: {product['title']}",
                'date': datetime.now().strftime('%d/%m/%Y'),
                'category': cat['nome'],
                'excerpt': f"Análise detalhada do {product['title']}. Confira características e preço."
            })
    
    blog_index_html = generate_blog_index(all_posts)
    blog_dir = os.path.join(os.path.dirname(__file__), '../noticias')
    os.makedirs(blog_dir, exist_ok=True)
    with open(os.path.join(blog_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(blog_index_html)
    
    print(f"✓ Blog gerado com {len(all_posts)} posts")

if __name__ == "__main__":
    main()
