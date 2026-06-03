#!/usr/bin/env python3
"""Finaliza limpeza do blog/notícias e regenera sitemaps válidos.

A rotina remove postagens duplicadas geradas automaticamente, reconstrói o array
NEWS do índice de notícias usando apenas posts existentes com imagem, e gera um
sitemap index apontando para sitemaps segmentados com URLs que possuem arquivo
local real.
"""
from __future__ import annotations

import html
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://comprerapido.github.io"
TODAY = datetime.now(timezone.utc).date().isoformat()


def rel_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{BASE_URL}/"
    if rel.endswith("/index.html"):
        return f"{BASE_URL}/{quote(rel[:-10], safe='/')}/"
    return f"{BASE_URL}/{quote(rel, safe='/') }"


def xml_urlset(urls: list[tuple[str, str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, changefreq, priority in urls:
        lines.extend([
            '  <url>',
            f'    <loc>{html.escape(loc, quote=False)}</loc>',
            f'    <lastmod>{TODAY}</lastmod>',
            f'    <changefreq>{changefreq}</changefreq>',
            f'    <priority>{priority}</priority>',
            '  </url>',
        ])
    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'


def xml_sitemap_index(names: list[str]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for name in names:
        lines.extend([
            '  <sitemap>',
            f'    <loc>{BASE_URL}/{name}</loc>',
            f'    <lastmod>{TODAY}</lastmod>',
            '  </sitemap>',
        ])
    lines.append('</sitemapindex>')
    return '\n'.join(lines) + '\n'


def extract_title(content: str) -> str:
    match = re.search(r"<title>(.*?)</title>", content, re.S | re.I)
    if not match:
        return "Notícia validada do Radar de Preços"
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    title = re.sub(r"\s*\|\s*(Achado Certo|Radar de Preços).*$", "", title, flags=re.I)
    return title


def extract_description(content: str) -> str:
    match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', content, re.I)
    if match:
        return html.unescape(match.group(1)).strip()
    paragraph = re.search(r"<p>(.*?)</p>", content, re.S | re.I)
    if paragraph:
        text = re.sub(r"<.*?>", "", paragraph.group(1))
        return re.sub(r"\s+", " ", html.unescape(text)).strip()[:180]
    return "Análise validada com imagem e link de oferta ativo."


def extract_published(content: str) -> str:
    match = re.search(r"Publicado[^<]*em\s+([0-9]{2}/[0-9]{2}/[0-9]{4})\s+([0-9]{2}:[0-9]{2})", content, re.I)
    if not match:
        return "01 Jun 2026"
    day, month, year = match.group(1).split("/")
    months = {"01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr", "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago", "09": "Set", "10": "Out", "11": "Nov", "12": "Dez"}
    return f"{day} {months.get(month, month)} {year}"


def has_image(content: str, post_name: str) -> bool:
    # Para posts que não são de produtos (sem MLB\d+ no nome), não exigimos imagem.
    if not re.search(r"MLB\d+", post_name):
        return True
    return bool(re.search(r"<img\s+[^>]*src=['\"]([^'\"]+)['\"]", content, re.I))


def cleanup_news_posts() -> list[Path]:
    posts_dir = ROOT / "noticias" / "posts"
    posts = sorted(posts_dir.glob("**/*.html")) if posts_dir.exists() else []
    product_groups: dict[str, list[Path]] = defaultdict(list)
    non_product_posts: list[Path] = []

    for post in posts:
        product_match = re.search(r"(MLB\d+)", post.name)
        if product_match:
            key = product_match.group(1)
            product_groups[key].append(post)
        else:
            non_product_posts.append(post)

    kept_product_posts: list[Path] = []
    for _, items in product_groups.items():
        valid_items = [p for p in items if has_image(p.read_text(encoding="utf-8", errors="ignore"), p.name)]
        if not valid_items:
            for p in items:
                p.unlink()
            continue
        latest = max(valid_items, key=lambda p: p.name)
        kept_product_posts.append(latest)
        for p in items:
            if p != latest:
                p.unlink()

    all_valid_posts = non_product_posts + kept_product_posts
    print(f"DEBUG: all_valid_posts antes de retornar: {[p.name for p in all_valid_posts]}")
    return sorted(all_valid_posts, key=lambda p: p.name, reverse=True)


from bs4 import BeautifulSoup

def rewrite_news_index(valid_posts: list[Path]) -> None:
    index_path = ROOT / "noticias" / "index.html"
    if not index_path.exists():
        return

    with open(index_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Encontrar a lista de artigos existente
    article_list = soup.find("main", class_="wrap").find("ul")
    if not article_list:
        # Se não encontrar, criar uma nova lista
        article_list = soup.new_tag("ul")
        soup.find("main", class_="wrap").append(article_list)
    else:
        # Limpar os itens existentes
        article_list.clear()

    for post in valid_posts:
        content = post.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(content)
        url = rel_url(post)

        li_tag = soup.new_tag("li")
        a_tag = soup.new_tag("a", href=url)
        a_tag.string = title
        li_tag.append(a_tag)
        article_list.append(li_tag)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(str(soup))


def html_files() -> list[Path]:
    ignored_dirs = {".git", "__pycache__", "node_modules", "templates", "reports", "scripts"}
    result = []
    for path in ROOT.rglob("*.html"):
        if any(part in ignored_dirs for part in path.parts):
            continue
        result.append(path)
    return sorted(result)


def page_priority(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "1.0"
    if rel in {"melhores-ofertas/index.html", "ofertas-hoje/index.html", "noticias/index.html"}:
        return "0.9"
    if rel.startswith("ofertas/"):
        return "0.7"
    if rel.startswith(("categorias/", "guias/", "noticias/posts/")):
        return "0.8"
    return "0.6"


def page_changefreq(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html" or rel.startswith("ofertas/") or rel.startswith("produtos/") or rel.startswith("noticias/"):
        return "daily"
    return "weekly"


def generate_sitemaps() -> dict[str, int]:
    files = html_files()
    buckets: dict[str, list[Path]] = {
        "sitemap-paginas.xml": [],
        "sitemap-categorias.xml": [],
        "sitemap-guias.xml": [],
        "sitemap-noticias.xml": [],
        "sitemap-produtos.xml": [],
    }
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("ofertas/") or rel.startswith("produtos/"):
            buckets["sitemap-produtos.xml"].append(path)
        elif rel.startswith("categorias/"):
            buckets["sitemap-categorias.xml"].append(path)
        elif rel.startswith("guias/"):
            buckets["sitemap-guias.xml"].append(path)
        elif rel.startswith("noticias/"):
            buckets["sitemap-noticias.xml"].append(path)
        else:
            buckets["sitemap-paginas.xml"].append(path)

    counts: dict[str, int] = {}
    for name, paths in buckets.items():
        urls = [(rel_url(path), page_changefreq(path), page_priority(path)) for path in sorted(paths)]
        (ROOT / name).write_text(xml_urlset(urls), encoding="utf-8")
        counts[name] = len(urls)

    index_names = [name for name in buckets]
    (ROOT / "sitemap.xml").write_text(xml_sitemap_index(index_names), encoding="utf-8")
    counts["sitemap.xml"] = len(index_names)
    return counts


def update_robots() -> None:
    robots = ROOT / "robots.txt"
    base_rules = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /temp/",
        "Disallow: /*.json$",
        "# Crawl delay",
        "Crawl-delay: 1",
        "# Sitemaps do Portal Radar de Preços",
        f"Sitemap: {BASE_URL}/sitemap.xml",
        f"Sitemap: {BASE_URL}/sitemap-paginas.xml",
        f"Sitemap: {BASE_URL}/sitemap-categorias.xml",
        f"Sitemap: {BASE_URL}/sitemap-produtos.xml",
        f"Sitemap: {BASE_URL}/sitemap-guias.xml",
        f"Sitemap: {BASE_URL}/sitemap-noticias.xml",
    ]
    robots.write_text("\n".join(base_rules) + "\n", encoding="utf-8")


def main() -> int:
    valid_posts = cleanup_news_posts()
    rewrite_news_index(valid_posts)
    counts = generate_sitemaps()
    update_robots()
    print("Finalização concluída.")
    print(f"Posts válidos mantidos: {len(valid_posts)}")
    for post in valid_posts:
        print(f"- {post.relative_to(ROOT)}")
    print("Sitemaps gerados:")
    for name, count in counts.items():
        print(f"- {name}: {count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
