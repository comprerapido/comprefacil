#!/usr/bin/env python3
"""
Auto Robot Enhanced - Sistema de automação 24/7 do Radar Ninja.

Responsabilidades:
- Executar ciclo completo de atualização a cada 30 minutos
- Gerar logs detalhados de cada execução
- Monitorar saúde do sistema
- Implementar auto-recuperação em caso de falha
- Gerar relatórios de status
"""

import json
import os
import sys
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Configuração de logging
ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / f"auto_robot_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def run_command(cmd: List[str], description: str) -> bool:
    """Executa comando e registra resultado."""
    logger.info(f"Iniciando: {description}")
    try:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            logger.info(f"✓ {description} concluído com sucesso")
            return True
        else:
            logger.error(f"✗ {description} falhou: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"✗ {description} expirou (timeout)")
        return False
    except Exception as e:
        logger.error(f"✗ {description} erro: {str(e)}")
        return False


def execute_growth_engine() -> bool:
    """Executa o motor de crescimento SEO."""
    return run_command(
        ["python3", "scripts/radar_ninja_growth_engine.py"],
        "Motor de crescimento SEO"
    )


def execute_product_audit() -> bool:
    """Audita produtos e detecta qualidade."""
    return run_command(
        ["python3", "scripts/audit_products.py"],
        "Auditoria de produtos"
    )


def generate_health_report() -> Dict[str, Any]:
    """Gera relatório de saúde do sistema."""
    health = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    # Verificar arquivos críticos
    critical_files = [
        "data/all_products.json",
        "data/health_report.json",
        "data/broken_pages_report.json",
        "sitemap.xml",
        "index.html"
    ]
    
    for file in critical_files:
        path = ROOT / file
        health["checks"][file] = path.exists()
        if not path.exists():
            health["status"] = "warning"
    
    # Contar páginas geradas
    product_pages = len(list((ROOT / "produtos").glob("*/index.html"))) if (ROOT / "produtos").exists() else 0
    category_pages = len(list((ROOT / "categorias").glob("*/index.html"))) if (ROOT / "categorias").exists() else 0
    
    health["checks"]["product_pages"] = product_pages
    health["checks"]["category_pages"] = category_pages
    
    # Salvar relatório
    report_path = ROOT / "data" / "system_health.json"
    report_path.write_text(json.dumps(health, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Relatório de saúde gerado: {product_pages} produtos, {category_pages} categorias")
    
    return health


def commit_and_push() -> bool:
    """Faz commit e push das alterações."""
    try:
        # Verificar se há mudanças
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            logger.info("Nenhuma alteração para commitar")
            return True
        
        # Adicionar arquivos
        subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True)
        
        # Commit
        timestamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
        commit_msg = f"🤖 AUTO: Atualização de ofertas — {timestamp} [skip ci]"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=ROOT,
            capture_output=True
        )
        
        # Push
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✓ Alterações enviadas ao GitHub")
            return True
        else:
            logger.warning(f"Aviso ao fazer push: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Erro ao commitar/push: {str(e)}")
        return False


def run_full_cycle() -> Dict[str, Any]:
    """Executa ciclo completo de atualização."""
    cycle_start = datetime.now(timezone.utc)
    logger.info("=" * 60)
    logger.info(f"INICIANDO CICLO DE ATUALIZAÇÃO: {cycle_start.isoformat()}")
    logger.info("=" * 60)
    
    results = {
        "timestamp": cycle_start.isoformat(),
        "steps": {}
    }
    
    # Passo 1: Auditoria de produtos (Link Checker + Image Optimizer)
    logger.info("Passo 1: Verificação de links e download de imagens...")
    run_command(["python3", "scripts/link_checker.py"], "Verificador de Links")
    run_command(["python3", "scripts/image_optimizer.py"], "Otimizador de Imagens")
    results["steps"]["product_audit"] = execute_product_audit()
    
    # Passo 2: Inteligência de Produto (Novo)
    logger.info("Passo 2: Aplicando inteligência de produto e histórico...")
    results["steps"]["product_intelligence"] = run_command(["python3", "scripts/product_intelligence.py"], "Inteligência de Produto")
    
    # Passo 3: Motor de crescimento
    logger.info("Passo 3: Gerando páginas e SEO...")
    results["steps"]["growth_engine"] = execute_growth_engine()
    
    # Passo 3: Relatório de saúde
    health = generate_health_report()
    results["steps"]["health_report"] = health["status"] == "healthy"
    results["health"] = health
    
    # Passo 4: Commit e push
    results["steps"]["git_push"] = commit_and_push()
    
    # Resumo
    cycle_end = datetime.now(timezone.utc)
    duration = (cycle_end - cycle_start).total_seconds()
    results["duration_seconds"] = duration
    results["success"] = all(results["steps"].values())
    
    logger.info("=" * 60)
    logger.info(f"CICLO CONCLUÍDO: {cycle_end.isoformat()}")
    logger.info(f"Duração: {duration:.1f}s")
    logger.info(f"Status: {'✓ SUCESSO' if results['success'] else '✗ FALHA'}")
    logger.info("=" * 60)
    
    # Salvar resultado do ciclo
    cycle_report = ROOT / "data" / "last_cycle_report.json"
    cycle_report.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return results


if __name__ == "__main__":
    try:
        results = run_full_cycle()
        sys.exit(0 if results["success"] else 1)
    except Exception as e:
        logger.error(f"Erro crítico: {str(e)}", exc_info=True)
        sys.exit(1)
