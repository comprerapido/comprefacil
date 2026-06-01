#!/usr/bin/env python3
"""Auditoria local do site Compra Rápido/Radar de Preços.

Verifica:
- arquivos HTML existentes;
- URLs listadas em sitemaps que não possuem arquivo local correspondente;
- links internos locais quebrados;
- imagens locais quebradas;
- posts de notícias sem imagem;
- referências de notícias no índice que apontam para posts inexistentes.
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://comprerapido.github.io"

class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.images: list[str] = []
        self.titles: list[str] = []
        self.meta_descriptions: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "a" and attrs_dict.get("href"):
            self.links.append(attrs_dict["href"])
        if tag.lower() == "img" and attrs_dict.get("src"):
            self.images.append(attrs_dict["src"])
        if tag.lower() == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.meta_descriptions.append(attrs_dict.get("content", ""))

    def handle_data(self, data: str) -> None:
        pass


def html_files() -> list[Path]:
    ignored_dirs = {".git", "__pycache__", "node_modules", "templates", "reports", "scripts"}
    return sorted(p for p in ROOT.rglob("*.html") if not any(part in ignored_dirs for part in p.parts))


def url_to_local(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc and parsed.netloc != "comprerapido.github.io":
        return None
    path = unquote(parsed.path)
    if not path or path == "/":
        return ROOT / "index.html"
    if path.endswith("/"):
        return ROOT / path.strip("/") / "index.html"
    return ROOT / path.strip("/")


def resolve_ref(current_file: Path, ref: str, *, image: bool = False) -> Path | None:
    ref = ref.strip()
    if not ref or ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(ref)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc == "comprerapido.github.io":
            return url_to_local(ref)
        return None
    clean_path = unquote(parsed.path)
    if not clean_path:
        return None
    if clean_path.startswith("/"):
        candidate = ROOT / clean_path.strip("/")
    else:
        candidate = (current_file.parent / clean_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return candidate
    if not image and ref.endswith("/"):
        candidate = candidate / "index.html"
    if not image and candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


def parse_html(path: Path) -> LinkParser:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def sitemap_urls(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [el.text.strip() for el in root.findall(".//sm:loc", ns) if el.text]


def audit() -> dict:
    files = html_files()
    broken_internal_links: list[dict] = []
    broken_local_images: list[dict] = []
    posts_without_image: list[str] = []

    for file_path in files:
        parser = parse_html(file_path)
        for link in parser.links:
            target = resolve_ref(file_path, link, image=False)
            if target is not None and not target.exists():
                broken_internal_links.append({
                    "file": str(file_path.relative_to(ROOT)),
                    "href": link,
                    "resolved": str(target.relative_to(ROOT)) if str(target).startswith(str(ROOT)) else str(target),
                })
        for img in parser.images:
            target = resolve_ref(file_path, img, image=True)
            if target is not None and not target.exists():
                broken_local_images.append({
                    "file": str(file_path.relative_to(ROOT)),
                    "src": img,
                    "resolved": str(target.relative_to(ROOT)) if str(target).startswith(str(ROOT)) else str(target),
                })
        if "noticias/posts" in str(file_path.relative_to(ROOT)).replace(os.sep, "/") and not parser.images:
            posts_without_image.append(str(file_path.relative_to(ROOT)))

    sitemap_missing: dict[str, list[dict]] = {}
    for sitemap in sorted(ROOT.glob("sitemap*.xml")):
        missing = []
        for url in sitemap_urls(sitemap):
            if url.endswith(".xml"):
                target = url_to_local(url)
            else:
                target = url_to_local(url)
            if target is not None and not target.exists():
                missing.append({
                    "url": url,
                    "resolved": str(target.relative_to(ROOT)) if str(target).startswith(str(ROOT)) else str(target),
                })
        sitemap_missing[sitemap.name] = missing

    news_index = ROOT / "noticias" / "index.html"
    news_index_missing_refs: list[dict] = []
    if news_index.exists():
        content = news_index.read_text(encoding="utf-8", errors="ignore")
        for ref in sorted(set(re.findall(r"url:\s*['\"]([^'\"]+)['\"]", content))):
            target = resolve_ref(news_index, ref, image=False)
            if target is not None and not target.exists():
                news_index_missing_refs.append({"url": ref, "resolved": str(target.relative_to(ROOT))})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "html_count": len(files),
        "broken_internal_links": broken_internal_links,
        "broken_local_images": broken_local_images,
        "posts_without_image": posts_without_image,
        "sitemap_missing": sitemap_missing,
        "news_index_missing_refs": news_index_missing_refs,
    }


def main() -> int:
    result = audit()
    out = ROOT / "reports" / "local_site_audit_latest.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "html_count": result["html_count"],
        "broken_internal_links": len(result["broken_internal_links"]),
        "broken_local_images": len(result["broken_local_images"]),
        "posts_without_image": len(result["posts_without_image"]),
        "news_index_missing_refs": len(result["news_index_missing_refs"]),
        "sitemap_missing_counts": {k: len(v) for k, v in result["sitemap_missing"].items()},
        "report": str(out),
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
