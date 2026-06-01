#!/usr/bin/env python3
"""
Pipeline de Automação Completo do Radar de Preços
Coordena: Fetch → Score → Generate Content → Deduplicate → Publish
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from logger import logger

class RadarAutomationPipeline:
    """Coordena todo o pipeline de automação do Radar de Preços."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.scripts_dir = os.path.join(project_root, "scripts")
        self.data_dir = os.path.join(project_root, "data")
        self.logs_dir = os.path.join(project_root, "logs")
        
        # Criar diretório de logs se não existir
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.execution_log = {
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "errors": [],
            "statistics": {}
        }
    
    def run_script(self, script_name: str, description: str) -> bool:
        """
        Executa um script Python e registra o resultado.
        """
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            error_msg = f"Script não encontrado: {script_path}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
        
        logger.info(f"▶️  Executando: {description}...")
        step_start = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos de timeout
            )
            
            step_duration = time.time() - step_start
            
            if result.returncode == 0:
                logger.info(f"✅ {description} concluído em {step_duration:.1f}s")
                self.execution_log["steps"].append({
                    "name": description,
                    "status": "success",
                    "duration": step_duration
                })
                return True
            else:
                error_msg = f"Erro ao executar {description}: {result.stderr}"
                logger.error(error_msg)
                self.execution_log["errors"].append(error_msg)
                self.execution_log["steps"].append({
                    "name": description,
                    "status": "failed",
                    "duration": step_duration,
                    "error": result.stderr
                })
                return False
        
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ao executar {description} (>600s)"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Erro inesperado ao executar {description}: {str(e)}"
            logger.error(error_msg)
            self.execution_log["errors"].append(error_msg)
            return False
    
    def load_json(self, file_path: str) -> dict:
        """Carrega um arquivo JSON com segurança."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar {file_path}: {e}")
            return {}
    
    def get_statistics(self) -> dict:
        """Coleta estatísticas do pipeline."""
        stats = {
            "products_fetched": 0,
            "products_scored": 0,
            "products_with_content": 0,
            "products_deduplicated": 0,
            "products_published": 0
        }
        
        # Contar produtos em cada etapa
        if os.path.exists(os.path.join(self.data_dir, "new_offers.json")):
            products = self.load_json(os.path.join(self.data_dir, "new_offers.json"))
            stats["products_fetched"] = len(products)
        
        if os.path.exists(os.path.join(self.data_dir, "scored_products.json")):
            products = self.load_json(os.path.join(self.data_dir, "scored_products.json"))
            stats["products_scored"] = len(products)
        
        if os.path.exists(os.path.join(self.data_dir, "products_with_content.json")):
            products = self.load_json(os.path.join(self.data_dir, "products_with_content.json"))
            stats["products_with_content"] = len(products)
        
        if os.path.exists(os.path.join(self.data_dir, "products_deduplicated.json")):
            products = self.load_json(os.path.join(self.data_dir, "products_deduplicated.json"))
            stats["products_deduplicated"] = len(products)
        
        # Contar páginas publicadas
        ofertas_dir = os.path.join(self.project_root, "ofertas")
        if os.path.exists(ofertas_dir):
            published_pages = sum(
                len(files) for _, _, files in os.walk(ofertas_dir)
                if any(f.endswith('.html') for f in files)
            )
            stats["products_published"] = published_pages
        
        return stats
    
    def run_full_pipeline(self) -> bool:
        """
        Executa o pipeline completo de automação.
        """
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO PIPELINE DE AUTOMAÇÃO DO RADAR DE PREÇOS")
        logger.info("=" * 80)
        
        pipeline_steps = [
            ("fetch_products.py", "1️⃣  Buscar produtos (Fetch)"),
            ("score_products.py", "2️⃣  Pontuar produtos (Score)"),
            ("generate_content.py", "3️⃣  Gerar conteúdo (1000+ palavras)"),
            ("deduplicate_products.py", "4️⃣  Remover duplicatas (Deduplicate)"),
            ("sync_database.py", "5️⃣  Sincronizar banco de dados"),
            ("build_homepage.py", "6️⃣  Construir homepage"),
            ("generate_product_pages_v2.py", "7️⃣  Publicar páginas de produtos (v2)"),
        ]
        
        all_success = True
        
        for script_name, description in pipeline_steps:
            if not self.run_script(script_name, description):
                all_success = False
                logger.warning(f"⚠️  Continuando pipeline mesmo com erro em {description}...")
        
        # Coletar estatísticas finais
        self.execution_log["statistics"] = self.get_statistics()
        self.execution_log["end_time"] = datetime.now().isoformat()
        
        # Salvar log de execução
        self.save_execution_log()
        
        # Exibir resumo
        self.print_summary(all_success)
        
        return all_success
    
    def save_execution_log(self) -> None:
        """Salva o log de execução em arquivo JSON."""
        log_file = os.path.join(
            self.logs_dir,
            f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_log, f, ensure_ascii=False, indent=2)
            logger.info(f"Log de execução salvo em: {log_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar log de execução: {e}")
    
    def print_summary(self, success: bool) -> None:
        """Exibe um resumo da execução do pipeline."""
        logger.info("=" * 80)
        logger.info("📊 RESUMO DA EXECUÇÃO")
        logger.info("=" * 80)
        
        stats = self.execution_log["statistics"]
        logger.info(f"✅ Produtos Buscados: {stats['products_fetched']}")
        logger.info(f"⭐ Produtos Pontuados: {stats['products_scored']}")
        logger.info(f"📝 Produtos com Conteúdo: {stats['products_with_content']}")
        logger.info(f"🔄 Produtos Dedupplicados: {stats['products_deduplicated']}")
        logger.info(f"🌐 Páginas Publicadas: {stats['products_published']}")
        
        if self.execution_log["errors"]:
            logger.warning(f"\n⚠️  {len(self.execution_log['errors'])} erro(s) encontrado(s):")
            for error in self.execution_log["errors"]:
                logger.warning(f"   - {error}")
        
        status = "✅ SUCESSO" if success else "⚠️  PARCIAL"
        logger.info(f"\n{status} - Pipeline concluído")
        logger.info("=" * 80)

def main():
    """Função principal."""
    # Determinar diretório raiz do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Criar e executar pipeline
    pipeline = RadarAutomationPipeline(project_root)
    success = pipeline.run_full_pipeline()
    
    # Retornar código de saída apropriado
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
