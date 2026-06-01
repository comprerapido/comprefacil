import os
import json
import hashlib
import difflib
from typing import Dict, List, Set, Tuple
from logger import logger

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calcula a similaridade entre duas strings (0-1).
    1.0 = idênticas, 0.0 = completamente diferentes
    """
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def get_product_hash(product: Dict) -> str:
    """
    Gera um hash único para um produto baseado em características principais.
    Isso ajuda a identificar duplicatas mesmo com variações no nome.
    """
    name = product.get('name', '').lower().strip()
    price = str(product.get('price', 0))
    
    # Usar nome + preço como base para o hash
    hash_input = f"{name}|{price}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def normalize_product_name(name: str) -> str:
    """
    Normaliza o nome do produto removendo variações comuns.
    Ex: "Produto XYZ 128GB" e "Produto XYZ 128 GB" são o mesmo.
    """
    name = name.lower().strip()
    
    # Remover espaços extras
    name = ' '.join(name.split())
    
    # Normalizar variações comuns
    replacements = {
        'gb ': 'gb',
        'mb ': 'mb',
        'tb ': 'tb',
        'ghz ': 'ghz',
        'w ': 'w',
        'v ': 'v',
        '  ': ' ',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name

def is_duplicate(product1: Dict, product2: Dict, similarity_threshold: float = 0.85) -> bool:
    """
    Verifica se dois produtos são duplicatas.
    Considera nome, preço e categoria.
    """
    
    # Comparar nomes normalizados
    name1 = normalize_product_name(product1.get('name', ''))
    name2 = normalize_product_name(product2.get('name', ''))
    
    name_similarity = calculate_similarity(name1, name2)
    
    # Se os nomes são muito similares, é provável que seja duplicata
    if name_similarity >= similarity_threshold:
        return True
    
    # Comparar por ID (se existir)
    id1 = product1.get('id')
    id2 = product2.get('id')
    if id1 and id2 and id1 == id2:
        return True
    
    # Comparar por URL (se existir)
    url1 = product1.get('permalink', '')
    url2 = product2.get('permalink', '')
    if url1 and url2 and url1 == url2:
        return True
    
    return False

def deduplicate_products(products: List[Dict], keep_highest_discount: bool = True) -> Tuple[List[Dict], Dict]:
    """
    Remove duplicatas de uma lista de produtos.
    
    Args:
        products: Lista de produtos
        keep_highest_discount: Se True, mantém o produto com maior desconto em caso de duplicata
    
    Returns:
        Tupla com (lista dedupplicada, dicionário de estatísticas)
    """
    
    if not products:
        return [], {"total": 0, "duplicates_found": 0, "unique": 0}
    
    logger.info(f"Iniciando deduplicação de {len(products)} produtos...")
    
    unique_products = []
    seen_hashes: Set[str] = set()
    duplicates_found = 0
    
    # Primeiro passo: remover por hash (duplicatas exatas)
    for product in products:
        product_hash = get_product_hash(product)
        
        if product_hash not in seen_hashes:
            seen_hashes.add(product_hash)
            unique_products.append(product)
        else:
            duplicates_found += 1
            logger.debug(f"Duplicata exata encontrada: {product.get('name')}")
    
    logger.info(f"Após hash: {len(unique_products)} produtos únicos, {duplicates_found} duplicatas exatas removidas.")
    
    # Segundo passo: remover por similaridade de nome
    final_products = []
    removed_indices: Set[int] = set()
    
    for i, product1 in enumerate(unique_products):
        if i in removed_indices:
            continue
        
        final_products.append(product1)
        
        # Comparar com produtos subsequentes
        for j in range(i + 1, len(unique_products)):
            if j in removed_indices:
                continue
            
            product2 = unique_products[j]
            
            if is_duplicate(product1, product2):
                # Decidir qual manter
                if keep_highest_discount:
                    discount1 = product1.get('custom_discount_pct', 0)
                    discount2 = product2.get('custom_discount_pct', 0)
                    
                    if discount2 > discount1:
                        # Remover product1 e adicionar product2
                        final_products.pop()
                        final_products.append(product2)
                        removed_indices.add(i)
                    else:
                        removed_indices.add(j)
                else:
                    removed_indices.add(j)
                
                duplicates_found += 1
                logger.debug(f"Duplicata por similaridade: {product1.get('name')} vs {product2.get('name')}")
    
    stats = {
        "total_input": len(products),
        "duplicates_found": duplicates_found,
        "unique_output": len(final_products),
        "removal_rate": f"{(duplicates_found / len(products) * 100):.1f}%" if products else "0%"
    }
    
    logger.info(f"Deduplicação concluída: {stats['unique_output']} produtos únicos, {duplicates_found} duplicatas removidas ({stats['removal_rate']})")
    
    return final_products, stats

def process_deduplicate(input_path: str, output_path: str, keep_highest_discount: bool = True) -> None:
    """
    Processa um arquivo JSON de produtos e remove duplicatas.
    """
    
    if not os.path.exists(input_path):
        logger.error(f"Arquivo de entrada {input_path} não encontrado.")
        return
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler {input_path}: {e}")
        return
    
    # Deduplicate
    unique_products, stats = deduplicate_products(products, keep_highest_discount)
    
    # Salvar resultado
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unique_products, f, ensure_ascii=False, indent=2)
        logger.info(f"Resultados salvos em {output_path}")
        logger.info(f"Estatísticas: {stats}")
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    process_deduplicate(
        "data/products_with_content.json",
        "data/products_deduplicated.json",
        keep_highest_discount=True
    )
