// ============================================================
//  COMPRE RÁPIDO — app.js v1.0
//  Motor de ofertas em tempo real
// ============================================================

const DATA_URL = '/data/database/all_products.json';
let allProducts = [];

// ========== UTILITÁRIOS ==========
function formatPrice(value) {
    return parseFloat(value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function getRandomProducts(products, count) {
    return [...products].sort(() => Math.random() - 0.5).slice(0, count);
}

// ========== SKELETON LOADING ==========
function createSkeletonCard() {
    return `
        <div class="product-card skeleton-card">
            <div class="skeleton skeleton-image"></div>
            <div class="skeleton skeleton-text" style="height: 18px; margin-bottom: 10px;"></div>
            <div class="skeleton skeleton-text" style="height: 14px; width: 80%; margin-bottom: 10px;"></div>
            <div class="skeleton skeleton-text short" style="height: 22px; margin-bottom: 10px;"></div>
            <div class="skeleton skeleton-text short" style="height: 38px;"></div>
        </div>
    `;
}
function showSkeletonLoading(gridId, count = 12) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = Array(count).fill(0).map(() => createSkeletonCard()).join('');
}

// ========== LÓGICA DE SELOS ==========
function getBadges(discount) {
    const badges = { left: '', right: '' };
    if (discount >= 60) {
        badges.left = `<span class="badge-best-price">⭐ Melhor Preço</span>`;
    } else if (discount > 5) {
        badges.left = `<span class="badge-discount">${discount}% OFF</span>`;
    }
    if (discount > 50) {
        badges.right = `<span class="badge-hot">🔥 HOT</span>`;
    } else if (discount >= 30) {
        badges.right = `<span class="badge-flash">⚡ Relâmpago</span>`;
    }
    return badges;
}

// ========== RENDERIZAÇÃO DE PRODUTOS ==========
function createProductCard(p) {
    const discount = p.custom_discount_pct || 0;
    const price = parseFloat(p.price);
    const oldPrice = p.original_price ? parseFloat(p.original_price) : (price / (1 - discount / 100));
    const savings = oldPrice - price;
    const badges = getBadges(discount);
    return `
        <div class="product-card">
            ${badges.left}
            ${badges.right}
            <img
                src="${p.image}"
                alt="${p.name}"
                class="product-img"
                loading="lazy"
                onerror="this.src='/assets/img/placeholder.png'"
            >
            <h3 class="product-title">${p.name}</h3>
            <div class="price-box">
                ${oldPrice > price ? `<span class="old-price">De R$ ${formatPrice(oldPrice)}</span>` : ''}
                <div class="current-price">R$ ${formatPrice(price)}</div>
                ${savings > 1 ? `<span class="savings">💰 Economize R$ ${formatPrice(savings)}</span>` : ''}
            </div>
            <a href="${p.custom_affiliate_url}" class="btn-buy" target="_blank" rel="noopener noreferrer sponsored">
                Ver Oferta ⚡
            </a>
        </div>
    `;
}

function renderProducts(products, gridId = 'featuredGrid', limit = 24) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    if (!products || products.length === 0) {
        grid.innerHTML = '<p style="text-align:center;padding:40px;grid-column:1/-1;color:var(--text-muted);">Nenhuma oferta encontrada no momento.</p>';
        return;
    }
    const sorted = [...products].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));
    const diversified = [];
    const seenCats = {};
    for (const p of sorted) {
        const cat = p.custom_category_slug || 'outros';
        seenCats[cat] = (seenCats[cat] || 0) + 1;
        if (seenCats[cat] <= 4) diversified.push(p);
        if (diversified.length >= limit) break;
    }
    grid.innerHTML = diversified.map(p => createProductCard(p)).join('');
    const cards = grid.querySelectorAll('.product-card');
    cards.forEach((card, index) => {
        card.style.animation = `fadeIn 0.45s ease-out ${index * 0.04}s both`;
    });
}

// ========== ESTATÍSTICAS ==========
function updateStats(products) {
    const totalEl = document.getElementById('statTotal');
    const discountEl = document.getElementById('statDiscount');
    if (totalEl) totalEl.textContent = products.length.toLocaleString('pt-BR') + '+';
    if (discountEl) {
        const maxDiscount = Math.max(...products.map(p => p.custom_discount_pct || 0));
        discountEl.textContent = maxDiscount + '%';
    }
}

// ========== BUSCA ==========
function setupSearch() {
    const searchInput = document.getElementById('mainSearch');
    if (!searchInput) return;
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.toLowerCase().trim();
        if (query.length === 0) {
            renderProducts(allProducts, 'featuredGrid', 24);
            return;
        }
        searchTimeout = setTimeout(() => {
            const filtered = allProducts.filter(p =>
                (p.name || '').toLowerCase().includes(query) ||
                (p.custom_category_slug || '').toLowerCase().includes(query)
            );
            renderProducts(filtered, 'featuredGrid', 48);
        }, 300);
    });
}

// ========== MENU MOBILE ==========
function setupMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav-links');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', () => {
        nav.classList.toggle('open');
        toggle.textContent = nav.classList.contains('open') ? '✕' : '☰';
    });
    nav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('open');
            toggle.textContent = '☰';
        });
    });
}

// ========== INICIALIZAÇÃO ==========
async function init() {
    try {
        showSkeletonLoading('featuredGrid', 12);
        showSkeletonLoading('offersGrid', 24);
        showSkeletonLoading('comparativesGrid', 12);
        showSkeletonLoading('guidesGrid', 12);

        const response = await fetch(DATA_URL + '?t=' + Date.now());
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        allProducts = Array.isArray(data) ? data : [];

        updateStats(allProducts);

        if (document.getElementById('featuredGrid')) {
            renderProducts(allProducts, 'featuredGrid', 24);
        }
        if (document.getElementById('offersGrid')) {
            renderProducts(allProducts, 'offersGrid', 50);
        }
        if (document.getElementById('comparativesGrid')) {
            renderProducts(getRandomProducts(allProducts, 12), 'comparativesGrid', 12);
        }
        if (document.getElementById('guidesGrid')) {
            renderProducts(getRandomProducts(allProducts, 12), 'guidesGrid', 12);
        }

        setupSearch();
        setupMobileMenu();
        console.log('✅ Compre Rápido carregado!', allProducts.length, 'ofertas disponíveis.');
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        const grid = document.getElementById('featuredGrid');
        if (grid) {
            grid.innerHTML = '<p style="text-align:center;padding:40px;grid-column:1/-1;color:var(--danger);">Não foi possível carregar as ofertas. Tente novamente em instantes.</p>';
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// ========== LAZY LOADING ==========
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    });
    document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// ========== SMOOTH SCROLL ==========
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// ========== ANALYTICS ==========
function trackEvent(category, action, label) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, { event_category: category, event_label: label });
    }
}
document.addEventListener('click', (e) => {
    const buyBtn = e.target.closest('.btn-buy');
    if (buyBtn) {
        const productTitle = buyBtn.closest('.product-card')?.querySelector('.product-title')?.textContent || 'Desconhecido';
        trackEvent('engajamento', 'clique_oferta', productTitle);
    }
});
