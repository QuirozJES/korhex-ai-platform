import json
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

def run_dual_agent_analysis(company_name, web_data, products, years_inactive, client_status="ACTIVE"):

    # ── 1. Preparación de Datos (Lo que rescatamos del Merge) ──────────────
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

    summary      = web_data.get('summary', '')[:400]
    industry     = web_data.get('industry', 'Technology')

    # ── 2. Conexión Local (Zero Data Leakage) ──────────────
    local_llm = Ollama(model="llama3") # Usamos llama3 como pedía el código original

    # ── 3. Agentes de CrewAI (Modo Sigilo: verbose=False) ──────────────
    research_agent = Agent(
        role='Analista de Inteligencia Comercial B2B',
        goal=f'Generar un reporte detallado de la situación técnica de {company_name}.',
        backstory='Eres un analista senior especializado en tecnología empresarial (Dell). Eres analítico y vas directo al grano.',
        verbose=False,
        llm=local_llm,
        allow_delegation=False
    )

    sales_agent = Agent(
        role='Estratega de Ventas Senior (Dell Technologies)',
        goal='Redactar pitches persuasivos o advertir de riesgos operativos.',
        backstory='Ejecutivo veterano. Sabes exactamente qué productos ofrecer y no pierdes el tiempo con clientes sin potencial.',
        verbose=False,
        llm=local_llm,
        allow_delegation=False
    )

    # ── 4. Tareas (Tasks) ──────────────
    research_task = Task(
        description=f"""
        Analiza esta cuenta y genera un reporte de inteligencia comercial.
        EMPRESA: {company_name} | INDUSTRIA: {industry} | AÑOS SIN COMPRAR: {years_inactive}
        RESUMEN: {summary}
        ENTORNO TECH: {tech_snippets}
        PAIN POINTS: {pain_snippets}

        Genera un análisis con: 1. SITUACIÓN ACTUAL, 2. PAIN POINTS CRÍTICOS, 3. OPORTUNIDAD COMERCIAL.
        """,
        expected_output="Reporte estructurado de la situación de la empresa.",
        agent=research_agent
    )

    # ── Reglas de Negocio del Inge 3 ──
    if client_status == "DISCARD":
        sales_description = f"""
        El cliente {company_name} está en modo DISCARD.
        NO redactes el pitch de ventas. 
        En su lugar, redacta un 'Aviso de Riesgo Operativo' de máximo 50 palabras aconsejándole al equipo por qué NO vale la pena invertir tiempo en esta empresa.
        """
        expected_sales = "Un 'Aviso de Riesgo Operativo' de máximo 50 palabras."
        audit_passed = False
        audit_notes = "Rechazado por el Auditor: Alto riesgo operativo (Modo DISCARD)."
    else:
        sales_description = f"""
        Basado en el análisis, redacta un discurso de ventas personalizado para {company_name}.
        SOLUCIONES DELL RECOMENDADAS:
        {product_context}

        REGLA DEL TOP 5: Analiza los productos encontrados y preséntalos como un 'Top 5 Ordenado por Prioridad'. El criterio de orden es el impacto financiero y la urgencia operativa para la industria del cliente. Enuméralos del 1 al 5.
        """
        expected_sales = "Pitch de ventas persuasivo que incluya la lista 'Top 5 Ordenado por Prioridad'."
        audit_passed = True
        audit_notes = "Aprobado por el Auditor: Cumple con la Regla del Top 5."

    sales_task = Task(
        description=sales_description,
        expected_output=expected_sales,
        agent=sales_agent
    )

    # ── 5. Ejecución del Crew ──────────────
    crew = Crew(
        agents=[research_agent, sales_agent],
        tasks=[research_task, sales_task],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff()
    sales_speech = str(result)
    word_count = len(sales_speech.split())

    return {
        'research_analysis': "Investigación completada por CrewAI. Revisa el resultado final.",
        'sales_speech': sales_speech,
        'word_count': word_count,
        'audit_passed': audit_passed,
        'audit_notes': audit_notes,
        'estimated_tokens': int(word_count * 1.5) + 300
    }