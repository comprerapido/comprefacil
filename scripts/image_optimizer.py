#!/usr/bin/env python3
"""
image_optimizer.py — Sistema de download local e otimização de imagens.
Faz o download das imagens do ML, salva localmente e otimiza para SEO.
"""

import os
import json
import requests
import hashlib
from pathlib import Path
from PIL import Image
from logger import logger
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets" / "products"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS_IMG = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.mercadolivre.com.br/",
}

def get_image_filename(url: str, product_name: str) -> str:
    """Gera um nome de arquivo amigável para SEO baseado no nome do produto."""
    import unicodedata
    import re
    
    # Criar hash da URL para evitar duplicatas se o nome mudar
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    
    # Slugify nome do produto
    name_slug = unicodedata.normalize('NFKD', product_name).encode('ascii', 'ignore').decode('ascii')
    name_slug = re.sub(r'[^a-z0-9]+', '-', name_slug.lower()).strip('-')
    name_slug = name_slug[:50] # Limitar tamanho
    
    return f"{name_slug}-{url_hash}.webp"

def download_and_optimize_image(url: str, product_name: str) -> str:
    """Faz download, converte para WebP e salva localmente."""
    if not url or "placehold.jp" in url:
        return ""
    
    filename = get_image_filename(url, product_name)
    local_path = ASSETS_DIR / filename
    relative_path = f"/assets/products/{filename}"
    
    # Se já existe, não baixa de novo
    if local_path.exists():
        return relative_path
    
    try:
        resp = requests.get(url, headers=HEADERS_IMG, timeout=15, stream=True)
        if resp.status_code == 200:
            # Salvar temporariamente
            temp_path = local_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            
            # Otimizar com Pillow
            with Image.open(temp_path) as img:
                # Converter para RGB se necessário (WebP prefere RGB)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Redimensionar se for muito grande (max 800px)
                if img.width > 800 or img.height > 800:
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                # Salvar como WebP
                img.save(local_path, "WEBP", quality=85, optimize=True)
            
            # Remover temporário
            os.remove(temp_path)
            logger.info(f"✓ Imagem salva localmente: {filename}")
            return relative_path
        else:
            logger.warning(f"✗ Falha ao baixar imagem: {url} (Status: {resp.status_code})")
            return ""
    except Exception as e:
        logger.error(f"✗ Erro ao processar imagem {url}: {e}")
        return ""

def process_all_product_images(json_path: str):
    """Varre o JSON de produtos e baixa todas as imagens."""
    if not os.path.exists(json_path):
        logger.error(f"Arquivo {json_path} não encontrado.")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated_count = 0
    logger.info(f"Iniciando download de imagens para {len(products)} produtos...")
    
    for p in products:
        img_url = p.get('image') or p.get('thumbnail')
        if img_url and not img_url.startswith('/assets/'):
            local_url = download_and_optimize_image(img_url, p.get('name', 'produto'))
            if local_url:
                p['image_remote'] = img_url # Guardar original como backup
                p['image'] = local_url
                p['thumbnail'] = local_url
                updated_count += 1
    
    # Salvar de volta o JSON atualizado
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Processamento de imagens concluído. {updated_count} imagens atualizadas.")

if __name__ == "__main__":
    # Processar as bases principais
    process_all_product_images(str(ROOT / "data" / "database" / "all_products.json"))
    process_all_product_images(str(ROOT / "data" / "scored_products.json"))
