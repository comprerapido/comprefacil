#!/usr/bin/env python3
"""
Script para configurar agendamento automático do pipeline de automação.
Suporta cron (Linux/Mac) e agendador de tarefas (Windows).
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from logger import logger

class SchedulerSetup:
    """Configura agendamento automático do pipeline."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.scripts_dir = os.path.join(project_root, "scripts")
        self.pipeline_script = os.path.join(self.scripts_dir, "automation_pipeline.py")
        self.system = platform.system()
    
    def setup_cron_linux_mac(self, hour: int = 2, minute: int = 0) -> bool:
        """
        Configura agendamento via cron (Linux/Mac).
        Por padrão, executa diariamente às 2h da manhã.
        """
        logger.info(f"Configurando cron para {self.system}...")
        
        # Criar comando cron
        cron_command = f"{minute} {hour} * * * cd {self.project_root} && /usr/bin/python3 {self.pipeline_script}"
        
        try:
            # Obter crontab atual
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Verificar se já existe
            if "automation_pipeline.py" in current_crontab:
                logger.warning("⚠️  Agendamento já existe no crontab!")
                return False
            
            # Adicionar nova entrada
            new_crontab = current_crontab + "\n" + cron_command + "\n"
            
            # Salvar novo crontab
            process = subprocess.Popen(
                ["crontab", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=new_crontab)
            
            if process.returncode == 0:
                logger.info(f"✅ Cron configurado com sucesso!")
                logger.info(f"   Execução: Diariamente às {hour:02d}:{minute:02d}")
                logger.info(f"   Comando: {cron_command}")
                return True
            else:
                logger.error(f"Erro ao configurar cron: {stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Erro ao configurar cron: {e}")
            return False
    
    def setup_task_scheduler_windows(self, hour: int = 2, minute: int = 0) -> bool:
        """
        Configura agendamento via Task Scheduler (Windows).
        Por padrão, executa diariamente às 2h da manhã.
        """
        logger.info("Configurando Task Scheduler para Windows...")
        
        task_name = "RadarPrecosPipeline"
        python_exe = sys.executable
        
        # Comando para criar tarefa
        cmd = [
            "schtasks",
            "/create",
            "/tn", task_name,
            "/tr", f'"{python_exe}" "{self.pipeline_script}"',
            "/sc", "daily",
            "/st", f"{hour:02d}:{minute:02d}",
            "/f"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Task Scheduler configurado com sucesso!")
                logger.info(f"   Tarefa: {task_name}")
                logger.info(f"   Execução: Diariamente às {hour:02d}:{minute:02d}")
                return True
            else:
                logger.error(f"Erro ao configurar Task Scheduler: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Erro ao configurar Task Scheduler: {e}")
            return False
    
    def setup_systemd_timer_linux(self, hour: int = 2, minute: int = 0) -> bool:
        """
        Configura agendamento via systemd timer (Linux moderno).
        """
        logger.info("Configurando systemd timer para Linux...")
        
        service_name = "radar-precos-pipeline"
        
        # Criar arquivo de serviço
        service_content = f"""[Unit]
Description=Radar de Preços - Pipeline de Automação
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {self.pipeline_script}
WorkingDirectory={self.project_root}
StandardOutput=journal
StandardError=journal
"""
        
        # Criar arquivo de timer
        timer_content = f"""[Unit]
Description=Radar de Preços - Pipeline Timer
Requires={service_name}.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* {hour:02d}:{minute:02d}:00
Persistent=true

[Install]
WantedBy=timers.target
"""
        
        try:
            systemd_dir = Path("/etc/systemd/system")
            
            if not systemd_dir.exists():
                logger.warning("systemd não encontrado no sistema")
                return False
            
            # Salvar arquivos (requer sudo)
            service_path = systemd_dir / f"{service_name}.service"
            timer_path = systemd_dir / f"{service_name}.timer"
            
            logger.info(f"⚠️  Requer permissões de administrador!")
            logger.info(f"   Salve os seguintes arquivos manualmente:")
            logger.info(f"   {service_path}")
            logger.info(f"   {timer_path}")
            logger.info(f"\n   Conteúdo do serviço:\n{service_content}")
            logger.info(f"\n   Conteúdo do timer:\n{timer_content}")
            
            return False
        
        except Exception as e:
            logger.error(f"Erro ao configurar systemd timer: {e}")
            return False
    
    def setup(self, hour: int = 2, minute: int = 0) -> bool:
        """
        Configura agendamento automático baseado no sistema operacional.
        """
        logger.info("=" * 80)
        logger.info("🔧 CONFIGURANDO AGENDAMENTO AUTOMÁTICO")
        logger.info("=" * 80)
        
        if not os.path.exists(self.pipeline_script):
            logger.error(f"Script de pipeline não encontrado: {self.pipeline_script}")
            return False
        
        if self.system == "Linux":
            # Tentar systemd primeiro, depois cron
            if not self.setup_systemd_timer_linux(hour, minute):
                return self.setup_cron_linux_mac(hour, minute)
            return True
        
        elif self.system == "Darwin":  # macOS
            return self.setup_cron_linux_mac(hour, minute)
        
        elif self.system == "Windows":
            return self.setup_task_scheduler_windows(hour, minute)
        
        else:
            logger.error(f"Sistema operacional não suportado: {self.system}")
            return False

def main():
    """Função principal."""
    # Determinar diretório raiz do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Criar e executar setup
    scheduler = SchedulerSetup(project_root)
    
    # Configurar para rodar às 2h da manhã todos os dias
    success = scheduler.setup(hour=2, minute=0)
    
    if success:
        logger.info("\n✅ Agendamento configurado com sucesso!")
    else:
        logger.warning("\n⚠️  Falha ao configurar agendamento automático")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
