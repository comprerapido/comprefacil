import subprocess
import sys
import os
import time
from datetime import datetime
from logger import logger

def run_script(script_name):
    logger.info(f"🚀 [MESTRE] Iniciando etapa: {script_name}")
    try:
        script_path = os.path.join("scripts", script_name)
        if not os.path.exists(script_path):
             logger.error(f"❌ Erro: {script_path} não encontrado.")
             return False
             
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao executar {script_name}: {e}")
        print(e.stderr)
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🥷  RADAR NINJA - SISTEMA MESTRE (ROBÔ 3)  🥷")
    print(f"{'='*60}\n")
    
    steps = [
        "fetch_products.py",
        "sanitize_offers.py",
        "generate_deep_blog.py",
        "generate_categories.py",
        "build_homepage.py",
        "generate_sitemap.py"
    ]
    
    start_time = time.time()
    success_count = 0
    
    for step in steps:
        if run_script(step):
            success_count += 1
        else:
            if step in ["fetch_products.py", "build_homepage.py"]:
                logger.error(f"⛔ Falha em etapa crítica: {step}. Abortando ciclo.")
                sys.exit(1)
            logger.warning(f"⚠ Etapa {step} falhou, mas continuando ciclo mestre...")
            
    duration = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ CICLO MESTRE CONCLUÍDO!")
    print(f"📊 Etapas: {success_count}/{len(steps)}")
    print(f"⏱ Duração: {duration:.2f}s")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
