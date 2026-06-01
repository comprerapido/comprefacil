#!/bin/bash

# =================================================================
# SCRIPT DE INSTALAÇÃO MESTRE - RADAR DE PREÇOS
# =================================================================
# Este script configura um novo repositório com toda a inteligência
# de automação, agendamento e geração de conteúdo.
# =================================================================

echo "🚀 Iniciando configuração do novo Radar de Preços..."

# 1. Criar estrutura de diretórios necessária
echo "📂 Criando estrutura de pastas..."
mkdir -p data/database
mkdir -p data/products
mkdir -p logs
mkdir -p templates
mkdir -p ofertas
mkdir -p scripts

# 2. Verificar dependências Python
echo "🐍 Verificando dependências Python..."
pip3 install requests beautifulsoup4 jinja2 pandas 2>/dev/null

# 3. Tornar scripts executáveis
echo "⚙️  Configurando permissões..."
chmod +x scripts/*.py 2>/dev/null
chmod +x scripts/*.sh 2>/dev/null

# 4. Inicializar banco de dados de agendamento
echo "📅 Inicializando sistema de agendamento..."
python3 scripts/global_scheduler.py

# 5. Gerar primeira versão da homepage
echo "🏠 Gerando homepage inicial..."
python3 scripts/build_homepage.py

# 6. Configurar Agendamento Automático (Cron)
echo "⏰ Deseja configurar o agendamento automático (Cron) agora? (s/n)"
read -r response
if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
    python3 scripts/setup_scheduler.py
else
    echo "⚠️  Lembre-se de configurar o agendamento manualmente depois."
fi

echo "================================================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
echo "================================================================="
echo "Próximos passos:"
echo "1. Configure suas chaves de API em scripts/fetch_products.py"
echo "2. Execute './scripts/automation_pipeline.py' para o primeiro teste"
echo "3. Submeta seu site ao Google Search Console e AdSense"
echo "================================================================="
