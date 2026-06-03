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
    
    # Remover arquivos HTML de produtos que não estão mais no catálogo (Otimização de Git)
    valid_ids = {p.get('id') for p in products if p.get('id')}
    prod_dir = 'produtos'
    if os.path.exists(prod_dir):
        import shutil
        for cat in os.listdir(prod_dir):
            cat_path = os.path.join(prod_dir, cat)
            if os.path.isdir(cat_path):
                for p_folder in os.listdir(cat_path):
                    # O ID do produto costuma ser o final do slug da pasta
                    p_id = p_folder.split('-')[-1]
                    if p_id not in valid_ids:
                        full_p_path = os.path.join(cat_path, p_folder)
                        print(f"Removendo produto antigo: {p_folder}")
                        shutil.rmtree(full_p_path)
            
    print(f"Limpeza concluída: {initial_count} -> {len(products)} produtos.")

if __name__ == "__main__":
    main()
