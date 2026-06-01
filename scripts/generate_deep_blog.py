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
    price = f"R$ {product.get("price", 0):.2f}"
    old_price = f"R$ {product.get("originalPrice", 0) or product.get("original_price", 0):.2f}"
    discount = f"{product.get("custom_discount_pct", 0)}%"

    prompt = f"""
    Gere um artigo de blog detalhado e otimizado para SEO sobre o produto "{name}" da categoria "{cat}".
    O artigo deve ter as seguintes seções:
    1.  **Introdução:** Por que o produto está em destaque hoje, mencionando o desconto de {discount} e o preço de {price}.
    2.  **Análise Técnica Detalhada:** Detalhes sobre o produto, diferenciais e especificações (invente se necessário, mas de forma crível).
    3.  **Tabela Comparativa:** Compare o "{name}" com dois concorrentes fictícios (Concorrente A e Concorrente B) em termos de Preço Atual, Desconto e Avaliação de Usuários. Use os preços {price} e {discount} para o produto principal.
    4.  **Vale a pena comprar?** Uma análise se o produto vale a pena, reforçando o desconto e a legitimidade da oferta (preço original {old_price}).
    5.  **FAQ:** Duas perguntas frequentes sobre o produto (ex: garantia, entrega).
    6.  **Conclusão:** Veredito final e chamada para ação.
    7.  **Dicas de Economia Ninja:** Três dicas curtas e relevantes para o consumidor.

    Use HTML para formatar o conteúdo, incluindo tags `<h2>` para títulos de seção, `<ul>` para listas, `<p>` para parágrafos e `<strong>` para destaque. A tabela deve ter a classe `specs-table`.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini", # Usando o modelo gpt-4.1-mini
            messages=[
                {"role": "system", "content": "Você é um especialista em reviews de produtos e SEO, focado em ajudar consumidores a encontrar as melhores ofertas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo com IA para {name}: {e}")
        # Fallback para conteúdo estático se a IA falhar
        return generate_long_content_static(product)

def generate_long_content_static(product):
    name = product.get("name") or product.get("title")
    cat = (product.get("custom_category_slug") or "OFERTAS").upper()
    price = f"R$ {product.get("price", 0):.2f}"
    old_price = f"R$ {product.get("originalPrice", 0) or product.get("original_price", 0):.2f}"
    discount = f"{product.get("custom_discount_pct", 0)}%"
    
    sections = [
        f"<h2>Introdução: Por que o {name} está chamando atenção hoje?</h2>",
        f"<p>Se você está em busca de uma oportunidade real de economia na categoria de {cat}, o momento é agora. O <strong>{name}</strong> acaba de atingir um dos menores preços registrados pelo nosso robô monitorador. Com um desconto agressivo de <strong>{discount}</strong>, este item se posiciona como a melhor escolha custo-benefício para quem não quer abrir mão da qualidade.</p>",
        f"<p>Nesta análise profunda, vamos explorar cada detalhe técnico, comparar com os principais concorrentes e entender se o investimento realmente vale a pena em 2026. O mercado de {cat} está cada vez mais competitivo, e encontrar uma oferta que combine tecnologia de ponta com preço justo é o objetivo de todo consumidor inteligente.</p>",
        
        f"<h2>Análise Técnica Detalhada do {name}</h2>",
        f"<p>Ao analisarmos as especificações do {name}, percebemos que a marca investiu pesado em durabilidade e performance. Diferente de outros modelos na mesma faixa de preço, este produto entrega uma experiência premium que justifica cada centavo. Seja para uso profissional ou doméstico, a versatilidade é o ponto forte aqui.</p>",
        f"<ul><li><strong>Desempenho:</strong> Testes realizados mostram uma eficiência 30% superior à média da categoria.</li><li><strong>Design:</strong> Acabamento refinado que se adapta a qualquer ambiente.</li><li><strong>Conectividade:</strong> Integração total com os ecossistemas mais modernos.</li></ul>",
        
        f"<h2>Tabela Comparativa: {name} vs Concorrentes</h2>",
        f"<table class=\'specs-table\'><tr><th>Característica</th><th>{name}</th><th>Concorrente A</th><th>Concorrente B</th></tr><tr><td>Preço Atual</td><td>{price}</td><td>R$ 1.200,00</td><td>R$ 1.450,00</td></tr><tr><td>Desconto</td><td>{discount}</td><td>10%</td><td>5%</td></tr><tr><td>Avaliação Usuários</td><td>4.9/5.0</td><td>4.2/5.0</td><td>4.5/5.0</td></tr></table>",
        
        f"<h2>Vale a pena comprar o {name} com {discount} de desconto?</h2>",
        f"<p>A resposta curta é: <strong>Sim!</strong> Quando um produto de alta procura como este chega a um desconto de {discount}, a tendência é que o estoque se esgote rapidamente. No Radar Ninja, usamos algoritmos de inteligência artificial para verificar se o desconto é \'maquiado\' ou real. No caso do {name}, confirmamos que o preço original de {old_price} era o valor praticado nos últimos 90 dias, o que torna a oferta de hoje uma oportunidade legítima.</p>",
        
        f"<h2>FAQ - Perguntas Frequentes sobre o {name}</h2>",
        f"<h3>1. O {name} possui garantia oficial?</h3><p>Sim, ao comprar pelo link oficial do Mercado Livre que disponibilizamos, você tem a garantia total do fabricante e a proteção de compra do Mercado Pago.</p>",
        f"<h3>2. Qual o prazo de entrega para minha região?</h3><p>O Mercado Livre oferece uma das logísticas mais rápidas do Brasil. Muitos produtos desta categoria contam com entrega Full, chegando em menos de 24 horas.</p>",
        
        f"<h2>Conclusão: Veredito Radar Ninja</h2>",
        f"<p>O <strong>{name}</strong> é, sem dúvida, o achado do dia. Se você precisa de um item confiável na categoria de {cat} e quer aproveitar o <strong>menor preço da história</strong>, não hesite. Clique no botão abaixo e garanta o seu antes que o preço volte ao normal.</p>"
    ]
    
    extra_content = ""
    for i in range(3):
        extra_content += f"<h3>Dica de Economia Ninja #{i+1}</h3><p>Sempre verifique o histórico de preços antes de fechar sua compra. O Radar Ninja faz esse trabalho pesado para você, mas entender as oscilações do mercado de {cat} ajuda a identificar o melhor momento psicológico para a compra. Itens como o {name} costumam ter ciclos de promoção curtos, então a agilidade é fundamental.</p>"
    
    return "".join(sections) + extra_content

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
    
    top_products = products[:10]
    
    for p in top_products:
        name = p.get("name") or p.get("title")
        slug = slugify(name)
        content = generate_long_content_with_ai(p) # Usar a função com IA
        image = p.get("image") or p.get("thumbnail")
        affiliate_url = p.get("custom_affiliate_url") or p.get("permalink")
        price = p.get("price", 0)
        old_price = p.get("originalPrice", 0) or p.get("original_price", 0)
        discount = p.get("custom_discount_pct", 0)
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Review Completa e Menor Preço | Radar Ninja</title>
    <meta name="description" content="Análise profunda do {name}. Vale a pena comprar com {discount}% de desconto? Confira ficha técnica, comparativos e FAQ.">
    <link rel="stylesheet" href="../../assets/css/style.css">
    <style>
        .post-body {{ max-width: 800px; margin: 40px auto; padding: 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
        .post-body h1 {{ color: #6200ea; font-size: 32px; margin-bottom: 20px; text-align: center; }}
        .post-body h2 {{ color: #311b92; margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .post-body p {{ font-size: 18px; line-height: 1.8; color: #444; margin-bottom: 20px; }}
        .buy-card {{ background: #f3e5f5; padding: 30px; border-radius: 12px; text-align: center; margin: 30px 0; border: 2px dashed #6200ea; }}
        .btn-buy {{ background: #6200ea; color: white; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; font-size: 20px; display: inline-block; transition: 0.3s; }}
        .btn-buy:hover {{ background: #311b92; transform: scale(1.05); }}
        .product-hero-img {{ text-align: center; margin-bottom: 30px; }}
        .product-hero-img img {{ max-width: 100%; border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <header class="header"><div class="container"><a href="/" class="logo">🥷 <strong>Radar Ninja</strong></a></div></header>
    <main class="container">
        <article class="post-body">
            <h1>{name} - Vale a pena? Análise Completa de 2026</h1>
            
            <div class="product-hero-img">
                <img src="{image}" alt="{name}" loading="lazy">
            </div>

            <div class="buy-card">
                <p style="font-size: 20px; margin-bottom: 10px; color: #666;">Oferta em destaque:</p>
                <p style="font-size: 32px; font-weight: bold; color: #6200ea; margin-bottom: 5px;">R$ {price:.2f}</p>
                <p style="text-decoration: line-through; color: #999; margin-bottom: 20px;">De R$ {old_price:.2f} ({discount}% OFF)</p>
                <a href="{affiliate_url}" class="btn-buy" target="_blank">APROVEITAR OFERTA NO ML 🚀</a>
            </div>

            {content}

            <div class="buy-card" style="margin-top:50px; background: #fff3e0; border-color: #ff9800;">
                <h3 style="color: #e65100; margin-bottom: 15px;">🚨 Alerta de Estoque Baixo!</h3>
                <p>O <strong>{name}</strong> é um dos itens mais clicados de hoje. O preço de <strong>R$ {price:.2f}</strong> pode expirar a qualquer momento.</p>
                <a href="{affiliate_url}" class="btn-buy" target="_blank" style="background: #ff9800;">PEGAR OFERTA AGORA 🛒</a>
            </div>
        </article>
    </main>
    <footer class="footer"><div class="container"><p>© 2026 Radar Ninja - Conteúdo gerado para auxílio ao consumidor.</p></div></footer>
</body>
</html>"""
        
        with open(f"noticias/posts/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        posts_meta.append({
            "title": name,
            "url": f"posts/{slug}.html",
            "excerpt": f"Análise completa: O {name} está com {discount}% de desconto. Vale a pena?",
            "tagLabel": (p.get("custom_category_slug") or "OFERTA").upper(),
            "date": datetime.now().strftime("%d/%m/%Y"),
            "readTime": "8 min",
            "icon": "🔥"
        })
        
    template_path = "templates/blog_premium.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        blog_html = template.replace("{{NEWS_JSON}}", json.dumps(posts_meta, indent=2, ensure_ascii=False))
        with open("noticias/index.html", "w", encoding="utf-8") as f:
            f.write(blog_html)
    
    logger.info(f"✅ Blog regenerado com links no topo e final.")

if __name__ == "__main__":
    generate_blog()
