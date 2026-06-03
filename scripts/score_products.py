import os
import json
from logger import logger

def calculate_score(product):
    discount_pct = product.get("custom_discount_pct", 0)
    price = product.get("price", 0)
    original_price = product.get("originalPrice", 0)

    # Pontuação baseada no percentual de desconto (maior desconto = maior pontuação)
    score = discount_pct * 10 # Multiplicador para dar mais peso ao desconto

    # Adicionar pontuação baseada no valor absoluto do desconto
    if original_price > 0:
        absolute_discount = original_price - price
        score += absolute_discount / 10 # Adiciona 1 ponto a cada R$10 de desconto absoluto

    # Priorizar produtos com mais de 20% de desconto
    if discount_pct >= 20:
        score += 50

    return score

def process(input_p, output_p):
    if not os.path.exists(input_p):
        products = []
    else:
        with open(input_p, "r", encoding="utf-8") as f:
            try:
                raw_data = json.load(f)
                # Filtro defensivo: Título, Preço válido e ID único
                products = []
                seen_ids = set()
                for p in raw_data:
                    p_id = p.get("id")
                    if p_id and p_id not in seen_ids and p.get("name") and p.get("price", 0) > 0:
                        p["score"] = calculate_score(p) # Calcula a pontuação
                        products.append(p)
                        seen_ids.add(p_id)
                
                # Ordenar produtos pela pontuação (maior primeiro)
                products.sort(key=lambda x: x.get("score", 0), reverse=True)
            except Exception as e:
                logger.error(f"Erro ao ler {input_p}: {e}")
                products = []

    os.makedirs(os.path.dirname(output_p), exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    logger.info(f"Scoring concluído: {len(products)} produtos válidos processados.")

if __name__ == "__main__":
    process("data/new_offers.json", "data/scored_products.json")
