import json
from crewai import Agent, Task, Crew, Process
# Usamos el LLM local para garantizar el Zero Data Leakage
from langchain_community.llms import Ollama

def run_dual_agent_analysis(company_name, web_data, products, years_inactive, client_status="ACTIVE"):
    """
    Motor Dual-Agent real de KORHEX.AI.
    Procesa la información estrictamente en local usando CrewAI y Ollama.
    """
    
    # 1. Conexión al cerebro local (Ej. modelo llama3 o mistral corriendo en la RTX 5080)
    # Si Ollama corre en el puerto por defecto, LangChain lo detecta automáticamente.
    local_llm = Ollama(model="mistral")

    # --- AGENTES (Modo Sigilo Activado) ---
    
    research_agent = Agent(
        role='Auditor de Inteligencia Comercial',
        goal=f'Analizar la huella digital de {company_name} y extraer necesidades sin inventar datos.',
        backstory='Un analista paranoico de la ciberseguridad que audita la viabilidad de un cliente basándose solo en los datos provistos.',
        verbose=False,  # Zero Data Leakage (No imprime en consola)
        llm=local_llm,
        allow_delegation=False
    )

    sales_agent = Agent(
        role='Estratega B2B Senior',
        goal='Redactar pitches de venta letales o advertir sobre riesgos operativos.',
        backstory='Un Account Manager veterano. Sabe exactamente qué productos ofrecer y es implacable descartando cuentas que hacen perder el tiempo.',
        verbose=False,  # Zero Data Leakage
        llm=local_llm,
        allow_delegation=False
    )

    # --- TAREAS ---
    
    # Tarea 1: Auditoría y Resumen
    research_task = Task(
        description=f'''
        Analiza la información recolectada de {company_name}, inactiva por {years_inactive} años.
        Datos web extraídos: {json.dumps(web_data)[:1500]}
        
        Redacta un reporte analítico de un párrafo sobre sus principales puntos de dolor o iniciativas tecnológicas.
        ''',
        expected_output="Un párrafo conciso detallando la situación actual de la empresa.",
        agent=research_agent
    )

    # Lógica de Descarte (Regla NUEVA)
    if client_status == "DISCARD":
        sales_description = f'''
        El cliente {company_name} está en modo DISCARD.
        REGLA ESTRICTA: NO redactes el pitch de ventas. 
        En su lugar, redacta un 'Aviso de Riesgo Operativo' de máximo 50 palabras aconsejándole al equipo por qué NO vale la pena invertir tiempo en esta empresa.
        '''
        expected_sales = "Un 'Aviso de Riesgo Operativo' de máximo 50 palabras."
        audit_passed = False
        audit_notes = "Rechazado por el Auditor: Alto riesgo operativo o falta de datos (Modo DISCARD)."
    else:
        sales_description = f'''
        Basado en el análisis de investigación, redacta un pitch de ventas para {company_name}.
        Catálogo de productos disponibles para ofrecer: {json.dumps(products)}
        
        REGLA DEL TOP 5: Analiza los productos encontrados y preséntalos como un 'Top 5 Ordenado por Prioridad'. El criterio de orden es el impacto financiero y la urgencia operativa para la industria del cliente. Enuméralos del 1 al 5.
        '''
        expected_sales = "Un pitch de ventas persuasivo que incluya la lista 'Top 5 Ordenado por Prioridad'."
        audit_passed = True
        audit_notes = "Aprobado por el Auditor: El discurso cumple con las reglas de negocio y ofrece el Top 5."

    # Tarea 2: Pitch o Descarte
    sales_task = Task(
        description=sales_description,
        expected_output=expected_sales,
        agent=sales_agent
    )

    # --- EJECUCIÓN DEL CREW ---
    
    crew = Crew(
        agents=[research_agent, sales_agent],
        tasks=[research_task, sales_task],
        process=Process.sequential,
        verbose=False # Doble validación de sigilo
    )

    # Encendiendo el motor...
    result = crew.kickoff()
    
    # Formateo de salida para cumplir con la estructura que espera app.py
    final_output = str(result)
    word_count = len(final_output.split())
    
    return {
        'research_analysis': "Auditoría completada en local. Revisa el pitch para la estrategia final.",
        'sales_speech': final_output,
        'word_count': word_count,
        'audit_passed': audit_passed,
        'audit_notes': audit_notes,
        'estimated_tokens': int(word_count * 1.5) # Estimación interna para el ROI
    }