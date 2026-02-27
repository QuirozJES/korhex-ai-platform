import re, requests, time, os
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

def clean_text(text: str) -> str:
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u00A0-\u00FF\n\r\t ]', '', text)
    return text.strip()

def run_dual_agent_analysis(company_name, web_data, products, years_inactive, client_status="ACTIVE"):

    # ── 1. Preparación de contexto ──────────────────────
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

    summary       = web_data.get('summary', '')[:400]
    tech_keywords = web_data.get('tech_keywords', '')
    industry      = web_data.get('industry', 'Technology')
    data_quality  = web_data.get('data_quality', 'UNKNOWN')

    # ── 2. Conexión local a Ollama ───────────────────────
    local_llm = Ollama(model="llama3")

    # ── 3. Prompts ───────────────────────────────────────
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
[Análisis de situación actual y estrategia]

## 2. TECHNOLOGY ENVIRONMENT
[Análisis del entorno tecnológico detectado]

## 3. IT PAIN POINTS
[Pain points críticos identificados]

## 4. KEY DECISION MAKERS
[Tomadores de decisión identificados]

## 5. FINANCIAL SIGNALS
[Señales financieras relevantes]

## 6. COMPETITIVE CONTEXT
[Contexto competitivo de la empresa]

Sé específico con datos reales. Mínimo 30 palabras por sección."""

    # ── 4. Función helper Ollama ─────────────────────────
    def call_ollama(prompt: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False},
                timeout=120
            )
            return response.json().get("response", "Error: respuesta vacía de Ollama")
        except requests.exceptions.ConnectionError:
            return "Error: Ollama no está corriendo. Ejecuta 'ollama serve' en tu terminal."
        except Exception as e:
            return f"Error: {str(e)}"

    # ── 5. Agente Investigador (requests directo) ────────
    research_analysis = call_ollama(research_prompt)

    # ── 6. Agentes CrewAI ────────────────────────────────
    research_agent = Agent(
        role='Analista de Inteligencia Comercial',
        goal='Analizar cuentas empresariales e identificar oportunidades de venta.',
        backstory='Analista senior con 10 años en tecnología B2B. Experto en detectar señales de compra.',
        verbose=False,
        llm=local_llm,
        allow_delegation=False
    )

    sales_agent = Agent(
        role='Estratega de Ventas Senior (Dell Technologies)',
        goal='Redactar pitches persuasivos o advertir de riesgos operativos.',
        backstory='Ejecutivo veterano. Sabes exactamente qué productos ofrecer.',
        verbose=False,
        llm=local_llm,
        allow_delegation=False
    )

    # ── 7. Lógica DISCARD vs ACTIVE ──────────────────────
    if client_status == "DISCARD":
        sales_description = f"""
        El cliente {company_name} está en modo DISCARD.
        NO redactes el pitch de ventas.
        Redacta un 'Aviso de Riesgo Operativo' de máximo 50 palabras 
        explicando por qué NO vale la pena invertir tiempo en esta empresa.
        """
        expected_sales = "Aviso de Riesgo Operativo de máximo 50 palabras."
        audit_passed   = False
        audit_notes    = "Rechazado por el Auditor: Alto riesgo operativo (Modo DISCARD)."
    else:
        sales_description = f"""
        Basado en el análisis, redacta un discurso de ventas personalizado para {company_name}.
        INDUSTRIA: {industry} | AÑOS SIN COMPRAR: {years_inactive}
        ENTORNO TECH: {tech_snippets[:300]}
        PAIN POINTS: {pain_snippets[:200]}

        SOLUCIONES DELL RECOMENDADAS:
        {product_context}

        REGLA DEL TOP 5: Presenta los productos como 'Top 5 Ordenado por Prioridad'
        según impacto financiero y urgencia operativa. Enuméralos del 1 al 5.
        Entre 150 y 180 palabras. Termina con un call-to-action claro.
        """
        expected_sales = "Pitch de ventas con Top 5 Ordenado por Prioridad."
        audit_passed   = True
        audit_notes    = "Aprobado por el Auditor: Cumple con la Regla del Top 5."

    # ── 8. Tasks ─────────────────────────────────────────
    research_task = Task(
        description=f"""
        Analiza esta cuenta: {company_name} | {industry} | {years_inactive} años sin comprar
        RESUMEN: {summary}
        ENTORNO TECH: {tech_snippets}
        PAIN POINTS: {pain_snippets}
        Genera análisis con: 1. SITUACIÓN ACTUAL, 2. PAIN POINTS, 3. OPORTUNIDAD COMERCIAL.
        """,
        expected_output="Reporte estructurado de la situación de la empresa.",
        agent=research_agent
    )

    sales_task = Task(
        description=sales_description,
        expected_output=expected_sales,
        agent=sales_agent
    )

    # ── 9. Ejecución del Crew ─────────────────────────────
    crew = Crew(
        agents=[research_agent, sales_agent],
        tasks=[research_task, sales_task],
        process=Process.sequential,
        verbose=False
    )

    result     = crew.kickoff()
    sales_speech = clean_text(str(result))
    word_count   = len(sales_speech.split())

    if client_status != "DISCARD":
        audit_passed = 150 <= word_count <= 220
        audit_notes  = (
            f"Discurso aprobado: {word_count} palabras."
            if audit_passed else
            f"Discurso fuera de rango: {word_count} palabras (esperado: 150-180)."
        )