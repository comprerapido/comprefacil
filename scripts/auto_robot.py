import subprocess
import sys
import os
import time
from datetime import datetime

def run_script(script_name):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Executando {script_name}...")
    try:
        # Tenta executar o script a partir da pasta scripts/
        script_path = f"scripts/{script_name}"
        if not os.path.exists(script_path):
             print(f"Erro: {script_path} não encontrado.")
             return False
             
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_name}: {e}")
        print(e.stderr)
        return False

def main():
    print(f"\n{'='*50}")
    print(f"🤖 RADAR NINJA - CICLO DE AUTOMAÇÃO TOTAL")
    print(f"{'='*50}\n")
    
    steps = [
        "fetch_products.py",
        "sanitize_offers.py",
        "generate_deep_blog.py",
        "generate_categories.py",
        "build_homepage.py",
        "generate_sitemap.py"
    ]
    
    success = True
    for step in steps:
        if not run_script(step):
            # Alguns scripts podem falhar se não houver dados, mas build_homepage é crítico
            if step == "build_homepage.py":
                success = False
                break
            print(f"Aviso: {step} falhou, mas continuando...")
            
    if success:
        print(f"\n{'='*50}")
        print(f"✅ Ciclo de automação concluído com sucesso!")
        print(f"{'='*50}\n")
    else:
        print(f"\n{'='*50}")
        print(f"❌ Falha no ciclo de automação.")
        print(f"{'='*50}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
