from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]

GUIDES = [
    dict(slug='melhor-smartphone-2026', path='guias/melhor-smartphone-2026/index.html', title='Melhor Smartphone 2026', category='Celulares', keyword='smartphone', category_url='/categorias/celulares/', ranking_url='/melhores-2026/melhores-smartphones-2026.html', comparison_url='/comparacoes/estrategicas/iphone-15-pro-vs-galaxy-s23-fe/'),
    dict(slug='melhor-air-fryer-2026', path='guias/melhor-air-fryer-2026/index.html', title='Melhor Air Fryer 2026', category='Eletrodomésticos', keyword='air fryer', category_url='/categorias/eletrodomesticos/', ranking_url='/melhores-2026/melhores-eletrodomesticos-2026/', comparison_url='/comparacoes/estrategicas/air-fryer-mondial-vs-philips-walita/'),
    dict(slug='melhores-fones-bluetooth', path='guias/melhores-fones-bluetooth/index.html', title='Melhores Fones Bluetooth 2026', category='Tecnologia', keyword='fone bluetooth', category_url='/categorias/tecnologia/', ranking_url='/melhores-2026/melhores-tecnologia-2026/', comparison_url='/comparacoes/estrategicas/jbl-wave-buds-vs-galaxy-buds-core/'),
    dict(slug='guia-de-compra-celulares-2026', path='guias/guia-de-compra-celulares-2026/index.html', title='Guia de Compra de Celulares 2026', category='Celulares', keyword='celular', category_url='/categorias/celulares/', ranking_url='/melhores-2026/melhores-celulares-2026/', comparison_url='/comparacoes/estrategicas/samsung-galaxy-a36-vs-motorola-moto-g35/'),
    dict(slug='guia-de-compra-informatica-2026', path='guias/guia-de-compra-informatica-2026/index.html', title='Guia de Compra de Informática 2026', category='Informática', keyword='notebook e periféricos', category_url='/categorias/informatica/', ranking_url='/melhores-2026/melhores-informatica-2026/', comparison_url='/comparacoes/estrategicas/notebook-samsung-book-vs-lenovo-ideapad/'),
    dict(slug='guia-de-compra-tv-e-video-2026', path='guias/guia-de-compra-tv-e-video-2026/index.html', title='Guia de Compra de TV e Vídeo 2026', category='TV e Vídeo', keyword='smart TV', category_url='/categorias/tv-e-video/', ranking_url='/melhores-2026/melhores-tv-e-video-2026/', comparison_url='/comparacoes/estrategicas/tv-lg-oled-vs-samsung-crystal-uhd/'),
    dict(slug='guia-de-compra-eletrodomesticos-2026', path='guias/guia-de-compra-eletrodomesticos-2026/index.html', title='Guia de Compra de Eletrodomésticos 2026', category='Eletrodomésticos', keyword='eletrodoméstico', category_url='/categorias/eletrodomesticos/', ranking_url='/melhores-2026/melhores-eletrodomesticos-2026/', comparison_url='/comparacoes/estrategicas/geladeira-brastemp-vs-electrolux/'),
    dict(slug='guia-de-compra-casa-2026', path='guias/guia-de-compra-casa-2026/index.html', title='Guia de Compra para Casa 2026', category='Casa', keyword='produto para casa', category_url='/categorias/casa/', ranking_url='/melhores-2026/melhores-casa-2026/', comparison_url='/comparacoes/estrategicas/aspirador-robo-vs-aspirador-vertical/'),
    dict(slug='guia-de-compra-games-2026', path='guias/guia-de-compra-games-2026/index.html', title='Guia de Compra de Games 2026', category='Games', keyword='console e acessório gamer', category_url='/categorias/games/', ranking_url='/melhores-2026/melhores-games-2026/', comparison_url='/comparacoes/estrategicas/playstation-5-vs-xbox-series-x/'),
    dict(slug='guia-de-compra-beleza-2026', path='guias/guia-de-compra-beleza-2026/index.html', title='Guia de Compra de Beleza 2026', category='Beleza', keyword='produto de beleza', category_url='/categorias/beleza/', ranking_url='/melhores-2026/melhores-beleza-2026/', comparison_url='/comparacoes/estrategicas/creatina-growth-vs-dark-lab/'),
    dict(slug='guia-de-compra-tecnologia-2026', path='guias/guia-de-compra-tecnologia-2026/index.html', title='Guia de Compra de Tecnologia 2026', category='Tecnologia', keyword='produto de tecnologia', category_url='/categorias/tecnologia/', ranking_url='/melhores-2026/melhores-tecnologia-2026/', comparison_url='/comparacoes/estrategicas/tablet-samsung-a11-vs-ipad-10a-geracao/'),
    dict(slug='guia-de-compra-esporte-2026', path='guias/guia-de-compra-esporte-2026/index.html', title='Guia de Compra de Esporte 2026', category='Esporte', keyword='equipamento esportivo', category_url='/categorias/esporte/', ranking_url='/melhores-2026/melhores-esporte-2026/', comparison_url='/comparacoes/estrategicas/bicicleta-ergometrica-vs-esteira-residencial/'),
    dict(slug='guia-de-compra-ferramentas-2026', path='guias/guia-de-compra-ferramentas-2026/index.html', title='Guia de Compra de Ferramentas 2026', category='Ferramentas', keyword='ferramenta', category_url='/categorias/ferramentas/', ranking_url='/melhores-2026/melhores-ferramentas-2026/', comparison_url='/comparacoes/estrategicas/parafusadeira-bosch-vs-makita/'),
    dict(slug='guia-de-compra-notebooks-2026', path='guias/guia-de-compra-notebooks-2026/index.html', title='Guia de Compra de Notebooks 2026', category='Informática', keyword='notebook', category_url='/categorias/informatica/', ranking_url='/melhores-2026/melhores-notebooks-2026.html', comparison_url='/comparacoes/estrategicas/macbook-air-vs-dell-inspiron/'),
    dict(slug='guia-de-compra-smart-tv-4k-2026', path='guias/guia-de-compra-smart-tv-4k-2026/index.html', title='Guia de Compra de Smart TV 4K 2026', category='TV e Vídeo', keyword='smart TV 4K', category_url='/categorias/tv-e-video/', ranking_url='/melhores-2026/melhores-tv-e-video-2026/', comparison_url='/comparacoes/estrategicas/tv-philco-roku-vs-lg-webos/'),
    dict(slug='guia-de-compra-geladeira-inox-2026', path='guias/guia-de-compra-geladeira-inox-2026/index.html', title='Guia de Compra de Geladeira Inox 2026', category='Eletrodomésticos', keyword='geladeira inox', category_url='/categorias/eletrodomesticos/', ranking_url='/melhores-2026/melhores-eletrodomesticos-2026/', comparison_url='/comparacoes/estrategicas/geladeira-brastemp-vs-electrolux/'),
    dict(slug='guia-de-compra-maquina-de-lavar-2026', path='guias/guia-de-compra-maquina-de-lavar-2026/index.html', title='Guia de Compra de Máquina de Lavar 2026', category='Eletrodomésticos', keyword='máquina de lavar', category_url='/categorias/eletrodomesticos/', ranking_url='/melhores-2026/melhores-eletrodomesticos-2026/', comparison_url='/comparacoes/estrategicas/maquina-lavar-11kg-vs-15kg/'),
    dict(slug='guia-de-compra-console-games-2026', path='guias/guia-de-compra-console-games-2026/index.html', title='Guia de Compra de Console de Games 2026', category='Games', keyword='console de games', category_url='/categorias/games/', ranking_url='/melhores-2026/melhores-games-2026/', comparison_url='/comparacoes/estrategicas/playstation-5-vs-xbox-series-x/'),
    dict(slug='guia-de-compra-casa-inteligente-2026', path='guias/guia-de-compra-casa-inteligente-2026/index.html', title='Guia de Compra de Casa Inteligente 2026', category='Casa Inteligente', keyword='casa inteligente', category_url='/categorias/casa-inteligente/', ranking_url='/melhores-2026/melhores-tecnologia-2026/', comparison_url='/comparacoes/estrategicas/alexa-echo-dot-vs-google-nest-mini/'),
    dict(slug='guia-de-compra-moda-estilo-2026', path='guias/guia-de-compra-moda-estilo-2026/index.html', title='Guia de Compra de Moda e Estilo 2026', category='Moda e Estilo', keyword='moda e estilo', category_url='/categorias/moda-estilo/', ranking_url='/melhores-2026/', comparison_url='/comparacoes/estrategicas/tenis-corrida-vs-tenis-casual/'),
]

CRITERIA = [
    ('Uso real', 'Compatibilidade do produto com a rotina brasileira, considerando instalação, garantia, manutenção e facilidade de revenda.'),
    ('Custo-benefício', 'Equilíbrio entre preço, recursos essenciais, durabilidade esperada e risco de pagar caro por funções pouco usadas.'),
    ('Sinais de qualidade', 'Histórico de avaliações, consistência da ficha técnica, reputação de marca, disponibilidade de assistência e transparência do anúncio.'),
    ('Preço e timing', 'Tendência de desconto, variação recente de preço, sazonalidade e probabilidade de uma oferta realmente vantajosa.'),
]

FAQS = [
    ('Qual é o melhor momento para comprar?', 'O melhor momento costuma ocorrer quando há combinação de estoque alto, cupons ativos e queda recente de preço. Antes de fechar a compra, compare o valor atual com o histórico de ofertas e evite decidir apenas pelo percentual de desconto exibido.'),
    ('Como saber se a oferta é confiável?', 'Verifique se o anúncio informa especificações completas, garantia, voltagem quando aplicável, política de devolução e reputação do vendedor. Uma oferta muito abaixo do mercado precisa ser analisada com mais cautela.'),
    ('Vale pagar mais por uma marca conhecida?', 'Vale quando a marca entrega suporte, peças, atualizações, assistência técnica e melhor liquidez de revenda. Se a diferença for grande, compare se os recursos adicionais realmente afetam o seu uso.'),
    ('Devo priorizar preço ou ficha técnica?', 'O ideal é priorizar adequação ao uso. Um produto barato que não atende à rotina gera recompra precoce; um produto caro com recursos ociosos reduz o custo-benefício.'),
    ('Como o Compre Rápido seleciona recomendações?', 'A curadoria combina leitura editorial, sinais de preço, consistência do anúncio, relevância da categoria e cruzamento com rankings, comparativos e páginas de ofertas atualizadas.'),
]

PROS = ['Boa relação entre utilidade e preço quando a escolha é feita por perfil de uso.', 'Ampla disponibilidade de ofertas e variações de configuração.', 'Facilidade para comparar modelos, marcas e faixas de preço antes da compra.', 'Possibilidade de economizar ao acompanhar rankings e alertas de oferta.']
CONS = ['Alguns anúncios usam descontos inflados ou fichas técnicas incompletas.', 'Modelos muito parecidos podem gerar confusão na escolha.', 'A opção mais barata nem sempre tem melhor durabilidade ou garantia.', 'Promoções relâmpago exigem conferência rápida de estoque e vendedor.']

def card_style():
    return "background:var(--card,#fff);border:1px solid var(--border,#dfe4ee);border-radius:18px;padding:24px;margin:28px 0;box-shadow:0 10px 26px rgba(15,23,42,.07);"

def phase2_block(g):
    title = escape(g['title'])
    keyword = escape(g['keyword'])
    category = escape(g['category'])
    rows = ''.join(f"<tr><td><strong>{escape(a)}</strong></td><td>{escape(b)}</td><td>{escape(c)}</td></tr>" for a,b,c in [
        ('Entrada consciente', f'Quem quer comprar {keyword} gastando o mínimo possível sem abrir mão do essencial.', 'Priorize garantia, avaliações consistentes e recursos básicos bem implementados.'),
        ('Intermediário equilibrado', f'Quem usa {keyword} com frequência e precisa de desempenho, conforto e vida útil maiores.', 'É a faixa com melhor custo-benefício para a maioria dos consumidores.'),
        ('Premium ou especialista', f'Quem depende de {keyword} para trabalho, lazer intensivo ou busca a melhor experiência disponível.', 'Só vale se os diferenciais forem usados na prática e se houver suporte adequado.'),
    ])
    crit = ''.join(f"<tr><td><strong>{escape(a)}</strong></td><td>{escape(b)}</td></tr>" for a,b in CRITERIA)
    pros = ''.join(f"<li>{escape(x)}</li>" for x in PROS)
    cons = ''.join(f"<li>{escape(x)}</li>" for x in CONS)
    faqs = ''.join(f"<details style='margin:12px 0;padding:14px;border:1px solid var(--border,#dfe4ee);border-radius:12px;background:#fff;'><summary><strong>{escape(q)}</strong></summary><p>{escape(a)}</p></details>" for q,a in FAQS)
    links = f"""
    <p>Para aprofundar a pesquisa, consulte também a <a href='{g['category_url']}'>categoria {category}</a>, o <a href='{g['ranking_url']}'>ranking relacionado</a> e o comparativo editorial <a href='{g['comparison_url']}'>A vs B recomendado</a>. Essa malha de links ajuda a navegar do aprendizado inicial para a decisão final de compra.</p>
    """
    return f"""
<!-- CR_PHASE2_GUIDE_ENRICHMENT_START -->
<section class="card cr-phase2-guide" style="{card_style()}">
  <h2>Introdução editorial: como escolher {title}</h2>
  <p>Escolher {keyword} em 2026 exige mais do que procurar o menor preço. O mercado está cheio de versões parecidas, nomes comerciais longos e promoções que parecem urgentes, mas nem sempre entregam a melhor compra. Este guia foi estruturado para transformar a pesquisa em uma decisão objetiva, conectando necessidade real, orçamento, durabilidade e histórico de preço.</p>
  <p>No Compre Rápido, tratamos cada recomendação como uma hipótese editorial que precisa fazer sentido para diferentes perfis de consumidor. Por isso, este conteúdo combina critérios práticos, comparação por faixa de uso, perguntas frequentes e links para rankings e páginas de categoria. O objetivo é evitar compras impulsivas e ajudar você a entender quando vale pagar mais, quando economizar e quais sinais observar antes de clicar em comprar.</p>
  {links}
</section>
<section class="card cr-phase2-method" style="{card_style()}">
  <h2>Metodologia de análise</h2>
  <p>A metodologia prioriza critérios verificáveis e úteis para compra online. Em vez de destacar apenas especificações isoladas, avaliamos o conjunto: adequação ao uso, reputação da marca, clareza do anúncio, custo total de propriedade, disponibilidade de assistência, avaliações de consumidores e coerência do preço em relação a alternativas próximas.</p>
  <table><thead><tr><th>Critério</th><th>Como pesa na decisão</th></tr></thead><tbody>{crit}</tbody></table>
</section>
<section class="card cr-phase2-comparison" style="{card_style()}">
  <h2>Tabela comparativa por perfil de compra</h2>
  <p>A tabela abaixo resume qual tipo de {keyword} tende a fazer mais sentido para cada perfil. Ela não substitui a análise do produto específico, mas reduz o risco de escolher uma opção acima ou abaixo da necessidade real.</p>
  <table><thead><tr><th>Perfil</th><th>Indicado para</th><th>Recomendação editorial</th></tr></thead><tbody>{rows}</tbody></table>
</section>
<section class="card cr-phase2-proscons" style="{card_style()}">
  <h2>Prós e contras antes de comprar</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;">
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;padding:18px;"><h3>Prós</h3><ul>{pros}</ul></div>
    <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:14px;padding:18px;"><h3>Contras</h3><ul>{cons}</ul></div>
  </div>
</section>
<section class="card cr-phase2-faq" style="{card_style()}">
  <h2>FAQ sobre {title}</h2>
  {faqs}
</section>
<section class="card cr-phase2-conclusion" style="{card_style()}">
  <h2>Conclusão editorial</h2>
  <p>O melhor {keyword} não é necessariamente o mais caro, o mais vendido ou o que aparece com o maior desconto. A melhor escolha é aquela que resolve sua necessidade com margem de durabilidade, preço compatível e menor risco pós-compra. Use este guia como ponto de partida, avance para os rankings e comparativos internos e, antes de comprar, confirme se o anúncio mantém ficha técnica, garantia e condições comerciais coerentes.</p>
</section>
<!-- CR_PHASE2_GUIDE_ENRICHMENT_END -->
"""

def full_page(g):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(g['title'])} | Compre Rápido</title>
  <meta name="description" content="{escape(g['title'])}: metodologia, tabela comparativa, prós e contras, FAQ e links para rankings e categorias do Compre Rápido.">
  <link rel="canonical" href="https://comprerapido.github.io/{g['path'].replace('index.html','')}">
  <link rel="stylesheet" href="/assets/css/style.css">
  <style>
    body {{ background:linear-gradient(180deg,#f8fafc 0%,#eef2ff 100%); font-family:Inter,Arial,sans-serif; line-height:1.65; color:#172033; }}
    .wrap {{ width:min(1120px,92vw); margin:0 auto; }} header,footer {{ background:#101827;color:#fff;padding:20px 0; }} header a,footer a {{ color:#fff; margin-right:14px; font-weight:700; text-decoration:none; }}
    .hero {{ padding:42px 0 20px; }} .crumbs {{ display:inline-block;background:#fff;border:1px solid #e2e8f0;border-radius:999px;padding:10px 14px; }} h1 {{ font-size:clamp(2rem,4vw,3.2rem); line-height:1.15; }}
    table {{ width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; }} th,td {{ border:1px solid #dfe4ee; padding:10px; text-align:left; }} th {{ background:#eef3ff; }}
    h2 {{ color:#0f172a;border-left:5px solid #f97316;padding-left:14px; }} .cta {{ display:inline-block;background:#2563eb;color:#fff;padding:13px 18px;border-radius:12px;font-weight:800;text-decoration:none; }}
  </style>
</head>
<body>
<header><div class="wrap"><strong>Compre Rápido</strong> <nav style="display:inline"><a href="/">Início</a><a href="/categorias/">Categorias</a><a href="/melhores-2026/">Rankings 2026</a><a href="/guias/">Guias</a></nav></div></header>
<main class="wrap">
  <section class="hero"><p class="crumbs"><a href="/">Início</a> › <a href="/guias/">Guias</a> › {escape(g['title'])}</p><h1>{escape(g['title'])}</h1><p>Guia editorial completo para escolher com segurança, comparar alternativas e comprar melhor em 2026.</p></section>
  {phase2_block(g)}
  <section class="card" style="{card_style()}"><h2>Próximos passos</h2><p>Continue a pesquisa pela <a href="{g['category_url']}">categoria</a>, compare ofertas no <a href="{g['ranking_url']}">ranking relacionado</a> e leia o <a href="{g['comparison_url']}">comparativo A vs B</a> para fechar a decisão.</p><a class="cta" href="/ofertas-hoje/">Ver ofertas atuais</a></section>
</main>
<footer><div class="wrap"><p><strong>Compre Rápido</strong> — curadoria editorial, rankings e inteligência de compras.</p></div></footer>
<script src="/assets/js/app.js"></script>
</body>
</html>
"""

def inject_existing(path, block):
    html = path.read_text(encoding='utf-8', errors='ignore')
    html = re.sub(r"\n?<!-- CR_PHASE2_GUIDE_ENRICHMENT_START -->.*?<!-- CR_PHASE2_GUIDE_ENRICHMENT_END -->\n?", "\n", html, flags=re.S)
    if '<!-- CR_RELATED_PRODUCTS -->' in html:
        html = html.replace('<!-- CR_RELATED_PRODUCTS -->', block + '\n        <!-- CR_RELATED_PRODUCTS -->', 1)
    elif '</main>' in html:
        html = html.replace('</main>', block + '\n</main>', 1)
    else:
        html += block
    path.write_text(html, encoding='utf-8')

changed = []
created = []
for g in GUIDES:
    p = ROOT / g['path']
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        inject_existing(p, phase2_block(g))
        changed.append(g['path'])
    else:
        p.write_text(full_page(g), encoding='utf-8')
        created.append(g['path'])

report = ROOT / 'data' / 'phase2_guides_manifest.json'
report.parent.mkdir(exist_ok=True)
import json
report.write_text(json.dumps({'created': created, 'changed': changed, 'total_guides': len(GUIDES), 'guides': GUIDES}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Guias enriquecidos: {len(GUIDES)} | existentes alterados: {len(changed)} | novos criados: {len(created)}')
print('Manifesto:', report)
