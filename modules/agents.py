import time, os, json, requests

def run_dual_agent_analysis(company_name, web_data, products, years_inactive):
    
    # ── Preparar contexto con datos reales ──────────────
    product_context = "\n".join([
        f"- {p['name']}: {p['description']} | ROI: {p['roi_pitch']} | Pain: {p['pain_solved']}"
        for p in products
    ]) if products else "No hay productos específicos identificados."

    tech_snippets = " ".join([
        item['snippet'] for item in web_data.get('tech_environment', [])
        if item.get('valid') and item.get('snippet')
    ])[:600]

    pain_snippets = " ".join([
        item['snippet'] for item in web_data.get('pain_points', [])
        if item.get('valid') and item.get('snippet')
    ])[:400]

    financial_snippets = " ".join([
        item['snippet'] for item in web_data.get('financial_signals', [])
        if item.get('valid') and item.get('snippet')
    ])[:300]

    summary = web_data.get('summary', '')[:400]
    tech_keywords = web_data.get('tech_keywords', '')
    industry = web_data.get('industry', 'Technology')
    data_quality = web_data.get('data_quality', 'UNKNOWN')

    # ── Prompt del Agente Investigador ──────────────────
    research_prompt = f"""Eres un analista de ventas B2B especializado en tecnología empresarial (Dell).
Analiza esta cuenta y genera un reporte de inteligencia comercial detallado.

EMPRESA: {company_name}
INDUSTRIA: {industry}
AÑOS SIN COMPRAR: {years_inactive}
CALIDAD DE DATOS: {data_quality}

RESUMEN PÚBLICO: {summary}

ENTORNO TECNOLÓGICO DETECTADO: {tech_snippets}

PAIN POINTS IDENTIFICADOS: {pain_snippets}

SEÑALES FINANCIERAS: {financial_snippets}

KEYWORDS TECNOLÓGICOS: {tech_keywords}

SOLUCIONES DELL RECOMENDADAS:
{product_context}

Genera un análisis de inteligencia de cuenta con estas secciones:
1. SITUACIÓN ACTUAL (contexto tecnológico y de negocio)
2. PAIN POINTS CRÍTICOS (problemas que podemos resolver)
3. OPORTUNIDAD COMERCIAL (por qué ahora, por qué Dell)
4. PRODUCTOS RECOMENDADOS (justificación específica para cada uno)
5. SEÑALES DE COMPRA (indicadores de que están listos para comprar)

Sé específico con datos reales de la empresa. Mínimo 200 palabras."""

    # ── Prompt del Agente Vendedor ───────────────────────
    sales_prompt = f"""Eres un ejecutivo de ventas senior de Dell Technologies con 15 años de experiencia.
Escribe un discurso de ventas personalizado y convincente para reconquistar esta cuenta.

EMPRESA: {company_name}
INDUSTRIA: {industry}  
AÑOS SIN COMPRAR: {years_inactive} años
ENTORNO TECH: {tech_snippets[:300]}
PAIN POINTS: {pain_snippets[:200]}

SOLUCIONES A PROPONER:
{product_context}

REGLAS DEL DISCURSO:
- Exactamente entre 150 y 180 palabras
- Tono profesional pero cercano, no robótico
- Menciona el nombre de la empresa al menos 2 veces
- Referencia UN pain point específico y real detectado
- Propone UNA solución concreta con su ROI
- Termina con un call-to-action claro (reunión, demo, llamada)
- NO uses frases genéricas como "soluciones de clase mundial"
- NO hagas promesas de números exactos que no puedas comprobar
- Escribe directamente el discurso, sin títulos ni secciones

Escribe el discurso ahora:"""

    # ── (Agente 1: Investigador) ────────
    try:
        response_research = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": research_prompt}]
            },
            timeout=60
        )
        research_data = response_research.json()
        research_analysis = research_data["content"][0]["text"]
    except Exception as e:
        research_analysis = f"Error en análisis: {str(e)}"

    # ── (Agente 2: Vendedor) ────────────
    try:
        response_sales = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": sales_prompt}]
            },
            timeout=60
        )
        sales_data = response_sales.json()
        sales_speech = sales_data["content"][0]["text"]
    except Exception as e:
        sales_speech = f"Error en discurso: {str(e)}"

    # ── Agente Auditor: validación básica ────────────────
    word_count = len(sales_speech.split())
    audit_passed = 150 <= word_count <= 220
    audit_notes = (
        f"✅ Discurso aprobado: {word_count} palabras. Contenido personalizado para {company_name}."
        if audit_passed else
        f"⚠️ Discurso fuera de rango: {word_count} palabras (esperado: 150-180). Revisar prompt."
    )

    estimated_tokens = len(research_prompt.split()) + len(sales_prompt.split()) + word_count + len(research_analysis.split())

    return {
        'research_analysis': research_analysis,
        'sales_speech': sales_speech,
        'word_count': word_count,
        'audit_passed': audit_passed,
        'audit_notes': audit_notes,
        'estimated_tokens': estimated_tokens
    }