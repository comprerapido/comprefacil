import os
import json
import re
from datetime import datetime
from pathlib import Path

def generate_sitemap():
    ROOT = Path(__file__).resolve().parents[1]
    BASE_URL = "https://comprerapido.github.io"
    
    urls = [
        {"loc": f"{BASE_URL}/", "lastmod": datetime.now().strftime("%Y-%m-%d"), "priority": "1.0"},
        {"loc": f"{BASE_URL}/noticias/", "lastmod": datetime.now().strftime("%Y-%m-%d"), "priority": "0.8"},
    ]
    
    # Categorias
    cat_dir = ROOT / "categorias"
    if cat_dir.exists():
        for cat in cat_dir.iterdir():
            if cat.is_dir() and (cat / "index.html").exists():
                urls.append({
                    "loc": f"{BASE_URL}/categorias/{cat.name}/",
                    "lastmod": datetime.now().strftime("%Y-%m-%d"),
                    "priority": "0.7"
                })
                
    # Posts do Blog (com imagens)
    blog_dir = ROOT / "noticias/posts"
    if blog_dir.exists():
        for post_file in blog_dir.glob("*.html"):
            # Tentar extrair a imagem do post para incluir no sitemap
            image_url = None
            try:
                with open(post_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = re.search(r'<img src="(.*?)"', content)
                    if match:
                        image_url = match.group(1)
            except Exception as e:
                print(f"Erro ao ler post {post_file} para imagem: {e}")

            post_url = f"{BASE_URL}/noticias/posts/{post_file.name}"
            url_entry = {
                "loc": post_url,
                "lastmod": datetime.now().strftime("%Y-%m-%d"),
                "priority": "0.6"
            }
            if image_url:
                url_entry["image"] = image_url
            urls.append(url_entry)
            
    # XML Sitemap
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
    
    for url in urls:
        xml.append("  <url>")
        loc = url["loc"]
        lastmod = url["lastmod"]
        priority = url["priority"]
        xml.append(f"    <loc>{loc}</loc>")
        xml.append(f"    <lastmod>{lastmod}</lastmod>")
        xml.append(f"    <priority>{priority}</priority>")
        if "image" in url:
            xml.append("    <image:image>")
            image_loc = url["image"]
            xml.append(f"      <image:loc>{image_loc}</image:loc>")
            xml.append("    </image:image>")
        xml.append("  </url>")
        
    xml.append("</urlset>")
    
    sitemap_path = ROOT / "sitemap.xml"
    sitemap_path.write_text("\n".join(xml), encoding="utf-8")
    print(f"✅ Sitemap gerado com {len(urls)} URLs em {sitemap_path}")

if __name__ == "__main__":
    generate_sitemap()
