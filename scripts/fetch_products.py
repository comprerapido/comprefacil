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

def get_high_res_image(url):
    if not url:
        return ""
    # Mercado Livre: substitui -I.jpg ou -V.jpg por -O.jpg para alta resolução
    return url.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg")

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
        # Garante que o link de afiliado esteja presente
        if affiliate_param not in permalink:
            separator = '&' if '?' in permalink else '?'
            permalink = f"{permalink}{separator}{affiliate_param}"

    img = get_high_res_image(item.get('thumbnail') or "")

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

    if not products:
        return generate_example_products(category_id)
    return products[:50]

def generate_example_products(category_id):
    examples = {
        'celular': [
            {'id': 'MLB3542109828', 'title': 'Samsung Galaxy A15 5G 128GB Azul Escuro', 'name': 'Samsung Galaxy A15 5G 128GB Azul Escuro', 'price': 1099.0, 'original_price': 1399.0, 'permalink': 'https://www.mercadolivre.com.br/samsung-galaxy-a15-5g-128gb-azul-escuro/p/MLB3542109828?matt_tool=vendas0nline', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB74622340767_022024-O.jpg', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB74622340767_022024-O.jpg', 'custom_category_slug': 'celulares', 'custom_discount_pct': 21},
            {'id': 'MLB2789104432', 'title': 'Apple iPhone 15 128GB Preto', 'name': 'Apple iPhone 15 128GB Preto', 'price': 4699.0, 'original_price': 5299.0, 'permalink': 'https://www.mercadolivre.com.br/apple-iphone-15-128gb-preto/p/MLB2789104432?matt_tool=vendas0nline', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB71786659170_092023-O.jpg', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB71786659170_092023-O.jpg', 'custom_category_slug': 'celulares', 'custom_discount_pct': 11},
        ],
        'games': [
            {'id': 'MLB31000132', 'title': 'Nintendo Switch OLED 64GB Branco', 'name': 'Nintendo Switch OLED 64GB Branco', 'price': 2589.0, 'original_price': 2999.0, 'permalink': 'https://www.mercadolivre.com.br/nintendo-switch-oled-64gb-branco/p/MLB31000132?matt_tool=vendas0nline', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB48003100013_102021-O.jpg', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB48003100013_102021-O.jpg', 'custom_category_slug': 'games', 'custom_discount_pct': 13},
        ],
        'tv': [
            {'id': 'MLBU34610982', 'title': 'Smart TV 50" 4K UHD Samsung Crystal', 'name': 'Smart TV 50" 4K UHD Samsung Crystal', 'price': 2399.0, 'original_price': 2899.0, 'permalink': 'https://www.mercadolivre.com.br/smart-tv-50-4k-uhd-samsung/p/MLBU34610982?matt_tool=vendas0nline', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB75346109828_032024-O.jpg', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB75346109828_032024-O.jpg', 'custom_category_slug': 'tv-e-video', 'custom_discount_pct': 17},
        ],
        'moda': [
            {'id': 'MLB54229104437', 'title': 'Tênis Puma Flyer Runner Mesh BDP', 'name': 'Tênis Puma Flyer Runner Mesh BDP', 'price': 208.99, 'original_price': 250.00, 'permalink': 'https://www.mercadolivre.com.br/tenis-puma-flyer-runner-mesh-bdp/p/MLB54229104437?matt_tool=vendas0nline', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB54229104437_032023-O.jpg', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB54229104437_032023-O.jpg', 'custom_category_slug': 'moda', 'custom_discount_pct': 17},
        ]
    }
    # Adiciona campos extras para compatibilidade
    res = examples.get(category_id, [])
    for r in res:
        r['originalPrice'] = r['original_price']
        r['custom_affiliate_url'] = r['permalink']
        r['status'] = 'active'
    return res

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

    # Salva também o arquivo central
    central_path = os.path.join(os.path.dirname(__file__), '../data/products/offers.json')
    os.makedirs(os.path.dirname(central_path), exist_ok=True)
    with open(central_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
