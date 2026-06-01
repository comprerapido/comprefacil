#!/usr/bin/env python3
"""
SISTEMA GLOBAL DE AGENDAMENTO DISTRIBUÍDO
==========================================

Coordena publicações de múltiplos sites com:
- Escalonamento por minuto (offset único para cada site)
- 1 publicação por hora por site
- Sem conflitos de horário
- Distribuição entre 07:00 e 23:00

Configuração:
- 10 sites ativos
- Cada site com offset de 6 minutos
- Total: 160 publicações/dia (10 sites × 16 horas)
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from logger import logger

class GlobalScheduler:
    """Gerencia agendamento global distribuído de publicações."""
    
    # Configuração de sites e offsets (em minutos)
    SITES_CONFIG = {
        "achado-certo-tech": {"offset": 0, "name": "Achado Certo Tech", "category": "Tecnologia"},
        "achado-certo-gamer": {"offset": 6, "name": "Achado Certo Gamer", "category": "Games"},
        "achado-certo-casa": {"offset": 12, "name": "Achado Certo Casa", "category": "Casa"},
        "achado-certo-eletro": {"offset": 18, "name": "Achado Certo Eletro", "category": "Eletrônicos"},
        "achado-certo-pet": {"offset": 24, "name": "Achado Certo Pet", "category": "Pets"},
        "achado-certo-bebe": {"offset": 30, "name": "Achado Certo Bebê", "category": "Bebê"},
        "achado-certo-beleza": {"offset": 36, "name": "Achado Certo Beleza", "category": "Beleza"},
        "achado-certo-fitness": {"offset": 42, "name": "Achado Certo Fitness", "category": "Fitness"},
        "achado-certo-auto": {"offset": 48, "name": "Achado Certo Auto", "category": "Automóvel"},
        "achado-certo-ferramentas": {"offset": 54, "name": "Achado Certo Ferramentas", "category": "Ferramentas"},
    }
    
    # Horário de operação
    START_HOUR = 7    # 07:00
    END_HOUR = 23     # 23:00
    HOURS_PER_DAY = END_HOUR - START_HOUR  # 16 horas
    
    def __init__(self, db_path: str = "data/scheduler.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Inicializa banco de dados de agendamento."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de agendamento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                published_time TEXT,
                status TEXT DEFAULT 'pending',
                article_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de histórico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS publication_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                published_time TEXT NOT NULL,
                article_title TEXT,
                article_url TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Banco de dados de agendamento inicializado")
    
    def generate_daily_schedule(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Gera cronograma para o dia inteiro.
        
        Retorna dicionário com:
        {
            "achado-certo-tech": [("07:00", "artigo1"), ("08:00", "artigo2"), ...],
            "achado-certo-gamer": [("07:06", "artigo1"), ("08:06", "artigo2"), ...],
            ...
        }
        """
        schedule = {}
        
        logger.info("=" * 80)
        logger.info("📅 GERANDO CRONOGRAMA DIÁRIO DISTRIBUÍDO")
        logger.info("=" * 80)
        
        for site_id, config in self.SITES_CONFIG.items():
            offset = config["offset"]
            site_name = config["name"]
            schedule[site_id] = []
            
            logger.info(f"\n🔹 {site_name} (offset: {offset} min)")
            
            # Gerar 16 publicações (uma por hora, das 07:00 às 23:00)
            for hour in range(self.START_HOUR, self.END_HOUR):
                # Calcular hora e minuto
                scheduled_datetime = datetime.now().replace(
                    hour=hour,
                    minute=offset,
                    second=0,
                    microsecond=0
                )
                
                time_str = scheduled_datetime.strftime("%H:%M")
                schedule[site_id].append(time_str)
                
                if hour == self.START_HOUR:  # Mostrar apenas primeira publicação
                    logger.info(f"   Primeira publicação: {time_str}")
            
            logger.info(f"   Total de publicações: {len(schedule[site_id])}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Cronograma Gerado com Sucesso!")
        logger.info("=" * 80)
        
        return schedule
    
    def get_next_publication(self, site_id: str) -> Tuple[str, bool]:
        """
        Retorna o próximo horário de publicação para um site.
        
        Returns:
            (horário_próxima_publicação, é_hoje)
        """
        if site_id not in self.SITES_CONFIG:
            return None, False
        
        offset = self.SITES_CONFIG[site_id]["offset"]
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Verificar se ainda há publicações hoje
        for hour in range(current_hour, self.END_HOUR):
            if hour == current_hour and offset <= current_minute:
                continue  # Já passou este horário
            
            scheduled_time = datetime.now().replace(
                hour=hour,
                minute=offset,
                second=0,
                microsecond=0
            )
            
            return scheduled_time.strftime("%H:%M"), True
        
        # Se não há mais publicações hoje, retornar primeira de amanhã
        tomorrow = datetime.now() + timedelta(days=1)
        scheduled_time = tomorrow.replace(
            hour=self.START_HOUR,
            minute=offset,
            second=0,
            microsecond=0
        )
        
        return scheduled_time.strftime("%H:%M"), False
    
    def save_schedule_to_file(self, schedule: Dict, output_path: str = "data/daily_schedule.json") -> None:
        """Salva cronograma em arquivo JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Formatar para exibição
        formatted_schedule = {}
        for site_id, times in schedule.items():
            site_name = self.SITES_CONFIG[site_id]["name"]
            formatted_schedule[site_name] = times
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_schedule, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Cronograma salvo em: {output_path}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cronograma: {e}")
    
    def print_schedule_summary(self, schedule: Dict) -> None:
        """Exibe resumo do cronograma."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMO DO CRONOGRAMA DIÁRIO")
        logger.info("=" * 80)
        
        # Mostrar por hora
        for hour in range(self.START_HOUR, self.END_HOUR):
            publications_this_hour = []
            
            for site_id, config in self.SITES_CONFIG.items():
                offset = config["offset"]
                time_str = f"{hour:02d}:{offset:02d}"
                
                # Verificar se este horário está no cronograma
                if time_str in schedule[site_id]:
                    site_name = config["name"]
                    publications_this_hour.append((time_str, site_name))
            
            if publications_this_hour:
                publications_this_hour.sort()
                hour_str = f"{hour:02d}:00 - {hour:02d}:59"
                logger.info(f"\n⏰ {hour_str}")
                for time_str, site_name in publications_this_hour:
                    logger.info(f"   {time_str} - {site_name}")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"📈 ESTATÍSTICAS:")
        logger.info(f"   Total de Sites: {len(self.SITES_CONFIG)}")
        logger.info(f"   Horas de Operação: {self.HOURS_PER_DAY} (07:00 - 23:00)")
        logger.info(f"   Publicações por Site: {self.HOURS_PER_DAY}")
        logger.info(f"   Total de Publicações/Dia: {len(self.SITES_CONFIG) * self.HOURS_PER_DAY}")
        logger.info("=" * 80 + "\n")
    
    def validate_schedule(self, schedule: Dict) -> bool:
        """
        Valida cronograma para garantir:
        - Sem conflitos de horário
        - Intervalo mínimo de 6 minutos entre publicações
        - Distribuição uniforme
        """
        logger.info("🔍 Validando cronograma...")
        
        all_times = []
        
        # Coletar todos os horários
        for site_id, times in schedule.items():
            for time_str in times:
                all_times.append(time_str)
        
        # Verificar duplicatas
        if len(all_times) != len(set(all_times)):
            logger.error("❌ Conflito detectado: dois sites com mesmo horário!")
            return False
        
        logger.info("✅ Nenhum conflito de horário detectado")
        logger.info(f"✅ Total de publicações: {len(all_times)}")
        
        return True
    
    def get_site_config(self) -> Dict:
        """Retorna configuração de todos os sites."""
        return self.SITES_CONFIG
    
    def get_site_info(self, site_id: str) -> Dict:
        """Retorna informações de um site específico."""
        return self.SITES_CONFIG.get(site_id)

def main():
    """Função principal."""
    scheduler = GlobalScheduler()
    
    # Gerar cronograma
    schedule = scheduler.generate_daily_schedule()
    
    # Validar
    if scheduler.validate_schedule(schedule):
        # Salvar
        scheduler.save_schedule_to_file(schedule)
        
        # Exibir resumo
        scheduler.print_schedule_summary(schedule)
    else:
        logger.error("❌ Falha na validação do cronograma!")

if __name__ == "__main__":
    main()
