import os
os.environ["OPENAI_API_KEY"] = "NA"

import re, requests, time
from crewai import Agent, Task, Crew, Process, LLM

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
    mi_llm = LLM(
        model="ollama/llama3",
        base_url="http://localhost:11434"
    )

    # ── 3. Prompts ───────────────────────────────────────
    research_prompt = f"""You are a B2B sales analyst specialized in enterprise technology (Dell).
Analyze this account and generate a detailed commercial intelligence report.

COMPANY: {company_name}
INDUSTRY: {industry}
YEARS WITHOUT PURCHASING: {years_inactive}
DATA QUALITY: {data_quality}

PUBLIC SUMMARY: {summary}
TECHNOLOGY ENVIRONMENT: {tech_snippets}
PAIN POINTS: {pain_snippets}
FINANCIAL SIGNALS: {financial_snippets}
TECH KEYWORDS: {tech_keywords}

RECOMMENDED DELL SOLUTIONS:
{product_context}

CRITICAL: You MUST use EXACTLY these section tags, in this exact order, with no changes:

[SECTION_1]
Write 40-60 words about company current situation and strategy.

[SECTION_2]
Write 40-60 words about the detected technology environment.

[SECTION_3]
Write 40-60 words about the critical IT pain points identified.

[SECTION_4]
Write 40-60 words about key decision makers and stakeholders.

[SECTION_5]
Write 40-60 words about relevant financial signals and budget capacity.

[SECTION_6]
Write 40-60 words about the competitive context of the company.

RULES: Do NOT skip any section. Do NOT use markdown headers like ## or **. Only use [SECTION_N] tags as delimiters.
IMPORTANT: Write your entire response in English."""

    # ── 4. Función helper Ollama ─────────────────────────
    def call_ollama(prompt: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 2048}   # evita truncamiento a mitad de oración
                },
                timeout=180
            )
            return response.json().get("response", "Error: empty response from Ollama")
        except requests.exceptions.ConnectionError:
            return "Error: Ollama is not running. Run 'ollama serve' in your terminal."
        except Exception as e:
            return f"Error: {str(e)}"

    # ── 5. Agente Investigador (requests directo) ────────
    research_analysis = call_ollama(research_prompt)

    # ── 6. Agentes CrewAI ────────────────────────────────
    research_agent = Agent(
        role='Commercial Intelligence Analyst',
        goal='Analyze enterprise accounts and identify sales opportunities.',
        backstory='Senior analyst with 10 years in B2B technology. Expert at detecting buying signals.',
        verbose=False,
        llm=mi_llm,
        allow_delegation=False
    )

    sales_agent = Agent(
        role='Senior Sales Strategist (Dell Technologies)',
        goal=(
            'Write persuasive pitches that include a Top 5 Solutions list ordered by priority. '
            'You MUST strictly provide a numbered list of exactly 5 products (Top 5 Solutions). '
            'Be extremely concise with each product description. '
            'Maximum word limit is 250 words.'
        ),
        backstory=(
            'Veteran executive. You know exactly which products to offer and how to position them. '
            'You are known for being precise: you always include the Top 5 Solutions numbered list '
            'and never exceed the agreed word budget of 250 words.'
        ),
        verbose=False,
        llm=mi_llm,
        allow_delegation=False
    )

    # ── 7. Lógica DISCARD vs ACTIVE ──────────────────────
    if client_status == "DISCARD":
        sales_description = f"""
        The client {company_name} is in DISCARD mode.
        DO NOT write the sales pitch.
        Write an 'Operational Risk Notice' of maximum 50 words
        explaining why it is NOT worth investing time in this company.
        IMPORTANT: You must write your entire response in English.
        """
        expected_sales = "Operational Risk Notice of maximum 50 words."
        audit_passed   = False
        audit_notes    = "Rejected by Auditor: High operational risk (DISCARD mode)."
    else:
        sales_description = f"""
        Based on the analysis, write a personalized sales pitch for {company_name}.
        INDUSTRY: {industry} | YEARS WITHOUT PURCHASING: {years_inactive}
        TECH ENVIRONMENT: {tech_snippets[:300]}
        PAIN POINTS: {pain_snippets[:200]}

        RECOMMENDED DELL SOLUTIONS:
        {product_context}

        FORMAT RULES (MANDATORY):
        - Write exactly 2 short opening paragraphs (context + main pain point).
        - Then write a numbered list titled 'Top 5 Solutions:' with exactly 5 products.
          For each product: one sentence max describing its benefit for {company_name}.
        - End with one clear call-to-action sentence.
        - Total word count must be between 150 and 250 words. DO NOT exceed 250 words.
        IMPORTANT: You must write your entire response in English.
        """
        expected_sales = "Sales pitch with Top 5 Solutions numbered list, 150-250 words."
        audit_passed   = True
        audit_notes    = "Approved by Auditor: Complies with the Top 5 Rule."

    # ── 8. Tasks ─────────────────────────────────────────
    research_task = Task(
        description=f"""
        Analyze this account: {company_name} | {industry} | {years_inactive} years without purchasing
        SUMMARY: {summary}
        TECH ENVIRONMENT: {tech_snippets}
        PAIN POINTS: {pain_snippets}
        Generate an analysis with: 1. CURRENT SITUATION, 2. PAIN POINTS, 3. COMMERCIAL OPPORTUNITY.
        IMPORTANT: You must write your entire response in English.
        """,
        expected_output="Structured report of the company's situation in English.",
        agent=research_agent
    )

    sales_task = Task(
        description=sales_description,
        expected_output=expected_sales,
        agent=sales_agent
    )

    # ── 9. Ejecución del Crew ─────────────────────────────
    try:
        crew = Crew(
            agents=[research_agent, sales_agent],
            tasks=[research_task, sales_task],
            process=Process.sequential,
            verbose=False
        )
        result       = crew.kickoff()
        sales_speech = clean_text(str(result))
    except Exception as crew_err:
        # Fallback: if CrewAI/LiteLLM is unavailable, call Ollama directly
        sales_speech = clean_text(call_ollama(sales_description))
        if not sales_speech or sales_speech.startswith("Error"):
            sales_speech = (f"[CrewAI unavailable. "
                            f"Install litellm to enable: pip install litellm]\n"
                            f"Raw error: {crew_err}")

    word_count   = len(sales_speech.split())

    if client_status != "DISCARD":
        audit_passed = 150 <= word_count <= 300
        audit_notes  = (
            f"Speech approved: {word_count} words."
            if audit_passed else
            f"Speech out of range: {word_count} words (expected: 150-300)."
        )

    return {
        "research_analysis": research_analysis,
        "sales_speech": sales_speech,
        "word_count": word_count,
        "audit_passed": audit_passed,
        "audit_notes": audit_notes,
        "estimated_tokens": word_count * 2
    }