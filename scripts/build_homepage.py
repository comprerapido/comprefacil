import json
import os
import re
import unicodedata
from urllib.parse import urlparse
from logger import logger

BASE_URL = "https://comprerapido.github.io/"
DEFAULT_INPUT = "data/products/offers.json"
DEFAULT_TEMPLATE = "templates/homepage.html"
DEFAULT_OUTPUT = "index.html"
CONFIG_PATH = "data/ROBO4_CONFIG.json"

CATEGORY_ALIASES = {
    "celular": {"celular", "celulares", "smartphones"},
    "games": {"games", "game", "video-games"},
    "tv": {"tv", "tv-e-video", "televisores"},
    "moda": {"moda", "roupas", "vestuario"},
}

def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"\b(kit|unidade|un|novo|original|promocao|oferta)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def normalize_slug(value: str) -> str:
    return normalize_text(value).replace(" ", "-")

def allowed_categories() -> set:
    fallback = {"celular", "celulares", "smartphones", "games", "game", "video-games", "tv", "tv-e-video", "televisores", "moda", "roupas", "vestuario"}
    if not os.path.exists(CONFIG_PATH):
        return fallback
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        allowed = set()
        for category in config.get("categorias", []):
            allowed.update(CATEGORY_ALIASES.get(category.get("id"), {category.get("id")}))
        return {normalize_slug(item) for item in allowed if item} or fallback
    except Exception as exc:
        logger.warning(f"Não foi possível carregar {CONFIG_PATH}: {exc}. Usando categorias padrão.")
        return fallback

def extract_ml_code(url: str) -> str:
    if not url:
        return ""
    parsed_path = urlparse(str(url)).path
    match = re.search(r"/(?:p|up)/(MLB[A-Z0-9]+)", parsed_path, re.I)
    if match:
        return match.group(1).upper()
    generic = re.search(r"\bMLB[A-Z0-9]{6,}\b", str(url), re.I)
    return generic.group(0).upper() if generic else ""

def product_key(product: dict) -> str:
    code = extract_ml_code(product.get("permalink")) or extract_ml_code(product.get("custom_affiliate_url"))
    if code:
        return f"ml:{code}"
    stable_id = product.get("catalog_product_id") or product.get("catalogProductId") or product.get("id")
    if stable_id:
        return f"id:{stable_id}"
    name = " ".join(normalize_text(product.get("name") or product.get("title")).split()[:10])
    image = str(product.get("image") or product.get("thumbnail") or "").split("?")[0]
    price = round(float(product.get("price") or 0) * 100)
    return f"fallback:{name}|{image}|{price}"

def sanitize_products(products: list) -> list:
    allowed = allowed_categories()
    seen = set()
    sanitized = []

    for product in products:
        slug = normalize_slug(product.get("custom_category_slug") or product.get("category") or "")
        if not slug or slug not in allowed:
            continue

        key = product_key(product)
        name_key = " ".join(normalize_text(product.get("name") or product.get("title")).split()[:8])
        image_key = str(product.get("image") or product.get("thumbnail") or "").split("?")[0]
        soft_key = f"{name_key}|{image_key}"

        if key in seen or soft_key in seen:
            continue
        seen.add(key)
        seen.add(soft_key)
        sanitized.append(product)

    return sorted(sanitized, key=lambda item: item.get("custom_discount_pct", 0), reverse=True)

def format_price(value) -> str:
    return f"{float(value or 0):.2f}"

def affiliate_url(product: dict) -> str:
    url = product.get("custom_affiliate_url") or product.get("permalink")
    if url:
        return url
    product_id = product.get('id')
    return f"https://www.mercadolivre.com.br/p/{product_id}?matt_tool=vendas0nline"

def build_homepage(input_path: str, template_path: str, output_path: str) -> None:
    logger.info("Gerando homepage com filtro estrito de categoria e deduplicação...")

    if not os.path.exists(template_path):
        logger.error(f"Template {template_path} não encontrado!")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    products = []
    if os.path.exists(input_path):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as exc:
            logger.error(f"Erro ao carregar {input_path}: {exc}")

    products = sanitize_products(products)
    if not products:
        logger.warning("Nenhum produto válido encontrado após filtro de categoria.")
        return

    hero = products[0]
    hero_name = hero.get("name") or hero.get("title") or "Oferta Mercado Livre"
    hero_cat = normalize_slug(hero.get("custom_category_slug", "oferta")).replace("-", " ").upper()
    hero_discount = hero.get("custom_discount_pct", 0)
    hero_price = hero.get("price", 0)
    hero_old = hero.get("original_price") or hero.get("originalPrice") or hero_price
    hero_img = hero.get("image") or hero.get("thumbnail") or ""

    hero_html = f"""
    <div class="hero-container">
        <div class="hero-card-premium">
            <div class="hero-img-box">
                <div class="hero-ninja-badge">NINJA CHOICE</div>
                <img src="{hero_img}" alt="{hero_name}" loading="lazy" width="360" height="280">
            </div>
            <div class="hero-info-box">
                <div class="hero-cat-label">
                    <span>{hero_cat}</span>
                    <span class="hero-cat-line"></span>
                </div>
                <h2 class="hero-title">{hero_name}</h2>
                <div class="hero-price-container">
                    <div class="hero-price-stack">
                        <span class="hero-old-price">R$ {format_price(hero_old)}</span>
                        <span class="hero-current-price">R$ {format_price(hero_price)}</span>
                    </div>
                    <div class="hero-discount-tag">-{hero_discount}%</div>
                </div>
                <a href="{affiliate_url(hero)}" target="_blank" rel="noopener noreferrer" class="hero-cta-btn">
                    PEGAR OFERTA NO MERCADO LIVRE
                </a>
                <p class="hero-verified">Verificado pelo Robô 3 agora pouco</p>
            </div>
        </div>
    </div>
    """

    products_html = ""
    for product in products[1:25]:
        name = product.get("name") or product.get("title") or "Oferta Mercado Livre"
        cat = normalize_slug(product.get("custom_category_slug", "outros")).replace("-", " ").upper()
        discount = product.get("custom_discount_pct", 0)
        old_price = product.get("original_price") or product.get("originalPrice") or product.get("price")
        prod_image = product.get('image') or product.get('thumbnail')
        prod_price = product.get('price')

        products_html += f"""
        <div class="product-card">
            <span class="badge">↓ {discount}% OFF</span>
            <div class="product-img">
                <img src="{prod_image}" alt="{name}" loading="lazy" width="260" height="200">
            </div>
            <div class="product-info">
                <span class="category-tag">{cat}</span>
                <h3>{name[:60]}{'...' if len(name) > 60 else ''}</h3>
                <div class="price">
                    <span class="old-price">R$ {format_price(old_price)}</span>
                    <span class="current-price">R$ {format_price(prod_price)}</span>
                </div>
                <a href="{affiliate_url(product)}" class="btn" target="_blank" rel="noopener noreferrer">Ver Oferta no ML</a>
            </div>
        </div>
        """

    content = template.replace("{{hero_section}}", hero_html)
    content = content.replace("{{featured_products_grid}}", products_html)
    content = content.replace("{{seo.title}}", "Radar Ninja — As Melhores Ofertas do Mercado Livre Hoje")
    content = content.replace("{{meta.description}}", "Economize com o Radar Ninja.")
    content = content.replace("{{canonical.url}}", BASE_URL)

    explorar_menu_html = ""
    if os.path.exists("templates/explorar_menu.html"):
        with open("templates/explorar_menu.html", "r", encoding="utf-8") as f:
            explorar_menu_html = f.read()
    content = content.replace("{{explorar_menu}}", explorar_menu_html)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Homepage gerada com {len(products)} produtos válidos: {output_path}")


if __name__ == "__main__":
    build_homepage(DEFAULT_INPUT, DEFAULT_TEMPLATE, DEFAULT_OUTPUT)
