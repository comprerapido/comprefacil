# 🔧 Configuração de Agendamento Automático

## Opção 1: Linux com Cron (Recomendado)

### Passo 1: Abrir o editor de crontab
```bash
crontab -e
```

### Passo 2: Adicionar a seguinte linha
```bash
0 2 * * * cd /home/ubuntu/radar && /usr/bin/python3 /home/ubuntu/radar/scripts/automation_pipeline.py >> /home/ubuntu/radar/logs/cron.log 2>&1
```

**Explicação:**
- `0 2 * * *` = Executa diariamente às 2h da manhã
- `cd /home/ubuntu/radar` = Muda para o diretório do projeto
- `python3 automation_pipeline.py` = Executa o pipeline
- `>> logs/cron.log 2>&1` = Registra saída em arquivo de log

### Passo 3: Salvar e sair
- Se estiver usando `nano`: `Ctrl+X` → `Y` → `Enter`
- Se estiver usando `vi`: `:wq` → `Enter`

### Verificar se foi adicionado:
```bash
crontab -l
```

---

## Opção 2: macOS com Cron

Mesmo processo que Linux acima.

---

## Opção 3: Windows com Task Scheduler

### Passo 1: Abrir Task Scheduler
- Pressione `Win + R`
- Digite `taskschd.msc`
- Clique em OK

### Passo 2: Criar Nova Tarefa
- Clique em "Create Basic Task"
- Nome: `RadarPrecosPipeline`
- Descrição: `Automação do Radar de Preços`

### Passo 3: Configurar Agendamento
- Trigger: Daily
- Horário: 02:00 AM
- Repetir: Todos os dias

### Passo 4: Configurar Ação
- Action: Start a program
- Program: `C:\Python311\python.exe` (ou seu caminho do Python)
- Arguments: `C:\Users\YourUser\radar\scripts\automation_pipeline.py`
- Start in: `C:\Users\YourUser\radar`

### Passo 5: Finalizar
- Clique em "Finish"

---

## Opção 4: Executar Manualmente (Teste)

Para testar se tudo está funcionando:

```bash
cd /home/ubuntu/radar
python3 scripts/automation_pipeline.py
```

---

## 📊 Monitorar Execução

### Verificar logs do pipeline:
```bash
tail -f /home/ubuntu/radar/logs/automation_*.json
```

### Verificar saúde do sistema:
```bash
python3 /home/ubuntu/radar/scripts/monitor_system.py
```

### Verificar logs do cron (Linux):
```bash
tail -f /home/ubuntu/radar/logs/cron.log
```

---

## 🚨 Solução de Problemas

### Cron não está executando?
1. Verifique se o cron está rodando: `sudo service cron status`
2. Verifique os logs: `grep CRON /var/log/syslog`
3. Certifique-se de que o caminho do Python está correto

### Permissões negadas?
```bash
chmod +x /home/ubuntu/radar/scripts/automation_pipeline.py
chmod +x /home/ubuntu/radar/scripts/generate_content.py
chmod +x /home/ubuntu/radar/scripts/deduplicate_products.py
```

### Verificar se Python está no PATH:
```bash
which python3
```

---

## ✅ Checklist de Configuração

- [ ] Pipeline testado manualmente
- [ ] Cron/Task Scheduler configurado
- [ ] Logs sendo gerados
- [ ] Monitoramento ativado
- [ ] Primeira execução agendada confirmada

---

**Próximas Etapas:**
1. Configure o agendamento usando uma das opções acima
2. Teste executando manualmente
3. Monitore a primeira execução agendada
4. Verifique os logs para confirmar sucesso
