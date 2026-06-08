from pathlib import Path
import json, re
from html import escape
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
BASE='https://comprerapido.github.io'

guides=json.loads((ROOT/'data/phase2_guides_manifest.json').read_text(encoding='utf-8'))['guides']
comparisons=json.loads((ROOT/'data/phase2_comparisons_manifest.json').read_text(encoding='utf-8'))['created']
support=json.loads((ROOT/'data/phase2_support_guides_manifest.json').read_text(encoding='utf-8'))['created']

def page_title_from_path(p):
    slug=Path(p).parts[-2] if p.endswith('/index.html') else Path(p).stem
    return slug.replace('-',' ').title().replace('Vs','vs').replace('Tv','TV').replace('Kg','kg')

def style_head(title,desc,canonical):
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | Compre Rápido</title><meta name="description" content="{escape(desc)}"><link rel="canonical" href="{canonical}"><style>body{{margin:0;background:linear-gradient(180deg,#f8fafc,#eef2ff);font-family:Inter,Arial,sans-serif;color:#172033;line-height:1.65}}.wrap{{width:min(1120px,92vw);margin:auto}}header,footer{{background:#101827;color:#fff;padding:20px 0}}header a,footer a{{color:#fff;margin-right:14px;text-decoration:none;font-weight:700}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card{{background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:22px;margin:18px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)}}h1{{font-size:clamp(2rem,4vw,3.2rem);line-height:1.15}}h2{{border-left:5px solid #f97316;padding-left:14px}}.tag{{display:inline-block;background:#eef3ff;padding:4px 10px;border-radius:999px;font-size:.9rem}}</style></head><body><header><div class="wrap"><strong>Compre Rápido</strong> <nav style="display:inline"><a href="/">Início</a><a href="/categorias/">Categorias</a><a href="/melhores-2026/">Rankings</a><a href="/guias/">Guias</a><a href="/comparacoes/">Comparações</a></nav></div></header><main class="wrap">'''

def footer():
    return '</main><footer><div class="wrap"><p><strong>Compre Rápido</strong> — inteligência editorial de compras.</p></div></footer></body></html>'

# Rebuild guias index with guides + support guides + category/ranking mesh
guide_cards=''.join(f"<article class='card'><span class='tag'>{escape(g['category'])}</span><h3><a href='/{g['path'].replace('index.html','')}'>{escape(g['title'])}</a></h3><p>Guia completo com metodologia, tabela comparativa, prós e contras, FAQ e conclusão editorial.</p><p><a href='{g['category_url']}'>Categoria</a> · <a href='{g['ranking_url']}'>Ranking</a> · <a href='{g['comparison_url']}'>Comparativo</a></p></article>" for g in guides)
support_cards=''.join(f"<article class='card'><h3><a href='/{p.replace('index.html','')}'>{escape(page_title_from_path(p))}</a></h3><p>Guia de apoio evergreen para dúvidas de pré-compra, erros comuns e critérios de decisão.</p></article>" for p in support)
html=style_head('Guias de compra completos','Hub editorial com guias principais, guias de apoio, rankings e comparativos do Compre Rápido.',BASE+'/guias/')+f"""
<h1>Guias de compra completos</h1><p>Este hub reúne os guias editoriais principais, guias de apoio e atalhos para comparativos, rankings e categorias. A estrutura foi reorganizada para reduzir profundidade de clique e distribuir autoridade interna entre conteúdos transacionais e informacionais.</p><h2>20 guias principais</h2><div class='grid'>{guide_cards}</div><h2>Guias de apoio</h2><div class='grid'>{support_cards}</div><section class='card'><h2>Como navegar</h2><p>Comece pelo guia principal, avance para um comparativo A vs B, valide alternativas no ranking e finalize pela categoria com ofertas atualizadas.</p><p><a href='/comparacoes/'>Ver comparativos</a> · <a href='/melhores-2026/'>Ver rankings 2026</a> · <a href='/categorias/'>Ver categorias</a></p></section>"""+footer()
(ROOT/'guias/index.html').write_text(html,encoding='utf-8')

# Rebuild comparacoes index with strategic comparisons featured + legacy section
comp_cards=''.join(f"<article class='card'><h3><a href='/{p.replace('index.html','')}'>{escape(page_title_from_path(p))}</a></h3><p>Comparativo editorial A vs B com tabela, prós e contras, FAQ e veredicto de compra.</p></article>" for p in comparisons)
legacy_note="<section class='card'><h2>Comparações automáticas por produto</h2><p>Além dos comparativos estratégicos, o site mantém páginas automáticas por categoria com produtos específicos. Use os comparativos editoriais para decisões amplas e as páginas automáticas para confronto direto entre ofertas do momento.</p></section>"
html=style_head('Comparações A vs B','Hub de comparativos editoriais entre produtos, marcas e modelos para orientar decisões de compra.',BASE+'/comparacoes/')+f"<h1>Comparações A vs B</h1><p>Os comparativos estratégicos conectam guias informacionais, rankings e categorias comerciais. Cada página responde uma dúvida objetiva de compra e direciona o usuário para a próxima etapa da jornada.</p><div class='grid'>{comp_cards}</div>{legacy_note}"+footer()
(ROOT/'comparacoes/index.html').write_text(html,encoding='utf-8')

# Enhance melhores index with link mesh to guides and comparisons
rank_index=ROOT/'melhores-2026/index.html'
if rank_index.exists():
    h=rank_index.read_text(encoding='utf-8',errors='ignore')
    block="""
<!-- CR_PHASE2_RANKING_LINK_MESH_START -->
<section class="card" style="background:#fff;border:1px solid #dfe4ee;border-radius:20px;padding:24px;margin:28px 0;box-shadow:0 12px 28px rgba(15,23,42,.07)"><h2>Guias e comparativos para decidir melhor</h2><p>Use os rankings como ponto de decisão e complemente a análise com os guias e comparativos editoriais abaixo.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">
""" + ''.join(f"<p><a href='/{g['path'].replace('index.html','')}'>{escape(g['title'])}</a><br><a href='{g['comparison_url']}'>Comparativo relacionado</a></p>" for g in guides[:12]) + "</div></section>\n<!-- CR_PHASE2_RANKING_LINK_MESH_END -->\n"
    h=re.sub(r"\n?<!-- CR_PHASE2_RANKING_LINK_MESH_START -->.*?<!-- CR_PHASE2_RANKING_LINK_MESH_END -->\n?","\n",h,flags=re.S)
    h=h.replace('</main>',block+'</main>',1) if '</main>' in h else h+block
    rank_index.write_text(h,encoding='utf-8')

# Update sitemaps with new URLs
new_urls=[]
for p in [*comparisons,*support,*[g['path'] for g in guides]]:
    url=BASE+'/'+p.replace('index.html','')
    new_urls.append(url)

def update_sitemap(path):
    p=ROOT/path
    txt=p.read_text(encoding='utf-8',errors='ignore') if p.exists() else '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
    existing=set(re.findall(r'<loc>(.*?)</loc>',txt))
    entries=''.join(f'<url><loc>{u}</loc><lastmod>{date.today().isoformat()}</lastmod><changefreq>weekly</changefreq><priority>0.72</priority></url>\n' for u in new_urls if u not in existing)
    if entries:
        txt=txt.replace('</urlset>',entries+'</urlset>') if '</urlset>' in txt else txt+entries
    p.write_text(txt,encoding='utf-8')
update_sitemap('sitemap.xml')
update_sitemap('sitemap-guias.xml')

manifest=ROOT/'data/phase2_internal_link_mesh_manifest.json'
manifest.write_text(json.dumps({'updated':['guias/index.html','comparacoes/index.html','melhores-2026/index.html','sitemap.xml','sitemap-guias.xml'],'linked_guides':len(guides),'linked_comparisons':len(comparisons),'linked_support_guides':len(support)},ensure_ascii=False,indent=2),encoding='utf-8')
print('Malha interna atualizada: guias, comparações, rankings e sitemaps')
