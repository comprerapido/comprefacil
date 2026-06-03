#!/usr/bin/env python3
from pathlib import Path
import json, re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent

def load_json(path):
    p = ROOT / path
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        return {'__error__': str(e)}

def as_list(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for key in ['products','items','data','offers','results']:
            if isinstance(obj.get(key), list):
                return obj[key]
    return []

def read_html(path):
    p = ROOT / path
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''

def soup(path):
    return BeautifulSoup(read_html(path), 'html.parser')

def text_has(path, needle):
    return needle.lower() in read_html(path).lower()

sources = {}
for rel in ['data/all_products.json','data/quality_products.json','data/scored_products.json','data/real_promotions.json','data/new_offers.json']:
    obj = load_json(rel)
    lst = as_list(obj)
    sources[rel] = {
        'exists': (ROOT/rel).exists(),
        'count': len(lst),
        'sample_titles': [(x.get('title') or x.get('name') or x.get('nome') or '')[:90] for x in lst[:5] if isinstance(x, dict)]
    }

product_pages = sorted((ROOT/'produto').rglob('*.html')) if (ROOT/'produto').exists() else []
alt_product_pages = sorted((ROOT/'produtos').rglob('*.html')) if (ROOT/'produtos').exists() else []
blog_pages = sorted((ROOT/'blog').rglob('*.html')) if (ROOT/'blog').exists() else []
noticias_pages = sorted((ROOT/'noticias').rglob('*.html')) if (ROOT/'noticias').exists() else []
guias_pages = sorted((ROOT/'guias').rglob('*.html')) if (ROOT/'guias').exists() else []

home = soup('index.html')
home_links = [a.get('href','') for a in home.find_all('a')]
home_product_links = [h for h in home_links if '/produto/' in h or h.startswith('produto/') or '/produtos/' in h or h.startswith('produtos/')]
home_blog_links = [h for h in home_links if '/blog/' in h or h.startswith('blog/') or '/guias/' in h or h.startswith('guias/') or '/noticias/' in h or h.startswith('noticias/')]

sitemap_prod = read_html('sitemap-produtos.xml')
sitemap_main = read_html('sitemap.xml')
sitemap_product_urls = re.findall(r'<loc>(.*?)</loc>', sitemap_prod)
sitemap_all_urls = re.findall(r'<loc>(.*?)</loc>', sitemap_main)

nav_links = []
nav = home.find('nav')
if nav:
    nav_links = [(a.get_text(' ', strip=True), a.get('href','')) for a in nav.find_all('a')]

report = {
    'data_sources': sources,
    'generated_product_pages_produto_dir': len(product_pages),
    'generated_product_pages_produtos_dir': len(alt_product_pages),
    'sample_product_urls': [str(p.relative_to(ROOT)) for p in product_pages[:10]] + [str(p.relative_to(ROOT)) for p in alt_product_pages[:10]],
    'home_product_link_count': len(home_product_links),
    'home_product_links_sample': home_product_links[:20],
    'blog_pages_count_blog_dir': len(blog_pages),
    'blog_pages_count_noticias_dir': len(noticias_pages),
    'blog_pages_count_guias_dir': len(guias_pages),
    'home_blog_link_count': len(home_blog_links),
    'home_blog_links_sample': home_blog_links[:20],
    'nav_links': nav_links,
    'has_blog_in_nav': any('blog' in (t+' '+h).lower() for t,h in nav_links),
    'has_latest_articles_block': 'últimos artigos' in home.get_text(' ', strip=True).lower() or 'ultimos artigos' in home.get_text(' ', strip=True).lower(),
    'has_buying_guides_block': 'guias de compra' in home.get_text(' ', strip=True).lower(),
    'sitemap_product_url_count': len(sitemap_product_urls),
    'sitemap_main_url_count': len(sitemap_all_urls),
    'sitemap_product_sample': sitemap_product_urls[:10],
}

out = ROOT/'audit_publication_flow.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
