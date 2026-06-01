import json
import os
import requests
from datetime import datetime

def get_safe_image(url):
    if not url: return ""
    return url.replace("-I.jpg", "-V.jpg").replace("-O.jpg", "-V.jpg")

def fetch_products(category_id, keywords):
    print(f"🔍 Buscando produtos para: {category_id}...")
    url = 'https://api.mercadolibre.com/sites/MLB/search'
    # Busca simplificada para garantir resultados
    params = {'q': keywords[0] if isinstance(keywords, list) else keywords, 'limit': 20, 'condition': 'new'}
    products = []
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('results', []):
                price = item.get('price', 0)
                old_price = item.get('original_price') or price
                discount = round(((old_price - price) / old_price * 100)) if old_price > price else 0
                
                permalink = item.get('permalink', '')
                if 'matt_tool=' not in permalink:
                    permalink += ('&' if '?' in permalink else '?') + 'matt_tool=vendas0nline'

                products.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'price': price,
                    'originalPrice': old_price,
                    'custom_discount_pct': discount,
                    'image': get_safe_image(item.get('thumbnail')),
                    'custom_affiliate_url': permalink,
                    'custom_category_slug': category_id
                })
    except Exception as e:
        print(f"Erro: {e}")
    return products

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'data/ROBO4_CONFIG.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    all_products = []
    for cat in config['categorias']:
        res = fetch_products(cat['id'], cat['keywords'])
        all_products.extend(res)

    central_path = os.path.join(base_dir, 'data/products/offers.json')
    os.makedirs(os.path.dirname(central_path), exist_ok=True)
    with open(central_path, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    print(f"✅ Total: {len(all_products)} produtos.")

if __name__ == '__main__':
    main()
