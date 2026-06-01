#!/usr/bin/env python3
"""
CICLO COMPLETO DE AUTOMAÇÃO
============================
Executa em sequência:
1. Busca novos produtos
2. Pontuação de produtos
3. Gera novo blog post
4. Atualiza homepage com novos produtos
5. Regenera sitemaps
6. Sincroniza tudo com o repositório

Uso: python3 scripts/automation_cycle.py
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def run_script(script_name, description):
    """Executa um script Python e reporta o resultado."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}▶ {description}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and "INFO" not in result.stderr:
            print(f"{YELLOW}{result.stderr}{RESET}")
        
        if result.returncode == 0:
            print(f"{GREEN}✓ {description} concluído com sucesso{RESET}")
            return True
        else:
            print(f"{RED}✗ Erro ao executar {description}{RESET}")
            return False
    except subprocess.TimeoutExpired:
        print(f"{RED}✗ Timeout ao executar {description}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}✗ Erro: {e}{RESET}")
        return False

def run_automation_cycle():
    """Executa o ciclo completo de automação."""
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}🤖 INICIANDO CICLO COMPLETO DE AUTOMAÇÃO{RESET}")
    print(f"{GREEN}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    
    steps = [
        ("fetch_products.py", "1️⃣  Buscando novos produtos do Mercado Livre"),
        ("score_products.py", "2️⃣  Pontuando produtos por relevância"),
        ("update_database.py", "2️⃣.5️⃣  Sincronizando database para a página principal"),
        ("generate_blog_posts.py", "3️⃣  Gerando novo artigo de blog"),
        ("build_homepage.py", "4️⃣  Atualizando homepage com novos produtos"),
        ("generate_radar_index.py", "5️⃣  Gerando índice de radar"),
        ("finalize_blog_and_sitemaps.py", "6️⃣  Finalizando blog e regenerando sitemaps"),
    ]
    
    results = []
    for script, description in steps:
        success = run_script(script, description)
        results.append((description, success))
        if not success:
            print(f"{YELLOW}⚠ Continuando mesmo com falha...{RESET}")
    
    # Resumo final
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 RESUMO DO CICLO DE AUTOMAÇÃO{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
        print(f"{status} {description}")
    
    print(f"\n{BLUE}Resultado: {successful}/{total} etapas concluídas{RESET}")
    
    if successful == total:
        print(f"{GREEN}✓ Ciclo de automação concluído com sucesso!{RESET}")
        print(f"{GREEN}✓ Blog atualizado com novo artigo{RESET}")
        print(f"{GREEN}✓ Novos produtos adicionados à homepage{RESET}")
        print(f"{GREEN}✓ Sitemaps regenerados{RESET}")
        return True
    else:
        print(f"{YELLOW}⚠ Ciclo concluído com algumas falhas{RESET}")
        return False

if __name__ == "__main__":
    success = run_automation_cycle()
    sys.exit(0 if success else 1)
