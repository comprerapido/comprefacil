from pathlib import Path
import re, json
ROOT=Path(__file__).resolve().parents[1]
areas=['guias','comparacoes','categorias','melhores-2026']
missing=[]
checked=0
for area in areas:
    for f in (ROOT/area).rglob('*.html'):
        txt=f.read_text(encoding='utf-8',errors='ignore')
        for href in re.findall(r'href=["\']([^"\']+)["\']',txt):
            if not href.startswith('/') or href.startswith('//'):
                continue
            if href.startswith('/assets/') or href.startswith('/produtos/') or href in ['/', '/ofertas-hoje/', '/noticias/', '/transparencia/', '/sobre/', '/contato/', '/politica-afiliados/', '/privacidade/']:
                continue
            checked+=1
            local=ROOT/href.strip('/');
            ok=False
            if href.endswith('/'):
                ok=(local/'index.html').exists()
            elif href.endswith('.html'):
                ok=local.exists()
            else:
                ok=local.exists() or (local/'index.html').exists()
            if not ok:
                missing.append({'source':str(f.relative_to(ROOT)),'href':href})
out={'checked_internal_links':checked,'missing_count':len(missing),'missing':missing[:100]}
(ROOT/'data/phase2_link_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
if missing:
    raise SystemExit(1)
