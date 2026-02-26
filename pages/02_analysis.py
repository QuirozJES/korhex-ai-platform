"""
02_analysis.py — Los 6 Elementos del Análisis de Cuenta
Propietario: Ingeniero 5 (UI)
"""
import streamlit as st

try:
    from modules.ui_theme import page_header, badge, no_data_state, get_analysis
except ImportError:
    st.error("⚠️ modules/ui_theme.py no encontrado.")
    st.stop()

st.set_page_config(page_title="Análisis · KORHEX.AI", page_icon="🔬", layout="wide")

page_header(
    title="🔬 Account Intelligence Analysis",
    subtitle="6 elementos de inteligencia B2B generados localmente por Llama 3 vía Ollama — sin envío de datos a la nube."
)

current = get_analysis()

if not current:
    no_data_state(
        msg="No hay análisis activo en esta sesión.",
        hint="← Ingresa una empresa en el sidebar de la página principal y presiona 'Execute Analysis'."
    )
    st.stop()

analysis  = current.get("analysis", {})
web_data  = current.get("web_data", {})
company   = current.get("company_name", "N/A")
industry  = current.get("web_data", {}).get("industry", "N/A")
years     = current.get("years_inactive", 0)
research  = analysis.get("research_analysis") or ""
audit_ok  = analysis.get("audit_passed", False)
audit_notes = analysis.get("audit_notes") or "Sin notas de auditoría."
tokens    = analysis.get("estimated_tokens", 0)
ms        = analysis.get("processing_ms", 0)

# ── Header de cuenta ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kx-card kx-card-accent" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div>
        <div style="font-size:1.2rem;font-weight:700;color:#FFF;">{company}</div>
        <div style="color:#6B7280;font-size:0.8rem;font-family:'Share Tech Mono',monospace;">
            {industry} &nbsp;|&nbsp; {years} año(s) inactivo
        </div>
    </div>
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;">
        {'<span class="kx-badge badge-green">✓ AUDIT PASSED</span>' if audit_ok else '<span class="kx-badge badge-red">⚠ AUDIT ISSUES</span>'}
        <span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;color:#6B7280;">
            {tokens:,} tokens &nbsp;|&nbsp; {ms:,}ms
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

if not audit_ok:
    st.warning(f"⚠️ **Auditoría:** {audit_notes}")

st.markdown("---")

# ── 6 Secciones de análisis ───────────────────────────────────────────────────
SECTIONS = [
    ("1. Company Snapshot & Strategy",  "strategy_background",  "🏢", "kx-card-accent"),
    ("2. Technology Environment",       "tech_environment",     "💻", "kx-card-blue"),
    ("3. IT Pain Points",               "pain_points",          "⚡", "kx-card-red"),
    ("4. Key Decision Makers",          "decision_makers",      "👤", "kx-card-yellow"),
    ("5. Financial Signals",            "financial_signals",    "💰", "kx-card-accent"),
    ("6. Competitive Context",          "competitive_context",  "🎯", "kx-card-blue"),
]

# Intentar parsear secciones del texto del agente
def extract_section(full_text: str, section_num: int) -> str:
    """Extrae una sección numerada del output del agente."""
    if not full_text:
        return ""
    lines = full_text.split("\n")
    capturing = False
    out = []
    for line in lines:
        if f"## {section_num}." in line or f"#{section_num}." in line:
            capturing = True
            continue
        if capturing:
            next_section = any(f"## {section_num+1}." in line or f"#{section_num+1}." in line
                               for _ in [None])
            if next_section or ("[OPENING" in line.upper()):
                break
            out.append(line)
    return "\n".join(out).strip()

for idx, (title, web_key, icon, card_class) in enumerate(SECTIONS, 1):
    section_text = extract_section(research, idx)
    raw_snippets = web_data.get(web_key, []) or []

    with st.expander(f"{icon} {title}", expanded=(idx <= 3)):
        if section_text:
            st.markdown(f"""
            <div class="kx-card {card_class}" style="margin-bottom:0.8rem;">
                <div class="kx-section-title">◈ Análisis del Agente IA</div>
                <div style="font-size:0.9rem;line-height:1.7;color:#C9D1D9;white-space:pre-wrap;">{section_text}</div>
            </div>
            """, unsafe_allow_html=True)
        elif raw_snippets:
            st.markdown(f'<div class="kx-section-title">◈ Fuentes Web Recopiladas</div>', unsafe_allow_html=True)
            for item in raw_snippets[:4]:
                snippet = item.get("snippet","") or item if isinstance(item, str) else str(item)
                source  = item.get("url","") if isinstance(item, dict) else ""
                st.markdown(f"""
                <div class="kx-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem;">
                    <div style="font-size:0.85rem;color:#C9D1D9;line-height:1.6;">{snippet}</div>
                    {f'<div style="font-size:0.7rem;color:#00B4FF;margin-top:0.3rem;font-family:monospace;">{source}</div>' if source else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="color:#6B7280;font-size:0.85rem;font-family:'Share Tech Mono',monospace;padding:1rem 0;">
                Sin datos disponibles para esta sección. El scraper no encontró información de '{web_key}'.
            </div>
            """, unsafe_allow_html=True)

# ── Notas de auditoría ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="kx-section-title">◈ Reporte de Auditoría del Compliance Agent</div>', unsafe_allow_html=True)
audit_color = "kx-card-accent" if audit_ok else "kx-card-red"
st.markdown(f"""
<div class="kx-card {audit_color}">
    <div style="display:flex;align-items:center;gap:0.8rem;">
        <div style="font-size:1.5rem;">{"✅" if audit_ok else "⚠️"}</div>
        <div>
            <div style="font-weight:700;color:#FFF;">
                {"Análisis verificado — sin alucinaciones detectadas" if audit_ok else "Se detectaron posibles imprecisiones"}
            </div>
            <div style="color:#C9D1D9;font-size:0.85rem;margin-top:0.3rem;">{audit_notes}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)