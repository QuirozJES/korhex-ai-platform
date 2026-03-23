import requests
try:
    login_res = requests.post('http://localhost:8003/api/v1/auth/token', data={'username': 'admin', 'password': 'admin123'})
    token = login_res.json()['access_token']
    requests.post('http://localhost:8003/api/v1/analyze', json={'company_name': 'Valero', 'company_url': 'https://valero.com', 'industry': 'Energy', 'years_inactive': 0, 'report_language': 'en'}, headers={'Authorization': f'Bearer {token}'})
except Exception as e:
    pass
