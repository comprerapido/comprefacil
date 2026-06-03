import json
import os
from datetime import datetime, timedelta

def main():
    db_path = 'data/database/all_products.json'
    all_path = 'data/all_products.json'
    
    if not os.path.exists(db_path):
        return
        
    with open(db_path, 'r') as f:
        products = json.load(f)
    
    initial_count = len(products)
    
    # Manter apenas produtos com fetch nos últimos 30 dias ou os 100 mais recentes
    # Para este site, vamos manter os 120 mais recentes para garantir volume de páginas
    products.sort(key=lambda x: x.get('fetched_at', ''), reverse=True)
    products = products[:120]
    
    # Salvar bases limpas
    for path in [db_path, all_path]:
        with open(path, 'w') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
            
    print(f"Limpeza concluída: {initial_count} -> {len(products)} produtos.")

if __name__ == "__main__":
    main()
