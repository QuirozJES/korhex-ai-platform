"""
04_speech.py — KORHEX.AI
Sales pitch verificado por Compliance Auditor. Con componentes y copy-ready.
Propietario: Inge 5
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from streamlit_app.ui_utils import inject_global_css, render_page_header, render_empty_state, priority_badge

st.set_page_config(page_title="Sales Speech | KORHEX.AI", page_icon="◉", layout="wide")
inject_global_css()
render_page_header(title="SALES SPEECH", subtitle="AI-generated · Compliance-audited · Ready to deliver", icon="◉")

data = st.session_state.get("current_analysis")
if not data:
    try:
        from streamlit_app.mock_modules import MOCK_ANALYSIS
        data = MOCK_ANALYSIS
        st.markdown('<div style="background:#F59E0B11;border:1px solid #F59E0B44;border-radius:4px;padding:0.5rem 1rem;font-family:Share Tech Mono,monospace;font-size:0.75rem;color:#F59E0B;margin-bottom:1.5rem;">⚡ MODO DEMO</div>', unsafe_allow_html=True)
    except ImportError:
        render_empty_state("Sin análisis activo."); st.stop()

company  = data.get("company_name", "—")
analysis = data.get("analysis", {})
speech   = analysis.get("sales_speech", "").strip()
wc       = analysis.get("word_count", 0)
passed   = analysis.get("audit_passed", False)
notes    = analysis.get("audit_notes", "")
priority = data.get("score", {}).get("priority", "MEDIUM")
ms       = analysis.get("processing_ms", 0)

audit_color = "#00FF9C" if passed else "#FF6B6B"
audit_icon  = "✓" if passed else "⚠"
audit_label = "COMPLIANCE AUDITOR: APPROVED" if passed else "COMPLIANCE AUDITOR: FLAGGED"
st.markdown(f"""
<div style="background:{audit_color}11;border:1px solid {audit_color}33;border-radius:4px;
            padding:0.7rem 1.2rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem;">
    <div style="font-size:1.5rem;">{audit_icon}</div>
    <div>
        <div style="font-family:Orbitron,monospace;font-size:0.7rem;letter-spacing:0.1em;color:{audit_color};margin-bottom:0.2rem;">{audit_label}</div>
        <div style="font-size:0.72rem;color:#6B7280;font-family:Share Tech Mono,monospace;">{notes}</div>
    </div>
    <div style="margin-left:auto;">{priority_badge(priority)}</div>
</div>
""", unsafe_allow_html=True)

m1,m2,m3,m4 = st.columns(4)
m1.metric("Account", company[:18]+"..." if len(company)>18 else company)
m2.metric("Word Count", wc, delta="✓ OK" if wc>=120 else "⚠ Short")
m3.metric("Processing", f"{ms:,} ms", delta="Local LLM")
m4.metric("Audit", "PASSED ✓" if passed else "FLAGGED ⚠")
st.divider()

COMPONENTS = [("[OPENING","OPENING HOOK","#00FF9C","Dato verificado de apertura"),("[CHALLENGE","CHALLENGE","#FF6B6B","Pain points de IT"),("[SOLUTION","SOLUTION","#00C8FF","Productos con ROI"),("[CTA","CALL TO ACTION","#F59E0B","Siguiente paso concreto")]

def extract_component(text, marker):
    if not text or marker not in text: return ""
    idx = text.index(marker); rest = text[idx:]
    markers = ["[OPENING","[CHALLENGE","[SOLUTION","[CTA"]
    end = len(rest)
    for m in markers:
        if m != marker and m in rest[1:]:
            end = min(end, rest.index(m,1))
    chunk = rest[:end].strip()
    lines = []; 
    for line in chunk.split("\n"):
        l = line.strip()
        if not l: continue
        if l.startswith("[") and any(l.startswith(m) for m in markers):
            l = l[l.index("]")+1:].strip() if "]" in l else l[l.index(":")+1:].strip() if ":" in l else ""
            if not l: continue
        lines.append(l)
    return "\n".join(lines).strip()

st.markdown('<div class="kx-section-title">▸ SPEECH COMPONENTS</div>', unsafe_allow_html=True)
found = False
for marker, label, color, desc in COMPONENTS:
    txt = extract_component(speech, marker)
    if not txt: continue
    found = True
    st.markdown(f"""
    <div class="kx-card" style="border-left-color:{color};margin-bottom:1rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:0.15em;color:{color};">{label}</span>
            <span style="font-size:0.65rem;color:#374151;font-family:Share Tech Mono,monospace;">{desc}</span>
        </div>
        <div style="font-family:Share Tech Mono,monospace;font-size:0.82rem;color:#E0E6F0;line-height:1.75;white-space:pre-wrap;">{txt}</div>
    </div>""", unsafe_allow_html=True)

if not found:
    st.markdown(f'<div class="kx-speech-block">{speech or "Sin discurso generado."}</div>', unsafe_allow_html=True)

st.divider()
st.markdown('<div class="kx-section-title">▸ FULL SPEECH (COPY-READY)</div>', unsafe_allow_html=True)
col_s, col_a = st.columns([3,1])
with col_s:
    final = speech or "Sin discurso generado."
    st.markdown(f'<div class="kx-speech-block">{final}</div>', unsafe_allow_html=True)
with col_a:
    st.text_area("Copiar:", value=final, height=220, key="copy_area", label_visibility="collapsed", help="Ctrl+A → Ctrl+C")
    st.caption("⬆ Selecciona todo y copia")
    st.markdown(f"""
    <div class="kx-terminal" style="font-size:0.72rem;margin-top:0.8rem;">
        <span class="prompt">STATUS:</span><br><br>
        Words : {wc}<br>
        Min   : {'✓ OK' if wc>=120 else '⚠ Low'}<br>
        Audit : {'✓ SAFE' if passed else '⚠ REVIEW'}<br>
        Time  : {ms:,}ms<br>
        Cloud : 0 calls
    </div>""", unsafe_allow_html=True)

with st.expander("⚡ Ajustes rápidos"):
    c1,c2 = st.columns(2)
    with c1:
        st.selectbox("Tono:", ["Consultivo","Ejecutivo","Técnico","Urgente"])
        st.selectbox("Longitud:", ["Estándar 120w","Breve 80w","Detallado 200w+"])
    with c2:
        st.text_input("Decision Maker:", placeholder="ej: Hiroshi Tanaka")
        st.selectbox("Tipo reunión:", ["Primera llamada","Demo técnica","Propuesta ejecutiva"])
    if st.button("🔄 Regenerar", use_container_width=True):
        st.info("Vuelve al panel principal y ejecuta un nuevo análisis con los parámetros deseados.")

st.divider()
st.markdown('<div style="text-align:center;font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#1F2937;letter-spacing:0.2em;">LLAMA 3 LOCAL // COMPLIANCE VERIFIED // ZERO HALLUCINATION POLICY</div>', unsafe_allow_html=True)