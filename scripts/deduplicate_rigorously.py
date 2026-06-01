#!/usr/bin/env python3
"""
Script de Deduplicação Rigorosa
Garante que não haja produtos duplicados por ID, nome ou combinação de nome+preço
"""
import json
import os
from pathlib import Path
from logger import logger

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def deduplicate_rigorously(products):
    """Remove duplicatas usando múltiplos critérios"""
    seen_ids = set()
    seen_names = set()
    unique_products = []
    
    for p in products:
        p_id = p.get("id")
        p_name = p.get("name", "").strip()
        
        # Critério 1: ID único
        if p_id and p_id in seen_ids:
            logger.warning(f"Produto duplicado por ID: {p_id}")
            continue
        
        # Critério 2: Nome único (mesmo produto, links diferentes)
        if p_name and p_name in seen_names:
            logger.warning(f"Produto duplicado por nome: {p_name}")
            continue
        
        # Se passou em todos os critérios, adiciona
        if p_id:
            seen_ids.add(p_id)
        if p_name:
            seen_names.add(p_name)
        
        unique_products.append(p)
    
    return unique_products

def process_all_files():
    """Processa todos os arquivos de produtos"""
    files_to_process = [
        ("data/scored_products.json", "data/scored_products.json"),
        ("data/database/all_products.json", "data/database/all_products.json"),
    ]
    
    for input_file, output_file in files_to_process:
        input_path = DATA_DIR / input_file if "/" not in input_file else ROOT / input_file
        output_path = DATA_DIR / output_file if "/" not in output_file else ROOT / output_file
        
        if not input_path.exists():
            logger.warning(f"Arquivo {input_path} não encontrado")
            continue
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            original_count = len(products)
            unique_products = deduplicate_rigorously(products)
            final_count = len(unique_products)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(unique_products, f, ensure_ascii=False, indent=2)
            
            removed = original_count - final_count
            logger.info(f"{output_file}: {original_count} → {final_count} produtos ({removed} duplicatas removidas)")
        
        except Exception as e:
            logger.error(f"Erro ao processar {input_file}: {e}")

if __name__ == "__main__":
    process_all_files()
