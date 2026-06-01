import os
import json
import unicodedata
from datetime import datetime
from logger import logger
from openai import OpenAI

# Inicializa o cliente OpenAI
client = OpenAI()

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace(" ", "-")
    return "".join(c for c in text if c.isalnum() or c == "-")

def generate_long_content_with_ai(product):
    name = product.get("name") or product.get("title")
    cat = (product.get("custom_category_slug") or "OFERTAS").upper()
    price = f"R$ {product.get('price', 0):.2f}"
    old_price = f"R$ {product.get('originalPrice', 0) or product.get('original_price', 0):.2f}"
    discount = f"{product.get('custom_discount_pct', 0)}%"

    prompt = f"""
    Gere um artigo de blog PROFUNDO e EXTENSO (mínimo de 1000 palavras) sobre o produto "{name}" da categoria "{cat}".
    Este artigo deve seguir as diretrizes de E-E-A-T (Experiência, Especialidade, Autoridade e Confiança) do Google AdSense.

    Estrutura obrigatória do artigo:
    1.  **Introdução Detalhada:** Contexto do mercado de {cat} em 2026, por que o {name} é relevante e análise do desconto real de {discount}.
    2.  **Ficha Técnica Comentada:** Explicação detalhada de cada especificação técnica, o que elas significam na prática para o usuário.
    3.  **Experiência de Uso:** Como é utilizar o produto no dia a dia, pontos positivos e negativos honestos.
    4.  **Análise de Custo-Benefício:** Comparação profunda com o preço histórico e se o valor de {price} é realmente o melhor momento de compra.
    5.  **Comparativo com Concorrentes:** Crie uma seção comparando com pelo menos 3 concorrentes diretos (use nomes reais se souber, ou fictícios plausíveis).
    6.  **FAQ Extenso:** Pelo menos 5 perguntas e respostas detalhadas sobre o produto.
    7.  **Guia de Compra:** Dicas para o consumidor não cair em ciladas ao comprar {cat}.
    8.  **Veredito Final:** Conclusão baseada em autoridade técnica.

    Use HTML para formatar o conteúdo. Use <h2> e <h3> para títulos, <p> para parágrafos longos e informativos, <ul> para listas e <strong> para termos chave.
    IMPORTANTE: O texto deve ser rico, útil e muito longo para passar de 1000 palavras.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um redator sênior especializado em reviews de tecnologia e consumo, focado em criar o conteúdo mais completo da internet para o Google AdSense."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo com IA para {name}: {e}")
        return f"<p>Ocorreu um erro ao gerar o review detalhado para {name}. No entanto, confirmamos que o produto está com um excelente desconto de {discount} e é uma das melhores opções na categoria {cat} hoje.</p>"

def generate_blog():
    db_path = "data/products/offers.json"
    if not os.path.exists(db_path):
        logger.error("Arquivo de ofertas não encontrado!")
        return
        
    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    if not products:
        logger.warning("Nenhum produto encontrado para gerar blog.")
        return

    os.makedirs("noticias/posts", exist_ok=True)
    posts_meta = []
    
    # Gerar blog para os 5 produtos mais recentes
    top_products = products[:5]
    
    for p in top_products:
        name = p.get("name") or p.get("title")
        slug = slugify(name)
        content = generate_long_content_with_ai(p)
        image = (p.get("image") or p.get("thumbnail") or "").split("?")[0].replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg")
        affiliate_url = p.get("custom_affiliate_url") or p.get("permalink")
        price = p.get("price", 0)
        old_price = p.get("originalPrice", 0) or p.get("original_price", 0)
        discount = p.get("custom_discount_pct", 0)
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Review Completa Mestre | Radar Ninja</title>
    <meta name="description" content="Análise profunda e honesta do {name}. Vale a pena comprar? Confira o review completo com mais de 1000 palavras.">
    <link rel="stylesheet" href="../../assets/css/style.css">
    <style>
        :root {{ --primary: #6200ea; --secondary: #ffab00; --dark: #121212; --light: #f5f5f7; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--light); color: var(--dark); line-height: 1.8; }}
        .post-container {{ max-width: 900px; margin: 40px auto; padding: 40px; background: white; border-radius: 30px; box-shadow: 0 10px 50px rgba(0,0,0,0.05); }}
        .post-header {{ text-align: center; margin-bottom: 40px; }}
        .post-header h1 {{ font-size: 36px; font-weight: 900; color: var(--dark); margin-bottom: 20px; }}
        .hero-img {{ width: 100%; max-height: 500px; object-fit: contain; border-radius: 20px; margin-bottom: 30px; background: #fff; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
        .affiliate-box {{ background: linear-gradient(135deg, #6200ea 0%, #311b92 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; margin: 30px 0; }}
        .affiliate-box p {{ font-size: 20px; margin-bottom: 15px; }}
        .affiliate-box .price {{ font-size: 36px; font-weight: 900; color: var(--secondary); margin-bottom: 20px; display: block; }}
        .btn-buy {{ background: var(--secondary); color: var(--dark); padding: 18px 40px; border-radius: 50px; text-decoration: none; font-weight: 900; font-size: 20px; display: inline-block; transition: 0.3s; }}
        .btn-buy:hover {{ transform: scale(1.05); box-shadow: 0 10px 30px rgba(255,171,0,0.4); }}
        .post-content h2 {{ color: var(--primary); margin: 40px 0 20px; font-size: 28px; border-left: 5px solid var(--secondary); padding-left: 15px; }}
        .post-content p {{ margin-bottom: 25px; font-size: 18px; color: #444; }}
        .footer-cta {{ background: #f3e5f5; padding: 40px; border-radius: 20px; text-align: center; margin-top: 60px; border: 2px dashed var(--primary); }}
    </style>
</head>
<body>
    <header style="background: var(--dark); padding: 20px 0; text-align: center;">
        <a href="/" style="color: white; text-decoration: none; font-size: 24px; font-weight: 900;">RADAR <span style="color: var(--secondary);">NINJA</span></a>
    </header>
    <main class="container">
        <article class="post-container">
            <div class="post-header">
                <h1>{name} - Vale a pena comprar? Análise Completa 2026</h1>
                <img src="{image}" alt="{name}" class="hero-img">
                <div class="affiliate-box">
                    <p>🔥 OFERTA NINJA DETECTADA!</p>
                    <span class="price">R$ {price:.2f}</span>
                    <a href="{affiliate_url}" class="btn-buy" target="_blank" rel="noopener noreferrer">APROVEITAR AGORA NO MERCADO LIVRE 🚀</a>
                </div>
            </div>

            <div class="post-content">
                {content}
            </div>

            <div class="footer-cta">
                <h3 style="color: var(--primary); margin-bottom: 15px;">Ainda com dúvida?</h3>
                <p>O <strong>{name}</strong> é um dos itens mais vendidos da semana e o preço de <strong>R$ {price:.2f}</strong> é um dos menores dos últimos meses.</p>
                <a href="{affiliate_url}" class="btn-buy" target="_blank" rel="noopener noreferrer">GARANTIR MEU PRODUTO COM DESCONTO 🛒</a>
            </div>
        </article>
    </main>
    <footer style="text-align: center; padding: 40px; color: #888;">
        <p>© 2026 Radar Ninja - Review Mestre Independente</p>
    </footer>
</body>
</html>"""
        
        with open(f"noticias/posts/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        posts_meta.append({
            "title": name,
            "url": f"posts/{slug}.html",
            "excerpt": f"Análise profunda do {name}. Vale a pena comprar com {discount}% de desconto? Confira o veredito mestre.",
            "tagLabel": (p.get("custom_category_slug") or "OFERTA").upper(),
            "date": datetime.now().strftime("%d/%m/%Y"),
            "readTime": "12 min",
            "icon": "💎"
        })
        
    template_path = "templates/blog_premium.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        blog_html = template.replace("{{NEWS_JSON}}", json.dumps(posts_meta, indent=2, ensure_ascii=False))
        with open("noticias/index.html", "w", encoding="utf-8") as f:
            f.write(blog_html)
    
    logger.info(f"✅ Blog Mestre regenerado com {len(top_products)} artigos profundos.")

if __name__ == "__main__":
    generate_blog()
