#!/usr/bin/env python3
"""
Script para gerar páginas de produtos com o novo template v2.
Inclui foto no topo, links de afiliado em destaque, e menu de exploração.
"""

import os
import json
import unicodedata
from datetime import datetime
from typing import Dict, Any
from logger import logger

BASE_URL = "https://radardeprecos.github.io/radar/"

def slugify(text: str) -> str:
    """Converte texto em slug amigável para URL."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')

def escape_html(text: str) -> str:
    """Escapa caracteres HTML."""
    if not text:
        return ""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#39;'))

def generate_product_page_v2(product: Dict[str, Any], template_path: str, output_dir: str) -> bool:
    """
    Gera uma página HTML completa para um produto com o novo template v2.
    """
    
    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        logger.error(f"Erro ao ler template: {e}")
        return False
    
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
    economy = original_price - price
    
    # Formatar preços
    price_formatted = f"R$ {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    original_price_formatted = f"R$ {original_price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    economy_formatted = f"R$ {economy:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Imagem
    product_image = product.get('image') or product.get('thumbnail') or ''
    
    # URL de afiliado
    affiliate_url = product.get('custom_affiliate_url', '')
    if not affiliate_url or '/social/' in affiliate_url or 'vendas0nline?' in affiliate_url:
        affiliate_url = product.get('permalink', '')
    
    # Conteúdo gerado
    generated_content = product.get('generated_description', '')
    
    # SEO
    seo_title = f"{product_name} com {discount_pct}% de Desconto | Radar de Preços"
    meta_description = f"Confira a oferta de {product_name} no Radar de Preços. Economize com os melhores descontos do Mercado Livre. {discount_pct}% OFF!"
    canonical_url = f"{BASE_URL}ofertas/{category_slug}/{product_slug}-{product_id}.html"
    
    # Schema.json
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
            "availability": "https://schema.org/InStock",
            "priceValidUntil": "2026-12-31"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.5",
            "reviewCount": "100"
        }
    }
    
    # Substituições no template
    content = template
    content = content.replace('{{seo.title}}', escape_html(seo_title))
    content = content.replace('{{meta.description}}', escape_html(meta_description))
    content = content.replace('{{canonical.url}}', canonical_url)
    content = content.replace('{{schema.json}}', json.dumps(schema_json, ensure_ascii=False))
    
    content = content.replace('{{product.name}}', escape_html(product_name))
    content = content.replace('{{product.price}}', price_formatted)
    content = content.replace('{{product.original_price}}', original_price_formatted)
    content = content.replace('{{product.economy}}', economy_formatted)
    content = content.replace('{{product.discount}}', str(discount_pct))
    content = content.replace('{{product.image}}', escape_html(product_image))
    content = content.replace('{{product.url}}', escape_html(affiliate_url))
    content = content.replace('{{product.category}}', category_slug)
    content = content.replace('{{product.generated_content}}', generated_content)
    content = content.replace('{{current_date}}', datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    # Criar diretório de saída
    output_path = os.path.join(output_dir, category_slug, f'{product_slug}-{product_id}.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar página
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"✅ Página publicada: {output_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar página {output_path}: {e}")
        return False

def generate_all_product_pages_v2(input_path: str, template_path: str, output_dir: str) -> None:
    """
    Gera todas as páginas de produtos usando o novo template v2.
    """
    
    logger.info("=" * 80)
    logger.info("🚀 GERANDO PÁGINAS DE PRODUTOS (TEMPLATE V2)")
    logger.info("=" * 80)
    
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
    
    logger.info(f"Processando {len(products)} produtos...")
    
    for idx, product in enumerate(products, 1):
        try:
            if generate_product_page_v2(product, template_path, output_dir):
                published_count += 1
            else:
                error_count += 1
        except Exception as e:
            logger.error(f"❌ Erro ao processar produto {idx}: {e}")
            error_count += 1
        
        # Mostrar progresso a cada 10 produtos
        if idx % 10 == 0:
            logger.info(f"   Progresso: {idx}/{len(products)} ({published_count} sucesso, {error_count} erro)")
    
    logger.info("=" * 80)
    logger.info(f"✅ Geração concluída!")
    logger.info(f"   Páginas publicadas: {published_count}")
    logger.info(f"   Erros: {error_count}")
    logger.info("=" * 80)

if __name__ == "__main__":
    generate_all_product_pages_v2(
        "data/products_deduplicated.json",
        "templates/product_page_v2.html",
        "ofertas"
    )
