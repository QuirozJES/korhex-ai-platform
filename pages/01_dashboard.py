"""
01_dashboard.py — Top 5 Leads + Lead Score Dashboard
Propietario: Ingeniero 5 (UI)
"""
import streamlit as st
from modules.ui_theme import page_header, badge, no_data_state, get_analysis, page_footer

try:
    from modules.ui_theme import page_header, badge, score_bar, priority_badge, no_data_state, get_analysis
except ImportError:
    st.error("⚠️ modules/ui_theme.py no encontrado. Verifica la estructura de carpetas.")
    st.stop()

try:
    from modules.database import get_top5
except ImportError:
    def get_top5(): return []

st.set_page_config(page_title="Dashboard · KORHEX.AI", page_icon="📊", layout="wide")

page_header(
    title="📊 Lead Intelligence Dashboard",
    subtitle="Top 5 cuentas rankeadas por algoritmo de lead score — actualizado desde SQLite local."
)

# ── Cargar datos defensivamente ───────────────────────────────────────────────
top5 = []
try:
    top5 = get_top5() or []
except Exception as e:
    st.warning(f"No se pudo cargar el ranking: {e}")

current = get_analysis()

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="kx-section-title">◈ Health del Pipeline</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Cuentas Analizadas", len(top5))
with c2:
    high = sum(1 for r in top5 if (r.get("priority") or "").upper() in ("HIGH","CRITICAL"))
    st.metric("Prioridad Alta 🔴", high)
with c3:
    net_new = sum(1 for r in top5 if r.get("is_net_new"))
    st.metric("Net New Logos ✨", net_new)
with c4:
    if current:
        score_val = current.get("score", {}).get("total_score", "—")
        st.metric("Cuenta Activa", f"{score_val}/100")
    else:
        st.metric("Cuenta Activa", "—")

st.markdown("---")
st.markdown('<div class="kx-section-title">◈ Ranking de Oportunidades</div>', unsafe_allow_html=True)

# ── Ranking ───────────────────────────────────────────────────────────────────
if not top5:
    no_data_state(
        msg="Aún no hay cuentas analizadas.",
        hint="← Ejecuta un análisis desde la página principal para poblar este ranking."
    )
else:
    rank_colors = {1:"#00FFB2", 2:"#00B4FF", 3:"#FFD600", 4:"#E0E0E0", 5:"#6B7280"}
    for rank, row in enumerate(top5, 1):
        company  = row.get("company_name", "N/A")
        url      = row.get("company_url") or "#"
        industry = row.get("industry", "N/A")
        score    = int(row.get("lead_score") or 0)
        priority = row.get("priority") or "LOW"
        years    = row.get("years_inactive") or 0
        net_new  = bool(row.get("is_net_new"))
        rc       = rank_colors.get(rank, "#6B7280")

        net_new_html = badge("NET NEW", "red") if net_new else badge("REACTIVACIÓN", "blue")

        st.markdown(f"""
        <div class="kx-card kx-card-accent" style="display:flex;align-items:flex-start;gap:1.2rem;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:2rem;
                        font-weight:900;color:{rc};min-width:2.2rem;line-height:1.1;">#{rank}</div>
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.35rem;">
                    <span style="font-size:1.12rem;font-weight:800;color:#FFF;letter-spacing:0.02em;">{company}</span>
                    {priority_badge(priority)} {net_new_html}
                </div>
                <div style="color:#6B7280;font-size:0.78rem;font-family:'Share Tech Mono',monospace;margin-bottom:0.4rem;">
                    {industry} &nbsp;|&nbsp;
                    <a href="{url}" target="_blank" style="color:#00B4FF;text-decoration:none;">{url}</a>
                    &nbsp;|&nbsp; {years} año(s) inactivo
                </div>
                {score_bar(score)}
            </div>
            <div style="text-align:right;min-width:4rem;">
                <div style="font-family:'Share Tech Mono',monospace;font-size:1.5rem;
                            font-weight:700;color:#00FFB2;">{score}</div>
                <div style="font-size:0.65rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.1em;">SCORE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Cuenta activa en sesión ───────────────────────────────────────────────────
if current:
    st.markdown("---")
    st.markdown('<div class="kx-section-title">◈ Cuenta Activa en Sesión</div>', unsafe_allow_html=True)
    score_data = current.get("score", {})
    total      = int(score_data.get("total_score", 0))
    priority   = score_data.get("priority", "N/A")
    years      = current.get("years_inactive", 0)
    net_new    = score_data.get("is_net_new", False)

    ca, cb, cc = st.columns(3)
    with ca:
        st.markdown(f"""
        <div class="kx-card kx-card-accent">
            <div style="color:#6B7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Empresa</div>
            <div style="font-size:1.1rem;font-weight:700;color:#FFF;margin-top:0.2rem;">
                {current.get('company_name','N/A')}
            </div>
            <div style="color:#6B7280;font-size:0.78rem;margin-top:0.3rem;">
                {current.get('web_data',{}).get('industry','N/A')}
            </div>
        </div>""", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""
        <div class="kx-card kx-card-blue">
            <div style="color:#6B7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Lead Score</div>
            <div style="font-size:1.8rem;font-weight:900;color:#00FFB2;font-family:'Share Tech Mono',monospace;">{total}/100</div>
            {score_bar(total)}
        </div>""", unsafe_allow_html=True)
    with cc:
        nn_html = badge("NET NEW LOGO", "red") if net_new else badge("REACTIVACIÓN", "blue")
        st.markdown(f"""
        <div class="kx-card kx-card-yellow">
            <div style="color:#6B7280;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;">Clasificación</div>
            <div style="margin-top:0.4rem;">{priority_badge(priority)} &nbsp; {nn_html}</div>
            <div style="color:#6B7280;font-size:0.78rem;margin-top:0.5rem;">{years} año(s) sin compra</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("🔍 Ver desglose del score"):
        factors = score_data.get("factors", {})
        if factors:
            for k, v in factors.items():
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid #1E2A35;">
                    <span style="color:#C9D1D9;font-size:0.85rem;">{k.replace('_',' ').title()}</span>
                    <span style="font-family:'Share Tech Mono',monospace;color:#00FFB2;">{v}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("El módulo scraper.py debe retornar un dict 'factors' dentro del score para ver el desglose.")

page_footer()