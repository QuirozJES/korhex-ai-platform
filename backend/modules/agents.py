import os
os.environ["OPENAI_API_KEY"] = "NA"

import re, requests, time
from crewai import Agent, Task, Crew, Process, LLM

def clean_text(text: str) -> str:
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u00A0-\u00FF\n\r\t ]', '', text)
    return text.strip()

def run_dual_agent_analysis(company_name, web_data, products, years_inactive, client_status="ACTIVE", report_language="en"):
    # Language instruction injected into every prompt
    lang_name   = "Spanish" if report_language == "es" else "English"
    lang_rule   = f"CRITICAL LANGUAGE RULE: You MUST write your ENTIRE response in professional {lang_name}. DO NOT use any other language."
    lang_suffix = f"Everything must be in {lang_name}."
    # ── 1. Contexto de Datos Reales ──────────────
    product_context = "\n".join([
        f"- {p['name']}: {p['description']} | ROI: {p['roi_pitch']} | Pain: {p['pain_solved']}"
        for p in products
    ]) if products else "There's no fitting products."

    tech_snippets = " ".join([i['snippet'] for i in web_data.get('tech_environment', []) if i.get('valid')])[:600]
    pain_snippets = " ".join([i['snippet'] for i in web_data.get('pain_points', []) if i.get('valid')])[:400]


    financial_snippets = " ".join([
        item['snippet'] for item in web_data.get('financial_signals', [])
        if item.get('valid') and item.get('snippet')
    ])[:300]

    summary       = web_data.get('summary', '')[:400]
    tech_keywords = web_data.get('tech_keywords', '')
    industry      = web_data.get('industry', 'Technology')
    data_quality  = web_data.get('data_quality', 'UNKNOWN')

    # ── 2. Conexión local a Ollama (Singleton — modelo cargado una sola vez) ──
    from modules.agent import OllamaClient
    mi_llm = OllamaClient().llm

    # Fallback: si el singleton no pudo inicializar el LLM, crear directo
    if mi_llm is None:
        mi_llm = LLM(
            model="ollama/llama3",
            base_url="http://localhost:11434"
        )

    # ── 3. Prompts ───────────────────────────────────────
    research_prompt = f"""You are a B2B sales analyst specialized in enterprise technology (HPE).
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

RECOMMENDED HPE SOLUTIONS:
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

You are a Senior Sales Intelligence Strategist. Your output must be professional, data-driven, and perfectly formatted for a modern UI dashboard.
CRITICAL FORMATTING RULES:
    NO MARKDOWN HEADERS: Never use symbols like '#', '##', or '###'.
    EMPHASIS: Use bold text (**text**) only for key terms or titles within the paragraph.
    STRUCTURE: Use clear paragraphs and bullet points (*) for lists.
    TONE: Professional, concise, and focused on ROI.
    {lang_rule}
Failure to follow these formatting rules will break the user interface. Ensure the text is clean and ready to be displayed in a dashboard card."""

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
        role='Senior HPE Sales Specialist',
        goal=(
            f'Write persuasive pitches that include a Top 5 Solutions list ordered by priority. '
            f'You MUST strictly provide a numbered list of exactly 5 products from the HPE portfolio (Top 5 HPE Solutions). '
            f'Use ONLY HPE products in your speech — never mention Dell, NVIDIA, Cisco, or any competitor brand. '
            f'Be extremely concise with each product description. '
            f'Maximum word limit is 350 words. '
            f'{lang_rule}'
        ),
        backstory=(
            f'You are a Senior HPE Sales Specialist with 12 years of experience selling HPE enterprise infrastructure. '
            f'You know the HPE portfolio inside out: ProLiant Gen11, Alletra Storage, GreenLake, Aruba Networking, Zerto, EliteBook, and EdgeConnect SecOps. '
            f'You NEVER recommend competitor products. You always include the Top 5 HPE Solutions list, '
            f'never exceed 350 words, and you ALWAYS write in {lang_name}.'
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
        {lang_rule}
        """
        expected_sales = f"Operational Risk Notice of maximum 50 words in {lang_name}."
        audit_passed   = False
        audit_notes    = "Rejected by Auditor: High operational risk (DISCARD mode)."
    else:
        sales_description = f"""
        Based on the analysis, write a personalized HPE Enterprise sales pitch for {company_name}.
        INDUSTRY: {industry} | YEARS WITHOUT PURCHASING: {years_inactive}
        TECH ENVIRONMENT: {tech_snippets[:300]}
        PAIN POINTS: {pain_snippets[:200]}

        HPE RECOMMENDED SOLUTIONS:
        {product_context}

        FORMAT RULES (MANDATORY — FOLLOW EXACTLY):
        - Write exactly 2 short opening paragraphs (context + main pain point).
        - Then write a numbered list titled 'Top 5 HPE Solutions:' with exactly 5 HPE products.
          For each product: one sentence max describing its specific benefit for {company_name}.
        - End with one clear call-to-action sentence.
        - Total word count must be between 150 and 350 words. DO NOT exceed 350 words.
        - Use ONLY HPE products. DO NOT mention Dell, NVIDIA, Cisco, or any competitor.

        {lang_rule}
        CRITICAL LENGTH RULE: You must strictly limit your entire speech to a MAXIMUM of 350 words.
        """
        expected_sales = f"HPE sales pitch with Top 5 HPE Solutions numbered list, 150-350 words, in {lang_name}."
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
        {lang_rule}
        """,
        expected_output=f"Structured report of the company's situation in {lang_name}.",
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
        audit_passed = 150 <= word_count <= 350
        audit_notes  = (
            f"Speech approved: {word_count} words."
            if audit_passed else
            f"Speech out of range: {word_count} words (expected: 150-350)."
        )

    return {
        "research_analysis": research_analysis,
        "sales_speech": sales_speech,
        "word_count": word_count,
        "audit_passed": audit_passed,
        "audit_notes": audit_notes,
        "estimated_tokens": word_count * 2
    }