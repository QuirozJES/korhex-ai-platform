# test_agent.py (borrar despues de probar)
from agent import generate_analysis

fake_products = [
    {'name': 'Product A', 'category': 'Servers', 'description': 'Enterprise servers',
     'roi_pitch': 'Reduce TCO 30%', 'evidence_url': 'https://example.com'},
]
fake_web_data = {
    'company_url': 'https://toyota.com', 'industry': 'Manufacturing',
    'strategy_background': [{'snippet': 'Toyota expanding EV production globally'}],
    'tech_environment': [{'snippet': 'Toyota using legacy on-premise systems'}],
    'pain_points': [{'snippet': 'Toyota struggling with supply chain visibility'}],
    'decision_makers': [{'snippet': 'CTO James Smith leads digital transformation'}],
    'financial_signals': [{'snippet': 'Toyota reported revenue of 274 billion USD'}],
    'competitive_context': [{'snippet': 'Toyota competes with Tesla and GM in EV market'}],
}
result = generate_analysis('Toyota', fake_web_data, fake_products, 4)
print('Word count:', result['word_count'])
print('Speech preview:', result['sales_speech'][:200])
print('AGENT OK' if result['word_count'] >= 120 else 'WARNING: speech too short')
