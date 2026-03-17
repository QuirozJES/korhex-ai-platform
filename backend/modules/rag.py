import json, os

def load_portfolio():
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, 'data', 'portfolio.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)['products']

def get_relevant_products(industry: str, web_data: dict, top_k: int = 3) -> list:
    products = load_portfolio()
    if not products:
        return []

    context = f"{industry} {web_data.get('summary', '')} {web_data.get('tech_keywords', '')}".lower()

    scored = []
    for product in products:
        score = 0
        for kw in product.get('keywords', []):
            if kw.lower() in context:
                score += 2
        for uc in product.get('use_cases', []):
            if any(w in context for w in uc.split()):
                score += 1
        scored.append((score, product))   

    scored.sort(key=lambda x: x[0], reverse=True)
    result = [p for _, p in scored[:top_k]]
    return result if result else products[:top_k]