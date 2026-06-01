import json
import os
import re
import unicodedata
from datetime import datetime
import requests

CATEGORY_RULES = {
    'celular': {
        'slug': 'celulares',
        'must_have_any': ['celular', 'smartphone', 'iphone', 'samsung', 'xiaomi', 'motorola'],
        'block': ['capa', 'pelicula', 'fone', 'carregador', 'suporte']
    },
    'games': {
        'slug': 'games',
        'must_have_any': ['game', 'console', 'playstation', 'xbox', 'nintendo', 'jogo', 'gamer', 'controle', 'headset'],
        'block': ['capa', 'adesivo', 'suporte']
    },
    'tv': {
        'slug': 'tv-e-video',
        'must_have_any': ['tv', 'smart tv', 'televisao', 'televisor', 'monitor', 'projetor', 'chromecast', 'roku'],
        'block': ['controle remoto', 'suporte tv', 'cabo hdmi']
    },
    'moda': {
        'slug': 'moda',
        'must_have_any': ['roupa', 'moda', 'calcado', 'tenis', 'vestido', 'camisa', 'calca', 'sapato', 'oculos', 'bolsa'],
        'block': ['acessorio', 'bijuteria', 'joia', 'relogio']
    }
}

def normalize_text(value):
    value = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode('ascii')
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def matches_category(item, category_id):
    rules = CATEGORY_RULES.get(category_id, {})
    title = normalize_text(item.get('title'))
    if any(blocked in title for blocked in rules.get('block', [])):
        return False
    required = rules.get('must_have_any', [])
    return not required or any(term in title for term in required)

def get_safe_image(url):
    if not url:
        return ""
    # O formato -O as vezes é bloqueado ou não carrega em iframes/github pages. 
    # O formato -V ou -I é mais estável para exibição direta.
    return url.replace("-O.jpg", "-V.jpg").replace("-I.jpg", "-V.jpg")

def to_product(item, category_id):
    rules = CATEGORY_RULES.get(category_id, {})
    original_price = item.get('original_price') or item.get('price')
    price = item.get('price') or 0
    discount = 0
    try:
        if original_price and original_price > price:
            discount = round((original_price - price) / original_price * 100)
    except Exception:
        discount = 0

    permalink = item.get('permalink') or ''
    affiliate_param = 'matt_tool=vendas0nline'
    if permalink:
        if affiliate_param not in permalink:
            separator = '&' if '?' in permalink else '?'
            permalink = f"{permalink}{separator}{affiliate_param}"

    img = get_safe_image(item.get('thumbnail') or "")

    return {
        'id': item.get('id'),
        'title': item.get('title'),
        'name': item.get('title'),
        'price': price,
        'original_price': original_price,
        'originalPrice': original_price,
        'permalink': permalink,
        'custom_affiliate_url': permalink,
        'thumbnail': img,
        'image': img,
        'condition': item.get('condition'),
        'custom_category_slug': rules.get('slug', category_id),
        'custom_discount_pct': discount,
        'status': 'active',
        'last_seen': datetime.now().isoformat()
    }

def fetch_products(category_id, keywords):
    print(f"🔍 Buscando produtos para: {category_id}...")
    queries = keywords[:4] if isinstance(keywords, list) else [str(keywords)]
    products = []
    seen_ids = set()

    for query in queries:
        url = 'https://api.mercadolibre.com/sites/MLB/search'
        params = {'q': query, 'limit': 50, 'condition': 'new'}
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                continue
            data = response.json()
            for item in data.get('results', []):
                item_id = item.get('id')
                if not item_id or item_id in seen_ids:
                    continue
                if not matches_category(item, category_id):
                    continue
                seen_ids.add(item_id)
                products.append(to_product(item, category_id))
        except Exception as e:
            print(f"❌ Erro na busca '{query}': {e}")

    return products[:50]

def main():
    config_path = os.path.join(os.path.dirname(__file__), '../data/ROBO4_CONFIG.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    all_products = []
    for cat in config['categorias']:
        products = fetch_products(cat['id'], cat['keywords'])
        all_products.extend(products)
        output_path = os.path.join(os.path.dirname(__file__), f"../data/products_{cat['id']}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

    central_path = os.path.join(os.path.dirname(__file__), '../data/products/offers.json')
    os.makedirs(os.path.dirname(central_path), exist_ok=True)
    with open(central_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
