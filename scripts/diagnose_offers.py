import json
import re
import unicodedata
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFERS = ROOT / 'data/products/offers.json'
CONFIG = ROOT / 'data/ROBO3_CONFIG.json'

CATEGORY_ALIASES = {
    'tv': {'tv', 'tv-e-video', 'televisores'},
    'games': {'games', 'game', 'video-games'},
    'celular': {'celular', 'celulares', 'smartphones'},
    'moda': {'moda', 'roupas', 'vestuario'},
}

def normalize_text(value):
    value = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode('ascii')
    value = value.lower()
    value = re.sub(r'\b(kit|unidade|un|novo|original|promo[cç][aã]o|oferta)\b', ' ', value)
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def canonical_product_key(product):
    for field in ('id', 'catalog_product_id'):
        value = product.get(field)
        if value:
            return f'id:{value}'
    for field in ('permalink', 'custom_affiliate_url'):
        url = product.get(field)
        if url:
            parsed = urlparse(url)
            match = re.search(r'/(?:p/)?(MLB\d+)', parsed.path, re.I)
            if match:
                return f'mlb:{match.group(1).upper()}'
            path = parsed.path.rstrip('/').lower()
            if path:
                return f'url:{path}'
    name = normalize_text(product.get('name') or product.get('title'))
    image = product.get('image') or product.get('thumbnail') or ''
    return f'name:{name[:80]}|img:{image}'

def main():
    offers = json.loads(OFFERS.read_text(encoding='utf-8'))
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    allowed = set()
    for cat in config.get('categorias', []):
        allowed.update(CATEGORY_ALIASES.get(cat.get('id'), {cat.get('id')}))

    seen = {}
    duplicates = []
    out_of_category = []
    for p in offers:
        cat = str(p.get('custom_category_slug') or '').lower()
        if cat and cat not in allowed:
            out_of_category.append((p.get('id'), p.get('name'), cat))
        key = canonical_product_key(p)
        if key in seen:
            duplicates.append((key, seen[key].get('name'), p.get('name')))
        else:
            seen[key] = p

    print('total', len(offers))
    print('allowed_categories', sorted(allowed))
    print('categories_in_file', sorted({str(p.get('custom_category_slug') or '').lower() for p in offers}))
    print('out_of_category_count', len(out_of_category))
    print('duplicates_count', len(duplicates))
    print('first_out_of_category', out_of_category[:10])
    print('first_duplicates', duplicates[:10])

if __name__ == '__main__':
    main()
