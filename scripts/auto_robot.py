"""
auto_robot.py — Robô de automação principal do Compre Rápido
Executa o ciclo completo: coleta → score → publicação → sitemap
"""
import json
import os
import sys
import logging
from datetime import datetime

# Configuração de log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("auto_robot")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_DIR = os.path.join(DATA_DIR, "products")
SCORED_FILE = os.path.join(DATA_DIR, "scored_products.json")
ALL_PRODUCTS_FILE = os.path.join(DATA_DIR, "all_products.json")

os.makedirs(PRODUCTS_DIR, exist_ok=True)

# ─── PASSO 1: Coleta via API do Mercado Livre ────────────────────────────────

def fetch_from_mercadolivre():
    import requests

    categories = [
        {"id": "celular",    "q": "smartphone"},
        {"id": "games",      "q": "console videogame"},
        {"id": "tv",         "q": "smart tv 4k"},
        {"id": "moda",       "q": "tenis masculino"},
        {"id": "informatica","q": "notebook"},
        {"id": "eletrodomesticos", "q": "air fryer"},
    ]

    all_products = []
    seen_ids = set()

    for cat in categories:
        log.info(f"🔍 Buscando categoria: {cat['id']} (query: {cat['q']})")
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={cat['q']}&sort=relevance&limit=20"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            log.info(f"   ↳ API retornou {len(results)} resultados para '{cat['q']}'")

            count = 0
            for item in results:
                if count >= 5:
                    break
                item_id = item.get("id")
                if not item_id or item_id in seen_ids:
                    continue

                img = item.get("thumbnail", "")
                if not img or "http" not in img:
                    continue

                price = item.get("price", 0)
                original_price = item.get("original_price") or price
                discount = 0
                if original_price and original_price > price:
                    discount = round((original_price - price) / original_price * 100)

                permalink = item.get("permalink", "")
                if permalink:
                    permalink = permalink.split("?")[0] + "?matt_tool=vendas0nline"

                all_products.append({
                    "id": item_id,
                    "title": item.get("title"),
                    "name": item.get("title"),
                    "price": price,
                    "original_price": original_price,
                    "originalPrice": original_price,
                    "custom_discount_pct": discount,
                    "permalink": permalink,
                    "custom_affiliate_url": permalink,
                    "thumbnail": img.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg"),
                    "image": img.replace("-I.jpg", "-O.jpg").replace("-V.jpg", "-O.jpg"),
                    "custom_category_slug": cat["id"],
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source": "mercadolivre_api"
                })
                seen_ids.add(item_id)
                count += 1

            log.info(f"   ↳ {count} produtos adicionados da categoria '{cat['id']}'")

        except Exception as e:
            log.error(f"   ✗ Erro ao buscar '{cat['id']}': {e}")

    log.info(f"\n📦 Total coletado via API: {len(all_products)} produtos")
    return all_products


# ─── PASSO 2: Merge com base existente ──────────────────────────────────────

def merge_with_existing(new_products):
    existing = []
    if os.path.exists(ALL_PRODUCTS_FILE):
        try:
            with open(ALL_PRODUCTS_FILE, encoding="utf-8") as f:
                existing = json.load(f)
            log.info(f"📂 Base existente: {len(existing)} produtos em all_products.json")
        except Exception as e:
            log.warning(f"Não foi possível ler all_products.json: {e}")

    existing_ids = {p.get("id") for p in existing}
    new_count = 0
    for p in new_products:
        if p.get("id") not in existing_ids:
            existing.append(p)
            existing_ids.add(p.get("id"))
            new_count += 1

    log.info(f"➕ Produtos novos adicionados: {new_count}")
    log.info(f"📊 Total após merge: {len(existing)} produtos")
    return existing, new_count


# ─── PASSO 3: Score e seleção dos melhores ──────────────────────────────────

def score_and_select(products, top_n=80):
    def score(p):
        discount = p.get("custom_discount_pct", 0) or 0
        price = p.get("price", 9999) or 9999
        return discount * 2 - (price / 1000)

    sorted_products = sorted(products, key=score, reverse=True)
    return sorted_products[:top_n]


# ─── PASSO 4: Persistência ───────────────────────────────────────────────────

def save_data(all_products, scored_products, new_offers):
    with open(ALL_PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    log.info(f"💾 all_products.json salvo com {len(all_products)} produtos")

    with open(SCORED_FILE, "w", encoding="utf-8") as f:
        json.dump(scored_products, f, indent=2, ensure_ascii=False)
    log.info(f"💾 scored_products.json salvo com {len(scored_products)} produtos")

    offers_file = os.path.join(PRODUCTS_DIR, "offers.json")
    with open(offers_file, "w", encoding="utf-8") as f:
        json.dump(new_offers, f, indent=2, ensure_ascii=False)
    log.info(f"💾 offers.json salvo com {len(new_offers)} produtos")

    new_offers_file = os.path.join(DATA_DIR, "new_offers.json")
    with open(new_offers_file, "w", encoding="utf-8") as f:
        json.dump(scored_products, f, indent=2, ensure_ascii=False)
    log.info(f"💾 new_offers.json atualizado")


# ─── PASSO 5: Atualizar homepage ─────────────────────────────────────────────

def update_homepage(scored_products):
    index_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(index_path):
        log.warning("index.html não encontrado, pulando atualização da homepage")
        return

    try:
        with open(index_path, encoding="utf-8") as f:
            content = f.read()

        timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
        marker = "<!-- LAST_UPDATE -->"
        new_marker = f"<!-- LAST_UPDATE -->{timestamp}"

        if marker in content:
            content = content.replace(marker, new_marker, 1)
        else:
            content = content.replace("</body>", f"\n<!-- LAST_UPDATE -->{timestamp}\n</body>", 1)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

        log.info(f"🏠 Homepage atualizada com timestamp: {timestamp}")
    except Exception as e:
        log.error(f"Erro ao atualizar homepage: {e}")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 60)
    log.info("🤖 ROBÔ COMPRE RÁPIDO — INICIANDO CICLO DE AUTOMAÇÃO")
    log.info(f"⏰ Data/Hora: {datetime.utcnow().isoformat()}Z")
    log.info("=" * 60)

    # 1. Coleta
    new_products = fetch_from_mercadolivre()

    if not new_products:
        log.warning("⚠️  Nenhum produto coletado via API. Usando base existente.")
        if os.path.exists(SCORED_FILE):
            log.info("Base existente mantida sem alterações.")
        return

    # 2. Merge
    all_products, new_count = merge_with_existing(new_products)

    # 3. Score
    scored = score_and_select(all_products)
    log.info(f"🏆 Top {len(scored)} produtos selecionados por score")

    # Exibir exemplo de produto capturado
    if new_products:
        ex = new_products[0]
        log.info("\n📌 EXEMPLO DE PRODUTO CAPTURADO NESTA EXECUÇÃO:")
        log.info(f"   Título:    {ex.get('title')}")
        log.info(f"   Preço:     R$ {ex.get('price')}")
        log.info(f"   Desconto:  {ex.get('custom_discount_pct')}%")
        log.info(f"   Link:      {ex.get('permalink')}")
        log.info(f"   Categoria: {ex.get('custom_category_slug')}")
        log.info(f"   Coletado:  {ex.get('fetched_at')}")

    # 4. Salvar
    save_data(all_products, scored, new_products)

    # 5. Homepage
    update_homepage(scored)

    log.info("\n" + "=" * 60)
    log.info(f"✅ CICLO CONCLUÍDO: {new_count} produtos novos | {len(scored)} no ranking")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
