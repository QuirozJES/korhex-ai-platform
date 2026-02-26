"""
03_recommendations.py — KORHEX.AI
Portfolio de productos recomendados por RAG, con fit score y pitch de ROI.
Propietario: Inge 5
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from streamlit_app.ui_utils import (
    inject_global_css, render_page_header,
    render_empty_state, render_score_bar
)

st.set_page_config(page_title="Recommendations | KORHEX.AI", page_icon="◇", layout="wide")
inject_global_css()
render_page_header(
    title="SOLUTION RECOMMENDATIONS",
    subtitle="RAG-powered portfolio matching · Local vector search · No cloud",
    icon="◇",
)

data = st.session_state.get("current_analysis")
if not data:
    try:
        from streamlit_app.mock_modules import MOCK_ANALYSIS
        data = MOCK_ANALYSIS
        st.markdown('<div style="background:#F59E0B11;border:1px solid #F59E0B44;border-radius:4px;padding:0.5rem 1rem;font-family:Share Tech Mono,monospace;font-size:0.75rem;color:#F59E0B;margin-bottom:1.5rem;">⚡ MODO DEMO</div>', unsafe_allow_html=True)
    except ImportError:
        render_empty_state("Sin análisis activo.", "Ejecuta un análisis desde el panel principal.")
        st.stop()

company   = data.get("company_name", "—")
analysis  = data.get("analysis", {})
products  = analysis.get("products_recommended") or data.get("products", [])
industry  = data.get("web_data", {}).get("industry", "—")

st.markdown(f"""
<div style="background:#0D1117;border:1px solid #1F2937;border-radius:4px;
            padding:1rem 1.4rem;margin-bottom:1.5rem;
            display:flex;align-items:center;justify-content:space-between;">
    <div>
        <div style="font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:0.2em;color:#6B7280;margin-bottom:0.3rem;">TARGET ACCOUNT</div>
        <div style="font-family:Orbitron,monospace;font-size:1rem;color:#E0E6F0;">{company}</div>
        <div style="font-size:0.72rem;color:#6B7280;font-family:Share Tech Mono,monospace;">{industry}</div>
    </div>
    <div style="text-align:right;">
        <div style="font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:0.2em;color:#6B7280;margin-bottom:0.3rem;">SOLUTIONS MATCHED</div>
        <div style="font-family:Orbitron,monospace;font-size:1.8rem;color:#00FF9C;">{len(products)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not products:
    render_empty_state("No se encontraron productos.", "Verifica data/portfolio.json y rag.py.")
else:
    st.markdown('<div class="kx-section-title">▸ MATCHED SOLUTIONS</div>', unsafe_allow_html=True)
    sorted_products = sorted(products, key=lambda p: p.get("fit_score", 0), reverse=True)
    cols = st.columns(min(3, len(sorted_products)))
    for i, product in enumerate(sorted_products):
        col = cols[i % 3]
        name      = product.get("name", "—")
        category  = product.get("category", "—")
        roi_pitch = product.get("roi_pitch", "Sin descripción.")
        fit_score = product.get("fit_score", 0)
        if fit_score >= 80:   badge_cls, bar_color = "kx-badge-green", "#00FF9C"
        elif fit_score >= 60: badge_cls, bar_color = "kx-badge-yellow", "#F59E0B"
        else:                 badge_cls, bar_color = "kx-badge-blue", "#00C8FF"
        with col:
            st.markdown(f"""
            <div class="kx-product-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
                    <div class="kx-product-name">{name}</div>
                    <span class="kx-badge {badge_cls}">{fit_score}% FIT</span>
                </div>
                <div class="kx-product-cat">◈ {category}</div>
                <div class="kx-product-roi">{roi_pitch}</div>
                <div style="margin-top:0.8rem;">
                    <div style="font-size:0.6rem;color:#6B7280;font-family:Share Tech Mono,monospace;margin-bottom:3px;">FIT SCORE</div>
                    <div class="kx-score-bar-wrap"><div class="kx-score-bar" style="width:{fit_score}%;background:{bar_color};"></div></div>
                </div>
            </div><br>
            """, unsafe_allow_html=True)

    import pandas as pd
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="kx-section-title">▸ COMPARISON TABLE</div>', unsafe_allow_html=True)
    rows = [{"Solution": p.get("name","—"), "Category": p.get("category","—"), "Fit Score": f"{p.get('fit_score',0)}%", "ROI Pitch": p.get("roi_pitch","—")[:80]} for p in sorted_products]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    top = sorted_products[0] if sorted_products else {}
    st.markdown(f"""
    <div class="kx-terminal" style="margin-top:1rem;">
        <span class="prompt">$ </span>korhex --strategy "{company}"<br><br>
        RECOMMENDED ORDER:<br>
        {''.join(f'  {i+1}. [{p.get("fit_score",0)}%] {p.get("name","—")}<br>' for i, p in enumerate(sorted_products))}
        <br>OPENING WITH : {top.get("name","—")}<br>
        ANCHOR ROI   : {top.get("roi_pitch","—")[:60]}...
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown('<div style="text-align:center;font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#1F2937;letter-spacing:0.2em;">RAG MATCHING // LOCAL VECTORS // 0 EXTERNAL API CALLS</div>', unsafe_allow_html=True)