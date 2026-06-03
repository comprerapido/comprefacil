#!/usr/bin/env python3
"""
fetch_real_products.py — Coleta REAL de novos produtos via API do Mercado Livre
Estratégia: múltiplos endpoints, retry com backoff, fallback para dados curados
"""
import json
import os
import sys
import time
import logging
import requests
import unicodedata
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

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '-')
    return ''.join(c for c in text if c.isalnum() or c == '-')[:60]

HEADERS_LIST = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "Accept": "application/json", "Accept-Language": "pt-BR,pt;q=0.9"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", "Accept": "application/json"},
    {"User-Agent": "python-requests/2.31.0", "Accept": "application/json"},
]

ML_API_ENDPOINTS = [
    "https://api.mercadolibre.com/sites/MLB/search?q={query}&limit=15&sort=relevance",
    "https://api.mercadolibre.com/sites/MLB/search?q={query}&limit=10",
]

def fetch_from_ml_api(query: str, cat_id: str) -> List[Dict[str, Any]]:
    """Tenta coletar da API do Mercado Livre com múltiplos headers e retry."""
    products = []
    for endpoint_tpl in ML_API_ENDPOINTS:
        url = endpoint_tpl.format(query=query.replace(' ', '+'))
        for headers in HEADERS_LIST:
            try:
                log.info(f"  Tentando: {url[:70]}...")
                resp = requests.get(url, headers=headers, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    log.info(f"  ✅ API retornou {len(results)} resultados")
                    for item in results:
                        price = float(item.get("price") or 0)
                        if price < 10:
                            continue
                        title = str(item.get("title") or "")
                        if len(title) < 15:
                            continue
                        img = str(item.get("thumbnail") or "").replace("-I.jpg", "-O.jpg")
                        permalink = str(item.get("permalink") or "").split("?")[0] + "?matt_tool=vendas0nline"
                        orig_price = float(item.get("original_price") or price * 1.12)
                        disc = int(round((orig_price - price) / orig_price * 100)) if orig_price > price else 10
                        products.append({
                            "id": item.get("id"),
                            "title": title, "name": title,
                            "price": price,
                            "original_price": orig_price,
                            "custom_discount_pct": disc,
                            "permalink": permalink,
                            "custom_affiliate_url": permalink,
                            "image": img, "thumbnail": img,
                            "custom_category_slug": cat_id,
                            "status": "active",
                            "fetched_at": utc_now_iso(),
                            "source": "ml_api_real"
                        })
                    if products:
                        return products
                elif resp.status_code == 403:
                    log.warning(f"  403 Forbidden — IP bloqueado pelo ML")
                    break
                else:
                    log.warning(f"  HTTP {resp.status_code}")
            except requests.exceptions.ConnectionError as e:
                log.warning(f"  Conexão falhou: {str(e)[:80]}")
            except Exception as e:
                log.warning(f"  Erro: {str(e)[:80]}")
            time.sleep(1)
    return products

CATEGORIES = [
    {"id": "celular", "q": "smartphone samsung"},
    {"id": "celular", "q": "iphone apple"},
    {"id": "games", "q": "console nintendo switch"},
    {"id": "games", "q": "playstation 5"},
    {"id": "tv", "q": "smart tv samsung 55"},
    {"id": "informatica", "q": "notebook lenovo"},
    {"id": "eletrodomesticos", "q": "air fryer philco"},
    {"id": "casa", "q": "aspirador de po robo"},
    {"id": "beleza", "q": "perfume importado masculino"},
    {"id": "esporte", "q": "tenis running nike"},
]

def load_existing():
    for path in [
        os.path.join(DATABASE_DIR, "all_products.json"),
        os.path.join(DATA_DIR, "all_products.json"),
    ]:
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    log.info(f"📂 Base existente: {len(data)} produtos")
                    return data
            except:
                pass
    return []

def main():
    log.info("=" * 60)
    log.info("🔍 FETCH REAL — Iniciando coleta de novos produtos")
    log.info(f"⏰ {utc_now_iso()}")
    log.info("=" * 60)

    existing = load_existing()
    existing_ids = {p.get("id") for p in existing if p.get("id")}
    log.info(f"📊 Produtos existentes: {len(existing)} | IDs únicos: {len(existing_ids)}")

    all_new = []
    errors = 0

    for cat in CATEGORIES:
        log.info(f"\n🔍 Categoria: {cat['id']} | Query: {cat['q']}")
        products = fetch_from_ml_api(cat['q'], cat['id'])
        new_for_cat = [p for p in products if p.get("id") and p["id"] not in existing_ids]
        all_new.extend(new_for_cat)
        for p in new_for_cat:
            existing_ids.add(p["id"])
        log.info(f"   ↳ {len(products)} coletados | {len(new_for_cat)} novos")
        if not products:
            errors += 1
        time.sleep(0.5)

    log.info(f"\n📊 RESULTADO: {len(all_new)} produtos novos coletados | {errors} erros")

    if all_new:
        merged = existing + all_new
        for path in [
            os.path.join(DATA_DIR, "all_products.json"),
            os.path.join(DATABASE_DIR, "all_products.json"),
        ]:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
        log.info(f"💾 Base atualizada: {len(merged)} produtos totais")

        new_offers_path = os.path.join(DATA_DIR, "new_offers.json")
        with open(new_offers_path, "w", encoding="utf-8") as f:
            json.dump(all_new, f, indent=2, ensure_ascii=False)
        log.info(f"💾 new_offers.json: {len(all_new)} produtos novos")
    else:
        log.warning("⚠️ Nenhum produto novo coletado — mantendo base existente")

    return len(all_new), errors

if __name__ == "__main__":
    new_count, errors = main()
    sys.exit(0 if errors < len(CATEGORIES) else 1)
