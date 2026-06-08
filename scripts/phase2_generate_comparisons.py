from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]

COMPARISONS = [
    ('iphone-15-pro-vs-galaxy-s23-fe','iPhone 15 Pro','Galaxy S23 FE','Celulares','/guias/melhor-smartphone-2026/','/categorias/celulares/'),
    ('samsung-galaxy-a36-vs-motorola-moto-g35','Samsung Galaxy A36','Motorola Moto G35','Celulares','/guias/guia-de-compra-celulares-2026/','/categorias/celulares/'),
    ('samsung-galaxy-a17-vs-galaxy-a07','Samsung Galaxy A17','Samsung Galaxy A07','Celulares','/guias/guia-de-compra-celulares-2026/','/categorias/celulares/'),
    ('macbook-air-vs-dell-inspiron','MacBook Air','Dell Inspiron','Informática','/guias/guia-de-compra-notebooks-2026/','/categorias/informatica/'),
    ('notebook-samsung-book-vs-lenovo-ideapad','Samsung Book','Lenovo IdeaPad','Informática','/guias/guia-de-compra-informatica-2026/','/categorias/informatica/'),
    ('tablet-samsung-a11-vs-ipad-10a-geracao','Samsung Galaxy Tab A11','iPad 10ª geração','Tecnologia','/guias/guia-de-compra-tecnologia-2026/','/categorias/tecnologia/'),
    ('jbl-wave-buds-vs-galaxy-buds-core','JBL Wave Buds','Galaxy Buds Core','Tecnologia','/guias/melhores-fones-bluetooth/','/categorias/tecnologia/'),
    ('tv-lg-oled-vs-samsung-crystal-uhd','LG OLED','Samsung Crystal UHD','TV e Vídeo','/guias/guia-de-compra-smart-tv-4k-2026/','/categorias/tv-e-video/'),
    ('tv-philco-roku-vs-lg-webos','Philco Roku TV','LG webOS','TV e Vídeo','/guias/guia-de-compra-tv-e-video-2026/','/categorias/tv-e-video/'),
    ('air-fryer-mondial-vs-philips-walita','Air Fryer Mondial','Air Fryer Philips Walita','Eletrodomésticos','/guias/melhor-air-fryer-2026/','/categorias/eletrodomesticos/'),
    ('geladeira-brastemp-vs-electrolux','Geladeira Brastemp','Geladeira Electrolux','Eletrodomésticos','/guias/guia-de-compra-geladeira-inox-2026/','/categorias/eletrodomesticos/'),
    ('maquina-lavar-11kg-vs-15kg','Máquina de Lavar 11 kg','Máquina de Lavar 15 kg','Eletrodomésticos','/guias/guia-de-compra-maquina-de-lavar-2026/','/categorias/eletrodomesticos/'),
    ('aspirador-robo-vs-aspirador-vertical','Aspirador Robô','Aspirador Vertical','Casa','/guias/guia-de-compra-casa-2026/','/categorias/casa/'),
    ('alexa-echo-dot-vs-google-nest-mini','Echo Dot Alexa','Google Nest Mini','Casa Inteligente','/guias/guia-de-compra-casa-inteligente-2026/','/categorias/casa-inteligente/'),
    ('playstation-5-vs-xbox-series-x','PlayStation 5','Xbox Series X','Games','/guias/guia-de-compra-console-games-2026/','/categorias/games/'),
    ('nintendo-switch-vs-steam-deck','Nintendo Switch','Steam Deck','Games','/guias/guia-de-compra-games-2026/','/categorias/games/'),
    ('creatina-growth-vs-dark-lab','Creatina Growth','Creatina Dark Lab','Beleza','/guias/guia-de-compra-beleza-2026/','/categorias/beleza/'),
    ('tenis-corrida-vs-tenis-casual','Tênis de Corrida','Tênis Casual','Moda e Estilo','/guias/guia-de-compra-moda-estilo-2026/','/categorias/moda-estilo/'),
    ('bicicleta-ergometrica-vs-esteira-residencial','Bicicleta Ergométrica','Esteira Residencial','Esporte','/guias/guia-de-compra-esporte-2026/','/categorias/esporte/'),
    ('parafusadeira-bosch-vs-makita','Parafusadeira Bosch','Parafusadeira Makita','Ferramentas','/guias/guia-de-compra-ferramentas-2026/','/categorias/ferramentas/'),
]

def page(slug,a,b,cat,guide,category):
    title = f'{a} vs {b}: qual vale mais a pena em 2026?'
    rows = [
        ('Perfil ideal', f'{a} tende a ser melhor para quem prioriza experiência mais refinada, ecossistema ou construção.', f'{b} costuma fazer mais sentido para quem busca equilíbrio entre preço, recursos e disponibilidade.'),
        ('Custo-benefício', 'Vale quando o preço está próximo do histórico mínimo ou quando os diferenciais serão usados todos os dias.', 'Ganha força quando entrega recursos essenciais com preço menor e menor custo de manutenção.'),
        ('Risco de compra', 'Exige conferir garantia, versão correta e compatibilidade com acessórios ou instalação.', 'Também exige atenção a geração, capacidade, voltagem, armazenamento ou acessórios inclusos.'),
        ('Melhor para', 'Usuários exigentes, uso profissional ou quem pretende ficar mais tempo com o produto.', 'Consumidores que querem boa compra racional, sem pagar por recursos pouco usados.'),
    ]
    trs = ''.join(f'<tr><td><strong>{escape(k)}</strong></td><td>{escape(va)}</td><td>{escape(vb)}</td></tr>' for k,va,vb in rows)
    faqs = ''.join(f"<details><summary><strong>{escape(q)}</strong></summary><p>{escape(ans)}</p></details>" for q,ans in [
        (f'{a} é sempre melhor que {b}?', 'Não. A melhor escolha depende do preço no dia, do uso pretendido e dos diferenciais que você realmente aproveitará.'),
        ('Qual opção costuma ter melhor custo-benefício?', 'A alternativa com menor preço total e recursos suficientes para sua rotina tende a vencer em custo-benefício, mesmo que não seja a mais avançada.'),
        ('Como decidir em uma promoção relâmpago?', 'Compare preço, garantia, ficha técnica, avaliações e histórico de oferta. Se algum dado essencial estiver ausente, evite comprar por impulso.'),
    ])
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | Compre Rápido</title><meta name="description" content="Comparativo {escape(a)} vs {escape(b)} com tabela, prós e contras, veredicto editorial e links para guias do Compre Rápido."><link rel="canonical" href="https://comprerapido.github.io/comparacoes/estrategicas/{slug}/"><style>:root{{--bg:#f7f8fb;--card:#fff;--text:#172033;--muted:#5b6475;--brand:#0f62fe;--border:#dfe4ee}}body{{margin:0;background:linear-gradient(180deg,#f8fafc,#eef2ff);font-family:Inter,Arial,sans-serif;color:var(--text);line-height:1.65}}.wrap{{width:min(1120px,92vw);margin:auto}}header,footer{{background:#101827;color:#fff;padding:20px 0}}header a,footer a{{color:#fff;margin-right:14px;text-decoration:none;font-weight:700}}.card{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:24px;margin:24px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)}}h1{{font-size:clamp(2rem,4vw,3.2rem);line-height:1.15}}h2{{border-left:5px solid #f97316;padding-left:14px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{border:1px solid var(--border);padding:11px;text-align:left;vertical-align:top}}th{{background:#eef3ff}}details{{margin:12px 0;padding:14px;border:1px solid var(--border);border-radius:12px;background:#fff}}.cta{{display:inline-block;background:#2563eb;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:800}}</style></head><body><header><div class="wrap"><strong>Compre Rápido</strong> <nav style="display:inline"><a href="/">Início</a><a href="/comparacoes/">Comparações</a><a href="/guias/">Guias</a><a href="/melhores-2026/">Rankings</a></nav></div></header><main class="wrap"><p style="margin-top:24px"><a href="/">Início</a> › <a href="/comparacoes/">Comparações</a> › {escape(a)} vs {escape(b)}</p><h1>{escape(title)}</h1><section class="card"><h2>Resumo editorial</h2><p>Este comparativo foi criado para responder uma dúvida direta de compra: entre <strong>{escape(a)}</strong> e <strong>{escape(b)}</strong>, qual opção entrega mais valor em 2026? A resposta depende do perfil de uso, do preço atual e do risco pós-compra. Por isso, analisamos critérios práticos em vez de declarar um vencedor absoluto.</p><p>Antes de comprar, leia também o <a href="{guide}">guia de compra relacionado</a> e veja a <a href="{category}">categoria {escape(cat)}</a> para conferir alternativas e ofertas atualizadas.</p></section><section class="card"><h2>Tabela comparativa</h2><table><thead><tr><th>Critério</th><th>{escape(a)}</th><th>{escape(b)}</th></tr></thead><tbody>{trs}</tbody></table></section><section class="card"><h2>Prós e contras</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px"><div><h3>{escape(a)}</h3><p><strong>Prós:</strong> melhor para quem valoriza acabamento, estabilidade e diferenciais específicos.</p><p><strong>Contras:</strong> pode custar mais caro e exigir atenção a versões, acessórios ou ecossistema.</p></div><div><h3>{escape(b)}</h3><p><strong>Prós:</strong> costuma entregar bom equilíbrio para compra racional e orçamento controlado.</p><p><strong>Contras:</strong> pode abrir mão de recursos premium ou ter variações de qualidade entre versões.</p></div></div></section><section class="card"><h2>Veredicto: qual comprar?</h2><p>Escolha <strong>{escape(a)}</strong> se os diferenciais técnicos e de experiência forem relevantes para sua rotina e se o preço estiver competitivo. Escolha <strong>{escape(b)}</strong> se a prioridade for pagar menos mantendo os recursos essenciais. O vencedor real é o produto que combina preço confiável, garantia clara e adequação ao uso.</p><a class="cta" href="{category}">Ver ofertas da categoria</a></section><section class="card"><h2>FAQ</h2>{faqs}</section></main><footer><div class="wrap"><p><strong>Compre Rápido</strong> — comparativos editoriais para comprar melhor.</p></div></footer></body></html>'''

created=[]
for item in COMPARISONS:
    slug,*rest = item
    path = ROOT / 'comparacoes' / 'estrategicas' / slug / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page(slug,*rest), encoding='utf-8')
    created.append(str(path.relative_to(ROOT)))

manifest = ROOT / 'data' / 'phase2_comparisons_manifest.json'
manifest.write_text(json.dumps({'total_comparisons':len(created),'created':created}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Comparativos criados/atualizados: {len(created)}')
print('Manifesto:', manifest)
