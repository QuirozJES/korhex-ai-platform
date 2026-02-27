import os
from dotenv import load_dotenv
load_dotenv()  # Reads TAVILY_API_KEY (and other keys) from the .env file

import streamlit as st

# 1. SECURITY KEY LOADING
# This forces the system to read your .env file before initializing anything else

# Importaciones locales centralizadas para Pylance
from modules.database import (
    initialize_database, get_cached_account, save_account_cache,
    get_cached_analysis, save_analysis, save_lead_score
)
from modules.scraper import search_account, calculate_net_new_score
from modules.rag import get_relevant_products
from modules.agents import run_dual_agent_analysis
from modules.audit_logger import AuditLogger
from modules.ui_theme import page_header

# 2. Initialize the local database memory
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
    years_inactive = st.slider('Years since last purchase', 0, 10, 3)
    analyze_btn = st.button('Execute Analysis', type='primary', use_container_width=True)

if analyze_btn:
    if not company_name or not company_url:
        st.warning('Please enter both Company Name and URL.')
    else:
        # Save values to session_state BEFORE any operations
        st.session_state['company_name']    = company_name
        st.session_state['company_url']     = company_url
        st.session_state['industry']        = industry
        st.session_state['years_inactive']  = years_inactive

        prog = st.progress(0, text='Checking local cache...')

        # 3. Look up the account in local database memory
        web_data = get_cached_account(company_name, company_url, industry)
        if web_data:
            st.toast('Loaded from local cache!', icon='⚡')
        else:
            # If not found, trigger the Tavily web scraper
            prog.progress(20, text='Searching public information...')
            with AuditLogger('SCRAPE', company_name) as log:
                web_data = search_account(company_name, company_url, industry)
                log.set_tokens(500)
            save_account_cache(company_name, company_url, industry, web_data)

        prog.progress(40, text='Matching portfolio solutions...')
        products = get_relevant_products(industry, web_data)

        # 4. Check if AI has already completed this analysis before
        cached = get_cached_analysis(company_name, company_url, industry, years_inactive)
        if cached:
            analysis = cached
            st.toast('Analysis loaded from memory!', icon='🧠')
        else:
            # If not, execute the dual-agent workflow on the local GPU
            prog.progress(60, text='Running Dual-Agent Analysis...')
            with AuditLogger('DUAL_AGENT', company_name) as log:
                analysis = run_dual_agent_analysis(company_name, web_data, products, years_inactive)
                log.set_tokens(analysis.get('estimated_tokens', 1500))

            save_analysis(
                company_name, company_url, industry, years_inactive,
                analysis['research_analysis'], analysis['sales_speech'],
                analysis['word_count'], analysis['audit_passed'], analysis['audit_notes']
            )

        prog.progress(90, text='Saving to local database...')
        score = calculate_net_new_score(years_inactive, web_data)
        save_lead_score(
            company_name, company_url, industry,
            score['total_score'], score['priority'], years_inactive, score['is_net_new']
        )

        # Persist the consolidated result into the current session
        st.session_state['current_analysis'] = {
            'company_url':    company_url,
            'industry':       industry,
            'company_name': company_name, 'web_data': web_data,
            'analysis': analysis, 'products': products,
            'score': score, 'years_inactive': years_inactive
        }

        prog.progress(100, text='Complete!')
        st.success('Analysis complete. Go to the tabs above.')
else:
    st.info('Enter a company URL and name in the sidebar to begin.')