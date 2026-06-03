#!/usr/bin/env python3
"""
verify_links_health.py — Verificador de Saúde do Catálogo
Valida se os produtos ainda existem e estão ativos no Mercado Livre.
"""
import json
import os
import requests
import time
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("HealthCheck")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_DIR = os.path.join(DATA_DIR, "database")

def check_link(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    try:
        # Request HEAD é mais rápido e consome menos banda
        resp = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        # Se 404 ou 410, o produto sumiu
        if resp.status_code in [404, 410]:
            return False
        return True
    except:
        return True # Em caso de erro de rede, manter o produto para não remover por falso positivo

def main():
    db_path = os.path.join(DATABASE_DIR, "all_products.json")
    if not os.path.exists(db_path):
        return

    with open(db_path, 'r') as f:
        products = json.load(f)

    log.info(f"Iniciando verificação de saúde para {len(products)} produtos...")
    
    active_products = []
    removed_count = 0
    
    # Verificar apenas uma amostra ou produtos mais antigos para economizar tempo
    # Aqui vamos verificar todos, mas com delay curto
    for p in products:
        url = p.get('permalink')
        if not url:
            removed_count += 1
            continue
            
        if check_link(url):
            active_products.append(p)
        else:
            log.info(f"🚫 Removendo produto expirado: {p.get('id')} - {p.get('title')[:40]}")
            removed_count += 1
        
        time.sleep(0.1) # Delay curto

    if removed_count > 0:
        log.info(f"Limpeza concluída. {removed_count} produtos removidos.")
        # Salvar base atualizada
        all_path = os.path.join(DATA_DIR, "all_products.json")
        for path in [db_path, all_path]:
            with open(path, 'w') as f:
                json.dump(active_products, f, indent=2, ensure_ascii=False)
    else:
        log.info("Todos os produtos estão saudáveis.")

if __name__ == "__main__":
    main()
