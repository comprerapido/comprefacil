import os
import json
import unicodedata
from datetime import datetime
from logger import logger

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace(" ", "-")
    return "".join(c for c in text if c.isalnum() or c == "-")

def get_proxy_image(url):
    if not url: return ""
    return f"https://wsrv.nl/?url={url}&w=800&h=600&fit=contain&output=jpg"

def generate_blog():
    with open("data/products/offers.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    
    os.makedirs("noticias/posts", exist_ok=True)
    
    for p in products:
        name = p.get("title")
        slug = slugify(name)
        image = get_proxy_image(p.get("image"))
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>{name} - Radar Ninja</title>
            <link rel="stylesheet" href="../../assets/css/style.css">
        </head>
        <body>
            <div class="container" style="max-width: 800px; margin: 40px auto; padding: 20px; background: white; border-radius: 12px;">
                <a href="/noticias/">← Voltar ao Blog</a>
                <h1 style="margin: 20px 0;">{name}</h1>
                <img src="{image}" style="width: 100%; border-radius: 12px; margin-bottom: 20px;">
                <div style="background: #f0fdf4; padding: 20px; border-radius: 12px; text-align: center; border: 2px dashed #28a745;">
                    <h2 style="color: #28a745;">R$ {p['price']:.2f}</h2>
                    <a href="{p['custom_affiliate_url']}" style="display: inline-block; background: #28a745; color: white; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; margin-top: 10px;" target="_blank">APROVEITAR OFERTA NO ML</a>
                </div>
                <div style="margin-top: 30px; line-height: 1.6;">
                    <p>Análise completa do {name}. Este produto está com um excelente desconto hoje...</p>
                </div>
            </div>
        </body>
        </html>
        """
        with open(f"noticias/posts/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
    logger.info("✅ Blog com proxy gerado.")

if __name__ == "__main__":
    generate_blog()
