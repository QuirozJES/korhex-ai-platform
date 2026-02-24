import streamlit as st

# 1. Configuración de la página (El layout 'wide' aprovecha toda la pantalla)
st.set_page_config(page_title='KORHEX.AI | Dashboard', page_icon='🤖', layout='wide', initial_sidebar_state='expanded')

# 2. Inyección de CSS (La magia del diseño para imitar el mockup)
st.markdown("""
<style>
    /* Ocultar elementos por defecto de Streamlit para un look más limpio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo para el botón principal en la barra lateral (Azul neón) */
    .stButton > button {
        width: 100%;
        background-color: #0F62FE; 
        color: white;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0353e9;
        border-color: #0353e9;
    }
    
    /* Estilo para las tarjetas de métricas (KPIs) */
    div[data-testid="metric-container"] {
        background-color: #1a1c23;
        border: 1px solid #2e3039;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. BARRA LATERAL (Sidebar - Input Area)
with st.sidebar:
    st.markdown("## 🤖 KORHEX.AI")
    st.caption("ACCOUNT INTELLIGENCE")
    st.markdown("---")
    
    st.caption("ANALYSIS PARAMETERS")
    url_input = st.text_input("Company URL", placeholder="https://acme-corp.com")
    name_input = st.text_input("Company Name", placeholder="Acme Corporation")
    industry_input = st.selectbox("Industry", ["Technology", "Finance", "Healthcare", "Manufacturing"])
    years_slider = st.slider("Years Since Last Purchase", 0, 10, 3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón principal
    if st.button("⚡ Execute AI Analysis"):
        st.toast("Iniciando análisis de agentes...", icon="🤖")
        
    st.markdown("---")
    st.caption("🔒 **Zero Data Leakage Protocol**\n\nAll analysis runs in an isolated sandbox. No data leaves your environment.")

# 4. ÁREA PRINCIPAL (Main Dashboard)
st.title("Intelligence Dashboard ⚡")

# Fila de Métricas (KPIs) usando st.columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="AI LEAD SCORE", value="87", delta="+12.4% vs. industry avg")
    
with col2:
    st.metric(label="ESTIMATED ROI", value="$2.4M", delta="+340% projected annual")
    
with col3:
    st.metric(label="PROCESSING TIME SAVED", value="96hrs", delta="-28% vs. manual analysis", delta_color="inverse")

st.markdown("---")

# Resumen Ejecutivo
st.subheader("🧠 Executive Summary")
st.info("""
**Acme Corporation** is a mid-market SaaS enterprise headquartered in San Francisco, specializing in cloud-based supply chain optimization. The company has demonstrated **32% YoY revenue growth** and recently closed a Series C funding round of $85M.

Key decision-makers include **Sarah Chen (CTO)** and **Michael Torres (VP of Engineering)**, both of whom have publicly discussed their need for enhanced data pipeline infrastructure. 

Competitive analysis reveals Acme is evaluating alternatives to their current provider. Their contract renewal window opens in **Q3 2026**, creating a time-sensitive engagement window for our solutions team.
""")

# Noticias Recientes (Usando st.expander)
with st.expander("📰 Recent News (4 items)", expanded=True):
    st.markdown("""
    * 🟢 **Acme Corp Closes $85M Series C Led by Sequoia Capital** - *TechCrunch (Feb 12, 2026)*
    * 🟢 **Acme Expands Engineering Team by 40% in Q1** - *LinkedIn (Jan 28, 2026)*
    * 🔴 **Supply Chain Disruptions Impact Acme's Client Retention** - *Bloomberg (Jan 15, 2026)*
    * 🟢 **Acme Announces Partnership with AWS for Cloud Migration** - *PR Newswire (Dec 20, 2025)*
    """)