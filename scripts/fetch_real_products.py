#!/usr/bin/env python3
"""
fetch_real_products.py — Coleta REAL de novos produtos via API do Mercado Livre
Melhoria: Rotação de Queries ampliada para maior volume de catálogo.
"""
import json
import os
import sys
import time
import logging
import requests
import unicodedata
import random
from datetime import datetime, timezone
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("fetch_real")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_DIR = os.path.join(DATA_DIR, "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

HEADERS_LIST = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "Accept": "application/json", "Accept-Language": "pt-BR,pt;q=0.9"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", "Accept": "application/json"},
]

ML_API_ENDPOINTS = [
    "https://api.mercadolibre.com/sites/MLB/search?q={query}&limit=20&sort=relevance",
]

# Lista ampliada de queries para rotação
MASTER_QUERIES = [
    {"id": "celular", "q": "iphone 15 pro max"}, {"id": "celular", "q": "samsung galaxy s24 ultra"},
    {"id": "celular", "q": "xiaomi redmi note 13"}, {"id": "celular", "q": "motorola edge 40"},
    {"id": "games", "q": "playstation 5 slim"}, {"id": "games", "q": "xbox series x"},
    {"id": "games", "q": "nintendo switch oled"}, {"id": "games", "q": "controle dualsense ps5"},
    {"id": "informatica", "q": "macbook air m2"}, {"id": "informatica", "q": "notebook gamer rtx"},
    {"id": "informatica", "q": "monitor 144hz"}, {"id": "informatica", "q": "teclado mecanico rgb"},
    {"id": "tv", "q": "smart tv oled 55"}, {"id": "tv", "q": "smart tv qled 65"},
    {"id": "tv", "q": "fire tv stick 4k"}, {"id": "tv", "q": "soundbar samsung"},
    {"id": "eletrodomesticos", "q": "geladeira inverter"}, {"id": "eletrodomesticos", "q": "maquina de lavar lg"},
    {"id": "eletrodomesticos", "q": "air fryer dual"}, {"id": "eletrodomesticos", "q": "microondas espelhado"},
    {"id": "casa", "q": "aspirador robo xiaomi"}, {"id": "casa", "q": "cafeteira nespresso"},
    {"id": "casa", "q": "fechadura eletronica"}, {"id": "casa", "q": "lampada inteligente alexa"},
    {"id": "beleza", "q": "perfume sauvage dior"}, {"id": "beleza", "q": "secador dyson"},
    {"id": "beleza", "q": "maquiagem mac"}, {"id": "beleza", "q": "skincare cerave"},
    {"id": "esporte", "q": "tenis nike air max"}, {"id": "esporte", "q": "apple watch ultra"},
    {"id": "esporte", "q": "bicicleta aro 29"}, {"id": "esporte", "q": "suplemento whey protein"},
]

def fetch_from_ml_api(query: str, cat_id: str) -> List[Dict[str, Any]]:
    products = []
    url = ML_API_ENDPOINTS[0].format(query=query.replace(' ', '+'))
    headers = random.choice(HEADERS_LIST)
    try:
        log.info(f"  Tentando: {url[:70]}...")
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            log.info(f"  ✅ API retornou {len(results)} resultados")
            for item in results:
                price = float(item.get("price") or 0)
                if price < 15: continue
                title = str(item.get("title") or "")
                if len(title) < 15: continue
                img = str(item.get("thumbnail") or "").replace("-I.jpg", "-O.jpg")
                permalink = str(item.get("permalink") or "").split("?")[0] + "?matt_tool=60566305"
                orig_price = float(item.get("original_price") or price * 1.15)
                disc = int(round((orig_price - price) / orig_price * 100)) if orig_price > price else 5
                products.append({
                    "id": item.get("id"),
                    "title": title, "name": title,
                    "price": price, "original_price": orig_price,
                    "custom_discount_pct": disc,
                    "permalink": permalink, "custom_affiliate_url": permalink,
                    "image": img, "thumbnail": img,
                    "custom_category_slug": cat_id,
                    "status": "active",
                    "fetched_at": utc_now_iso(),
                    "source": "ml_api_rotation"
                })
    except Exception as e:
        log.warning(f"  Erro na coleta: {str(e)[:80]}")
    return products

def main():
    log.info("=" * 60)
    log.info("🔍 FETCH REAL (ROTAÇÃO) — Iniciando coleta")
    log.info("=" * 60)

    # Carregar base existente
    db_path = os.path.join(DATA_DIR, "all_products.json")
    existing = []
    if os.path.exists(db_path):
        with open(db_path, encoding="utf-8") as f:
            existing = json.load(f)
    existing_ids = {p.get("id") for p in existing if p.get("id")}

    # Selecionar 12 queries aleatórias para esta rodada
    current_batch = random.sample(MASTER_QUERIES, min(12, len(MASTER_QUERIES)))
    all_new = []

    for cat in current_batch:
        log.info(f"\n🔍 Query: {cat['q']}")
        products = fetch_from_ml_api(cat['q'], cat['id'])
        new_for_cat = [p for p in products if p.get("id") and p["id"] not in existing_ids]
        all_new.extend(new_for_cat)
        for p in new_for_cat: existing_ids.add(p["id"])
        log.info(f"   ↳ {len(products)} coletados | {len(new_for_cat)} novos")
        time.sleep(1)

    if all_new:
        merged = existing + all_new
        # Salvar em ambos os locais para redundância
        for p in [os.path.join(DATA_DIR, "all_products.json"), os.path.join(DATABASE_DIR, "all_products.json")]:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
        
        with open(os.path.join(DATA_DIR, "new_offers.json"), "w", encoding="utf-8") as f:
            json.dump(all_new, f, indent=2, ensure_ascii=False)
        log.info(f"\n✅ Sucesso: {len(all_new)} novos produtos. Total: {len(merged)}")
    else:
        log.warning("\n⚠️ Nenhum produto novo coletado.")

if __name__ == "__main__":
    main()
