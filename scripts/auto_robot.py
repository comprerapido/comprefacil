#!/usr/bin/env python3
"""
auto_robot.py — Orquestrador Blindado do Radar Ninja
Focado 100% no Mercado Livre com múltiplos métodos de coleta e recuperação automática.
"""
import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timezone

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("RadarNinja")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

def run_script(script_name):
    path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(path):
        log.error(f"Script não encontrado: {script_name}")
        return False
    
    try:
        log.info(f"🚀 Executando: {script_name}")
        # Usar subprocess.run para garantir execução isolada
        result = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log.info(f"✅ {script_name} concluído com sucesso.")
            if result.stdout:
                log.debug(f"Saída {script_name}:\n{result.stdout}")
            return True
        else:
            log.warning(f"⚠️ {script_name} falhou (code {result.returncode}).")
            log.warning(f"Erro {script_name}:\n{result.stderr}")
            return False
    except Exception as e:
        log.error(f"❌ Erro ao executar {script_name}: {e}")
        return False

def main():
    log.info("="*60)
    log.info(f"🤖 RADAR NINJA — CICLO DE AUTOMAÇÃO: {datetime.now(timezone.utc).isoformat()}")
    log.info("="*60)

    # 1. Limpeza Preventiva e Rotação de Catálogo
    run_script("cleanup_database.py")

    # 2. Coleta — Estratégia de Múltiplas Camadas
    # Tentativa A: API Real (ou Scraping via fetch_real_products)
    run_script("fetch_real_products.py")
    
    # Atualizar histórico de preços
    run_script("price_history_manager.py")
    
    # Verificar se a coleta trouxe resultados suficientes
    new_offers_path = os.path.join(BASE_DIR, "data", "new_offers.json")
    new_count = 0
    if os.path.exists(new_offers_path):
        try:
            with open(new_offers_path) as f:
                new_count = len(json.load(f))
        except:
            new_count = 0
    
    # Tentativa B: Injeção Dinâmica (Fallback Robusto com Scraping leve + Backup)
    if new_count < 5:
        log.info(f"Coleta insuficiente ({new_count} itens). Acionando Injeção Dinâmica...")
        run_script("inject_new_products.py")
    else:
        log.info(f"Coleta satisfatória ({new_count} itens).")

    # 3. Motor de Crescimento (SEO, Páginas, Sitemap)
    # Gerar vereditos com IA antes de rodar o growth engine
    run_script("generate_verdicts.py")

    # Importar e rodar o growth engine
    sys.path.insert(0, SCRIPTS_DIR)
    try:
        from radar_ninja_growth_engine import main as growth_main
        stats = growth_main()
        log.info(f"📈 Growth Engine Stats: {json.dumps(stats, indent=2)}")
    except Exception as e:
        log.error(f"❌ Falha no Growth Engine: {e}")

    # 4. Pós-publicação UX/SEO: garante que o site gerado fique navegável,
    # com homepage estática de produtos reais, blog visível, links cruzados,
    # design moderno e sitemap classificado corretamente.
    post_publish_scripts = [
        "fix_homepage_blog_product_integration.py",
        "enhance_blog_product_crosslinks.py",
        "enhance_internal_page_design.py",
        "apply_seo_and_published_data.py",
        "finalize_blog_and_sitemaps.py",
    ]
    for script in post_publish_scripts:
        if os.path.exists(os.path.join(SCRIPTS_DIR, script)):
            run_script(script)
        else:
            log.warning(f"Script de pós-publicação ausente: {script}")

    # 5. Verificação de Saúde (A cada 4 ciclos ou via cron específico)
    # Implementaremos o verify_links_health.py a seguir
    if os.path.exists(os.path.join(SCRIPTS_DIR, "verify_links_health.py")):
        # Rodar verificação de saúde apenas em horários específicos (ex: 04:00 UTC)
        if datetime.now(timezone.utc).hour == 4:
            run_script("verify_links_health.py")

    log.info("="*60)
    log.info("🏁 CICLO FINALIZADO")
    log.info("="*60)

if __name__ == "__main__":
    main()
