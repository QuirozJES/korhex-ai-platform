import os
from tavily import TavilyClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─── VALIDADOR DE DATOS ───────────────────────────────────

def validate_item(item: dict, field_name: str) -> dict:
    """
    Valida un item individual del scraping.
    Retorna el item con un campo 'valid' y 'reason'.
    """
    issues = []

    # Verificar que el snippet no este vacio
    snippet = item.get('snippet', '').strip()
    if not snippet or len(snippet) < 30:
        issues.append("snippet too short or empty")

    # Verificar que el titulo no este vacio
    title = item.get('title', '').strip()
    if not title:
        issues.append("missing title")

    # Verificar que la URL sea real
    url = item.get('url', '')
    if not url or url == '#' or 'error' in url.lower():
        issues.append("invalid or missing URL")

    # Verificar que el snippet sea relevante al campo
    relevance_keywords = {
        'strategy_background': ['strategy', 'business', 'plan', 'growth', 'expand', 'announce', 'launch', 'initiative'],
        'tech_environment':    ['technology', 'cloud', 'server', 'data', 'IT', 'software', 'platform', 'system', 'infrastructure'],
        'pain_points':         ['challenge', 'problem', 'issue', 'struggle', 'legacy', 'risk', 'cost', 'difficult', 'need'],
        'decision_makers':     ['CEO', 'CTO', 'CIO', 'CFO', 'VP', 'director', 'chief', 'president', 'officer', 'executive'],
        'financial_signals':   ['revenue', 'profit', 'billion', 'million', 'earnings', 'financial', 'growth', 'quarter', 'fiscal'],
        'competitive_context': ['competitor', 'market', 'industry', 'versus', 'rival', 'leader', 'position', 'share', 'ranking']
    }

    keywords = relevance_keywords.get(field_name, [])
    snippet_lower = snippet.lower()
    matches = [kw for kw in keywords if kw.lower() in snippet_lower]
    
    if len(matches) == 0:
        issues.append(f"snippet not relevant to {field_name}")

    item['valid'] = len(issues) == 0
    item['validation_issues'] = issues
    item['relevance_matches'] = matches
    return item


def validate_field(items: list, field_name: str, min_valid: int = 1) -> dict:
    """
    Valida todos los items de un campo.
    Retorna estadisticas de validacion.
    """
    validated = [validate_item(item.copy(), field_name) for item in items]
    valid_items = [i for i in validated if i['valid']]
    invalid_items = [i for i in validated if not i['valid']]

    return {
        'items': validated,
        'valid_count': len(valid_items),
        'invalid_count': len(invalid_items),
        'has_minimum': len(valid_items) >= min_valid,
        'status': 'OK' if len(valid_items) >= min_valid else 'INSUFFICIENT'
    }


def cross_validate(web_data: dict, company_name: str) -> dict:
    """
    Validacion cruzada: verifica que los datos sean sobre
    la empresa correcta y no sobre otra con nombre similar.
    """
    company_words = [w.lower() for w in company_name.split() if len(w) > 2]
    validation_report = {}
    total_valid = 0
    total_items = 0

    fields = [
        'strategy_background', 'tech_environment', 'pain_points',
        'decision_makers', 'financial_signals', 'competitive_context'
    ]

    for field in fields:
        items = web_data.get(field, [])
        field_validation = validate_field(items, field)
        
        # Validacion cruzada: el snippet menciona el nombre de la empresa?
        for item in field_validation['items']:
            snippet_lower = item.get('snippet', '').lower()
            title_lower = item.get('title', '').lower()
            combined = snippet_lower + ' ' + title_lower
            
            company_mentions = sum(1 for word in company_words if word in combined)
            item['mentions_company'] = company_mentions > 0
            
            if not item['mentions_company']:
                item['valid'] = False
                item['validation_issues'].append(f"does not mention {company_name}")

        # Recalcular validos despues de validacion cruzada
        valid_after_cross = [i for i in field_validation['items'] if i['valid']]
        field_validation['valid_count'] = len(valid_after_cross)
        field_validation['status'] = 'OK' if len(valid_after_cross) >= 1 else 'INSUFFICIENT'

        validation_report[field] = field_validation
        total_valid += field_validation['valid_count']
        total_items += len(items)

    # Score de calidad general (0-100)
    quality_score = int((total_valid / total_items * 100)) if total_items > 0 else 0

    return {
        'fields': validation_report,
        'total_valid_items': total_valid,
        'total_items': total_items,
        'quality_score': quality_score,
        'quality_label': (
            'HIGH' if quality_score >= 70 else
            'MEDIUM' if quality_score >= 40 else
            'LOW'
        ),
        'fields_with_data': sum(
            1 for f in validation_report.values() if f['status'] == 'OK'
        ),
        'fields_missing': [
            f for f, v in validation_report.items() if v['status'] == 'INSUFFICIENT'
        ]
    }


# ─── SCRAPER PRINCIPAL ────────────────────────────────────

def search_account(company_name: str, company_url: str = '', industry: str = 'Technology') -> dict:

    client = TavilyClient(api_key=os.environ.get('TAVILY_API_KEY'))

    results = {
        'company': company_name,
        'company_url': company_url,
        'industry': industry,
        'search_date': datetime.now().strftime('%Y-%m-%d'),
        'strategy_background': [],
        'tech_environment': [],
        'pain_points': [],
        'decision_makers': [],
        'financial_signals': [],
        'competitive_context': [],
        'summary': '',
        'tech_keywords': '',
        'recent_news': [],
        'sources': [],
        'validation_report': {},
        'data_quality': 'PENDING'
    }

    searches = [
        ('strategy_background', f'{company_name} corporate strategy business expansion 2024 2025', 'advanced'),
        ('tech_environment',    f'{company_name} IT infrastructure technology stack cloud servers', 'advanced'),
        ('pain_points',         f'{company_name} IT challenges technology problems legacy infrastructure', 'advanced'),
        ('decision_makers',     f'{company_name} CTO CIO CEO CFO VP technology executives 2024 2025', 'basic'),
        ('financial_signals',   f'{company_name} revenue earnings financial results investment 2024', 'basic'),
        ('competitive_context', f'{company_name} competitors market position industry ranking', 'basic'),
    ]

    # ── Ejecutar busquedas ──────────────────────────────
    for key, query, depth in searches:
        try:
            response = client.search(
                query=query,
                search_depth=depth,
                max_results=5,
                include_answer=True,
                include_raw_content=False
            )

            items = []
            for r in response.get('results', []):
                url = r.get('url', '')
                domain = url.split('/')[2] if url and '/' in url else url
                items.append({
                    'title': r.get('title', ''),
                    'snippet': r.get('content', '')[:400],
                    'url': url,
                    'source': domain,
                    'score': r.get('score', 0),
                    'valid': None,
                    'validation_issues': [],
                    'mentions_company': None
                })
                if url:
                    results['sources'].append(url)

            items.sort(key=lambda x: x['score'], reverse=True)
            results[key] = items

            if response.get('answer'):
                results['summary'] += f"\n{response['answer']}"

        except Exception as e:
            results[key] = [{
                'title': 'Data unavailable',
                'snippet': f'Search failed: {str(e)}',
                'url': company_url or '#',
                'source': 'error',
                'score': 0,
                'valid': False,
                'validation_issues': ['search_failed'],
                'mentions_company': False
            }]

    # ── Noticias recientes ──────────────────────────────
    try:
        news = client.search(
            query=f'{company_name} news announcement 2024 2025',
            search_depth='basic',
            max_results=3
        )
        for r in news.get('results', []):
            results['recent_news'].append({
                'title': r.get('title', ''),
                'snippet': r.get('content', '')[:300],
                'url': r.get('url', ''),
                'source': r.get('url', '').split('/')[2] if r.get('url') else ''
            })
    except:
        pass

    # ── Validacion cruzada completa ─────────────────────
    validation = cross_validate(results, company_name)
    results['validation_report'] = validation
    results['data_quality'] = validation['quality_label']

    # ── Advertencia si la calidad es baja ───────────────
    if validation['quality_label'] == 'LOW':
        results['data_warning'] = (
            f"Low quality data detected for {company_name}. "
            f"Only {validation['fields_with_data']}/6 fields have verified data. "
            f"Missing: {', '.join(validation['fields_missing'])}. "
            f"Manual research recommended before using this account profile."
        )
    else:
        results['data_warning'] = None

    # ── Keywords tecnologicos ───────────────────────────
    all_tech_text = ' '.join([i['snippet'] for i in results['tech_environment']]).lower()
    tech_kws = [
        'cloud', 'AI', 'servers', 'storage', 'network', 'data center',
        'migration', 'hybrid', 'automation', 'ERP', 'SAP', 'VMware',
        'cybersecurity', 'IoT', 'edge computing', 'HPC', 'GPU',
        'digital transformation', 'modernization', 'infrastructure'
    ]
    results['tech_keywords'] = ' '.join([kw for kw in tech_kws if kw.lower() in all_tech_text])
    results['sources'] = list(dict.fromkeys([s for s in results['sources'] if s]))

    return results


def calculate_net_new_score(years_inactive: int, web_data: dict) -> dict:

    inactivity_score = min(years_inactive * 15, 40)

    # Solo contar items VALIDOS en el score
    validation = web_data.get('validation_report', {})
    
    tech_valid = validation.get('fields', {}).get('tech_environment', {}).get('valid_count', 0)
    tech_score = min(tech_valid * 8, 25)

    pain_valid = validation.get('fields', {}).get('pain_points', {}).get('valid_count', 0)
    pain_score = min(pain_valid * 10, 25)

    news_score = min(len(web_data.get('recent_news', [])) * 3, 10)

    total = inactivity_score + tech_score + pain_score + news_score

    if total >= 70:
        priority = 'HIGH PRIORITY'
        color = 'red'
    elif total >= 40:
        priority = 'MEDIUM PRIORITY'
        color = 'orange'
    else:
        priority = 'MONITORING'
        color = 'green'

    return {
        'total_score': total,
        'priority': priority,
        'color': color,
        'factors': {
            'Inactivity Factor': inactivity_score,
            'Tech Initiatives': tech_score,
            'Pain Points Detected': pain_score,
            'Recent Activity': news_score
        },
        'is_net_new': years_inactive >= 3,
        'data_quality': web_data.get('data_quality', 'UNKNOWN')
    }