#!/usr/bin/env python3
"""
SEO Content Optimizer - Otimização de SEO, conteúdo evergreen, clusters e qualidade editorial.

Responsabilidades:
- Gerar conteúdo evergreen (guias, tutoriais, FAQs)
- Criar clusters de conteúdo por tema
- Otimizar títulos e meta descriptions
- Melhorar interligação interna
- Adicionar Schema.org estruturado
- Criar breadcrumbs
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import hashlib

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_json(path: Path, default: Any = None) -> Any:
    """Carrega arquivo JSON."""
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except:
        return default


def save_json(path: Path, data: Any) -> None:
    """Salva dados em JSON."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def generate_evergreen_content() -> Dict[str, Any]:
    """Gera conteúdo evergreen para SEO de longo prazo."""
    evergreen = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "guides": [],
        "tutorials": [],
        "faqs": []
    }
    
    # Guias evergreen por categoria
    evergreen_guides = [
        {
            "slug": "como-escolher-smartphone",
            "title": "Como Escolher o Melhor Smartphone para Suas Necessidades",
            "description": "Guia completo sobre como escolher um smartphone considerando processador, câmera, bateria e preço.",
            "category": "celular",
            "keywords": ["como escolher smartphone", "melhor celular", "smartphone barato"]
        },
        {
            "slug": "guia-compra-fone-bluetooth",
            "title": "Guia Completo: Fones Bluetooth - Qualidade, Preço e Durabilidade",
            "description": "Tudo que você precisa saber para comprar um fone Bluetooth de qualidade com melhor custo-benefício.",
            "category": "audio",
            "keywords": ["fone bluetooth", "fone sem fio", "melhor fone"]
        },
        {
            "slug": "como-economizar-em-compras",
            "title": "10 Estratégias Comprovadas para Economizar em Compras Online",
            "description": "Técnicas práticas e eficazes para conseguir melhores preços e descontos em suas compras.",
            "category": "geral",
            "keywords": ["como economizar", "dicas de compra", "descontos online"]
        },
        {
            "slug": "diferenca-produtos-originais-falsificados",
            "title": "Como Identificar Produtos Originais e Evitar Falsificações",
            "description": "Guia prático para diferenciar produtos originais de falsificados e fazer compras seguras.",
            "category": "geral",
            "keywords": ["produto original", "falsificação", "compra segura"]
        }
    ]
    
    evergreen["guides"] = evergreen_guides
    
    # Tutoriais evergreen
    evergreen_tutorials = [
        {
            "slug": "como-usar-cupons-desconto",
            "title": "Como Usar Cupons de Desconto e Maximizar Suas Economias",
            "description": "Passo a passo para encontrar, aplicar e aproveitar cupons de desconto em compras online.",
            "keywords": ["cupom desconto", "código promocional", "como usar cupom"]
        },
        {
            "slug": "dicas-seguranca-compras-online",
            "title": "Segurança em Compras Online: Dicas Essenciais para Proteger Seus Dados",
            "description": "Guia de segurança para fazer compras online com confiança e proteger suas informações pessoais.",
            "keywords": ["compra segura", "segurança online", "proteção dados"]
        }
    ]
    
    evergreen["tutorials"] = evergreen_tutorials
    
    # FAQs evergreen
    evergreen_faqs = [
        {
            "question": "Qual é a melhor época para comprar eletrônicos?",
            "answer": "A melhor época geralmente é durante Black Friday, Cyber Monday e datas comemorativas. Porém, comparar preços regularmente pode revelar boas oportunidades em qualquer período."
        },
        {
            "question": "Como saber se um produto é de qualidade?",
            "answer": "Verifique avaliações de outros compradores, número de vendas, marca conhecida, garantia oferecida e especificações técnicas. Produtos com muitas avaliações positivas são geralmente mais confiáveis."
        },
        {
            "question": "Vale a pena comprar produtos importados?",
            "answer": "Depende do produto. Alguns importados têm melhor preço, mas considere custos de importação, garantia internacional e tempo de entrega."
        },
        {
            "question": "Como rastrear meu pedido?",
            "answer": "Após a compra, você receberá um código de rastreamento por email. Use este código no site da transportadora para acompanhar seu pedido em tempo real."
        }
    ]
    
    evergreen["faqs"] = evergreen_faqs
    
    return evergreen


def create_content_clusters() -> Dict[str, Any]:
    """Cria estratégia de clusters de conteúdo por tema."""
    clusters = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "clusters": {}
    }
    
    # Definir clusters principais
    cluster_definitions = {
        "smartphones": {
            "pillar": "Guia Completo de Smartphones",
            "topics": [
                "Melhores smartphones 2026",
                "Smartphones baratos",
                "Smartphones premium",
                "Comparação de marcas",
                "Especificações técnicas explicadas"
            ],
            "keywords": ["smartphone", "celular", "iPhone", "Samsung", "Xiaomi"]
        },
        "audio": {
            "pillar": "Guia de Áudio e Fones",
            "topics": [
                "Melhores fones Bluetooth",
                "Fones com melhor custo-benefício",
                "Caixas de som portáteis",
                "Headphones profissionais",
                "Diferenças entre tipos de fone"
            ],
            "keywords": ["fone", "headphone", "bluetooth", "áudio", "som"]
        },
        "informatica": {
            "pillar": "Guia de Informática e Computadores",
            "topics": [
                "Melhores notebooks 2026",
                "Notebooks para programação",
                "Notebooks para games",
                "Tablets vs notebooks",
                "Componentes de PC"
            ],
            "keywords": ["notebook", "computador", "laptop", "tablet", "PC"]
        },
        "casa-inteligente": {
            "pillar": "Casa Inteligente e IoT",
            "topics": [
                "Dispositivos de casa inteligente",
                "Lâmpadas inteligentes",
                "Câmeras de segurança",
                "Assistentes de voz",
                "Automação residencial"
            ],
            "keywords": ["casa inteligente", "IoT", "automação", "smart home"]
        }
    }
    
    for cluster_name, cluster_data in cluster_definitions.items():
        clusters["clusters"][cluster_name] = {
            "name": cluster_name,
            "pillar_page": cluster_data["pillar"],
            "topics": cluster_data["topics"],
            "keywords": cluster_data["keywords"],
            "internal_links": []
        }
    
    return clusters


def optimize_page_metadata() -> Dict[str, Any]:
    """Gera metadata otimizada para páginas."""
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "templates": {}
    }
    
    # Templates de meta descriptions por tipo de página
    metadata["templates"]["product_page"] = {
        "title_template": "{product_name} - Melhor Preço | Compre Rápido",
        "description_template": "Encontre {product_name} com melhor preço. Análise completa, avaliações de clientes e comparação com concorrentes. Compre agora com segurança.",
        "min_description_length": 120,
        "max_description_length": 160
    }
    
    metadata["templates"]["category_page"] = {
        "title_template": "Melhores {category} 2026 - Preços e Comparação | Compre Rápido",
        "description_template": "Conheça os melhores {category} de 2026. Análises detalhadas, comparação de preços e dicas de compra. Encontre o produto ideal para você.",
        "min_description_length": 120,
        "max_description_length": 160
    }
    
    metadata["templates"]["guide_page"] = {
        "title_template": "{guide_title} - Guia Completo 2026 | Compre Rápido",
        "description_template": "{guide_description} Guia prático com dicas, comparações e recomendações de especialistas.",
        "min_description_length": 120,
        "max_description_length": 160
    }
    
    metadata["templates"]["comparison_page"] = {
        "title_template": "{product1} vs {product2} - Qual é Melhor? | Compre Rápido",
        "description_template": "Comparação detalhada entre {product1} e {product2}. Veja diferenças, preços, especificações e qual é a melhor opção para você.",
        "min_description_length": 120,
        "max_description_length": 160
    }
    
    return metadata


def generate_breadcrumb_schema() -> Dict[str, Any]:
    """Gera Schema.org Breadcrumb para navegação."""
    breadcrumbs = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "examples": {}
    }
    
    # Exemplos de breadcrumbs estruturados
    breadcrumbs["examples"]["product"] = {
        "path": ["Home", "Eletrônicos", "Smartphones", "iPhone 15"],
        "schema_type": "BreadcrumbList",
        "description": "Breadcrumb para página de produto"
    }
    
    breadcrumbs["examples"]["category"] = {
        "path": ["Home", "Eletrônicos", "Smartphones"],
        "schema_type": "BreadcrumbList",
        "description": "Breadcrumb para página de categoria"
    }
    
    breadcrumbs["examples"]["guide"] = {
        "path": ["Home", "Guias", "Como Escolher Smartphone"],
        "schema_type": "BreadcrumbList",
        "description": "Breadcrumb para página de guia"
    }
    
    return breadcrumbs


def generate_internal_linking_strategy() -> Dict[str, Any]:
    """Gera estratégia de interligação interna."""
    linking = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "strategies": {}
    }
    
    linking["strategies"]["product_to_category"] = {
        "description": "Cada página de produto deve linkar para sua categoria",
        "anchor_text": "Ver mais {category}",
        "priority": "high"
    }
    
    linking["strategies"]["product_to_comparison"] = {
        "description": "Páginas de produto devem linkar para comparações relevantes",
        "anchor_text": "Comparar com {competitor}",
        "priority": "high"
    }
    
    linking["strategies"]["product_to_guide"] = {
        "description": "Páginas de produto devem linkar para guias relacionados",
        "anchor_text": "Leia nosso guia: {guide_title}",
        "priority": "medium"
    }
    
    linking["strategies"]["category_to_guide"] = {
        "description": "Páginas de categoria devem linkar para guias de compra",
        "anchor_text": "Guia de compra de {category}",
        "priority": "high"
    }
    
    linking["strategies"]["guide_to_products"] = {
        "description": "Guias devem linkar para produtos recomendados",
        "anchor_text": "Ver produto recomendado",
        "priority": "high"
    }
    
    return linking


def main():
    """Executa otimização de SEO e conteúdo."""
    DATA_DIR.mkdir(exist_ok=True)
    
    print("Gerando estratégia de SEO e conteúdo...")
    
    # 1. Conteúdo evergreen
    evergreen = generate_evergreen_content()
    save_json(DATA_DIR / "evergreen_content.json", evergreen)
    print(f"✓ {len(evergreen['guides'])} guias evergreen gerados")
    
    # 2. Clusters de conteúdo
    clusters = create_content_clusters()
    save_json(DATA_DIR / "content_clusters_strategy.json", clusters)
    print(f"✓ {len(clusters['clusters'])} clusters de conteúdo criados")
    
    # 3. Metadata otimizada
    metadata = optimize_page_metadata()
    save_json(DATA_DIR / "metadata_templates.json", metadata)
    print(f"✓ Templates de metadata gerados")
    
    # 4. Breadcrumbs
    breadcrumbs = generate_breadcrumb_schema()
    save_json(DATA_DIR / "breadcrumb_schema.json", breadcrumbs)
    print(f"✓ Schema Breadcrumb gerado")
    
    # 5. Estratégia de interligação
    linking = generate_internal_linking_strategy()
    save_json(DATA_DIR / "internal_linking_strategy.json", linking)
    print(f"✓ Estratégia de interligação interna gerada")
    
    return {
        "evergreen_guides": len(evergreen["guides"]),
        "evergreen_tutorials": len(evergreen["tutorials"]),
        "clusters": len(clusters["clusters"]),
        "metadata_templates": len(metadata["templates"]),
        "linking_strategies": len(linking["strategies"])
    }


if __name__ == "__main__":
    result = main()
    print("\n" + json.dumps(result, indent=2, ensure_ascii=False))
