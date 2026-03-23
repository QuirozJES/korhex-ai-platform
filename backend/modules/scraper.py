import os
import time
import random
import asyncio
import urllib.parse
from ddgs import DDGS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─── CONFIGURACIÓN DE PROXY CORPORATIVO ──────────────────────
_PROXY = os.environ.get("CORP_PROXY_URL", "").strip() or None

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

_BLACKLIST = [
    "calculator", "translate.google", "facebook.com", "instagram.com",
    "twitter.com", "x.com", "tiktok.com", "youtube.com", "pinterest.com",
    "zhihu.com", "quora.com", "reddit.com", "medium.com", "wikipedia.org",
    "glassdoor.com", "indeed.com", "stackoverflow.com", "stackexchange.com",
    "github.com", "ycombinator.com", "yahoo.com"
]

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

def _ddgs_client() -> DDGS:
    return DDGS(proxy=_PROXY, timeout=20)

def _fetch_and_filter(query: str, max_results: int, company_name: str, company_domain: str) -> list[dict]:
    client = _ddgs_client()
    try:
        raw = client.text(query, region='wt-wt', max_results=max_results)
    except Exception:
        return []

    company_words = [w.lower() for w in company_name.split() if len(w) > 2] if company_name else []
    filtered = []

    for r in (raw or []):
        url    = r.get("href", "")
        title  = r.get("title", "")
        body   = r.get("body", "")[:400]
        url_lower = url.lower()
        domain = url.split("/")[2].lower() if url and "/" in url else url.lower()

        if any(junk in url_lower for junk in _JUNK_PATTERNS) or any(bad in domain for bad in _BLACKLIST):
            continue

        if company_domain and company_domain.lower() in url_lower:
            pass
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
            "validation_issues":[],
            "mentions_company": True if company_words else None,
        })
    return filtered

def _sync_ddg_search(query: str, max_results: int, company_name: str, company_domain: str) -> list[dict]:
    items = _fetch_and_filter(query, max_results, company_name, company_domain)
    
    # Intento de fallback más rápido si es nulo
    if len(items) < max_results and company_name:
        time.sleep(random.uniform(0.5, 1.0))
        extra_words = [w for w in query.split() if w.lower() not in [cn.lower() for cn in company_name.split()]]
        simple_query = f'{company_name} {" ".join(extra_words[:3])}'
        more = _fetch_and_filter(simple_query, max_results, company_name, company_domain)
        seen_urls = {i['url'] for i in items}
        for m in more:
            if m['url'] not in seen_urls:
                items.append(m)
                seen_urls.add(m['url'])
                
    return items[:max_results]

# ─── ASYNC SEARCH ─────────────────────────────────────────────

async def _async_ddg_search(query: str, max_results: int, company_name: str, company_domain: str) -> list[dict]:
    loop = asyncio.get_running_loop()
    def _blocking_search():
        time.sleep(random.uniform(0.1, 1.5)) # Small stagger
        return _sync_ddg_search(query, max_results, company_name, company_domain)
    
    return await loop.run_in_executor(None, _blocking_search)

async def _fetch_with_timeout(query: str, max_results: int, timeout: float, company_name: str, company_domain: str) -> list[dict]:
    try:
        return await asyncio.wait_for(_async_ddg_search(query, max_results, company_name, company_domain), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"[Scraper] TIMEOUT for query: {query}")
        return []
    except Exception as e:
        print(f"[Scraper] ERROR for query: {query} -> {str(e)}")
        import traceback
        traceback.print_exc()
        return []

async def _async_search_account(company_name: str, company_url: str = '', industry: str = 'Technology') -> dict:
    company_domain = ''
    if company_url:
        try:
            parsed = urllib.parse.urlparse(company_url)
            company_domain = parsed.netloc.lower().replace("www.", "")
        except:
            pass

    results = {
        'company':            company_name,
        'company_url':        company_url,
        'industry':           industry,
        'search_date':        datetime.now().strftime('%Y-%m-%d'),
        'strategy_background': [],
        'tech_environment':   [],
        'pain_points':        [],
        'decision_makers':    [],
        'financial_signals':  [],
        'competitive_context': [],
        'summary':            '',
        'tech_keywords':      '',
        'recent_news':        [],
        'sources':            [],
        'validation_report':  {},
        'data_quality':       'PENDING'
    }

    # Mezcla: queries de dev con paralelismo via async 
    queries = [
        ('strategy_background', f'"{company_name}" corporate strategy business expansion 2024 2025', 5),
        ('tech_environment',    f'"{company_name}" IT infrastructure technology stack cloud servers', 5),
        ('pain_points',         f'"{company_name}" IT challenges technology problems legacy infrastructure', 5),
        ('decision_makers',     f'"{company_name}" CTO CIO CEO CFO VP technology executives 2024 2025', 5),
        ('financial_signals',   f'"{company_name}" revenue earnings financial results investment 2024', 5),
        ('competitive_context', f'"{company_name}" competitors market position industry ranking', 5),
    ]

    tasks = [_fetch_with_timeout(q, n, 10.0, company_name, company_domain) for (_, q, n) in queries]
    task_results = await asyncio.gather(*tasks)

    for (key, _q, _n), items in zip(queries, task_results):
        results[key] = items
        for item in items:
            if item.get('url'):
                results['sources'].append(item['url'])

    # Noticias recientes en paralelo 
    news_items = await _fetch_with_timeout(
        f'"{company_name}" news announcement 2024', 5, 10.0, company_name, company_domain
    )
    
    company_words = [w.lower() for w in company_name.split() if w.strip()]
    for r in news_items:
        combined_text = (r['title'] + " " + r['snippet']).lower()
        if any(w in combined_text for w in company_words):
            results['recent_news'].append({
                'title':   r['title'],
                'snippet': r['snippet'][:300],
                'url':     r['url'],
                'source':  r['source'],
            })

    # ── Validación cruzada ──
    validation = cross_validate(results, company_name)
    results['validation_report'] = validation
    results['data_quality']      = validation['quality_label']

    if validation['quality_label'] == 'LOW':
        results['data_warning'] = (
            f"Low quality data detected for {company_name}. "
            f"Only {validation['fields_with_data']}/6 fields have verified data. "
            f"Missing: {', '.join(validation['fields_missing'])}. "
            f"Manual research recommended before using this account profile."
        )
    else:
        results['data_warning'] = None

    # ── Keywords tecnológicos ──
    all_tech_text = ' '.join([i['snippet'] for i in results['tech_environment']]).lower()
    tech_kws = [
        'cloud', 'AI', 'servers', 'storage', 'network', 'data center',
        'migration', 'hybrid', 'automation', 'ERP', 'SAP', 'VMware',
        'cybersecurity', 'IoT', 'edge computing', 'HPC', 'GPU',
        'digital transformation', 'modernization', 'infrastructure'
    ]
    results['tech_keywords'] = ' '.join([kw for kw in tech_kws if kw.lower() in all_tech_text])

    # ── Limpiar fuentes: solo conservar URLs de items válidos ──
    # Combina lógica dev/HEAD
    valid_urls = set()
    for field in ['strategy_background', 'tech_environment', 'pain_points',
                  'decision_makers', 'financial_signals', 'competitive_context']:
        for item in results.get(field, []):
            if item.get('valid') and item.get('url'):
                valid_urls.add(item['url'])
                
    if valid_urls:
        results['sources'] = list(valid_urls)[:15]
    else:
        results['sources'] = list(dict.fromkeys([s for s in results['sources'] if s]))[:15]

    return results

# ─── VALIDADOR DE DATOS ───────────────────────────────────────
def validate_item(item: dict, field_name: str) -> dict:
    issues = []
    snippet = item.get('snippet', '').strip()
    if not snippet or len(snippet) < 30:
        issues.append("snippet too short or empty")

    title = item.get('title', '').strip()
    if not title:
        issues.append("missing title")

    url = item.get('url', '')
    if not url or url == '#' or 'error' in url.lower():
        issues.append("invalid or missing URL")

    relevance_keywords = {
        'strategy_background': ['strategy', 'business', 'plan', 'growth', 'expand', 'announce', 'launch', 'initiative'],
        'tech_environment':    ['technology', 'cloud', 'server', 'data', 'IT', 'software', 'platform', 'system', 'infrastructure'],
        'pain_points':         ['challenge', 'problem', 'issue', 'struggle', 'legacy', 'risk', 'cost', 'difficult', 'need'],
        'decision_makers':     ['CEO', 'CTO', 'CIO', 'CFO', 'VP', 'director', 'chief', 'president', 'officer', 'executive'],
        'financial_signals':   ['revenue', 'profit', 'billion', 'million', 'earnings', 'financial', 'growth', 'quarter', 'fiscal'],
        'competitive_context': ['competitor', 'market', 'industry', 'versus', 'rival', 'leader', 'position', 'share', 'ranking']
    }

    keywords      = relevance_keywords.get(field_name, [])
    snippet_lower = snippet.lower()
    matches       = [kw for kw in keywords if kw.lower() in snippet_lower]

    if len(matches) == 0:
        issues.append(f"snippet not relevant to {field_name}")

    item['valid']             = len(issues) == 0
    item['validation_issues'] = issues
    item['relevance_matches'] = matches
    return item

def validate_field(items: list, field_name: str, min_valid: int = 1) -> dict:
    validated     = [validate_item(item.copy(), field_name) for item in items]
    valid_items   = [i for i in validated if i['valid']]
    invalid_items = [i for i in validated if not i['valid']]

    return {
        'items':       validated,
        'valid_count': len(valid_items),
        'invalid_count': len(invalid_items),
        'has_minimum': len(valid_items) >= min_valid,
        'status':      'OK' if len(valid_items) >= min_valid else 'INSUFFICIENT'
    }

def cross_validate(web_data: dict, company_name: str) -> dict:
    company_words     = [w.lower() for w in company_name.split() if len(w) > 2]
    validation_report = {}
    total_valid       = 0
    total_items       = 0

    fields = [
        'strategy_background', 'tech_environment', 'pain_points',
        'decision_makers', 'financial_signals', 'competitive_context'
    ]

    for field in fields:
        items            = web_data.get(field, [])
        field_validation = validate_field(items, field)

        for item in field_validation['items']:
            snippet_lower  = item.get('snippet', '').lower()
            title_lower    = item.get('title', '').lower()
            combined       = snippet_lower + ' ' + title_lower
            company_mentions = sum(1 for word in company_words if word in combined)
            item['mentions_company'] = company_mentions > 0

            if not item['mentions_company']:
                item['valid'] = False
                item['validation_issues'].append(f"does not mention {company_name}")

        valid_after_cross            = [i for i in field_validation['items'] if i['valid']]
        field_validation['valid_count'] = len(valid_after_cross)
        field_validation['status']   = 'OK' if len(valid_after_cross) >= 1 else 'INSUFFICIENT'

        validation_report[field] = field_validation
        total_valid += field_validation['valid_count']
        total_items += len(items)

    quality_score = int((total_valid / total_items * 100)) if total_items > 0 else 0

    return {
        'fields':             validation_report,
        'total_valid_items':  total_valid,
        'total_items':        total_items,
        'quality_score':      quality_score,
        'quality_label': (
            'HIGH'   if quality_score >= 70 else
            'MEDIUM' if quality_score >= 40 else
            'LOW'
        ),
        'fields_with_data': sum(1 for f in validation_report.values() if f['status'] == 'OK'),
        'fields_missing':   [f for f, v in validation_report.items() if v['status'] == 'INSUFFICIENT']
    }

# ─── SCRAPER PRINCIPAL (API PÚBLICA — BACKWARD COMPATIBLE) ────

def search_account(company_name: str, company_url: str = '', industry: str = 'Technology') -> dict:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _async_search_account(company_name, company_url, industry))
                return future.result()
        else:
            return asyncio.run(_async_search_account(company_name, company_url, industry))
    except RuntimeError:
        return asyncio.run(_async_search_account(company_name, company_url, industry))

def calculate_net_new_score(years_inactive: int, web_data: dict) -> dict:
    inactivity_score = min(years_inactive * 15, 40)
    validation = web_data.get('validation_report', {})
    tech_valid = validation.get('fields', {}).get('tech_environment', {}).get('valid_count', 0)
    tech_score = min(tech_valid * 8, 25)
    pain_valid = validation.get('fields', {}).get('pain_points', {}).get('valid_count', 0)
    pain_score = min(pain_valid * 10, 25)
    news_score = min(len(web_data.get('recent_news', [])) * 3, 10)

    total = inactivity_score + tech_score + pain_score + news_score

    if total >= 70:
        priority = 'HIGH PRIORITY'
        color    = 'red'
    elif total >= 40:
        priority = 'MEDIUM PRIORITY'
        color    = 'orange'
    else:
        priority = 'MONITORING'
        color    = 'green'

    return {
        'total_score': total,
        'priority':    priority,
        'color':       color,
        'factors': {
            'Inactivity Factor':     inactivity_score,
            'Tech Initiatives':      tech_score,
            'Pain Points Detected':  pain_score,
            'Recent Activity':       news_score
        },
        'is_net_new':   years_inactive >= 3,
        'data_quality': web_data.get('data_quality', 'UNKNOWN')
    }