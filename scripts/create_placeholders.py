import os

placeholders = [
    "melhores-2026", "premio-radar-2026", "quedas-hoje", "mais-clicados", "explodindo",
    "comparativos", "comparar", "marcas", "radar-de-mercado", "o-que-esta-em-alta", "metodologia",
    "guias", "glossario", "aprender", "vale-a-pena-esperar", "calendario-de-precos",
    "alertas", "cupons", "black-friday", "ferramentas/economia", "estatisticas", "meus-favoritos"
]

template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Achado Certo</title>
    <link rel="stylesheet" href="{base_path}assets/css/style.css">
    <style>
        .placeholder-content {{ text-align: center; padding: 100px 20px; }}
        .placeholder-content h1 {{ color: var(--primary); margin-bottom: 20px; }}
        .placeholder-content p {{ color: var(--text-light); font-size: 18px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
            <a href="{base_path}index.html" class="logo" style="text-decoration: none; font-size: 24px; font-weight: 800; color: var(--primary);">💰 Achado Certo</a>
            <a href="{base_path}index.html" class="btn btn-primary">Voltar para Home</a>
        </div>
    </header>
    <main class="container placeholder-content">
        <h1>🚧 {title} em Construção</h1>
        <p>Estamos preparando o melhor conteúdo de {title} para você. Volte em breve!</p>
        <div style="margin-top: 40px;">
            <a href="{base_path}index.html" class="btn btn-primary">Ver Ofertas de Hoje</a>
        </div>
    </main>
    <footer class="footer" style="margin-top: 50px;">
        <div class="container"><p>© 2026 Achado Certo. As melhores ofertas do Mercado Livre.</p></div>
    </footer>
</body>
</html>"""

for path in placeholders:
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, "index.html")
    
    # Calcular base_path relativo
    depth = path.count('/') + 1
    base_path = "../" * depth
    
    title = path.replace("-", " ").replace("/", " - ").title()
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(template.format(title=title, base_path=base_path))
    print(f"✓ Criado: {file_path}")

