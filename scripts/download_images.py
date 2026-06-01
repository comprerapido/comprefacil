import json
import os
import requests
from logger import logger

def download_images():
    logger.info("📸 Baixando imagens reais (GIF/JPG)...")
    
    if not os.path.exists("data/products/offers.json"):
        return

    with open("data/products/offers.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    os.makedirs("assets/img/products", exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    updated_products = []
    for p in products:
        img_url = p.get("image")
        if img_url and img_url.startswith("http"):
            # O Mercado Livre às vezes retorna GIF para o thumbnail
            file_name = f"{p['id']}.gif"
            local_path = f"assets/img/products/{file_name}"
            
            try:
                response = requests.get(img_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"✓ Baixada: {file_name}")
                
                p["image_local"] = f"/assets/img/products/{file_name}"
            except Exception as e:
                logger.error(f"Erro ao baixar {img_url}: {e}")
        
        updated_products.append(p)

    with open("data/products/offers.json", "w", encoding="utf-8") as f:
        json.dump(updated_products, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    download_images()
