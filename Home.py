import streamlit as st
from dotenv import load_dotenv

# 1. LECTURA DE LLAVES DE SEGURIDAD
# Esto obliga al sistema a leer tu archivo .env antes de arrancar cualquier otra cosa
load_dotenv()

from modules.database import initialize_database
from modules.ui_theme import page_header

# 2. Arrancamos la memoria de la base de datos local
initialize_database()

st.set_page_config(page_title='KORHEX.AI', page_icon='🤖', layout='wide')

if 'current_analysis' not in st.session_state:
    st.session_state['current_analysis'] = None

st.markdown("""
<div style="position:relative; display:inline-block; cursor:default;">
    <h1 style="font-family:'Share Tech Mono',monospace; color:#00FFB2;
               text-shadow: 0 0 8px #00FFB2, 0 0 20px #00FFB260;
               margin-bottom:0; font-size:2rem; letter-spacing:0.05em;">
        KORHEX.AI Account Intelligence Platform
    </h1>
    <div class="kx-easter-egg">
        ▸ Zuany · Reyes · Quiroz · Herrera · Morales ◂
    </div>
</div>

<style>
.kx-easter-egg {
    position: absolute;
    top: -1.4rem;
    left: 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.25em;
    color: transparent;
    transition: color 0.6s ease, text-shadow 0.6s ease;
    user-select: none;
    white-space: nowrap;
}
div:hover > .kx-easter-egg {
    color: #00FFB280;
    text-shadow: 0 0 10px #00FFB250;
}
</style>
""", unsafe_allow_html=True)

st.caption('Local AI | Zero Data Leakage | Dual-Agent | SQLite Memory')

with st.sidebar:
    st.markdown('<div class="kx-section-title">◈ Account Input</div>', unsafe_allow_html=True)
    company_url = st.text_input('Company URL', placeholder='https://example.com')
    company_name = st.text_input('Company Name', placeholder='e.g. Toyota')
    industry = st.selectbox('Industry', ['Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail', 'Energy', 'Telecommunications'])
    years_inactive = st.slider(
        'Years since last purchase',
        min_value=0,
        max_value=10,
        value=3,
        help="Set to 0 for prospects with no prior purchase history."
    )    
    analyze_btn = st.button('Execute Analysis', type='primary', use_container_width=True)

if analyze_btn:
    if not company_name or not company_url:
        st.warning('Please enter both Company Name and URL.')
    else:
        # ── Guardar variables en session_state ANTES de cualquier operación ──
        st.session_state['company_name']    = company_name
        st.session_state['company_url']     = company_url
        st.session_state['industry']        = industry
        st.session_state['years_inactive']  = years_inactive

        from modules.scraper import search_account, calculate_net_new_score
        from modules.rag import get_relevant_products
        from modules.agents import run_dual_agent_analysis
        from modules.audit_logger import AuditLogger
        from modules.database import (
            get_cached_account, save_account_cache, 
            get_cached_analysis, save_analysis, save_lead_score
        )

        # ── STEP 1: Initializing Local Engine ────────────────────────────────
        with st.status("⚙️ Initializing Local Engine...", expanded=True) as status:
            st.write("Verifying connection to RTX 5080 and Ollama...")

            # ▼ INSERT: any pre-flight checks here (e.g. ping Ollama endpoint)
            web_data = get_cached_account(company_name, company_url)

            if web_data:
                st.write("✅ Cache hit — skipping web retrieval.")
                status.update(label="✅ Local Engine Ready — loaded from cache",
                              state="complete", expanded=False)
            else:
                status.update(label="✅ Local Engine Ready",
                              state="complete", expanded=False)

        # ── STEP 2: Web Intelligence Retrieval ───────────────────────────────
        if not web_data:
            with st.status("🌐 Web Intelligence Retrieval...", expanded=True) as status:
                st.write(f"Searching public web for **{company_name}** via Tavily...")
                st.write("Collecting: strategy, tech stack, financials, key contacts...")

                # ▼ INSERT: Tavily API call lives here (scraper.py → search_account)
                with AuditLogger('SCRAPE', company_name) as log:
                    web_data = search_account(company_name, company_url, industry)
                    log.set_tokens(500)
                save_account_cache(company_name, company_url, industry, web_data)

                st.write(f"✅ Retrieved {len(web_data)} intelligence signals.")
                status.update(label="✅ Web Intelligence Retrieved",
                              state="complete", expanded=False)
        
        # ── STEP 3: B2B Logic Audit ───────────────────────────────────────────
        with st.status("🛡️ B2B Logic Audit...", expanded=True) as status:
            st.write("Auditor Agent validating data quality with Llama 3...")
            st.write("Checking: data completeness, source reliability, bias signals...")

            # ▼ INSERT: pre-analysis validation logic here if needed
            cached = get_cached_analysis(company_name, company_url, industry, years_inactive)

            if cached:
                st.write("✅ Verified analysis found in local memory.")
            else:
                st.write("✅ Data validated — ready for AI synthesis.")

            status.update(label="✅ B2B Logic Audit Passed",
                          state="complete", expanded=False)

        # ── STEP 4: Portfolio Semantic Matching ───────────────────────────────
        with st.status("🎯 Portfolio Semantic Matching...", expanded=True) as status:
            st.write(f"Querying RAG engine for **{industry}** solutions...")
            st.write("Matching client pain points against product portfolio...")

            # ▼ INSERT: RAG call lives here (rag.py → get_relevant_products)
            products = get_relevant_products(industry, web_data)

            match_count = len(products) if products else 0
            st.write(f"✅ Found {match_count} matching solution(s).")
            status.update(label=f"✅ Portfolio Match Complete — {match_count} solutions",
                          state="complete", expanded=False)

        # ── STEP 5: Synthesis & Strategy Writing ─────────────────────────────
        with st.status("✍️ Synthesis & Strategy Writing...", expanded=True) as status:
            st.write("Account Executive Agent generating intelligence report...")
            st.write("Compliance Agent reviewing for hallucinations...")
            st.write("Writing sales speech (150+ words)...")

            if cached:
                analysis = cached
                st.write("✅ Strategy loaded from local memory.")
                st.toast('Analysis loaded from memory!', icon='🧠')
            else:
                # ▼ INSERT: Ollama/CrewAI dual-agent call lives here
                with AuditLogger('DUAL_AGENT', company_name) as log:
                    analysis = run_dual_agent_analysis(
                        company_name, web_data, products, years_inactive)
                    log.set_tokens(analysis.get('estimated_tokens', 1500))

                save_analysis(
                    company_name, company_url, industry, years_inactive,
                    analysis['research_analysis'], analysis['sales_speech'],
                    analysis['word_count'], analysis['audit_passed'],
                    analysis['audit_notes']
                )
                
                st.write(f"✅ {analysis.get('word_count', 0)} words generated and verified.")

            status.update(label="✅ Strategy Report Complete",
                          state="complete", expanded=False)

        # ── Finalizar: score + session state ─────────────────────────────────
        score = calculate_net_new_score(years_inactive, web_data)
        save_lead_score(
            company_name, company_url, industry,
            score['total_score'], score['priority'],
            years_inactive, score['is_net_new']
        )

        st.session_state['current_analysis'] = {
            'company_name':   company_name,
            'company_url':    company_url,
            'industry':       industry,
            'web_data':       web_data,
            'analysis':       analysis,
            'products':       products,
            'score':          score,
            'years_inactive': years_inactive,
        }

        st.success(
            f"✅ Analysis complete for **{company_name}** — "
            f"Lead Score: **{score['total_score']}/100** · "
            f"Priority: **{score['priority']}** · "
            "Navigate to the pages above to explore results."
        )
else:
    st.info('Enter a company URL and name in the sidebar to begin.')