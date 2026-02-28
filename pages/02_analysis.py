"""
02_analysis.py — The 6 Elements of Account Analysis (REMASTERED)
Owner: Engineer 5 (UI)
"""
import time
import streamlit as st
import re
import html
from modules.ui_theme import page_header, badge, no_data_state, get_analysis, page_footer

# 1. Función de limpieza "Escudo" para evitar títulos gigantes y basura de Markdown
def clean_ai_text(text):
    if not text:
        return ""
    # Eliminamos símbolos de Markdown (#) al inicio de las líneas para evitar saltos de tamaño
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Limpiamos asteriscos triples o dobles si son excesivos
    text = text.replace('***', '**')
    # Escapamos HTML básico para evitar que caracteres especiales rompan el diseño
    return html.escape(text).strip()

st.set_page_config(page_title="Analysis · KORHEX.AI", page_icon="🔬", layout="wide")

# 2. Inyección de CSS para forzar el ancho total y el estilo de las tarjetas
st.markdown("""
    <style>
    /* Eliminar márgenes laterales de Streamlit para llegar al borde derecho */
    .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 1rem !important;
    }
    
    /* Estilo para las tarjetas de análisis de ancho total */
    .kx-analysis-card {
        width: 100% !important;
        background: rgba(10, 20, 28, 0.4);
        border: 1px solid rgba(0, 255, 178, 0.15);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-sizing: border-box;
        transition: all 0.3s ease;
    }
    
    .kx-analysis-card:hover {
        border-color: rgba(0, 255, 178, 0.5);
        box-shadow: 0 0 15px rgba(0, 255, 178, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

page_header(
    title="🔬 Account Intelligence Analysis",
    subtitle="6 B2B intelligence elements generated locally by Llama 3 via Ollama — zero data sent to the cloud."
)

current = get_analysis()

if not current:
    no_data_state(
        msg="No active analysis in this session.",
        hint="← Enter a company in the main page sidebar and press 'Execute Analysis'."
    )
    st.stop()

analysis  = current.get("analysis", {})
web_data  = current.get("web_data", {})
company   = current.get("company_name", "N/A")
industry  = current.get("web_data", {}).get("industry", "N/A")
years     = current.get("years_inactive", 0)
research  = analysis.get("research_analysis") or ""
audit_ok  = analysis.get("audit_passed", False)
audit_notes = analysis.get("audit_notes") or "No audit notes available."
tokens    = analysis.get("estimated_tokens", 0)
ms        = analysis.get("processing_ms", 0)

# ── Account header (Full Width) ──────────────────────────────────────────────
st.markdown(f"""
<div class="kx-card kx-card-accent" style="width:100%; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom: 2rem;">
    <div>
        <div style="font-size:1.3rem; font-weight:800; color:#00FFB2; text-shadow: 0 0 10px rgba(0,255,178,0.3);">{company}</div>
        <div style="color:#6B7280; font-size:0.85rem; font-family:'Share Tech Mono',monospace;">
            {industry} &nbsp;|&nbsp; {years} yr(s) inactive
        </div>
    </div>
    <div style="display:flex; gap:1rem; align-items:center;">
        {'<span class="kx-badge badge-green">✓ AUDIT PASSED</span>' if audit_ok else '<span class="kx-badge badge-red">⚠ AUDIT ISSUES</span>'}
        <span style="font-family:\'Share Tech Mono\',monospace; font-size:0.8rem; color:#6B7280;">
            {tokens:,} tokens &nbsp;|&nbsp; {ms:,}ms
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="kx-section-title" style="margin-bottom:1rem;">◈ 6 Strategic Intelligence Blocks</div>', unsafe_allow_html=True)

# ── 6 analysis sections ───────────────────────────────────────────────────────
SECTIONS = [
    ("1. Company Snapshot & Strategy",  "strategy_background",  "🏢", "kx-card-accent"),
    ("2. Technology Environment",       "tech_environment",     "💻", "kx-card-blue"),
    ("3. IT Pain Points",               "pain_points",          "⚡", "kx-card-red"),
    ("4. Key Decision Makers",          "decision_makers",      "👤", "kx-card-yellow"),
    ("5. Financial Signals",            "financial_signals",    "💰", "kx-card-accent"),
    ("6. Competitive Context",          "competitive_context",  "🎯", "kx-card-blue"),
]

def extract_section(full_text: str, section_num: int) -> str:
    """Extrae secciones numeradas del output del agente."""
    if not full_text: return ""
    lines = full_text.split("\n")
    capturing = False
    out = []
    for line in lines:
        if f"{section_num}." in line and (line.strip().startswith("#") or line.strip()[0].isdigit()):
            capturing = True
            continue
        if capturing:
            if re.match(r'^(#+\s*)?' + str(section_num + 1) + r'\.', line.strip()):
                break
            out.append(line)
    return "\n".join(out).strip()

# Renderizado de Bloques
for idx, (title, web_key, icon, card_class) in enumerate(SECTIONS, 1):
    section_text = extract_section(research, idx)
    raw_snippets = web_data.get(web_key, []) or []

    # Usamos el contenedor principal para asegurar ancho total
    with st.container():
        st.markdown(f'<div style="margin-top: 1.5rem; margin-bottom: 0.5rem; font-weight: 700; color: #FFF; font-size: 1.1rem;">{icon} {title}</div>', unsafe_allow_html=True)
        
        if section_text:
            # Limpiamos el texto antes de renderizar
            clean_content = clean_ai_text(section_text)
            
            st.markdown(f"""
            <div class="kx-analysis-card">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #00FFB2; margin-bottom: 0.8rem; letter-spacing: 0.1rem;">◈ AI AGENT INSIGHT</div>
                <div style="font-size: 0.95rem; line-height: 1.8; color: #C9D1D9;">
                    {clean_content}
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif raw_snippets:
            for item in raw_snippets[:3]:
                snippet = item.get("snippet") or item.get("title") or str(item)
                source = item.get("url") or ""
                
                st.markdown(f"""
                <div class="kx-analysis-card" style="border-left: 2px solid #58A6FF; background: rgba(88, 166, 255, 0.05);">
                    <div style="font-size:0.9rem; color:#C9D1D9; line-height:1.6;">{clean_ai_text(snippet)}</div>
                    {f'<div style="font-size:0.75rem; color:#58A6FF; margin-top:0.6rem; font-family:monospace;">🔗 {source[:80]}...</div>' if source else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#4B5563; font-size:0.85rem; padding: 1rem;">No real-time data found for this segment.</div>', unsafe_allow_html=True)

# ── Audit notes footer ────────────────────────────────────────────────────────
if not audit_ok:
    st.markdown(f'<div style="color:#6B7280; font-family:monospace; font-size:0.75rem; padding:1rem; border-top:1px solid #1F2937; margin-top:2rem;">⚠ COMPLIANCE AUDIT: {audit_notes}</div>', unsafe_allow_html=True)

page_footer()