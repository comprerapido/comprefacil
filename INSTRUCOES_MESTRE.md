# 🚀 Guia Mestre: Como Criar 10 Sites "Radar de Preços" em Minutos

Este guia contém tudo o que você precisa para replicar a inteligência do **Radar de Preços** em 10 novos repositórios e garantir a aprovação no AdSense.

---

## 📋 Pré-requisitos
1. Uma conta no GitHub.
2. Python 3 instalado.
3. Chave de API do Mercado Livre (opcional, mas recomendado).

---

## 🛠️ Passo a Passo para Cada Novo Site

### 1. Criar o Repositório
- No GitHub, crie um novo repositório (ex: `radar-tech`, `radar-pet`, etc.).
- **Importante:** Ative o **GitHub Pages** nas configurações (Settings > Pages > Deploy from a branch).

### 2. Copiar os Arquivos
- Baixe todos os arquivos deste repositório mestre.
- Cole no diretório do seu novo projeto.

### 3. Executar o Instalador
Abra o terminal na pasta do projeto e digite:
```bash
bash setup_novo_site.sh
```

### 4. Configurar o Nicho (Personalização)
Para que cada site seja único e o AdSense aprove todos:
- Abra `scripts/fetch_products.py`.
- Mude os termos de busca para o nicho do site (ex: se for `radar-pet`, mude para "ração", "brinquedo gato", etc.).
- Isso garante que cada um dos 10 sites tenha **conteúdo exclusivo**.

---

## 🤖 Inteligência Inclusa (Já Configurada)

✅ **Geração de Conteúdo (1000+ palavras):**
O robô cria automaticamente textos gigantes e profissionais para cada produto, garantindo que o Google veja "valor real" no site.

✅ **Deduplicação Inteligente:**
O sistema impede que produtos repetidos sejam postados, mantendo o site limpo.

✅ **Agendamento Distribuído Global:**
Já configuramos os 10 sites para publicarem em horários diferentes (offset de 6 min). 
*Basta você definir qual é o número do site (1 a 10) no `scripts/global_scheduler.py`.*

✅ **Template v2 Profissional:**
- Foto do produto no topo.
- Links de afiliado em destaque (topo e final).
- Menu de exploração com 24 seções para SEO.

---

## 💰 Dicas para Aprovação AdSense
1. **Tráfego Orgânico:** Deixe o robô postar por pelo menos 15 dias antes de pedir a aprovação.
2. **Páginas Legais:** Atualize os links de Privacidade e Termos com o nome do novo site.
3. **Nicho Específico:** Tente fazer cada um dos 10 sites focar em um nicho (Tech, Casa, Pet, etc.).

---

## 🚀 Comandos Úteis

**Rodar o robô manualmente:**
```bash
python3 scripts/automation_pipeline.py
```

**Verificar se está tudo certo:**
```bash
python3 scripts/monitor_system.py
```

---

**Desenvolvido com IA para ser o sistema de afiliados mais potente do mercado.** 🚀
