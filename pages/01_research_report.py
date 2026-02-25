import streamlit as st

st.set_page_config(page_title="Research Report", page_icon="🔍", layout="wide")

# Verificamos si hay una sesión activa
if not st.session_state.get('current_analysis'):
    st.warning("⚠️ No hay datos activos. Realiza un análisis en la página principal primero.")
    st.stop()

data = st.session_state['current_analysis']
name = data.get('company_name', 'Unknown Company')
web = data.get('web_data', {})
analysis = data.get('analysis', {})
score = data.get('score', {})

st.title(f"🔍 Deep Research: {name}")

# --- Sección de Lead Scoring ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Lead Score", f"{score.get('total_score', 0)}/100")
with c2:
    # Usamos .get() con un valor por defecto para evitar el KeyError
    st.metric("Priority", score.get('priority', 'N/A'))
with c3:
    status = "NET NEW" if score.get('is_net_new') else "EXISTING"
    st.metric("Status", status)

st.divider()

# --- Información del Scraper ---
st.subheader("🌐 Public Information & Intelligence")
col_info, col_desc = st.columns([1, 2])

with col_info:
    st.write(f"**Industry:** {web.get('industry', 'N/A')}")
    # AQUÍ ESTÁ EL TRUCO: Si no encuentra 'url', pone 'N/A' en lugar de romperse
    url_display = web.get('url') or data.get('company_url', 'N/A')
    st.write(f"**URL:** {url_display}")

with col_desc:
    st.info(f"**Company Summary:**\n\n{web.get('summary', 'No summary available.')}")

st.divider()

# --- Análisis de la IA ---
st.subheader("🤖 AI Technical Analysis (Local)")
# Si no hay análisis, ponemos un mensaje amigable
st.markdown(analysis.get('research_analysis', 'No detailed analysis found in database.'))