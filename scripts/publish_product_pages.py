import os
import json
import unicodedata
from typing import Dict, Any, List
from logger import logger

BASE_URL = "https://comprerapido.github.io/"

def slugify(text: str) -> str:
    """Converte texto em slug amigável para URL."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def generate_product_page(product: Dict[str, Any], template_path: str, output_dir: str) -> None:
    """
    Gera uma página HTML completa para um produto com conteúdo gerado.
    """
    
    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Extrair informações do produto
    product_id = product.get('id', '0')
    product_name = product.get('name') or product.get('title') or 'Produto'
    product_slug = slugify(product_name)
    category_slug = product.get('custom_category_slug', 'outros')
    
    # Preços e desconto
    try:
        price = float(product.get('price', 0))
        original_price = float(product.get('originalPrice', 0))
    except (ValueError, TypeError):
        price = 0.0
        original_price = 0.0
    
    discount_pct = product.get('custom_discount_pct', 0)
    
    # Formatar preços
    price_formatted = f"R$ {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    original_price_formatted = f"R$ {original_price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Imagem
    product_image = product.get('image') or product.get('thumbnail') or ''
    
    # URL de afiliado
    affiliate_url = product.get('custom_affiliate_url', '')
    if not affiliate_url or '/social/' in affiliate_url or 'vendas0nline?' in affiliate_url:
        affiliate_url = product.get('permalink', '')
    
    # Conteúdo gerado
    generated_content = product.get('generated_description', '')
    word_count = product.get('word_count', 0)
    
    # Score e status
    score = product.get('score', 0)
    status = product.get('status', 'active')
    
    # SEO
    seo_title = f"{product_name} com {discount_pct}% de Desconto | Radar de Preços"
    meta_description = f"Confira a oferta de {product_name} no Radar de Preços. Economize com os melhores descontos do Mercado Livre. {discount_pct}% OFF!"
    canonical_url = f"{BASE_URL}ofertas/{category_slug}/{product_slug}-{product_id}.html"
    
    # Estrutura de schema.json para SEO
    schema_json = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product_name,
        "image": product_image,
        "description": f"Oferta de {product_name} com {discount_pct}% de desconto. Preço: R$ {price:.2f}",
        "brand": {
            "@type": "Brand",
            "name": "Radar de Preços"
        },
        "offers": {
            "@type": "Offer",
            "url": canonical_url,
            "priceCurrency": "BRL",
            "price": str(price),
            "priceCurrencyCode": "BRL",
            "availability": "https://schema.org/InStock",
            "priceValidUntil": "2026-12-31"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.5",
            "reviewCount": "100"
        }
    }
    
    # Badges de status
    status_html = ""
    if status == 'expired':
        status_html = '<div class="status-banner expired">⚠️ Esta oferta encerrou, mas confira produtos similares abaixo!</div>'
    elif discount_pct >= 50:
        status_html = '<div class="status-banner hot">🔥 OFERTA QUENTE - Desconto acima de 50%!</div>'
    
    # Botão de CTA
    cta_button = f'<a href="{affiliate_url}" class="btn btn-primary btn-lg" target="_blank" rel="nofollow sponsored">🛒 Ver Oferta no Mercado Livre</a>'
    
    # Informações adicionais
    info_box = f"""
    <div class="info-box">
        <h3>💰 Detalhes da Oferta</h3>
        <ul>
            <li><strong>Preço Original:</strong> {original_price_formatted}</li>
            <li><strong>Preço Atual:</strong> {price_formatted}</li>
            <li><strong>Desconto:</strong> {discount_pct}%</li>
            <li><strong>Economia:</strong> R$ {original_price - price:.2f}</li>
            <li><strong>Categoria:</strong> {category_slug.replace('-', ' ').title()}</li>
            <li><strong>Conteúdo:</strong> {word_count} palavras (Artigo Completo)</li>
        </ul>
    </div>
    """
    
    # Substituições no template
    content = template.replace('{{seo.title}}', seo_title)
    content = content.replace('{{meta.description}}', meta_description)
    content = content.replace('{{canonical.url}}', canonical_url)
    content = content.replace('{{schema.json}}', json.dumps(schema_json, ensure_ascii=False))
    
    content = content.replace('{{product.name}}', product_name)
    content = content.replace('{{product.price}}', price_formatted)
    content = content.replace('{{product.original_price}}', original_price_formatted)
    content = content.replace('{{product.discount}}', str(discount_pct))
    content = content.replace('{{product.image}}', product_image)
    content = content.replace('{{product.url}}', affiliate_url)
    content = content.replace('{{product.id}}', product_id)
    content = content.replace('{{product.category}}', category_slug)
    
    content = content.replace('{{product.status_banner}}', status_html)
    content = content.replace('{{product.info_box}}', info_box)
    content = content.replace('{{product.cta_button}}', cta_button)
    content = content.replace('{{product.generated_content}}', generated_content)
    
    # Criar diretório de saída
    output_path = os.path.join(output_dir, category_slug, f'{product_slug}-{product_id}.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar página
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Página publicada: {output_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar página {output_path}: {e}")

def publish_all_products(input_path: str, template_path: str, output_dir: str) -> None:
    """
    Publica todas as páginas de produtos a partir do arquivo com conteúdo gerado.
    """
    
    logger.info(f"Iniciando publicação de páginas de produtos...")
    
    if not os.path.exists(input_path):
        logger.error(f"Arquivo de entrada {input_path} não encontrado.")
        return
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler {input_path}: {e}")
        return
    
    published_count = 0
    error_count = 0
    
    for idx, product in enumerate(products, 1):
        try:
            generate_product_page(product, template_path, output_dir)
            published_count += 1
        except Exception as e:
            logger.error(f"Erro ao publicar produto {idx}: {e}")
            error_count += 1
    
    logger.info(f"Publicação concluída: {published_count} páginas publicadas, {error_count} erros.")

if __name__ == "__main__":
    publish_all_products(
        "data/products_with_content.json",
        "templates/product_template.html",
        "ofertas"
    )
