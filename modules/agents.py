import time, os, requests
import re

def clean_text(text: str) -> str:
    # Elimina caracteres que Streamlit no puede renderizar
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u00A0-\u00FF\n\r\t ]', '', text)
    return text.strip()

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

    summary      = web_data.get('summary', '')[:400]
    tech_keywords = web_data.get('tech_keywords', '')
    industry     = web_data.get('industry', 'Technology')
    data_quality = web_data.get('data_quality', 'UNKNOWN')

    # ── Prompt Agente Investigador ───────────────────────
    research_prompt = f"""Eres un analista de ventas B2B especializado en tecnología empresarial (Dell).
Analiza esta cuenta y genera un reporte de inteligencia comercial detallado.

EMPRESA: {company_name}
INDUSTRIA: {industry}
AÑOS SIN COMPRAR: {years_inactive}
CALIDAD DE DATOS: {data_quality}

RESUMEN PÚBLICO: {summary}
ENTORNO TECNOLÓGICO: {tech_snippets}
PAIN POINTS: {pain_snippets}
SEÑALES FINANCIERAS: {financial_snippets}
KEYWORDS TECNOLÓGICOS: {tech_keywords}

SOLUCIONES DELL RECOMENDADAS:
{product_context}

IMPORTANTE: Responde EXACTAMENTE con este formato y estos encabezados:

## 1. COMPANY SNAPSHOT & STRATEGY
[Escribe aquí el análisis de situación actual y estrategia de la empresa]

## 2. TECHNOLOGY ENVIRONMENT
[Escribe aquí el análisis del entorno tecnológico detectado]

## 3. IT PAIN POINTS
[Escribe aquí los pain points críticos identificados]

## 4. KEY DECISION MAKERS
[Escribe aquí los tomadores de decisión identificados]

## 5. FINANCIAL SIGNALS
[Escribe aquí las señales financieras relevantes]

## 6. COMPETITIVE CONTEXT
[Escribe aquí el contexto competitivo de la empresa]

Sé específico con datos reales de la empresa. Mínimo 30 palabras por sección."""

    # ── Prompt Agente Vendedor ───────────────────────────
    sales_prompt = f"""Eres un ejecutivo de ventas senior de Dell Technologies con 15 años de experiencia.
Escribe un discurso de ventas personalizado para reconquistar esta cuenta.

EMPRESA: {company_name}
INDUSTRIA: {industry}
AÑOS SIN COMPRAR: {years_inactive} años
ENTORNO TECH: {tech_snippets[:300]}
PAIN POINTS: {pain_snippets[:200]}

SOLUCIONES A PROPONER:
{product_context}

REGLAS:
- Entre 150 y 180 palabras exactamente
- Tono profesional pero cercano
- Menciona el nombre de la empresa al menos 2 veces
- Referencia un pain point específico detectado
- Propone una solución concreta con su ROI
- Termina con un call-to-action claro
- NO uses frases genéricas como "soluciones de clase mundial"
- Escribe directamente el discurso, sin títulos ni secciones

Escribe el discurso ahora:"""

    # ── Función helper para llamar a Ollama ──────────────
    def call_ollama(prompt: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            return response.json().get("response", "Error: respuesta vacía de Ollama")
        except requests.exceptions.ConnectionError:
            return "Error: Ollama no está corriendo. Ejecuta 'ollama serve' en tu terminal."
        except Exception as e:
            return f"Error: {str(e)}"

    # ── Agente 1: Investigador ───────────────────────────
    research_analysis = call_ollama(research_prompt)

    # ── Agente 2: Vendedor ───────────────────────────────
    sales_speech = call_ollama(sales_prompt)

    # ── Agente Auditor: validación básica ────────────────
    word_count   = len(sales_speech.split())
    audit_passed = 150 <= word_count <= 220
    audit_notes  = (
        f"✅ Discurso aprobado: {word_count} palabras. Contenido personalizado para {company_name}."
        if audit_passed else
        f"⚠️ Discurso fuera de rango: {word_count} palabras (esperado: 150-180). Revisar prompt."
    )

    estimated_tokens = (
        len(research_prompt.split()) + len(sales_prompt.split()) +
        len(research_analysis.split()) + word_count
    )

    return {
        'research_analysis': clean_text(research_analysis),
        'sales_speech':      clean_text(sales_speech),
        'word_count':        word_count,
        'audit_passed':      audit_passed,
        'audit_notes':       audit_notes,
        'estimated_tokens':  estimated_tokens
    }