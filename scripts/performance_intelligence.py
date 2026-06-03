#!/usr/bin/env python3
"""
Performance Intelligence - Sistema de detecção de baixo desempenho e atualização automática.

Responsabilidades:
- Identificar páginas com baixo desempenho
- Detectar oportunidades de palavras-chave
- Gerar novas páginas quando identificar demanda
- Priorizar conteúdos com maior potencial de tráfego
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def analyze_page_performance() -> Dict[str, Any]:
    """Analisa desempenho das páginas geradas."""
    analysis = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pages_analyzed": 0,
        "low_performance_pages": [],
        "recommendations": []
    }
    
    # Contar páginas por tipo
    page_counts = {
        "products": len(list((ROOT / "produtos").glob("*/index.html"))) if (ROOT / "produtos").exists() else 0,
        "categories": len(list((ROOT / "categorias").glob("*/index.html"))) if (ROOT / "categorias").exists() else 0,
        "guides": len(list((ROOT / "guias").glob("*/index.html"))) if (ROOT / "guias").exists() else 0,
        "comparisons": len(list((ROOT / "comparacoes").glob("*/index.html"))) if (ROOT / "comparacoes").exists() else 0,
        "articles": len(list((ROOT / "noticias").glob("*/index.html"))) if (ROOT / "noticias").exists() else 0,
    }
    
    analysis["pages_analyzed"] = sum(page_counts.values())
    analysis["page_counts"] = page_counts
    
    # Detectar páginas rasas (thin content)
    thin_content_pages = []
    for page_type, count in page_counts.items():
        if page_type == "products" and count < 10:
            thin_content_pages.append(f"Apenas {count} páginas de produtos geradas (esperado: 50+)")
        elif page_type == "guides" and count < 5:
            thin_content_pages.append(f"Apenas {count} guias gerados (esperado: 8+)")
    
    analysis["low_performance_pages"] = thin_content_pages
    
    # Recomendações
    if page_counts["products"] < 50:
        analysis["recommendations"].append(
            "Aumentar quantidade de produtos na base de dados ou melhorar critérios de filtragem"
        )
    
    if page_counts["guides"] < 8:
        analysis["recommendations"].append(
            "Gerar mais guias de compra por categoria para melhorar cobertura SEO"
        )
    
    if page_counts["comparisons"] < 20:
        analysis["recommendations"].append(
            "Criar mais comparações automáticas entre produtos populares"
        )
    
    return analysis


def detect_keyword_opportunities() -> Dict[str, Any]:
    """Detecta oportunidades de palavras-chave não cobertas."""
    opportunities = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uncovered_keywords": [],
        "high_potential_keywords": []
    }
    
    # Palavras-chave comuns em e-commerce que devem ter cobertura
    common_keywords = [
        "melhor preço",
        "promoção",
        "desconto",
        "oferta do dia",
        "comparação",
        "análise",
        "guia de compra",
        "melhores produtos",
        "tendências",
    ]
    
    # Verificar se existem páginas para cada categoria de palavra-chave
    page_types = {
        "melhor preço": (ROOT / "melhores-2026").exists(),
        "promoção": (ROOT / "ofertas-hoje").exists(),
        "desconto": (ROOT / "ofertas-hoje").exists(),
        "oferta do dia": (ROOT / "ofertas-hoje").exists(),
        "comparação": (ROOT / "comparacoes").exists(),
        "análise": (ROOT / "produtos").exists(),
        "guia de compra": (ROOT / "guias").exists(),
        "melhores produtos": (ROOT / "melhores-2026").exists(),
        "tendências": (ROOT / "noticias").exists(),
    }
    
    for keyword, has_coverage in page_types.items():
        if not has_coverage:
            opportunities["uncovered_keywords"].append(keyword)
    
    # Palavras-chave com alto potencial
    opportunities["high_potential_keywords"] = [
        "como escolher",
        "qual é o melhor",
        "vale a pena",
        "preço justo",
        "alternativas",
        "vs comparação",
    ]
    
    return opportunities


def identify_update_candidates() -> Dict[str, Any]:
    """Identifica páginas que devem ser atualizadas."""
    candidates = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pages_to_update": [],
        "new_pages_to_create": []
    }
    
    # Páginas antigas (mais de 7 dias) devem ser revisadas
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    # Verificar última atualização de arquivos críticos
    critical_pages = [
        ("index.html", "Homepage"),
        ("ofertas-hoje/index.html", "Ofertas do dia"),
        ("melhores-2026/index.html", "Melhores de 2026"),
    ]
    
    for page_path, page_name in critical_pages:
        full_path = ROOT / page_path
        if full_path.exists():
            mtime = datetime.fromtimestamp(full_path.stat().st_mtime, tz=timezone.utc)
            if mtime < seven_days_ago:
                candidates["pages_to_update"].append({
                    "page": page_name,
                    "path": page_path,
                    "last_modified": mtime.isoformat(),
                    "reason": "Página antiga, recomenda-se atualização"
                })
    
    # Páginas novas que devem ser criadas
    candidates["new_pages_to_create"] = [
        {
            "type": "seasonal_content",
            "suggestion": "Criar páginas de tendências sazonais (ex: 'Melhores ofertas de inverno')",
            "priority": "medium"
        },
        {
            "type": "evergreen_content",
            "suggestion": "Expandir conteúdo evergreen com guias de manutenção e dicas de compra",
            "priority": "high"
        },
        {
            "type": "comparison_pages",
            "suggestion": "Criar mais páginas de comparação entre marcas populares",
            "priority": "medium"
        }
    ]
    
    return candidates


def generate_content_strategy() -> Dict[str, Any]:
    """Gera estratégia de conteúdo baseada em análise."""
    strategy = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "performance": analyze_page_performance(),
        "keywords": detect_keyword_opportunities(),
        "update_candidates": identify_update_candidates(),
        "action_plan": []
    }
    
    # Plano de ação
    if strategy["performance"]["low_performance_pages"]:
        strategy["action_plan"].append({
            "priority": "high",
            "action": "Aumentar volume de conteúdo",
            "details": strategy["performance"]["recommendations"]
        })
    
    if strategy["keywords"]["uncovered_keywords"]:
        strategy["action_plan"].append({
            "priority": "high",
            "action": "Cobrir palavras-chave não atendidas",
            "keywords": strategy["keywords"]["uncovered_keywords"]
        })
    
    if strategy["update_candidates"]["pages_to_update"]:
        strategy["action_plan"].append({
            "priority": "medium",
            "action": "Atualizar páginas antigas",
            "pages": strategy["update_candidates"]["pages_to_update"]
        })
    
    return strategy


def main():
    """Executa análise de inteligência de desempenho."""
    DATA_DIR.mkdir(exist_ok=True)
    
    strategy = generate_content_strategy()
    
    # Salvar relatório
    report_path = DATA_DIR / "performance_intelligence.json"
    report_path.write_text(json.dumps(strategy, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(json.dumps(strategy, indent=2, ensure_ascii=False))
    
    return strategy


if __name__ == "__main__":
    main()
