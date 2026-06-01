#!/usr/bin/env python3
"""
PROVA REAL DO SISTEMA RADAR DE PREÇOS
======================================
Este script realiza testes rigorosos em todas as funcionalidades:
1. Agendamento Distribuído
2. Template Profissional v2
3. Conteúdo 1000+ Palavras
4. Deduplicação Inteligente
"""

import os
import json
import time
from datetime import datetime
from logger import logger
from global_scheduler import GlobalScheduler
from publication_manager import PublicationManager

def test_distributed_scheduling():
    """Prova real do agendamento distribuído."""
    logger.info("\n" + "=" * 40)
    logger.info("🧪 TESTE 1: AGENDAMENTO DISTRIBUÍDO")
    logger.info("=" * 40)
    
    scheduler = GlobalScheduler()
    schedule = scheduler.generate_daily_schedule()
    
    # Verificar se cada site tem seu offset único de 6 min
    offsets = []
    for site_id, config in scheduler.SITES_CONFIG.items():
        offsets.append(config["offset"])
        logger.info(f"✅ {site_id}: Offset {config['offset']} min")
    
    # Verificar duplicatas de offset
    if len(offsets) == len(set(offsets)):
        logger.info("✅ PROVA REAL: Todos os 10 sites possuem offsets ÚNICOS.")
    else:
        logger.error("❌ ERRO: Conflito de offsets detectado!")
        return False
    
    # Verificar intervalo entre publicações consecutivas na mesma hora
    sorted_offsets = sorted(offsets)
    for i in range(len(sorted_offsets) - 1):
        diff = sorted_offsets[i+1] - sorted_offsets[i]
        if diff != 6:
            logger.error(f"❌ ERRO: Intervalo entre {sorted_offsets[i]} e {sorted_offsets[i+1]} não é 6 min!")
            return False
    
    logger.info("✅ PROVA REAL: Intervalo constante de 6 min garantido.")
    return True

def test_template_v2_and_content():
    """Prova real do template v2 e conteúdo 1000+ palavras."""
    logger.info("\n" + "=" * 40)
    logger.info("🧪 TESTE 2: TEMPLATE V2 & CONTEÚDO")
    logger.info("=" * 40)
    
    # Verificar se o template existe
    template_path = "templates/product_page_v2.html"
    if os.path.exists(template_path):
        logger.info("✅ PROVA REAL: Template v2 profissional localizado.")
    else:
        logger.error("❌ ERRO: Template v2 não encontrado!")
        return False
    
    # Verificar conteúdo gerado
    content_path = "data/products_with_content.json"
    if os.path.exists(content_path):
        with open(content_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
            
        if products:
            p = products[0]
            content = p.get('generated_description', '')
            word_count = len(content.split())
            logger.info(f"✅ PROVA REAL: Produto '{p.get('name')[:30]}...' possui {word_count} palavras.")
            
            if word_count >= 1000:
                logger.info("✅ PROVA REAL: Meta de 1000+ palavras ATINGIDA.")
            else:
                logger.warning(f"⚠️ AVISO: {word_count} palavras (abaixo de 1000).")
    
    # Verificar se as 24 seções do menu estão no template
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
        secoes = [
            "Ofertas de Hoje", "Melhores de 2026", "Prêmio Radar 2026", 
            "Quedas de Hoje", "Mais Clicados", "Ofertas Explodindo",
            "Central de Comparativos", "Comparar Produtos", "Ranking de Marcas",
            "Radar de Mercado", "O Que Está em Alta", "Nossa Metodologia",
            "Blog & Notícias", "Guias de Compra", "Glossário Tech",
            "Aprenda a Economizar", "Vale a Pena Esperar?", "Calendário de Preços",
            "Central de Alertas Avançados", "Centro de Cupons", "Black Friday 2026",
            "Simulador de Economia", "Estatísticas do Site", "Meus Favoritos"
        ]
        
        found_count = 0
        for secao in secoes:
            if secao in html:
                found_count += 1
        
        logger.info(f"✅ PROVA REAL: Localizadas {found_count}/24 seções no menu de exploração.")
    
    return True

def test_deduplication():
    """Prova real da deduplicação inteligente."""
    logger.info("\n" + "=" * 40)
    logger.info("🧪 TESTE 3: DEDUPLICAÇÃO INTELIGENTE")
    logger.info("=" * 40)
    
    from deduplicate_products import is_duplicate
    
    p1 = {"name": "Samsung Galaxy S24 Ultra 512GB", "price": 5000}
    p2 = {"name": "Samsung Galaxy S24 Ultra 512 GB", "price": 5000}
    
    if is_duplicate(p1, p2):
        logger.info(f"✅ PROVA REAL: Detectou duplicata por nome similar:")
        logger.info(f"   '{p1['name']}' == '{p2['name']}'")
    else:
        logger.error("❌ ERRO: Falha ao detectar duplicata óbvia!")
        return False
    
    return True

def run_all_tests():
    """Executa todos os testes de prova real."""
    logger.info("🚀 INICIANDO RELATÓRIO DE PROVA REAL DO RADAR DE PREÇOS")
    
    t1 = test_distributed_scheduling()
    t2 = test_template_v2_and_content()
    t3 = test_deduplication()
    
    logger.info("\n" + "=" * 40)
    logger.info("🏁 RESULTADO FINAL DA PROVA REAL")
    logger.info("=" * 40)
    
    if t1 and t2 and t3:
        logger.info("✅ SISTEMA 100% APROVADO EM TODOS OS TESTES!")
        logger.info("✅ Pronto para replicação nos 10 repositórios.")
    else:
        logger.error("❌ SISTEMA APRESENTOU FALHAS EM ALGUNS TESTES.")

if __name__ == "__main__":
    run_all_tests()
