import os, json

def load_portfolio():
    # CORRECCIÓN DE RUTA: Ahora busca en 'modules/data/portfolio.json'
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, 'data', 'portfolio.json')
    
    if not os.path.exists(path):
        return {"products": []}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_relevant_products(industry, web_data):
    portfolio = load_portfolio()
    # Filtramos productos que coincidan con la industria
    relevant = [p for p in portfolio.get('products', []) if p.get('target_industry') == industry]
    
    # Si no hay match exacto, devolvemos los generales
    if not relevant:
        relevant = [p for p in portfolio.get('products', []) if p.get('target_industry') == 'General']
        
    return relevant[:3] # Devolvemos el top 3 de soluciones