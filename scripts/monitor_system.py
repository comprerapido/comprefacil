#!/usr/bin/env python3
"""
Script de monitoramento do sistema Radar de Preços.
Verifica a saúde do pipeline e gera alertas.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from logger import logger

class SystemMonitor:
    """Monitora a saúde do sistema Radar de Preços."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.data_dir = os.path.join(project_root, "data")
        self.logs_dir = os.path.join(project_root, "logs")
        self.alerts = []
    
    def check_file_age(self, file_path: str, max_age_hours: int = 25) -> bool:
        """
        Verifica se um arquivo foi atualizado recentemente.
        """
        if not os.path.exists(file_path):
            return False
        
        file_age = time.time() - os.path.getmtime(file_path)
        file_age_hours = file_age / 3600
        
        return file_age_hours <= max_age_hours
    
    def check_file_size(self, file_path: str, min_size_bytes: int = 100) -> bool:
        """
        Verifica se um arquivo tem tamanho mínimo.
        """
        if not os.path.exists(file_path):
            return False
        
        file_size = os.path.getsize(file_path)
        return file_size >= min_size_bytes
    
    def check_json_validity(self, file_path: str) -> bool:
        """
        Verifica se um arquivo JSON é válido.
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except:
            return False
    
    def get_product_count(self, file_path: str) -> int:
        """
        Retorna o número de produtos em um arquivo JSON.
        """
        if not os.path.exists(file_path):
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data) if isinstance(data, list) else 0
        except:
            return 0
    
    def check_pipeline_health(self) -> dict:
        """
        Verifica a saúde geral do pipeline.
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
            "alerts": []
        }
        
        # Verificar arquivo de produtos buscados
        new_offers_path = os.path.join(self.data_dir, "new_offers.json")
        check = {
            "file": "new_offers.json",
            "exists": os.path.exists(new_offers_path),
            "valid": self.check_json_validity(new_offers_path),
            "recent": self.check_file_age(new_offers_path),
            "count": self.get_product_count(new_offers_path)
        }
        health["checks"]["fetch"] = check
        
        if not check["recent"]:
            health["alerts"].append("⚠️  Produtos buscados não foram atualizados nas últimas 25 horas")
            health["status"] = "warning"
        
        # Verificar arquivo de produtos pontuados
        scored_path = os.path.join(self.data_dir, "scored_products.json")
        check = {
            "file": "scored_products.json",
            "exists": os.path.exists(scored_path),
            "valid": self.check_json_validity(scored_path),
            "recent": self.check_file_age(scored_path),
            "count": self.get_product_count(scored_path)
        }
        health["checks"]["score"] = check
        
        if not check["recent"]:
            health["alerts"].append("⚠️  Produtos pontuados não foram atualizados nas últimas 25 horas")
            health["status"] = "warning"
        
        # Verificar arquivo de produtos com conteúdo
        content_path = os.path.join(self.data_dir, "products_with_content.json")
        check = {
            "file": "products_with_content.json",
            "exists": os.path.exists(content_path),
            "valid": self.check_json_validity(content_path),
            "recent": self.check_file_age(content_path),
            "count": self.get_product_count(content_path)
        }
        health["checks"]["content"] = check
        
        if not check["recent"]:
            health["alerts"].append("⚠️  Conteúdo de produtos não foi gerado nas últimas 25 horas")
            health["status"] = "warning"
        
        # Verificar arquivo de produtos dedupplicados
        dedup_path = os.path.join(self.data_dir, "products_deduplicated.json")
        check = {
            "file": "products_deduplicated.json",
            "exists": os.path.exists(dedup_path),
            "valid": self.check_json_validity(dedup_path),
            "recent": self.check_file_age(dedup_path),
            "count": self.get_product_count(dedup_path)
        }
        health["checks"]["deduplicate"] = check
        
        if not check["recent"]:
            health["alerts"].append("⚠️  Deduplicação de produtos não foi executada nas últimas 25 horas")
            health["status"] = "warning"
        
        # Verificar banco de dados
        db_path = os.path.join(self.data_dir, "database", "all_products.json")
        check = {
            "file": "database/all_products.json",
            "exists": os.path.exists(db_path),
            "valid": self.check_json_validity(db_path),
            "recent": self.check_file_age(db_path),
            "count": self.get_product_count(db_path)
        }
        health["checks"]["database"] = check
        
        if not check["recent"]:
            health["alerts"].append("⚠️  Banco de dados não foi sincronizado nas últimas 25 horas")
            health["status"] = "warning"
        
        # Verificar homepage
        homepage_path = os.path.join(self.project_root, "index.html")
        check = {
            "file": "index.html",
            "exists": os.path.exists(homepage_path),
            "valid": os.path.exists(homepage_path),
            "recent": self.check_file_age(homepage_path),
            "size": os.path.getsize(homepage_path) if os.path.exists(homepage_path) else 0
        }
        health["checks"]["homepage"] = check
        
        if not check["recent"]:
            health["alerts"].append("⚠️  Homepage não foi atualizada nas últimas 25 horas")
            health["status"] = "warning"
        
        # Verificar logs recentes
        if os.path.exists(self.logs_dir):
            logs = sorted(Path(self.logs_dir).glob("automation_*.json"), reverse=True)
            if logs:
                latest_log_path = logs[0]
                try:
                    with open(latest_log_path, 'r', encoding='utf-8') as f:
                        latest_log = json.load(f)
                    
                    if latest_log.get("errors"):
                        health["alerts"].append(f"⚠️  Última execução teve {len(latest_log['errors'])} erro(s)")
                        health["status"] = "warning"
                except:
                    pass
        
        return health
    
    def generate_report(self) -> str:
        """
        Gera um relatório de saúde do sistema.
        """
        health = self.check_pipeline_health()
        
        report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   RELATÓRIO DE SAÚDE DO RADAR DE PREÇOS                    ║
╚════════════════════════════════════════════════════════════════════════════╝

📅 Data/Hora: {health['timestamp']}
🔍 Status Geral: {health['status'].upper()}

📊 VERIFICAÇÕES DO PIPELINE:
─────────────────────────────────────────────────────────────────────────────
"""
        
        for check_name, check_data in health['checks'].items():
            status_icon = "✅" if check_data.get('valid') and check_data.get('recent') else "❌"
            count = check_data.get('count', 0)
            report += f"\n{status_icon} {check_name.upper()}: {check_data['file']}"
            report += f"\n   Existe: {'Sim' if check_data.get('exists') else 'Não'}"
            report += f"\n   Válido: {'Sim' if check_data.get('valid') else 'Não'}"
            report += f"\n   Recente: {'Sim' if check_data.get('recent') else 'Não'}"
            if count > 0:
                report += f"\n   Itens: {count}"
        
        if health['alerts']:
            report += f"\n\n⚠️  ALERTAS ({len(health['alerts'])}):\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            for alert in health['alerts']:
                report += f"{alert}\n"
        
        report += "\n╔════════════════════════════════════════════════════════════════════════════╗\n"
        
        return report
    
    def save_health_report(self) -> None:
        """
        Salva o relatório de saúde em arquivo.
        """
        health = self.check_pipeline_health()
        report_path = os.path.join(
            self.logs_dir,
            f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        os.makedirs(self.logs_dir, exist_ok=True)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(health, f, ensure_ascii=False, indent=2)
            logger.info(f"Relatório de saúde salvo em: {report_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório de saúde: {e}")

def main():
    """Função principal."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    monitor = SystemMonitor(project_root)
    report = monitor.generate_report()
    
    print(report)
    monitor.save_health_report()

if __name__ == "__main__":
    main()
