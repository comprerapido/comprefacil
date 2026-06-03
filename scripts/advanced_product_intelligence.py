#!/usr/bin/env python3
"""
Advanced Product Intelligence - Aprimoramento de scraping, detecção de promoções reais,
filtros de qualidade e histórico de preços.

Responsabilidades:
- Melhorar scraping de produtos
- Detectar promoções reais (comparar com histórico)
- Filtrar produtos de baixa qualidade
- Priorizar por avaliações e volume de vendas
- Ignorar anúncios suspeitos
- Manter histórico de preços
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_json(path: Path, default: Any = None) -> Any:
    """Carrega arquivo JSON com fallback."""
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except:
        return default


def save_json(path: Path, data: Any) -> None:
    """Salva dados em JSON."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def detect_real_promotions(products: List[Dict]) -> Dict[str, Any]:
    """Detecta promoções reais comparando com histórico de preços."""
    promotions = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "real_promotions": [],
        "suspicious_promotions": [],
        "analysis": {}
    }
    
    price_history = load_json(DATA_DIR / "price_history.json", {})
    if isinstance(price_history, list):
        price_history = {}  # Converter se for lista antiga
    
    for product in products:
        product_id = product.get("id")
        current_price = product.get("price", 0)
        original_price = product.get("original_price", current_price)
        
        if not product_id or current_price <= 0:
            continue
        
        # Verificar histórico
        product_history_data = price_history.get(product_id, {})
        if not isinstance(product_history_data, dict):
            product_history_data = {}
        history = product_history_data.get("history", [])
        
        if history:
            # Comparar com preço anterior
            previous_price = history[-1].get("price") if history else original_price
            
            # Promoção real: preço atual é significativamente menor
            discount_pct = ((previous_price - current_price) / previous_price * 100) if previous_price > 0 else 0
            
            if discount_pct > 5:  # Mais de 5% de desconto
                promotions["real_promotions"].append({
                    "id": product_id,
                    "name": product.get("name"),
                    "current_price": current_price,
                    "previous_price": previous_price,
                    "discount_percent": round(discount_pct, 2),
                    "is_real": True
                })
            elif discount_pct > 0:
                promotions["suspicious_promotions"].append({
                    "id": product_id,
                    "name": product.get("name"),
                    "discount_percent": round(discount_pct, 2),
                    "reason": "Desconto muito pequeno ou preço original inflado"
                })
        else:
            # Sem histórico, usar original_price como referência
            if original_price > current_price:
                discount_pct = ((original_price - current_price) / original_price * 100)
                if discount_pct > 5:
                    promotions["real_promotions"].append({
                        "id": product_id,
                        "name": product.get("name"),
                        "current_price": current_price,
                        "original_price": original_price,
                        "discount_percent": round(discount_pct, 2),
                        "is_real": True
                    })
    
    promotions["analysis"] = {
        "total_real_promotions": len(promotions["real_promotions"]),
        "total_suspicious": len(promotions["suspicious_promotions"]),
        "real_promotion_percentage": round(
            len(promotions["real_promotions"]) / len(products) * 100, 2
        ) if products else 0
    }
    
    return promotions


def filter_quality_products(products: List[Dict]) -> Dict[str, Any]:
    """Filtra produtos de baixa qualidade."""
    quality_analysis = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_products": len(products),
        "quality_products": [],
        "rejected_products": [],
        "quality_score_distribution": defaultdict(int)
    }
    
    for product in products:
        score = calculate_quality_score(product)
        
        quality_analysis["quality_score_distribution"][f"score_{int(score)}"] += 1
        
        if score >= 60:  # Produtos com score >= 60 são considerados de qualidade
            quality_analysis["quality_products"].append({
                "id": product.get("id"),
                "name": product.get("name"),
                "score": score,
                "rating": product.get("rating", 0),
                "reviews": product.get("reviews_count", 0),
                "price": product.get("price", 0)
            })
        else:
            quality_analysis["rejected_products"].append({
                "id": product.get("id"),
                "name": product.get("name"),
                "score": score,
                "reason": get_rejection_reason(product, score)
            })
    
    quality_analysis["quality_percentage"] = round(
        len(quality_analysis["quality_products"]) / len(products) * 100, 2
    ) if products else 0
    
    return quality_analysis


def calculate_quality_score(product: Dict) -> float:
    """Calcula score de qualidade do produto."""
    score = 50  # Base score
    
    # Rating (até 30 pontos)
    rating = product.get("rating", 0)
    if rating >= 4.5:
        score += 30
    elif rating >= 4.0:
        score += 25
    elif rating >= 3.5:
        score += 15
    elif rating >= 3.0:
        score += 10
    
    # Número de avaliações (até 15 pontos)
    reviews = product.get("reviews_count", 0)
    if reviews >= 100:
        score += 15
    elif reviews >= 50:
        score += 10
    elif reviews >= 20:
        score += 5
    
    # Preço válido (até 10 pontos)
    price = product.get("price", 0)
    if 10 <= price <= 10000:
        score += 10
    
    # Descrição presente (até 5 pontos)
    description = product.get("description", "")
    if description and len(description) > 50:
        score += 5
    
    # Penalidades
    # Suspeita de anúncio
    if is_suspicious_ad(product):
        score -= 30
    
    # Preço muito baixo ou muito alto
    if price < 1 or price > 100000:
        score -= 20
    
    return max(0, min(100, score))


def is_suspicious_ad(product: Dict) -> bool:
    """Detecta anúncios suspeitos."""
    suspicious_keywords = [
        "clique aqui",
        "compre agora",
        "oferta limitada",
        "ganhe dinheiro",
        "trabalhe de casa",
        "curso online",
        "ebook",
        "dropshipping",
    ]
    
    name = (product.get("name") or "").lower()
    description = (product.get("description") or "").lower()
    
    for keyword in suspicious_keywords:
        if keyword in name or keyword in description:
            return True
    
    # Verificar se parece spam
    if name and (name.count("!!!") > 2 or name.count("***") > 2):
        return True
    
    return False


def get_rejection_reason(product: Dict, score: float) -> str:
    """Retorna motivo da rejeição do produto."""
    if is_suspicious_ad(product):
        return "Anúncio suspeito detectado"
    
    rating = product.get("rating", 0)
    if rating < 3.0:
        return f"Rating muito baixo ({rating})"
    
    reviews = product.get("reviews_count", 0)
    if reviews < 5:
        return "Pouquíssimas avaliações"
    
    price = product.get("price", 0)
    if price < 1 or price > 100000:
        return f"Preço fora do intervalo válido (R$ {price})"
    
    return f"Score de qualidade insuficiente ({score:.1f})"


def prioritize_by_demand(products: List[Dict]) -> List[Dict]:
    """Prioriza produtos por volume de vendas e avaliações."""
    def demand_score(product: Dict) -> float:
        # Score baseado em: avaliações + volume de vendas estimado
        rating = product.get("rating", 0)
        reviews = product.get("reviews_count", 0)
        
        # Estimativa de volume: reviews * rating
        estimated_volume = reviews * (rating / 5)
        
        return estimated_volume
    
    return sorted(products, key=demand_score, reverse=True)


def update_price_history_advanced(products: List[Dict]) -> Dict[str, Any]:
    """Atualiza histórico de preços com análise avançada."""
    history = load_json(DATA_DIR / "price_history.json", {})
    if isinstance(history, list):
        history = {}  # Converter se for lista antiga
    today = datetime.now(timezone.utc).date().isoformat()
    
    for product in products:
        product_id = product.get("id")
        if not product_id:
            continue
        
        if product_id not in history:
            history[product_id] = {
                "name": product.get("name"),
                "history": []
            }
        
        # Garantir que é dict
        if not isinstance(history[product_id], dict):
            history[product_id] = {"name": product.get("name"), "history": []}
        
        current_price = product.get("price", 0)
        product_hist = history[product_id].get("history", [])
        last_entry = product_hist[-1] if product_hist else None
        
        # Adicionar nova entrada se preço mudou ou é novo dia
        if not last_entry or last_entry.get("date") != today or last_entry.get("price") != current_price:
            history[product_id]["history"].append({
                "date": today,
                "price": current_price,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Manter apenas últimos 90 dias
        history[product_id]["history"] = history[product_id]["history"][-90:]
    
    return history


def main():
    """Executa análise avançada de produtos."""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Carregar produtos
    products = load_json(DATA_DIR / "all_products.json", [])
    if not isinstance(products, list):
        print("Erro: all_products.json não contém lista")
        return
    
    print(f"Analisando {len(products)} produtos...")
    
    # Análise 1: Detecção de promoções reais
    promotions = detect_real_promotions(products)
    save_json(DATA_DIR / "real_promotions_analysis.json", promotions)
    print(f"✓ {len(promotions['real_promotions'])} promoções reais detectadas")
    
    # Análise 2: Filtro de qualidade
    quality = filter_quality_products(products)
    save_json(DATA_DIR / "quality_analysis.json", quality)
    print(f"✓ {len(quality['quality_products'])} produtos de qualidade aprovados")
    
    # Análise 3: Priorização por demanda
    prioritized = prioritize_by_demand(quality["quality_products"])
    save_json(DATA_DIR / "prioritized_products.json", prioritized)
    print(f"✓ Produtos priorizados por demanda")
    
    # Análise 4: Histórico de preços
    price_history = update_price_history_advanced(products)
    save_json(DATA_DIR / "price_history_advanced.json", price_history)
    print(f"✓ Histórico de preços atualizado para {len(price_history)} produtos")
    
    return {
        "promotions": promotions,
        "quality": quality,
        "prioritized_count": len(prioritized),
        "price_history_count": len(price_history)
    }


if __name__ == "__main__":
    result = main()
    print("\n" + json.dumps(result, indent=2, ensure_ascii=False))
