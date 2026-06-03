#!/usr/bin/env python3
"""
product_intelligence.py — Inteligência avançada de produto.
Calcula nota de qualidade, histórico de preços e detecta promoções reais.
"""

import os
import json
import time
from pathlib import Path
from logger import logger
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]
HISTORY_DIR = ROOT / "data" / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def calculate_quality_score(product: Dict[str, Any]) -> float:
    """Calcula uma nota de 0 a 10 baseada em múltiplos fatores."""
    score = 5.0 # Base
    
    # 1. Desconto (até +2.0)
    discount = product.get('custom_discount_pct', 0)
    if discount > 50: score += 2.0
    elif discount > 30: score += 1.5
    elif discount > 15: score += 1.0
    
    # 2. Completude de dados (até +1.5)
    if product.get('generated_description'): score += 0.5
    if product.get('image') and not product.get('image').startswith('http'): score += 0.5 # Imagem local
    if len(product.get('name', '')) > 40: score += 0.5
    
    # 3. Preço (bonus para produtos populares/acessíveis)
    price = product.get('price', 0)
    if 50 <= price <= 500: score += 0.5
    
    # 4. Status
    if product.get('status') == 'expired': score -= 4.0
    
    return min(10.0, max(0.0, round(score, 1)))

def update_price_history(product: Dict[str, Any]):
    """Atualiza o histórico de preços do produto."""
    p_id = product.get('id')
    if not p_id: return
    
    history_file = HISTORY_DIR / f"{p_id}.json"
    current_price = product.get('price', 0)
    current_time = time.strftime('%Y-%m-%d', time.gmtime())
    
    history = []
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except: pass
    
    # Adicionar novo registro se o preço mudou ou se é um novo dia
    if not history or history[-1]['price'] != current_price or history[-1]['date'] != current_time:
        history.append({
            "date": current_time,
            "price": current_price
        })
        # Manter apenas os últimos 30 registros
        history = history[-30:]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    
    # Calcular se é promoção real (abaixo da média)
    if len(history) > 1:
        avg_price = sum(h['price'] for h in history) / len(history)
        product['is_real_promotion'] = current_price < avg_price
        product['price_history_count'] = len(history)
        product['min_price'] = min(h['price'] for h in history)
    else:
        product['is_real_promotion'] = product.get('custom_discount_pct', 0) > 10
        product['price_history_count'] = 1
        product['min_price'] = current_price

def process_intelligence(json_path: str):
    """Aplica inteligência a todos os produtos no JSON."""
    if not os.path.exists(json_path):
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    for p in products:
        update_price_history(p)
        p['quality_score'] = calculate_quality_score(p)
    
    # Salvar atualizações
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Inteligência de produto aplicada a {len(products)} itens.")

if __name__ == "__main__":
    process_intelligence(str(ROOT / "data" / "database" / "all_products.json"))
    process_intelligence(str(ROOT / "data" / "scored_products.json"))
