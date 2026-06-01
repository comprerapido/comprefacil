#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def update_all_products_database():
    """Copia scored_products.json para all_products.json para sincronizar com app.js"""
    scored_file = DATA_DIR / "scored_products.json"
    database_dir = DATA_DIR / "database"
    all_products_file = database_dir / "all_products.json"
    
    database_dir.mkdir(exist_ok=True)
    
    if not scored_file.exists():
        print(f"❌ Arquivo {scored_file} não encontrado")
        return False
    
    try:
        with open(scored_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        with open(all_products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Database atualizado: {len(products)} produtos sincronizados")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar database: {e}")
        return False

if __name__ == "__main__":
    update_all_products_database()
