#!/usr/bin/env python3
import json
import difflib
import os
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def get_similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def clean():
    files_to_clean = ["all_products.json", "quality_products.json", "scored_products.json", "real_promotions.json", "new_offers.json", "homepage_products.json"]
    
    main_file = DATA_DIR / "all_products.json"
    if not main_file.exists(): return
        
    with open(main_file, 'r') as f:
        products = json.load(f)
        
    initial_count = len(products)
    
    filtered = []
    for p in products:
        title = (p.get('name') or p.get('title') or "").lower()
        if p.get('status') == 'expired': continue
        if 'teste' in title and 'auditoria' in title: continue
        filtered.append(p)
    
    filtered.sort(key=lambda x: len(x.get('name') or x.get('title') or ""), reverse=True)
    
    unique_products = []
    removed_examples = []
    
    for p in filtered:
        t_current = (p.get('name') or p.get('title') or "").lower()
        is_dupe = False
        
        for u in unique_products:
            t_unique = (u.get('name') or u.get('title') or "").lower()
            sim = get_similarity(t_current, t_unique)
            is_sub = (len(t_current) > 20 and len(t_unique) > 20) and (t_current in t_unique or t_unique in t_current)
            
            if sim >= 0.85 or is_sub:
                is_dupe = True
                removed_examples.append({"kept": u.get('name') or u.get('title'), "removed": p.get('name') or p.get('title')})
                break
        
        if not is_dupe:
            unique_products.append(p)

    for filename in files_to_clean:
        path = DATA_DIR / filename
        if path.exists():
            with open(path, 'r') as f:
                current_data = json.load(f)
            unique_ids = {p.get('id') for p in unique_products}
            new_data = [p for p in current_data if p.get('id') in unique_ids]
            with open(path, 'w') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)

    print(f"Limpeza concluída: {initial_count - len(unique_products)} removidos. Total único: {len(unique_products)}")

if __name__ == "__main__":
    clean()
