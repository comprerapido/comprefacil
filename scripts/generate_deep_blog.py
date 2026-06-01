import os
import json
import unicodedata
from datetime import datetime
from logger import logger
from openai import OpenAI

client = OpenAI()

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace(" ", "-")
    return "".join(c for c in text if c.isalnum() or c == "-")

def affiliate_url(product: dict) -> str:
    url = product.get("custom_affiliate_url") or product.get("permalink") or ""
    if not url: return "https://www.mercadolivre.com.br"
    if "matt_tool=vendas0nline" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}matt_tool=vendas0nline"
    return url

def get_valid_image(product: dict) -> str:
    img = (product.get("image") or product.get("thumbnail") or "").split("?")[0]
    if not img or "http" not in img:
        return "https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp"
    return img.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg")

def generate_long_content_with_ai(product):
    name = product.get("name") or product.get("title")
    cat = (product.get("custom_category_slug") or "OFERTAS").upper()
    price = f"R$ {product.get('price', 0):.2f}"
    discount = f"{product.get('custom_discount_pct', 0)}%"

    prompt = f"""
    Gere um artigo de blog PROFUNDO e EXTENSO (mínimo de 1000 palavras) sobre o produto "{name}".
    Foco em AdSense e SEO. Use HTML. Estrutura: Introdução, Ficha Técnica, Review de Uso, Comparativo, FAQ, Veredito.
    O texto deve ser muito rico e informativo.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": "Você é um redator sênior de reviews técnicos."}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<p>Review detalhado para {name}. O produto está com {discount} de desconto.</p>"

def generate_blog():
    db_path = "data/products/offers.json"
    if not os.path.exists(db_path): return
        
    with open(db_path, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    if not products: return

    os.makedirs("noticias/posts", exist_ok=True)
    posts_meta = []
    
    # Gerar para os 5 mais recentes
    for p in products[-5:]:
        name = p.get("name") or p.get("title")
        slug = slugify(name)
        content = generate_long_content_with_ai(p)
        image = get_valid_image(p)
        url = affiliate_url(p)
        price = p.get("price", 0)
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Review Mestre | Radar Ninja</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.8; margin: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .post {{ background: white; padding: 40px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
        .cta-box {{ background: #f0fdf4; border: 2px solid #22c55e; padding: 30px; border-radius: 16px; text-align: center; margin: 30px 0; }}
        .btn {{ background: #22c55e; color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-weight: 700; display: inline-block; }}
        img {{ width: 100%; border-radius: 16px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <article class="post">
            <h1>{name}</h1>
            <img src="{image}" alt="{name}">
            
            <div class="cta-box">
                <h3>🔥 Melhor Preço Encontrado!</h3>
                <p style="font-size: 24px; font-weight: 800; color: #15803d;">R$ {price:.2f}</p>
                <a href="{url}" class="btn" target="_blank">VER OFERTA NO MERCADO LIVRE</a>
            </div>

            <div class="content">{content}</div>

            <div class="cta-box" style="background: #eff6ff; border-color: #3b82f6;">
                <h3>✅ Veredito Final</h3>
                <p>O {name} é uma escolha sólida. Aproveite enquanto o estoque dura!</p>
                <a href="{url}" class="btn" style="background: #3b82f6;" target="_blank">COMPRAR AGORA COM DESCONTO</a>
            </div>
        </article>
    </div>
</body>
</html>"""
        
        with open(f"noticias/posts/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        posts_meta.append({
            "title": name,
            "url": f"posts/{slug}.html",
            "excerpt": f"Análise profunda do {name}. Vale a pena comprar?",
            "tagLabel": "REVIEW",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "readTime": "10 min"
        })
        
    with open("noticias/index.html", "w", encoding="utf-8") as f:
        # Simplificando para o teste, o template completo já foi definido antes
        f.write(json.dumps(posts_meta))

if __name__ == "__main__":
    generate_blog()
