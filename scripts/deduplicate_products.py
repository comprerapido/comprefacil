#!/usr/bin/env python3
import json
import difflib
import os
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def get_similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate(similarity_threshold=0.85):
    products_file = DATA_DIR / "all_products.json"
    if not products_file.exists(): return 0, 0, []

    with open(products_file, 'r') as f:
        products = json.load(f)

    initial_count = len(products)
    products.sort(key=lambda x: len(x.get('name') or x.get('title') or ""), reverse=True)
    
    unique_products = []
    removed_examples = []
    processed_ids = set()
    
    for p_current in products:
        current_id = p_current.get('id')
        if current_id in processed_ids: continue
        t_current = (p_current.get('name') or p_current.get('title') or "").lower()
        is_dupe = False
        for p_unique in unique_products:
            t_unique = (p_unique.get('name') or p_unique.get('title') or "").lower()
            sim = get_similarity(t_current, t_unique)
            is_sub = (len(t_current) > 20 and len(t_unique) > 20) and (t_current in t_unique or t_unique in t_current)
            if sim >= similarity_threshold or is_sub:
                is_dupe = True
                removed_examples.append({"kept": p_unique.get('name') or p_unique.get('title'), "removed": p_current.get('name') or p_current.get('title')})
                break
        if not is_dupe:
            unique_products.append(p_current)
            processed_ids.add(current_id)

    with open(products_file, 'w') as f:
        json.dump(unique_products, f, indent=2, ensure_ascii=False)
    return initial_count - len(unique_products), len(unique_products), removed_examples

if __name__ == "__main__":
    removed, final, examples = deduplicate()
    print(f"Deduplicação: {removed} removidos, {final} únicos.")
