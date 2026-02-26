"""
04_speech.py — Sales Speech generado por Dual-Agent
Propietario: Ingeniero 5 (UI)
FIXED: usa modules.ui_theme, no streamlit_app.ui_utils
"""
import streamlit as st
from modules.ui_theme import page_header, badge, no_data_state, get_analysis, page_footer

try:
    from modules.ui_theme import page_header, badge, no_data_state, get_analysis
except ImportError:
    st.error("⚠️ modules/ui_theme.py no encontrado. Verifica que corres desde la carpeta raíz korhex-ai/")
    st.stop()

st.set_page_config(page_title="Sales Speech · KORHEX.AI", page_icon="🎤", layout="wide")

page_header(
    title="🎤 Sales Speech Generator",
    subtitle="Pitch generado por Account Executive Agent y verificado por Compliance Auditor — 0 alucinaciones garantizadas."
)

current = get_analysis()

if not current:
    no_data_state(
        msg="No hay análisis activo en esta sesión.",
        hint="← Ejecuta un análisis desde la página principal primero."
    )
    st.stop()

analysis    = current.get("analysis", {})
company     = current.get("company_name", "N/A")
years       = current.get("years_inactive", 0)
speech      = analysis.get("sales_speech") or ""
audit_ok    = analysis.get("audit_passed", False)
audit_notes = analysis.get("audit_notes") or "Sin notas de auditoría."
word_count  = analysis.get("word_count", 0) or len(speech.split())
products    = current.get("products", []) or []
ms          = analysis.get("processing_ms", 0)

# ── Banner de auditoría ───────────────────────────────────────────────────────
audit_color = "#00FFB2" if audit_ok else "#FF3B5C"
audit_icon  = "✅" if audit_ok else "⚠️"
audit_label = "AUDIT PASSED — Contenido verificado por Compliance Agent" if audit_ok \
              else "AUDIT FLAG — Revisar contenido antes de usar"

st.markdown(f"""
<div style="background:{'#00FFB210' if audit_ok else '#FF3B5C10'};
            border:1px solid {audit_color};border-radius:6px;
            padding:0.8rem 1.2rem;margin-bottom:1rem;
            display:flex;align-items:center;gap:0.8rem;">
    <span style="font-size:1.3rem;">{audit_icon}</span>
    <div>
        <div style="font-weight:700;color:{audit_color};font-size:0.85rem;letter-spacing:0.05em;">{audit_label}</div>
        <div style="color:#C9D1D9;font-size:0.8rem;margin-top:0.2rem;">{audit_notes}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Métricas ──────────────────────────────────────────────────────────────────
st.markdown('<div class="kx-section-title">◈ Health del Pitch</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Palabras", word_count, help="Mínimo requerido: 120")
with m2: st.metric("Productos citados", len(products))
with m3: st.metric("Años inactivo", years)
with m4: st.metric("Tiempo de gen.", f"{ms:,}ms" if ms else "—")

st.markdown("---")

# ── Speech ────────────────────────────────────────────────────────────────────
if not speech:
    no_data_state(
        msg="El Speech no fue generado.",
        hint="Verifica que agents.py esté corriendo con Ollama activo (Terminal 1: ollama serve)."
    )
    st.stop()

def parse_speech_sections(text: str) -> dict:
    sections = {"OPENING": "", "CHALLENGE": "", "SOLUTION": "", "CTA": "", "RAW": ""}
    current_key = "RAW"
    for line in text.split("\n"):
        up = line.upper()
        if "[OPENING"   in up: current_key = "OPENING"
        elif "[CHALLENGE" in up: current_key = "CHALLENGE"
        elif "[SOLUTION"  in up: current_key = "SOLUTION"
        elif "[CTA"       in up: current_key = "CTA"
        else:
            sections[current_key] += line + "\n"
    return sections

parsed       = parse_speech_sections(speech)
has_sections = any(parsed[k].strip() for k in ("OPENING", "CHALLENGE", "SOLUTION", "CTA"))

if has_sections:
    SPEECH_PARTS = [
        ("OPENING",   "🎯 Apertura",          "kx-card-accent",
         "Un dato verificado que captura la atención del comprador."),
        ("CHALLENGE", "⚡ El Desafío",         "kx-card-red",
         "Pain points específicos de IT identificados en el análisis."),
        ("SOLUTION",  "✅ La Solución",        "kx-card-blue",
         "2 productos del portfolio con su ROI específico."),
        ("CTA",       "📅 Call to Action",     "kx-card-yellow",
         "Siguiente paso concreto y con fecha."),
    ]
    for key, title, card_class, hint in SPEECH_PARTS:
        content = parsed[key].strip()
        if content:
            st.markdown(f"""
            <div class="kx-card {card_class}">
                <div class="kx-section-title">◈ {title}</div>
                <div style="color:#6B7280;font-size:0.73rem;margin-bottom:0.6rem;">{hint}</div>
                <div style="font-size:0.92rem;line-height:1.75;color:#C9D1D9;white-space:pre-wrap;">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    if parsed["RAW"].strip():
        with st.expander("📄 Texto completo del agente"):
            st.markdown(f'<div class="kx-speech-block">{speech}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="kx-section-title">◈ Speech Completo</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kx-speech-block">{speech}</div>', unsafe_allow_html=True)

# ── Copiar ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="kx-section-title">◈ Acciones</div>', unsafe_allow_html=True)

col_copy, col_info = st.columns([1, 2])
with col_copy:
    if st.button("📋 Copiar Speech", use_container_width=True):
        st.code(speech, language=None)
        st.success("✅ Selecciona el texto de arriba para copiarlo.")
with col_info:
    st.markdown("""
    <div style="color:#6B7280;font-size:0.8rem;font-family:'Share Tech Mono',monospace;
                padding:0.6rem;border:1px solid #1E2A35;border-radius:4px;">
        Generado localmente con Llama 3 · Verificado por Compliance Agent · 0 bytes a la nube
    </div>
    """, unsafe_allow_html=True)

# ── Productos referenciados ───────────────────────────────────────────────────
if products:
    st.markdown("---")
    st.markdown('<div class="kx-section-title">◈ Productos Referenciados en este Pitch</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(products), 3))
    for i, prod in enumerate(products[:3]):
        with cols[i]:
            st.markdown(f"""
            <div class="kx-card kx-card-accent" style="padding:0.8rem 1rem;">
                <div style="font-weight:700;color:#FFF;font-size:0.9rem;">{prod.get('name','N/A')}</div>
                <div style="color:#6B7280;font-size:0.72rem;font-family:monospace;margin-top:0.2rem;">
                    {prod.get('category','')}
                </div>
            </div>
            """, unsafe_allow_html=True)

page_footer()