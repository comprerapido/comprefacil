# 🚀 DOCUMENTAÇÃO MESTRE: REDE RADAR DE PREÇOS

Este documento contém a especificação técnica completa para replicar o sistema **Radar de Preços** em 10 repositórios diferentes, garantindo automação total, conteúdo de alta qualidade e aprovação no Google AdSense.

---

## 1. 📋 VISÃO GERAL DO SISTEMA

O sistema foi projetado para ser uma "fábrica de sites de afiliados". Cada site opera de forma independente, mas segue um cronograma global para evitar punições por spam.

### Principais Funcionalidades:
- **Geração de Conteúdo IA:** Artigos com mais de 1000 palavras por produto.
- **Deduplicação Inteligente:** Impede produtos repetidos na rede.
- **Agendamento Distribuído:** Publicações escalonadas a cada 6 minutos entre os sites.
- **Template v2 Profissional:** Otimizado para conversão e SEO.

---

## 2. 🛠️ GUIA DE INSTALAÇÃO RÁPIDA

Para cada novo site, siga estes passos:

1. **Clonar/Copiar:** Copie todos os arquivos do repositório mestre para a nova pasta.
2. **Executar Setup:** No terminal, execute:
   ```bash
   bash setup_novo_site.sh
   ```
3. **Personalizar Nicho:** No arquivo `scripts/fetch_products.py`, altere os termos de busca para o nicho desejado (Ex: Tech, Pet, Casa).
4. **Configurar Agendamento:** Escolha o número do site (1-10) para definir o horário de publicação automático.

---

## 📅 3. CRONOGRAMA GLOBAL DE PUBLICAÇÕES

Para evitar que os 10 sites publiquem ao mesmo tempo, utilizamos um sistema de **Offsets de 6 minutos**:

| Site # | Nome Sugerido | Minuto da Hora | Exemplo de Horário |
| :--- | :--- | :--- | :--- |
| 1 | Radar Tech | :00 | 08:00, 09:00... |
| 2 | Radar Gamer | :06 | 08:06, 09:06... |
| 3 | Radar Casa | :12 | 08:12, 09:12... |
| 4 | Radar Eletro | :18 | 08:18, 09:18... |
| 5 | Radar Pet | :24 | 08:24, 09:24... |
| 6 | Radar Bebê | :30 | 08:30, 09:30... |
| 7 | Radar Beleza | :36 | 08:36, 09:36... |
| 8 | Radar Fitness | :42 | 08:42, 09:42... |
| 9 | Radar Auto | :48 | 08:48, 09:48... |
| 10 | Radar Ferramentas | :54 | 08:54, 09:54... |

*As publicações ocorrem diariamente entre **07:00 e 23:00**.*

---

## 🤖 4. A LÓGICA DO ROBÔ (CÓDIGO)

### Geração de Conteúdo (SEO/AEET)
O robô utiliza o script `generate_content.py` para criar descrições que:
- Possuem mais de 1000 palavras.
- Incluem H2, H3 e listas técnicas.
- Demonstram Autoridade e Confiança (AEET).
- Inserem links de afiliado no topo e no final.

### Deduplicação
O script `deduplicate_products.py` utiliza algoritmos de similaridade de strings para garantir que o mesmo produto não seja postado duas vezes, mesmo que o nome mude levemente.

---

## 💰 5. CHECKLIST PARA APROVAÇÃO ADSENSE

Para garantir que o Google aprove seus 10 sites:

1. **Conteúdo Original:** Deixe o robô gerar pelo menos 30-50 artigos antes de pedir a aprovação.
2. **Navegação:** O menu de 24 seções incluído no Template v2 ajuda o Google a entender que o site é um portal completo.
3. **Páginas Obrigatórias:** Certifique-se de que as páginas de *Privacidade*, *Termos* e *Sobre* estão com o nome correto do novo site.
4. **Velocidade:** O site é estático (HTML), o que garante nota máxima no Google PageSpeed.

---

## 🚀 CONCLUSÃO

Este sistema transforma um simples site de ofertas em uma rede profissional de conteúdo. Ao seguir este modelo, você terá 10 ativos digitais trabalhando 24h por dia para você.

**Sucesso com seu Radar de Preços!**
