#!/usr/bin/env python3
"""
link_checker.py — Verificador de integridade de links e disponibilidade de produtos.
Detecta links 404/503 e marca produtos como "expired".
"""

import os
import json
import requests
import time
from pathlib import Path
from logger import logger
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

def check_link_status(url: str) -> tuple[int, bool]:
    """Verifica o status HTTP do link e se o produto ainda existe."""
    if not url or url == "#":
        return 0, False
    
    try:
        # Usar GET em vez de HEAD para evitar 405/503 falsos do ML
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        status = resp.status_code
        
        # Verificar se o conteúdo indica produto indisponível
        is_available = True
        if status == 404:
            is_available = False
        elif status == 200:
            html = resp.text.lower()
            indisponivel_markers = [
                "página não encontrada",
                "não encontramos",
                "anúncio pausado",
                "produto esgotado",
                "not found"
            ]
            if any(marker in html for marker in indisponivel_markers):
                is_available = False
        
        return status, is_available
    except Exception as e:
        logger.error(f"Erro ao checar link {url}: {e}")
        return 0, False

def audit_and_update_status(json_path: str):
    """Verifica todos os produtos no JSON e atualiza o status."""
    if not os.path.exists(json_path):
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    logger.info(f"Iniciando checagem de links para {len(products)} produtos...")
    
    expired_count = 0
    for i, p in enumerate(products):
        url = p.get('custom_affiliate_url') or p.get('permalink')
        status_code, is_available = check_link_status(url)
        
        if not is_available:
            if p.get('status') != 'expired':
                p['status'] = 'expired'
                p['expired_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                expired_count += 1
                logger.info(f"⚠ Produto marcado como ESGOTADO: {p.get('name', 'N/A')}")
        else:
            # Se voltou a ficar disponível (raro, mas possível)
            if p.get('status') == 'expired':
                p['status'] = 'active'
                logger.info(f"✓ Produto voltou a ficar ATIVO: {p.get('name', 'N/A')}")
        
        # Rate limit amigável
        if i % 10 == 0 and i > 0:
            time.sleep(1)
            logger.info(f"Progresso: {i}/{len(products)} verificados...")

    # Salvar atualizações
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Checagem concluída. {expired_count} novos produtos marcados como esgotados.")

if __name__ == "__main__":
    # Auditar base principal e produtos em destaque
    audit_and_update_status(str(ROOT / "data" / "database" / "all_products.json"))
    audit_and_update_status(str(ROOT / "data" / "scored_products.json"))
