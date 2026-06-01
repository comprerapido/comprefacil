import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OFFERS_PATH = ROOT / 'data/products/offers.json'
CONFIG_PATH = ROOT / 'data/ROBO4_CONFIG.json'

CATEGORY_ALIASES = {
    'celular': {'celular', 'celulares', 'smartphones'},
    'games': {'games', 'game', 'video-games'},
    'tv': {'tv', 'tv-e-video', 'televisores'},
    'moda': {'moda', 'roupas', 'vestuario'},
}

def normalize_text(value):
    value = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode('ascii')
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def normalize_slug(value):
    return normalize_text(value).replace(' ', '-')

def load_allowed_categories():
    # Fallback básico para garantir que nada seja deletado por engano
    fallback = {'celular', 'celulares', 'smartphones', 'games', 'game', 'tv', 'tv-e-video', 'moda'}
    try:
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
            allowed = set()
            for category in config.get('categorias', []):
                cat_id = category.get('id')
                allowed.add(cat_id)
                allowed.update(CATEGORY_ALIASES.get(cat_id, set()))
            return {normalize_slug(item) for item in allowed if item}
    except:
        pass
    return fallback

def extract_ml_code(url):
    if not url: return ''
    match = re.search(r'MLB-?([0-9]{8,15})', str(url), re.I)
    return match.group(1) if match else ''

def sanitize(products):
    allowed = load_allowed_categories()
    seen = set()
    clean = []
    removed_category = 0
    removed_duplicates = 0

    for product in products:
        # Pega o slug da categoria e normaliza
        cat_slug = normalize_slug(product.get('custom_category_slug') or product.get('category') or '')
        
        # Se a categoria não estiver na lista permitida, tentamos ver se o slug original (id) serve
        if cat_slug not in allowed:
            removed_category += 1
            continue

        # Chave de unicidade (ID ou Título+Preço)
        p_id = product.get('id') or extract_ml_code(product.get('permalink'))
        if p_id in seen:
            removed_duplicates += 1
            continue
        
        seen.add(p_id)
        clean.append(product)

    clean.sort(key=lambda item: item.get('custom_discount_pct', 0), reverse=True)
    return clean, removed_category, removed_duplicates

def main():
    if not OFFERS_PATH.exists():
        print("Arquivo de ofertas não encontrado.")
        return
        
    products = json.loads(OFFERS_PATH.read_text(encoding='utf-8'))
    clean, removed_category, removed_duplicates = sanitize(products)
    
    OFFERS_PATH.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Produtos originais: {len(products)}')
    print(f'Produtos finais: {len(clean)}')
    print(f'Removidos por categoria: {removed_category}')
    print(f'Removidos como duplicados: {removed_duplicates}')

if __name__ == '__main__':
    main()
