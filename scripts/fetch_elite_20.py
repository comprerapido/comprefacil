import requests
import json
import os
from logger import logger

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

def fetch_elite_products():
    categories = [
        {"id": "celular", "q": "smartphone"},
        {"id": "games", "q": "console"},
        {"id": "tv", "q": "smart tv"},
        {"id": "moda", "q": "tenis masculino"}
    ]
    
    all_products = []
    seen_ids = set()
    
    for cat in categories:
        logger.info(f"Buscando elite para: {cat['id']}")
        ml_url = f"https://api.mercadolibre.com/sites/MLB/search?q={cat['q']}&limit=10"
        scraper_key = os.environ.get("SCRAPERAPI_KEY")
        
        if scraper_key:
            url = f"http://api.scraperapi.com?api_key={scraper_key}&url={ml_url}"
        else:
            url = ml_url
            
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"API respondeu com {len(data.get('results', []))} resultados")
            count = 0
            for item in data.get('results', []):
                if count >= 5: break
                item_id = item.get('id')
                if item_id in seen_ids: continue
                
                # Validação básica de foto e link
                img = item.get('thumbnail', '')
                if not img or 'http' not in img: continue
                
                price = item.get('price', 0)
                original_price = item.get('original_price') or item.get('price')
                discount = 0
                if original_price > price:
                    discount = round((original_price - price) / original_price * 100)

                # Link de afiliado direto
                permalink = item.get('permalink', '')
                if permalink:
                    permalink = permalink.split('?')[0] + "?matt_tool=vendas0nline"

                all_products.append({
                    'id': item_id,
                    'title': item.get('title'),
                    'name': item.get('title'),
                    'price': price,
                    'original_price': original_price,
                    'originalPrice': original_price,
                    'custom_discount_pct': discount,
                    'permalink': permalink,
                    'custom_affiliate_url': permalink,
                    'thumbnail': img.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg"),
                    'image': img.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg"),
                    'custom_category_slug': cat['id']
                })
                seen_ids.add(item_id)
                count += 1
        except Exception as e:
            logger.error(f"Erro ao buscar {cat['id']}: {e}")

    os.makedirs("data/products", exist_ok=True)
    with open("data/products/offers.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ {len(all_products)} produtos de elite salvos em data/products/offers.json")

if __name__ == "__main__":
    fetch_elite_products()
