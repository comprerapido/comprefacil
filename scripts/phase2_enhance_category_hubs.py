from pathlib import Path
from html import escape
import json, re

ROOT=Path(__file__).resolve().parents[1]
CATEGORY_MAP={
 'celulares':('Celulares','/guias/guia-de-compra-celulares-2026/','/melhores-2026/melhores-celulares-2026/','/comparacoes/estrategicas/samsung-galaxy-a36-vs-motorola-moto-g35/'),
 'informatica':('Informática','/guias/guia-de-compra-informatica-2026/','/melhores-2026/melhores-informatica-2026/','/comparacoes/estrategicas/notebook-samsung-book-vs-lenovo-ideapad/'),
 'smartphones-informatica':('Smartphones e Informática','/guias/melhor-smartphone-2026/','/melhores-2026/melhores-smartphones-2026.html','/comparacoes/estrategicas/iphone-15-pro-vs-galaxy-s23-fe/'),
 'tecnologia':('Tecnologia','/guias/guia-de-compra-tecnologia-2026/','/melhores-2026/melhores-tecnologia-2026/','/comparacoes/estrategicas/tablet-samsung-a11-vs-ipad-10a-geracao/'),
 'tv-e-video':('TV e Vídeo','/guias/guia-de-compra-tv-e-video-2026/','/melhores-2026/melhores-tv-e-video-2026/','/comparacoes/estrategicas/tv-lg-oled-vs-samsung-crystal-uhd/'),
 'eletrodomesticos':('Eletrodomésticos','/guias/guia-de-compra-eletrodomesticos-2026/','/melhores-2026/melhores-eletrodomesticos-2026/','/comparacoes/estrategicas/air-fryer-mondial-vs-philips-walita/'),
 'casa':('Casa','/guias/guia-de-compra-casa-2026/','/melhores-2026/melhores-casa-2026/','/comparacoes/estrategicas/aspirador-robo-vs-aspirador-vertical/'),
 'casa-inteligente':('Casa Inteligente','/guias/guia-de-compra-casa-inteligente-2026/','/melhores-2026/melhores-tecnologia-2026/','/comparacoes/estrategicas/alexa-echo-dot-vs-google-nest-mini/'),
 'games':('Games','/guias/guia-de-compra-games-2026/','/melhores-2026/melhores-games-2026/','/comparacoes/estrategicas/playstation-5-vs-xbox-series-x/'),
 'beleza':('Beleza','/guias/guia-de-compra-beleza-2026/','/melhores-2026/melhores-beleza-2026/','/comparacoes/estrategicas/creatina-growth-vs-dark-lab/'),
 'esporte':('Esporte','/guias/guia-de-compra-esporte-2026/','/melhores-2026/melhores-esporte-2026/','/comparacoes/estrategicas/bicicleta-ergometrica-vs-esteira-residencial/'),
 'esporte-bem-estar':('Esporte e Bem-Estar','/guias/guia-de-compra-esporte-2026/','/melhores-2026/melhores-esporte-2026/','/comparacoes/estrategicas/bicicleta-ergometrica-vs-esteira-residencial/'),
 'ferramentas':('Ferramentas','/guias/guia-de-compra-ferramentas-2026/','/melhores-2026/melhores-ferramentas-2026/','/comparacoes/estrategicas/parafusadeira-bosch-vs-makita/'),
 'moda-estilo':('Moda e Estilo','/guias/guia-de-compra-moda-estilo-2026/','/melhores-2026/','/comparacoes/estrategicas/tenis-corrida-vs-tenis-casual/'),
 'entretenimento':('Entretenimento','/guias/guia-de-compra-tv-e-video-2026/','/melhores-2026/melhores-tv-e-video-2026/','/comparacoes/estrategicas/nintendo-switch-vs-steam-deck/'),
 'universo-infantil':('Universo Infantil','/guias/guia-de-compra-casa-2026/','/melhores-2026/','/guias/apoio/o-que-observar-antes-de-comprar-celular/'),
}

def block(slug,name,guide,ranking,comparison):
    return f'''
<!-- CR_PHASE2_CATEGORY_HUB_START -->
<section class="card cr-category-hub" style="background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:24px;margin:28px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)">
  <h2>Hub editorial de {escape(name)}</h2>
  <p>Esta categoria funciona como página hub para quem está pesquisando produtos de <strong>{escape(name)}</strong>. Além das ofertas listadas, ela reúne guias, rankings e comparativos que ajudam a transformar interesse em decisão de compra com menor risco.</p>
  <p>A recomendação editorial é iniciar pelo guia, comparar modelos semelhantes, validar alternativas no ranking e só então conferir a oferta ativa. Essa sequência reduz compras impulsivas e melhora a qualidade do tráfego orgânico enviado para páginas transacionais.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:18px">
    <article style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:16px"><h3>Guia principal</h3><p><a href="{guide}">Como escolher em {escape(name)}</a></p></article>
    <article style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:16px"><h3>Ranking</h3><p><a href="{ranking}">Melhores opções 2026</a></p></article>
    <article style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:16px"><h3>Comparativo</h3><p><a href="{comparison}">Comparar alternativas A vs B</a></p></article>
  </div>
</section>
<section class="card cr-category-method" style="background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:24px;margin:28px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)">
  <h2>Critérios de curadoria da categoria</h2>
  <table><thead><tr><th>Critério</th><th>Aplicação prática</th></tr></thead><tbody><tr><td><strong>Relevância</strong></td><td>Produtos e conteúdos precisam responder dúvidas reais de compra da categoria.</td></tr><tr><td><strong>Preço confiável</strong></td><td>Ofertas são analisadas considerando desconto plausível, histórico e custo total.</td></tr><tr><td><strong>Qualidade do anúncio</strong></td><td>Fichas completas, garantia, reputação e clareza reduzem risco de conversão ruim.</td></tr><tr><td><strong>Interligação editorial</strong></td><td>Guias, comparativos, rankings e produtos se reforçam para criar cluster temático consistente.</td></tr></tbody></table>
</section>
<section class="card cr-category-faq" style="background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:24px;margin:28px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)">
  <h2>Perguntas frequentes sobre {escape(name)}</h2>
  <details style="margin:12px 0;padding:14px;border:1px solid #dfe4ee;border-radius:12px"><summary><strong>Como escolher a melhor oferta?</strong></summary><p>Compare preço, garantia, ficha técnica e histórico de avaliações antes de decidir. Uma boa oferta combina valor competitivo e baixo risco pós-compra.</p></details>
  <details style="margin:12px 0;padding:14px;border:1px solid #dfe4ee;border-radius:12px"><summary><strong>Devo começar por guia, ranking ou produto?</strong></summary><p>Comece pelo guia se ainda estiver pesquisando, avance para o ranking se já sabe o tipo de produto e use o produto quando a decisão estiver praticamente tomada.</p></details>
  <details style="margin:12px 0;padding:14px;border:1px solid #dfe4ee;border-radius:12px"><summary><strong>Por que há links para comparativos?</strong></summary><p>Comparativos A vs B ajudam a resolver dúvidas de escolha entre marcas, modelos e faixas de preço, aumentando a confiança antes da compra.</p></details>
</section>
<!-- CR_PHASE2_CATEGORY_HUB_END -->
'''

updated=[]
for slug,data in CATEGORY_MAP.items():
    p=ROOT/'categorias'/slug/'index.html'
    if not p.exists():
        continue
    h=p.read_text(encoding='utf-8',errors='ignore')
    h=re.sub(r"\n?<!-- CR_PHASE2_CATEGORY_HUB_START -->.*?<!-- CR_PHASE2_CATEGORY_HUB_END -->\n?","\n",h,flags=re.S)
    b=block(slug,*data)
    if '</main>' in h:
        h=h.replace('</main>',b+'</main>',1)
    else:
        h+=b
    p.write_text(h,encoding='utf-8')
    updated.append(f'categorias/{slug}/index.html')

# Rebuild categories index as complete hub of hubs
cards=''.join(f"<article class='card'><h3><a href='/categorias/{slug}/'>{escape(name)}</a></h3><p><a href='{guide}'>Guia</a> · <a href='{ranking}'>Ranking</a> · <a href='{comparison}'>Comparativo</a></p></article>" for slug,(name,guide,ranking,comparison) in CATEGORY_MAP.items())
idx=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Categorias principais | Compre Rápido</title><meta name="description" content="Hub de categorias do Compre Rápido com links para guias, rankings, comparativos e ofertas."><link rel="canonical" href="https://comprerapido.github.io/categorias/"><style>body{{margin:0;background:linear-gradient(180deg,#f8fafc,#eef2ff);font-family:Inter,Arial,sans-serif;color:#172033;line-height:1.65}}.wrap{{width:min(1120px,92vw);margin:auto}}header,footer{{background:#101827;color:#fff;padding:20px 0}}header a,footer a{{color:#fff;margin-right:14px;text-decoration:none;font-weight:700}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card{{background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:22px;margin:18px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)}}h1{{font-size:clamp(2rem,4vw,3.2rem)}}h2{{border-left:5px solid #f97316;padding-left:14px}}</style></head><body><header><div class="wrap"><strong>Compre Rápido</strong> <nav style="display:inline"><a href="/">Início</a><a href="/guias/">Guias</a><a href="/comparacoes/">Comparações</a><a href="/melhores-2026/">Rankings</a></nav></div></header><main class="wrap"><h1>Categorias principais</h1><p>Este hub organiza as principais categorias do Compre Rápido e conecta cada uma a guias, rankings e comparativos. A página foi estruturada para reforçar clusters temáticos e reduzir a distância entre conteúdo educativo e páginas de oferta.</p><div class="grid">{cards}</div></main><footer><div class="wrap"><p><strong>Compre Rápido</strong> — encontre rápido, compre melhor.</p></div></footer></body></html>'''
(ROOT/'categorias/index.html').write_text(idx,encoding='utf-8')
updated.append('categorias/index.html')
manifest=ROOT/'data/phase2_category_hubs_manifest.json'
manifest.write_text(json.dumps({'updated_count':len(updated),'updated':updated},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Hubs de categoria atualizados: {len(updated)}')
