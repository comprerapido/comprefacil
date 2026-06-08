from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]

SUPPORT_GUIDES = [
    ('como-escolher-smartphone-2026','Como escolher smartphone em 2026','Celulares','smartphone','/guias/melhor-smartphone-2026/','/categorias/celulares/'),
    ('o-que-observar-antes-de-comprar-celular','O que observar antes de comprar celular','Celulares','celular','/guias/guia-de-compra-celulares-2026/','/categorias/celulares/'),
    ('vale-a-pena-comprar-smartphone-usado','Vale a pena comprar smartphone usado?','Celulares','smartphone usado','/guias/melhor-smartphone-2026/','/categorias/celulares/'),
    ('erros-comuns-ao-comprar-notebook','Erros comuns ao comprar notebook','Informática','notebook','/guias/guia-de-compra-notebooks-2026/','/categorias/informatica/'),
    ('como-escolher-notebook-para-trabalho','Como escolher notebook para trabalho','Informática','notebook para trabalho','/guias/guia-de-compra-informatica-2026/','/categorias/informatica/'),
    ('como-escolher-fone-bluetooth','Como escolher fone bluetooth','Tecnologia','fone bluetooth','/guias/melhores-fones-bluetooth/','/categorias/tecnologia/'),
    ('o-que-observar-antes-de-comprar-smart-tv','O que observar antes de comprar Smart TV','TV e Vídeo','smart TV','/guias/guia-de-compra-smart-tv-4k-2026/','/categorias/tv-e-video/'),
    ('erros-comuns-ao-comprar-tv-4k','Erros comuns ao comprar TV 4K','TV e Vídeo','TV 4K','/guias/guia-de-compra-tv-e-video-2026/','/categorias/tv-e-video/'),
    ('como-escolher-air-fryer','Como escolher air fryer','Eletrodomésticos','air fryer','/guias/melhor-air-fryer-2026/','/categorias/eletrodomesticos/'),
    ('o-que-observar-antes-de-comprar-geladeira','O que observar antes de comprar geladeira','Eletrodomésticos','geladeira','/guias/guia-de-compra-geladeira-inox-2026/','/categorias/eletrodomesticos/'),
    ('como-escolher-maquina-de-lavar','Como escolher máquina de lavar','Eletrodomésticos','máquina de lavar','/guias/guia-de-compra-maquina-de-lavar-2026/','/categorias/eletrodomesticos/'),
    ('vale-a-pena-comprar-eletrodomestico-usado','Vale a pena comprar eletrodoméstico usado?','Eletrodomésticos','eletrodoméstico usado','/guias/guia-de-compra-eletrodomesticos-2026/','/categorias/eletrodomesticos/'),
    ('como-escolher-aspirador-de-po','Como escolher aspirador de pó','Casa','aspirador de pó','/guias/guia-de-compra-casa-2026/','/categorias/casa/'),
    ('como-montar-casa-inteligente-gastando-pouco','Como montar casa inteligente gastando pouco','Casa Inteligente','casa inteligente','/guias/guia-de-compra-casa-inteligente-2026/','/categorias/casa-inteligente/'),
    ('como-escolher-console-de-games','Como escolher console de games','Games','console de games','/guias/guia-de-compra-console-games-2026/','/categorias/games/'),
    ('vale-a-pena-comprar-console-usado','Vale a pena comprar console usado?','Games','console usado','/guias/guia-de-compra-games-2026/','/categorias/games/'),
    ('como-escolher-creatina','Como escolher creatina','Beleza','creatina','/guias/guia-de-compra-beleza-2026/','/categorias/beleza/'),
    ('o-que-observar-antes-de-comprar-perfume-online','O que observar antes de comprar perfume online','Beleza','perfume online','/guias/guia-de-compra-beleza-2026/','/categorias/beleza/'),
    ('como-escolher-equipamentos-para-treinar-em-casa','Como escolher equipamentos para treinar em casa','Esporte','equipamento esportivo','/guias/guia-de-compra-esporte-2026/','/categorias/esporte/'),
    ('erros-comuns-ao-comprar-ferramentas','Erros comuns ao comprar ferramentas','Ferramentas','ferramentas','/guias/guia-de-compra-ferramentas-2026/','/categorias/ferramentas/'),
]

def build_page(slug,title,cat,keyword,guide,category):
    checklist = [
        ('Defina o uso principal', f'Antes de comparar preço, descreva como o {keyword} será usado na rotina. Isso evita pagar por recursos que não serão aproveitados.'),
        ('Compare especificações relevantes', 'Dê prioridade aos atributos que mudam a experiência real: capacidade, potência, autonomia, compatibilidade, garantia e assistência.'),
        ('Leia sinais de confiabilidade', 'Anúncios completos, avaliações coerentes, políticas de devolução claras e histórico do vendedor reduzem risco de compra.'),
        ('Avalie custo total', 'Preço de compra, acessórios, consumo, manutenção, frete e possível revenda devem entrar na conta.'),
    ]
    trs=''.join(f'<tr><td><strong>{escape(a)}</strong></td><td>{escape(b)}</td></tr>' for a,b in checklist)
    errors=''.join(f'<li>{escape(x)}</li>' for x in [
        'Comprar apenas pelo maior desconto anunciado, sem verificar histórico e preço médio.',
        'Ignorar garantia, voltagem, compatibilidade, dimensões ou geração do produto.',
        'Escolher o modelo mais caro sem necessidade real ou o mais barato sem suporte mínimo.',
        'Não comparar o produto com alternativas próximas na mesma categoria.',
    ])
    faq=''.join(f'<details><summary><strong>{escape(q)}</strong></summary><p>{escape(a)}</p></details>' for q,a in [
        ('Quando vale esperar por uma promoção?', 'Vale esperar quando o produto não é urgente, o preço atual está acima da média ou há datas promocionais próximas. Se o produto atende uma necessidade imediata e está com preço competitivo, a compra pode fazer sentido.'),
        ('Como saber se estou pagando caro?', 'Compare o preço entre lojas, confira ofertas recentes e observe se há modelos equivalentes com melhor custo-benefício. Diferenças pequenas podem ser justificadas por garantia e entrega melhores.'),
        ('Produto usado vale a pena?', 'Pode valer para categorias com boa durabilidade e fácil inspeção, mas exige nota fiscal, teste funcional, garantia residual e preço significativamente menor que o novo.'),
    ])
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | Guia de Apoio Compre Rápido</title><meta name="description" content="{escape(title)}: checklist, erros comuns, metodologia de compra e links para guias, rankings e categorias do Compre Rápido."><link rel="canonical" href="https://comprerapido.github.io/guias/apoio/{slug}/"><style>body{{margin:0;background:linear-gradient(180deg,#f8fafc,#eef2ff);font-family:Inter,Arial,sans-serif;color:#172033;line-height:1.65}}.wrap{{width:min(1120px,92vw);margin:auto}}header,footer{{background:#101827;color:white;padding:20px 0}}header a,footer a{{color:white;margin-right:14px;text-decoration:none;font-weight:700}}.card{{background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:24px;margin:24px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)}}h1{{font-size:clamp(2rem,4vw,3.2rem);line-height:1.15}}h2{{border-left:5px solid #f97316;padding-left:14px}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{border:1px solid #dfe4ee;padding:11px;text-align:left;vertical-align:top}}th{{background:#eef3ff}}details{{margin:12px 0;padding:14px;border:1px solid #dfe4ee;border-radius:12px;background:#fff}}.cta{{display:inline-block;background:#2563eb;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:800}}</style></head><body><header><div class="wrap"><strong>Compre Rápido</strong> <nav style="display:inline"><a href="/">Início</a><a href="/guias/">Guias</a><a href="/categorias/">Categorias</a><a href="/melhores-2026/">Rankings</a></nav></div></header><main class="wrap"><p style="margin-top:24px"><a href="/">Início</a> › <a href="/guias/">Guias</a> › Apoio</p><h1>{escape(title)}</h1><section class="card"><h2>Introdução</h2><p>Este guia de apoio aprofunda uma dúvida prática antes da compra de <strong>{escape(keyword)}</strong>. A proposta é reduzir incertezas, organizar critérios e conectar sua pesquisa aos guias principais do Compre Rápido.</p><p>Use este conteúdo junto com o <a href="{guide}">guia principal</a> e a <a href="{category}">categoria {escape(cat)}</a>. Assim, você passa da orientação geral para produtos, rankings e comparativos com mais segurança.</p></section><section class="card"><h2>Checklist objetivo antes de comprar</h2><table><thead><tr><th>Etapa</th><th>Como aplicar</th></tr></thead><tbody>{trs}</tbody></table></section><section class="card"><h2>Erros mais comuns</h2><p>Os erros abaixo aparecem com frequência em compras online e podem transformar uma oferta aparentemente boa em uma compra ruim.</p><ul>{errors}</ul></section><section class="card"><h2>Vale a pena?</h2><p>Vale a pena comprar quando o produto resolve uma necessidade clara, possui documentação comercial completa, preço compatível e baixo risco pós-compra. Se algum desses pontos estiver fraco, o melhor caminho é comparar opções, esperar nova oferta ou escolher uma configuração mais adequada.</p></section><section class="card"><h2>FAQ</h2>{faq}</section><section class="card"><h2>Conclusão editorial</h2><p>A melhor compra nasce de uma decisão informada. Antes de finalizar, volte ao guia principal, confira a categoria e compare alternativas próximas. Essa sequência aumenta a chance de economizar sem sacrificar qualidade.</p><a class="cta" href="{guide}">Ler guia principal</a></section></main><footer><div class="wrap"><p><strong>Compre Rápido</strong> — guias de apoio para decisões de compra melhores.</p></div></footer></body></html>'''

created=[]
for item in SUPPORT_GUIDES:
    slug,*rest=item
    path=ROOT/'guias'/'apoio'/slug/'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_page(slug,*rest), encoding='utf-8')
    created.append(str(path.relative_to(ROOT)))
manifest=ROOT/'data'/'phase2_support_guides_manifest.json'
manifest.write_text(json.dumps({'total_support_guides':len(created),'created':created}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Guias de apoio criados/atualizados: {len(created)}')
print('Manifesto:', manifest)
