import ollama, json

RESEARCHER_PROMPT = '''You are a senior B2B Account Intelligence Analyst.
Analyze enterprise accounts using ONLY the provided data.
Structure your output in exactly 6 labeled sections.
Never fabricate data. If information is unavailable, state: Insufficient public data.
Always write in English.'''

SALES_WRITER_PROMPT = '''You are an elite Enterprise Sales Strategist.
Your speeches have exactly 4 components:
1) Opening with a verified data point from research
2) Challenge statement based on detected pain points
3) Solution bridge connecting challenge to specific products with ROI
4) Clear call to action with specific next step
MINIMUM 120 WORDS - this is mandatory.
Reference at least 2 specific data points from the research.
Write exclusively in English. Consultative tone, never pushy.'''

def generate_analysis(company_name: str, web_data: dict, products: list, years_inactive: int) -> dict:
    context = f'''
    COMPANY: {company_name}
    URL: {web_data.get('company_url', 'N/A')}
    INDUSTRY: {web_data.get('industry')}
    YEARS INACTIVE: {years_inactive}
    STRATEGY: {json.dumps([i.get('snippet','') for i in web_data.get('strategy_background',[])])}
    TECH ENV: {json.dumps([i.get('snippet','') for i in web_data.get('tech_environment',[])])}
    PAIN POINTS: {json.dumps([i.get('snippet','') for i in web_data.get('pain_points',[])])}
    DECISION MAKERS: {json.dumps([i.get('snippet','') for i in web_data.get('decision_makers',[])])}
    FINANCIALS: {json.dumps([i.get('snippet','') for i in web_data.get('financial_signals',[])])}
    COMPETITIVE: {json.dumps([i.get('snippet','') for i in web_data.get('competitive_context',[])])}
    PRODUCTS: {json.dumps([p['name']+': '+p['roi_pitch'] for p in products])}
    '''

    research_prompt = context + '''
    Generate a structured account analysis with EXACTLY these 6 labeled sections:
    ## 1. COMPANY SNAPSHOT & STRATEGY
    ## 2. TECHNOLOGY ENVIRONMENT
    ## 3. IT PAIN POINTS
    ## 4. KEY DECISION MAKERS
    ## 5. FINANCIAL SIGNALS
    ## 6. COMPETITIVE CONTEXT
    Base everything strictly on the provided data. Never invent facts.
    '''

    try:
        res = ollama.chat(model='llama3',
            messages=[{'role':'system','content':RESEARCHER_PROMPT},{'role':'user','content':research_prompt}],
            options={'temperature':0.3})
        research = res['message']['content']
    except Exception as e:
        research = f'Analysis error: {e}. Verify Ollama is running with: ollama serve'

    products_str = chr(10).join([f"- {p['name']}: {p['description']} | ROI: {p['roi_pitch']}" for p in products])
    net_new = f'NET NEW LOGO: no purchase in {years_inactive} years.' if years_inactive >= 3 else f'Re-engagement: {years_inactive} years since last purchase.'

    speech_prompt = f'''{net_new}
    Account Research: {research}
    Available Solutions: {products_str}
    Write a personalized sales speech for {company_name}.
    MANDATORY STRUCTURE:
    [COMPONENT 1 - OPENING WITH VERIFIED DATA]
    [COMPONENT 2 - CHALLENGE STATEMENT]
    [COMPONENT 3 - SOLUTION BRIDGE WITH ROI]
    [COMPONENT 4 - CALL TO ACTION]
    Requirements: minimum 120 words, reference 2+ data points, English only.'''

    try:
        res2 = ollama.chat(model='llama3',
            messages=[{'role':'system','content':SALES_WRITER_PROMPT},{'role':'user','content':speech_prompt}],
            options={'temperature':0.7})
        speech = res2['message']['content']
    except Exception as e:
        speech = f'Speech generation error: {e}'

    word_count = len(speech.split())
    if word_count < 120:
        try:
            res3 = ollama.chat(model='llama3',
                messages=[{'role':'system','content':SALES_WRITER_PROMPT},
                    {'role':'user','content':f'Expand this speech to at least 120 words: {speech}'}])
            speech = res3['message']['content']
            word_count = len(speech.split())
        except: pass

    return {'research_analysis': research, 'sales_speech': speech,
            'word_count': word_count, 'products_recommended': products}
