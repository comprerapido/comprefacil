import os
import json
import re
from datetime import datetime
from logger import logger

# Importar OpenAI para geração de conteúdo
try:
    from openai import OpenAI
    client = OpenAI()
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.warning("OpenAI não está disponível. Usando fallback de conteúdo estático.")

def generate_product_description(product: dict) -> str:
    """
    Gera uma descrição detalhada de um produto com mais de 1000 palavras,
    otimizada para SEO e conformidade com AdSense (AEET).
    """
    
    if not HAS_OPENAI:
        return generate_fallback_description(product)
    
    product_name = product.get("name", "Produto")
    price = product.get("price", 0)
    original_price = product.get("originalPrice", 0)
    discount_pct = product.get("custom_discount_pct", 0)
    category = product.get("custom_category_slug", "outros")
    
    # Calcular economia
    economy = original_price - price if original_price > 0 else 0
    
    prompt = f"""
    Você é um especialista em análise de produtos e e-commerce. Crie uma descrição detalhada e profissional para o seguinte produto:
    
    **Produto:** {product_name}
    **Categoria:** {category}
    **Preço Atual:** R$ {price:.2f}
    **Preço Original:** R$ {original_price:.2f}
    **Desconto:** {discount_pct}%
    **Economia:** R$ {economy:.2f}
    
    Requisitos:
    1. Mínimo 1200 palavras
    2. Estrutura clara com títulos (H2, H3)
    3. Parágrafos bem desenvolvidos (3-5 frases cada)
    4. Incluir análise de benefícios e características
    5. Comparação com alternativas (genérico)
    6. Dicas de uso e manutenção
    7. Informações sobre garantia e suporte
    8. Call-to-action clara no final
    9. Otimizado para SEO (use palavras-chave naturalmente)
    10. Tom profissional e confiável (AEET - Autoridade, Especialidade, Experiência, Confiança)
    
    Estrutura sugerida:
    - Introdução ao produto
    - Principais características e especificações
    - Benefícios e vantagens
    - Análise detalhada
    - Comparação com alternativas
    - Dicas de uso e manutenção
    - Garantia e suporte
    - Por que comprar agora (urgência e valor)
    - Conclusão e recomendação
    
    Gere o conteúdo em Markdown, sem incluir o título principal (H1).
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em conteúdo de e-commerce e SEO. Crie descrições de produtos profissionais, detalhadas e otimizadas para mecanismos de busca."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content
        logger.info(f"Conteúdo gerado com sucesso para: {product_name}")
        return content
    
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo para {product_name}: {e}")
        return generate_fallback_description(product)

def generate_fallback_description(product: dict) -> str:
    """
    Gera uma descrição de fallback quando a API não está disponível.
    """
    
    product_name = product.get("name", "Produto")
    price = product.get("price", 0)
    original_price = product.get("originalPrice", 0)
    discount_pct = product.get("custom_discount_pct", 0)
    category = product.get("custom_category_slug", "outros")
    
    economy = original_price - price if original_price > 0 else 0
    
    description = f"""
## Descrição do Produto

{product_name} é uma excelente opção para quem busca qualidade e economia. Com um desconto de {discount_pct}%, você economiza R$ {economy:.2f} em relação ao preço original.

## Características Principais

Este produto oferece uma combinação perfeita de funcionalidade e valor. Ideal para uso diário, apresenta especificações técnicas robustas que garantem durabilidade e performance consistente.

### Especificações Técnicas

- **Preço Atual:** R$ {price:.2f}
- **Preço Original:** R$ {original_price:.2f}
- **Desconto:** {discount_pct}%
- **Economia Total:** R$ {economy:.2f}
- **Categoria:** {category.replace('-', ' ').title()}

## Benefícios e Vantagens

1. **Economia Significativa:** Com {discount_pct}% de desconto, você obtém um produto de qualidade por um preço competitivo.
2. **Qualidade Garantida:** Produto selecionado e verificado para garantir a melhor experiência de compra.
3. **Confiabilidade:** Vendedor verificado com histórico positivo no Mercado Livre.
4. **Suporte Completo:** Acesso a atendimento ao cliente profissional e políticas de devolução claras.

## Por Que Comprar Agora?

Esta é uma oportunidade limitada. O preço atual representa uma economia substancial comparado ao valor original. Produtos com descontos tão atrativos tendem a ter estoque limitado, portanto, é recomendável não adiar a compra.

## Informações de Compra

- **Plataforma:** Mercado Livre
- **Vendedor:** Verificado e confiável
- **Frete:** Consulte as opções disponíveis
- **Garantia:** Conforme política do vendedor

## Conclusão

{product_name} é uma escolha inteligente para quem deseja qualidade sem comprometer o orçamento. Com {discount_pct}% de desconto, você está fazendo um ótimo investimento.

**Não perca esta oportunidade!** Clique no botão abaixo para visualizar o produto completo e realizar sua compra com segurança no Mercado Livre.
"""
    
    return description.strip()

def process_products_with_content(input_path: str, output_path: str) -> None:
    """
    Processa produtos e adiciona conteúdo gerado a cada um.
    """
    
    logger.info(f"Iniciando geração de conteúdo para produtos em {input_path}...")
    
    if not os.path.exists(input_path):
        logger.error(f"Arquivo de entrada {input_path} não encontrado.")
        return
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler {input_path}: {e}")
        return
    
    processed_products = []
    
    for idx, product in enumerate(products, 1):
        try:
            # Gerar conteúdo para o produto
            description = generate_product_description(product)
            
            # Contar palavras
            word_count = len(description.split())
            
            # Adicionar conteúdo e metadados ao produto
            product["generated_description"] = description
            product["word_count"] = word_count
            product["content_generated_at"] = datetime.now().isoformat()
            
            processed_products.append(product)
            
            logger.info(f"[{idx}/{len(products)}] Conteúdo gerado para {product.get('name', 'Produto')} ({word_count} palavras)")
        
        except Exception as e:
            logger.error(f"Erro ao processar produto {idx}: {e}")
            processed_products.append(product)  # Adiciona sem conteúdo em caso de erro
    
    # Salvar produtos com conteúdo
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(processed_products, f, ensure_ascii=False, indent=2)
        logger.info(f"Geração de conteúdo concluída. {len(processed_products)} produtos processados.")
        logger.info(f"Resultados salvos em {output_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    process_products_with_content(
        "data/scored_products.json",
        "data/products_with_content.json"
    )
