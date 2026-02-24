import json, os
def load_portfolio():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'portfolio.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)['products']

def get_relevant_products(industry: str, web_data: dict, top_k: int = 3) -> list:
    products = load_portfolio()
    context = f"{industry} {web_data.get('summary','')}{web_data.get('tech_keywords','')}".lower()
    scored = []
    for product in products:
        score = 0
        for kw in product['keywords']:
            if kw.lower() in context:
                score += 2
        for uc in product['use_cases']:
            if any(w in context for w in uc.split()):
                score += 1
    scored.append((score, product))
    scored.sort(key=lambda x: x[0], reverse=True)
    result = [p for _, p in scored[:top_k]]
    return result if result else products[:top_k]
