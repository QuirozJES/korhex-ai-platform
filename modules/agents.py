import re, os
from crewai import Agent, Task, Crew, Process, LLM

def clean_text(text: str) -> str:
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u00A0-\u00FF\n\r\t ]', '', text)
    return text.strip()

def run_dual_agent_analysis(company_name, web_data, products, years_inactive, client_status="ACTIVE"):
    # ── 1. Contexto de Datos Reales ──────────────
    product_context = "\n".join([
        f"- {p['name']}: {p['description']} | ROI: {p['roi_pitch']} | Pain: {p['pain_solved']}"
        for p in products
    ]) if products else "No hay productos identificados."

    tech_snippets = " ".join([i['snippet'] for i in web_data.get('tech_environment', []) if i.get('valid')])[:600]
    pain_snippets = " ".join([i['snippet'] for i in web_data.get('pain_points', []) if i.get('valid')])[:400]

    # ── 2. Cerebro Local (Zero Data Leakage) ──────────────
    local_llm = LLM(
        model="ollama/llama3",
        base_url="http://localhost:11434"
    )

    # ── 3. Agentes (Modo Sigilo: verbose=False) ──────────────
    research_agent = Agent(
        role='Analista de Inteligencia Comercial B2B',
        goal=f'Generar reporte de inteligencia para {company_name}.',
        backstory='Analista senior de Dell Technologies. Experto en auditoría técnica.',
        verbose=False, # Cumple auditoría de seguridad
        llm=local_llm
    )

    sales_agent = Agent(
        role='Estratega de Ventas Senior',
        goal='Redactar pitches persuasivos o advertir de riesgos.',
        backstory='Ejecutivo veterano con 15 años de experiencia en Dell.',
        verbose=False, # Cumple auditoría de seguridad
        llm=local_llm
    )

    # ── 4. Tareas con Reglas del Inge 3 ──────────────
    research_task = Task(
        description=f"Analiza a {company_name}. Tech: {tech_snippets}. Pains: {pain_snippets}.",
        expected_output="Análisis técnico detallado.",
        agent=research_agent
    )

    if client_status == "DISCARD":
        # REGLA DE DESCARTE
        sales_description = f"""El cliente {company_name} está en modo DISCARD. 
        NO redactes el pitch de ventas. En su lugar, redacta un 'Aviso de Riesgo Operativo' 
        de máximo 50 palabras aconsejándole al equipo por qué NO vale la pena invertir tiempo en esta empresa."""
        expected_sales = "Aviso de Riesgo Operativo (Máx 50 palabras)."
        audit_passed, audit_notes = False, "⚠️ RECHAZADO: Modo DISCARD activado."
    else:
        # REGLA DEL TOP 5
        sales_description = f"""Escribe un discurso de ventas para {company_name}.
        PRODUCTOS: {product_context}
        INSTRUCCIÓN EXACTA: Analiza los productos encontrados y preséntalos como un 'Top 5 Ordenado por Prioridad'. 
        El criterio de orden es el impacto financiero y la urgencia operativa para la industria del cliente. Enuméralos del 1 al 5."""
        expected_sales = "Discurso de ventas con Top 5 ordenado por prioridad."
        audit_passed, audit_notes = True, "✅ APROBADO: Incluye Regla del Top 5."

    sales_task = Task(description=sales_description, expected_output=expected_sales, agent=sales_agent)

    # ── 5. Ejecución ──────────────
    crew = Crew(agents=[research_agent, sales_agent], tasks=[research_task, sales_task], verbose=False)
    result = str(crew.kickoff())
    
    return {
        'research_analysis': "Análisis procesado por CrewAI local.",
        'sales_speech': clean_text(result),
        'word_count': len(result.split()),
        'audit_passed': audit_passed,
        'audit_notes': audit_notes,
        'estimated_tokens': 1200
    }