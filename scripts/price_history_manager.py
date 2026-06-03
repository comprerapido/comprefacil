#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(BASE_DIR, "data", "price_history.json")

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def update_history(products):
    history = load_history()
    now = datetime.now(timezone.utc).isoformat()
    
    for p in products:
        pid = p.get("id")
        price = p.get("price")
        if not pid or not price: continue
        
        if pid not in history:
            history[pid] = []
        
        # Adicionar novo registro se o preço mudou ou se não há registros
        if not history[pid] or history[pid][-1]["price"] != price:
            history[pid].append({"price": price, "date": now})
            # Manter apenas os últimos 10 registros por produto
            history[pid] = history[pid][-10:]
            
    save_history(history)
    return history

def get_is_real_deal(product_id, current_price, history):
    if product_id not in history or len(history[product_id]) < 2:
        return False
    
    prices = [h["price"] for h in history[product_id]]
    min_price = min(prices)
    # É uma oferta real se o preço atual for a mínima histórica
    return current_price <= min_price

if __name__ == "__main__":
    # Teste simples
    all_products_path = os.path.join(BASE_DIR, "data", "all_products.json")
    if os.path.exists(all_products_path):
        with open(all_products_path) as f:
            products = json.load(f)
            update_history(products)
            print("Histórico de preços atualizado.")
