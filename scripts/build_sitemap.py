#!/usr/bin/env python3
"""Gerador defensivo de sitemaps do Compra Rápido/Radar de Preços.

Este script usa apenas arquivos HTML públicos existentes no repositório, evitando
que o `sitemap.xml` volte a apontar para URLs 404. Ele também atualiza o
`robots.txt` com todos os sitemaps segmentados.
"""
from __future__ import annotations

from finalize_blog_and_sitemaps import generate_sitemaps, update_robots


def generate_sitemap() -> dict[str, int]:
    counts = generate_sitemaps()
    update_robots()
    print("Sitemap gerado somente com URLs públicas existentes:")
    for name, total in counts.items():
        print(f"- {name}: {total}")
    return counts


if __name__ == "__main__":
    generate_sitemap()
