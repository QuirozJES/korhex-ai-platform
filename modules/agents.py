import time

def run_dual_agent_analysis(company_name, web_data, products, years_inactive):
    """
    Versión de contingencia (Mock) mientras el Inge 4 sube su código real de CrewAI.
    Simula el trabajo del Agente Vendedor y el Agente Auditor.
    """
    # Simulamos que tu tarjeta gráfica está "pensando" por 3 segundos
    time.sleep(3) 
    
    return {
        'research_analysis': f"Análisis de {company_name}: Detectamos interés en el mercado por soluciones escalables. Los datos muestran oportunidad después de {years_inactive} años de inactividad.",
        'sales_speech': f"Hola equipo de {company_name}. Hemos notado su reciente enfoque en innovación tecnológica. Nuestras soluciones pueden ayudarles a reducir costos operativos.",
        'word_count': 45,
        'audit_passed': True,
        'audit_notes': "Aprobado por el Agente Auditor (Policía Malo): El discurso es seguro y no contiene promesas falsas.",
        'estimated_tokens': 850
    }