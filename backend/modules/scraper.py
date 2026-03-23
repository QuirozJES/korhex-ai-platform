import os
import time
import random
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─── CONFIGURACIÓN DE PROXY CORPORATIVO ──────────────────────
# Configura CORP_PROXY_URL en tu .env, por ejemplo:
#   CORP_PROXY_URL=http://proxy.empresa.com:8080
# Si la variable no existe, se conecta directamente (modo dev).
_PROXY = os.environ.get("CORP_PROXY_URL", None)

# User-Agents para rotación y reducir riesgo de rate-limiting
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def _ddgs_client() -> DDGS:
    """Crea un cliente DDG con proxy corporativo y User-Agent rotativo."""
    return DDGS(
        headers={"User-Agent": random.choice(_USER_AGENTS)},
        proxies=_PROXY,   # None → conexión directa (modo dev sin proxy)
        timeout=20,
    )

def _ddg_search(query: str, max_results: int = 5, company_name: str = '', company_domain: str = '') -> list[dict]:
    """
    Ejecuta una búsqueda en DuckDuckGo y devuelve resultados normalizados.
    Usa filtrado por relevancia + retry con query simplificada si hay pocos resultados.
    """
    # ── Patrones de dominio spam/irrelevante ────────────────────────────
    _JUNK_PATTERNS = {
        'calculator', 'mathway', 'calc-online', 'askmathguru', 'fractioncalc',
        'symbolab', 'wolframalpha', 'mathpapa', 'cymath',
        'translate.google', 'deepl.com/translator', 'reverso.net',
        'pinterest.', 'tiktok.', 'instagram.', 'facebook.', 'youtube.',
        'reddit.', 'twitter.', 'x.com', 'quora.', 'tumblr.',
        'amazon.', 'ebay.', 'aliexpress.', 'mercadolibre.',
        'tripadvisor.', 'yelp.', 'allrecipes.', 'recetas',
        'booking.com', 'expedia.', 'airbnb.',
        'bokep', 'porn', 'xxx', 'xvideo', 'xnxx', 'xhamster',
        'wikihow.', 'answers.com',
        '/car-rental', '/math/', '/recipe',
    }

    company_words = [w.lower() for w in company_name.split() if len(w) > 2] if company_name else []

    def _fetch_and_filter(q: str, n: int) -> list[dict]:
        """Busca y filtra resultados de DDG."""
        client = _ddgs_client()
        try:
            raw = client.text(q, region='wt-wt', max_results=n)
        except Exception:
            return []

        filtered = []
        for r in (raw or []):
            url    = r.get("href", "")
            title  = r.get("title", "")
            body   = r.get("body", "")[:400]
            url_lower = url.lower()
            domain = url.split("/")[2] if url and url.count("/") >= 2 else url

            # FILTRO 1: Descartar spam obvio
            if any(junk in url_lower for junk in _JUNK_PATTERNS):
                continue

            # FILTRO 2: Relevancia — whitelist dominio de la empresa, o debe mencionar el nombre
            if company_domain and company_domain.lower() in url_lower:
                pass  # La URL es del sitio de la empresa → siempre relevante
            elif company_words:
                combined = (title + ' ' + body + ' ' + url).lower()
                if not any(word in combined for word in company_words):
                    continue

            filtered.append({
                "title":            title,
                "snippet":          body,
                "url":              url,
                "source":           domain,
                "score":            1.0,
                "valid":            None,
                "validation_issues": [],
                "mentions_company": True if company_words else None,
            })

        return filtered

    # ── Intento 1: query original con más resultados ───────────────────
    items = _fetch_and_filter(query, max_results * 4)

    # ── Intento 2: si hay pocos resultados, reintentar con query simple ─
    if len(items) < max_results and company_name:
        time.sleep(random.uniform(1.5, 3.0))
        # Extraer las keywords principales de la query original
        extra_words = [w for w in query.split() if w.lower() not in [cn.lower() for cn in company_name.split()]]
        simple_query = f'{company_name} {" ".join(extra_words[:3])}'
        more = _fetch_and_filter(simple_query, max_results * 3)
        # Agregar nuevos resultados que no estén duplicados
        seen_urls = {i['url'] for i in items}
        for m in more:
            if m['url'] not in seen_urls:
                items.append(m)
                seen_urls.add(m['url'])

    # Limitar al max_results
    items = items[:max_results]

    # Pausa para evitar rate-limiting
    time.sleep(random.uniform(2.5, 5.0))
    return items

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

    # Construir un nombre de búsqueda con contexto (ej: "Valero Energy company")
    search_name = f'{company_name} {industry} company'

    # Extraer dominio de company_url para whitelist (ej: "valero.com")
    company_domain = ''
    if company_url:
        try:
            company_domain = company_url.split('/')[2].replace('www.', '')
        except (IndexError, AttributeError):
            pass

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
        ('strategy_background', f'{search_name} corporate strategy business expansion', 'advanced'),
        ('tech_environment',    f'{search_name} IT infrastructure technology cloud servers', 'advanced'),
        ('pain_points',         f'{search_name} IT challenges technology problems legacy', 'advanced'),
        ('decision_makers',     f'{company_name} {industry} CTO CIO CEO technology executives', 'basic'),
        ('financial_signals',   f'{company_name} {industry} revenue earnings financial results', 'basic'),
        ('competitive_context', f'{company_name} {industry} competitors market position', 'basic'),
    ]

    # ── Ejecutar busquedas via DuckDuckGo + proxy corporativo ──
    for key, query, _depth in searches:
        try:
            items = _ddg_search(query, max_results=5, company_name=company_name, company_domain=company_domain)
            for item in items:
                if item['url']:
                    results['sources'].append(item['url'])
            results[key] = items

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
        news_items = _ddg_search(
            f'{company_name} {industry} latest news announcement',
            max_results=5,
            company_name=company_name,
            company_domain=company_domain
        )
        for r in news_items:
            results['recent_news'].append({
                'title':   r['title'],
                'snippet': r['snippet'][:300],
                'url':     r['url'],
                'source':  r['source'],
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

    # ── Limpiar fuentes: solo conservar URLs de items válidos ──
    valid_urls = set()
    for field in ['strategy_background', 'tech_environment', 'pain_points',
                  'decision_makers', 'financial_signals', 'competitive_context']:
        for item in results.get(field, []):
            if item.get('valid') and item.get('url'):
                valid_urls.add(item['url'])
    # Si hay URLs válidas, usarlas; si no, conservar las originales filtradas
    if valid_urls:
        results['sources'] = list(valid_urls)[:15]
    else:
        # Filtrar fuentes que al menos mencionen la empresa
        company_lower = company_name.lower()
        company_words = [w for w in company_lower.split() if len(w) > 2]
        filtered = []
        for s in results['sources']:
            s_lower = s.lower()
            if any(w in s_lower for w in company_words):
                filtered.append(s)
        results['sources'] = list(dict.fromkeys(filtered))[:15] if filtered else []

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