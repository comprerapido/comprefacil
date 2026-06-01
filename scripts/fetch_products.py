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
        separator = '&' if '?' in permalink else '?'
        if affiliate_param not in permalink:
            permalink = f"{permalink}{separator}{affiliate_param}"

    return {
        'id': item.get('id'),
        'title': item.get('title'),
        'name': item.get('title'),
        'price': price,
        'original_price': original_price,
        'originalPrice': original_price,
        'permalink': permalink,
        'custom_affiliate_url': permalink,
        'thumbnail': item.get('thumbnail'),
        'image': item.get('thumbnail'),
        'condition': item.get('condition'),
        'custom_category_slug': rules.get('slug', category_id),
        'custom_discount_pct': discount,
        'status': 'active',
        'last_seen': datetime.now().isoformat()
    }

def fetch_products(category_id, keywords):
    """Busca produtos na API do Mercado Livre com validação rígida da categoria configurada."""
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
                print(f"⚠ Erro {response.status_code} na busca '{query}'.")
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
        print('⚠ Nenhum produto válido retornado. Usando dados de exemplo da categoria correta...')
        return generate_example_products(category_id)

    print(f"✓ {len(products)} produtos válidos encontrados para {category_id}")
    return products[:50]

def generate_example_products(category_id):
    """Gera produtos de exemplo somente para a categoria correta."""
    examples = {
        'celular': [
            {'id': 'MLB1', 'title': 'Celular Samsung Galaxy A07 256GB', 'name': 'Celular Samsung Galaxy A07 256GB', 'price': 1200.00, 'original_price': 1500.00, 'originalPrice': 1500.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'celulares', 'custom_discount_pct': 20},
            {'id': 'MLB2', 'title': 'iPhone 15 Pro Max 256GB', 'name': 'iPhone 15 Pro Max 256GB', 'price': 8000.00, 'original_price': 9000.00, 'originalPrice': 9000.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'celulares', 'custom_discount_pct': 11},
        ],
        'games': [
            {'id': 'MLB3', 'title': 'Console PlayStation 5 Slim', 'name': 'Console PlayStation 5 Slim', 'price': 3500.00, 'original_price': 4000.00, 'originalPrice': 4000.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'games', 'custom_discount_pct': 12},
            {'id': 'MLB4', 'title': 'Jogo God of War Ragnarök PS5', 'name': 'Jogo God of War Ragnarök PS5', 'price': 200.00, 'original_price': 300.00, 'originalPrice': 300.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'games', 'custom_discount_pct': 33},
        ],
        'tv': [
            {'id': 'MLB5', 'title': 'Smart TV 55" 4K Ultra HD', 'name': 'Smart TV 55" 4K Ultra HD', 'price': 1899.90, 'original_price': 2399.90, 'originalPrice': 2399.90, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'tv-e-video', 'custom_discount_pct': 21},
            {'id': 'MLB6', 'title': 'TV 43" Full HD com Conversor', 'name': 'TV 43" Full HD com Conversor', 'price': 899.00, 'original_price': 1199.00, 'originalPrice': 1199.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'tv-e-video', 'custom_discount_pct': 25},
        ],
        'moda': [
            {'id': 'MLB7', 'title': 'Tênis Esportivo Masculino Nike', 'name': 'Tênis Esportivo Masculino Nike', 'price': 300.00, 'original_price': 400.00, 'originalPrice': 400.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'moda', 'custom_discount_pct': 25},
            {'id': 'MLB8', 'title': 'Vestido Longo Feminino Floral', 'name': 'Vestido Longo Feminino Floral', 'price': 150.00, 'original_price': 200.00, 'originalPrice': 200.00, 'permalink': 'https://www.mercadolivre.com.br', 'thumbnail': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'image': 'https://http2.mlstatic.com/D_NQ_NP_614131-MLB44622340767_012021-O.webp', 'condition': 'new', 'custom_category_slug': 'moda', 'custom_discount_pct': 25},
        ]
    }
    return examples.get(category_id, [])

def main():
    """Executa o script principal."""
    config_path = os.path.join(os.path.dirname(__file__), '../data/ROBO4_CONFIG.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    print(f"\n{'='*50}")
    print('🤖 ROBÔ 4 - SUPER NINJA')
    print(f"{'='*50}\n")

    for cat in config['categorias']:
        products = fetch_products(cat['id'], cat['keywords'])
        output_path = os.path.join(os.path.dirname(__file__), f"../data/products_{cat['id']}.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

        print(f"💾 Salvo: {output_path}\n")

    print(f"{'='*50}")
    print(f"✓ Busca concluída em {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
