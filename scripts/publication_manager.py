#!/usr/bin/env python3
"""
GERENCIADOR DE PUBLICAÇÕES
===========================

Coordena publicações respeitando o cronograma distribuído global.
Verifica se é hora de publicar e executa o pipeline de cada site.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from logger import logger
from global_scheduler import GlobalScheduler

class PublicationManager:
    """Gerencia publicações de múltiplos sites com agendamento distribuído."""
    
    def __init__(self, db_path: str = "data/scheduler.db"):
        self.scheduler = GlobalScheduler(db_path)
        self.db_path = db_path
    
    def should_publish_now(self, site_id: str) -> bool:
        """
        Verifica se é hora de publicar para um site específico.
        
        Retorna True se:
        1. O site está configurado
        2. A hora atual coincide com horário agendado (dentro de 1 minuto)
        3. Ainda não foi publicado nesta hora
        """
        
        if site_id not in self.scheduler.SITES_CONFIG:
            logger.warning(f"Site {site_id} não encontrado na configuração")
            return False
        
        offset = self.scheduler.SITES_CONFIG[site_id]["offset"]
        now = datetime.now()
        
        # Verificar se minuto atual coincide com offset do site
        if now.minute != offset:
            return False
        
        # Verificar se já foi publicado nesta hora
        if self.was_published_this_hour(site_id):
            return False
        
        return True
    
    def was_published_this_hour(self, site_id: str) -> bool:
        """Verifica se site já publicou nesta hora."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        current_hour = now.strftime("%Y-%m-%d %H:00:00")
        
        cursor.execute("""
            SELECT COUNT(*) FROM publication_history
            WHERE site_id = ? 
            AND published_time >= ?
            AND status = 'success'
        """, (site_id, current_hour))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def record_publication(self, site_id: str, article_title: str, 
                          article_url: str, status: str = "success") -> None:
        """Registra uma publicação no histórico."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO publication_history 
            (site_id, published_time, article_title, article_url, status)
            VALUES (?, ?, ?, ?, ?)
        """, (site_id, datetime.now().isoformat(), article_title, article_url, status))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Publicação registrada: {site_id} - {article_title}")
    
    def get_next_publications(self, hours_ahead: int = 24) -> List[Dict]:
        """
        Retorna lista de próximas publicações agendadas.
        
        Args:
            hours_ahead: Quantas horas no futuro verificar
        
        Returns:
            Lista com próximas publicações ordenadas por horário
        """
        
        next_pubs = []
        now = datetime.now()
        
        for site_id, config in self.scheduler.SITES_CONFIG.items():
            offset = config["offset"]
            site_name = config["name"]
            
            # Calcular próxima publicação
            for hour_offset in range(hours_ahead):
                check_time = now.replace(minute=offset, second=0, microsecond=0) + \
                            timedelta(hours=hour_offset)
                
                # Verificar se está dentro do horário de operação
                if check_time.hour < self.scheduler.START_HOUR or \
                   check_time.hour >= self.scheduler.END_HOUR:
                    continue
                
                # Se é no passado, pular
                if check_time <= now:
                    continue
                
                next_pubs.append({
                    "site_id": site_id,
                    "site_name": site_name,
                    "scheduled_time": check_time.isoformat(),
                    "time_str": check_time.strftime("%H:%M"),
                    "minutes_until": int((check_time - now).total_seconds() / 60)
                })
                
                break  # Uma publicação por site
        
        # Ordenar por horário
        next_pubs.sort(key=lambda x: x["scheduled_time"])
        
        return next_pubs
    
    def get_publication_status(self) -> Dict:
        """Retorna status geral de publicações do dia."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT site_id, COUNT(*) as count, 
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success
            FROM publication_history
            WHERE published_time LIKE ?
            GROUP BY site_id
        """, (f"{today}%",))
        
        results = cursor.fetchall()
        conn.close()
        
        status = {}
        for site_id, total, success in results:
            site_name = self.scheduler.SITES_CONFIG[site_id]["name"]
            status[site_name] = {
                "total": total,
                "success": success,
                "failed": total - success
            }
        
        return status
    
    def print_next_publications(self, hours_ahead: int = 24) -> None:
        """Exibe próximas publicações agendadas."""
        next_pubs = self.get_next_publications(hours_ahead)
        
        logger.info("\n" + "=" * 80)
        logger.info("📅 PRÓXIMAS PUBLICAÇÕES AGENDADAS")
        logger.info("=" * 80)
        
        for pub in next_pubs:
            logger.info(f"{pub['time_str']} - {pub['site_name']} ({pub['minutes_until']} min)")
        
        logger.info("=" * 80 + "\n")
    
    def print_daily_status(self) -> None:
        """Exibe status de publicações do dia."""
        status = self.get_publication_status()
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 STATUS DE PUBLICAÇÕES DO DIA")
        logger.info("=" * 80)
        
        total_success = 0
        total_failed = 0
        
        for site_name, stats in status.items():
            success = stats["success"]
            failed = stats["failed"]
            total = stats["total"]
            
            logger.info(f"{site_name}: {success}/{total} ✅ ({failed} ❌)")
            total_success += success
            total_failed += failed
        
        logger.info("=" * 80)
        logger.info(f"Total: {total_success} ✅ | {total_failed} ❌")
        logger.info("=" * 80 + "\n")

def main():
    """Função principal."""
    from datetime import timedelta
    
    manager = PublicationManager()
    
    # Exibir próximas publicações
    manager.print_next_publications(hours_ahead=24)
    
    # Exibir status do dia
    manager.print_daily_status()

if __name__ == "__main__":
    main()
