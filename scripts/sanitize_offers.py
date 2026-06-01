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
    value = re.sub(r'\b(kit|unidade|un|novo|original|promocao|oferta)\b', ' ', value)
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def normalize_slug(value):
    return normalize_text(value).replace(' ', '-')

def load_allowed_categories():
    fallback = {'celular', 'celulares', 'smartphones', 'games', 'game', 'video-games', 'tv', 'tv-e-video', 'televisores', 'moda', 'roupas', 'vestuario'}
    if not CONFIG_PATH.exists():
        return fallback

    config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    allowed = set()
    for category in config.get('categorias', []):
        allowed.update(CATEGORY_ALIASES.get(category.get('id'), {category.get('id')}))
    return {normalize_slug(item) for item in allowed if item} or fallback

def extract_ml_code(url):
    if not url:
        return ''
    path = urlparse(str(url)).path
    match = re.search(r'/(?:p|up)/(MLB[A-Z0-9]+)', path, re.I)
    if match:
        return match.group(1).upper()
    generic = re.search(r'\bMLB[A-Z0-9]{6,}\b', str(url), re.I)
    return generic.group(0).upper() if generic else ''

def product_key(product):
    code = extract_ml_code(product.get('permalink')) or extract_ml_code(product.get('custom_affiliate_url'))
    if code:
        return f'ml:{code}'
    stable_id = product.get('catalog_product_id') or product.get('catalogProductId') or product.get('id')
    if stable_id:
        return f'id:{stable_id}'
    name = ' '.join(normalize_text(product.get('name') or product.get('title')).split()[:10])
    image = str(product.get('image') or product.get('thumbnail') or '').split('?')[0]
    price = round(float(product.get('price') or 0) * 100)
    return f'fallback:{name}|{image}|{price}'

def sanitize(products):
    allowed = load_allowed_categories()
    seen = set()
    clean = []
    removed_category = 0
    removed_duplicates = 0

    for product in products:
        slug = normalize_slug(product.get('custom_category_slug') or product.get('category') or '')
        if slug not in allowed:
            removed_category += 1
            continue

        key = product_key(product)
        name_key = ' '.join(normalize_text(product.get('name') or product.get('title')).split()[:8])
        image_key = str(product.get('image') or product.get('thumbnail') or '').split('?')[0]
        soft_key = f'{name_key}|{image_key}'

        if key in seen or soft_key in seen:
            removed_duplicates += 1
            continue

        seen.add(key)
        seen.add(soft_key)
        clean.append(product)

    clean.sort(key=lambda item: item.get('custom_discount_pct', 0), reverse=True)
    return clean, removed_category, removed_duplicates

def main():
    products = json.loads(OFFERS_PATH.read_text(encoding='utf-8'))
    clean, removed_category, removed_duplicates = sanitize(products)
    OFFERS_PATH.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Produtos originais: {len(products)}')
    print(f'Produtos finais: {len(clean)}')
    print(f'Removidos por categoria: {removed_category}')
    print(f'Removidos como duplicados: {removed_duplicates}')

if __name__ == '__main__':
    main()
