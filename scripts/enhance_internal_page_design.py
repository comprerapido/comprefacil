#!/usr/bin/env python3
"""Aplica camada visual moderna a páginas HTML internas geradas estaticamente."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = "<!-- CR_INTERNAL_UX_V2 -->"
STYLE = f"""{MARK}
<style>
  body {{ background: linear-gradient(180deg,#f8fafc 0%,#eef2ff 100%); }}
  header {{ box-shadow:0 10px 30px rgba(15,23,42,.18); border-bottom:3px solid #f97316; }}
  .card {{ border-radius:22px !important; border:1px solid rgba(148,163,184,.32) !important; box-shadow:0 18px 45px rgba(15,23,42,.08) !important; }}
  .hero {{ gap:32px !important; }}
  .hero img, .product-img {{ box-shadow:0 16px 40px rgba(15,23,42,.08); }}
  .price {{ color:#16a34a !important; letter-spacing:-.03em; }}
  .badge {{ background:linear-gradient(135deg,#dcfce7,#bbf7d0) !important; color:#166534 !important; }}
  .cta {{ background:linear-gradient(135deg,#2563eb,#1d4ed8) !important; box-shadow:0 14px 30px rgba(37,99,235,.22); text-decoration:none !important; }}
  .cta:hover {{ filter:brightness(.96); transform:translateY(-1px); }}
  .crumbs {{ background:#fff; border:1px solid #e2e8f0; border-radius:999px; padding:10px 14px; display:inline-block; }}
  table {{ box-shadow:0 10px 24px rgba(15,23,42,.06); }}
  h1 {{ letter-spacing:-.04em; }}
  h2 {{ color:#0f172a; border-left:5px solid #f97316; padding-left:14px; }}
  main ul li {{ margin-bottom:8px; }}
  @media(max-width:760px) {{ .wrap {{ width:min(100% - 24px,1120px); }} .crumbs {{ border-radius:16px; }} .cta {{ width:100%; text-align:center; }} }}
</style>"""


def enhance(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    changed = False
    if MARK not in html and "</head>" in html:
        html = html.replace("</head>", STYLE + "\n</head>", 1)
        changed = True
    if '<a href="/noticias/">Blog</a>' not in html:
        html2 = html.replace('<a href="/guias/">Guias</a><a href="/transparencia/">', '<a href="/guias/">Guias</a><a href="/noticias/">Blog</a><a href="/transparencia/">')
        changed = changed or html2 != html
        html = html2
    if changed:
        path.write_text(html, encoding="utf-8")
    return changed


def main() -> None:
    paths = []
    for dirname in ["produtos", "noticias", "guias", "categorias"]:
        base = ROOT / dirname
        if base.exists():
            paths.extend(base.rglob("*.html"))
    updated = sum(1 for p in paths if enhance(p))
    print({"internal_pages_scanned": len(paths), "internal_pages_updated": updated})


if __name__ == "__main__":
    main()
