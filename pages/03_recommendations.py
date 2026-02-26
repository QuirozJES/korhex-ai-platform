"""
03_recommendations.py — Portfolio de Productos Recomendados (RAG)
Propietario: Ingeniero 5 (UI)
FIXED: usa modules.ui_theme, no streamlit_app.ui_utils
"""
import streamlit as st
from modules.ui_theme import page_header, badge, no_data_state, get_analysis, page_footer

try:
    from modules.ui_theme import page_header, badge, no_data_state, score_bar, get_analysis
except ImportError:
    st.error("⚠️ modules/ui_theme.py no encontrado. Verifica que corres desde la carpeta raíz korhex-ai/")
    st.stop()

st.set_page_config(page_title="Recomendaciones · KORHEX.AI", page_icon="🎯", layout="wide")

page_header(
    title="🎯 Recomendaciones de Portfolio",
    subtitle="Productos seleccionados por RAG local — coincidencia semántica contra portfolio.json sin APIs externas."
)

current = get_analysis()

if not current:
    no_data_state(
        msg="No hay análisis activo en esta sesión.",
        hint="← Ejecuta un análisis desde la página principal primero."
    )
    st.stop()

products  = current.get("products", []) or []
company   = current.get("company_name", "N/A")
industry  = current.get("web_data", {}).get("industry", "N/A")
web_data  = current.get("web_data", {})

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kx-card kx-card-accent" style="display:flex;justify-content:space-between;align-items:center;">
    <div>
        <div style="font-size:1.12rem;font-weight:800;color:#FFF;letter-spacing:0.02em;">{company}</div>
        <div style="color:#6B7280;font-size:0.78rem;font-family:'Share Tech Mono',monospace;">{industry}</div>
    </div>
    <div>
        <span class="kx-badge badge-green">{len(products)} SOLUCIONES MATCH</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if not products:
    no_data_state(
        msg="No se encontraron productos recomendados.",
        hint="Verifica que modules/rag.py y data/portfolio.json estén correctamente configurados."
    )
    st.stop()

# ── Grid de productos ──────────────────────────────────────────────────────────
st.markdown('<div class="kx-section-title">◈ Soluciones Recomendadas por RAG</div>', unsafe_allow_html=True)

for i, product in enumerate(products):
    name        = product.get("name", f"Producto {i+1}")
    category    = product.get("category", "")
    description = product.get("description", "")
    roi_pitch   = product.get("roi_pitch", "")
    match_score = int(product.get("match_score", 0))
    features    = product.get("features", []) or []
    pain_points = product.get("pain_points_addressed", []) or []

    card_classes = ["kx-card-accent", "kx-card-blue", "kx-card-yellow"]
    card_class   = card_classes[i % len(card_classes)]

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown(f"""
        <div class="kx-card {card_class}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
                <div>
                    <div style="font-size:1.05rem;font-weight:700;color:#FFF;">{name}</div>
                    {f'<div style="color:#6B7280;font-size:0.75rem;font-family:monospace;margin-top:0.2rem;">{category}</div>' if category else ''}
                </div>
                {f'<span class="kx-badge badge-green">MATCH {match_score}%</span>' if match_score else ''}
            </div>
            {f'<div style="color:#C9D1D9;font-size:0.88rem;line-height:1.6;margin-bottom:0.8rem;">{description}</div>' if description else ''}
            {f'<div style="background:#050A0E;border-radius:4px;padding:0.8rem;border-left:2px solid #00FFB2;font-size:0.85rem;color:#C9D1D9;line-height:1.6;"><span style="color:#00FFB2;font-family:monospace;font-size:0.7rem;letter-spacing:0.1em;">◈ ROI PITCH &nbsp;</span><br>{roi_pitch}</div>' if roi_pitch else ''}
        </div>
        """, unsafe_allow_html=True)

    with col_side:
        if features:
            st.markdown('<div class="kx-section-title" style="margin-top:0.5rem;">◈ Features Clave</div>', unsafe_allow_html=True)
            for f in features[:5]:
                st.markdown(f'<div style="font-size:0.78rem;color:#C9D1D9;padding:0.2rem 0;border-bottom:1px solid #1E2A35;">✓ {f}</div>', unsafe_allow_html=True)
        if pain_points:
            st.markdown('<div class="kx-section-title" style="margin-top:0.8rem;">◈ Pain Points Cubiertos</div>', unsafe_allow_html=True)
            for pp in pain_points[:3]:
                st.markdown(f'<div style="font-size:0.78rem;color:#FF3B5C;padding:0.2rem 0;">⚡ {pp}</div>', unsafe_allow_html=True)
        if not features and not pain_points:
            st.markdown("""
            <div style="color:#6B7280;font-size:0.75rem;font-family:monospace;margin-top:1rem;
                        padding:0.5rem;border:1px dashed #1E2A35;border-radius:4px;text-align:center;">
                Agrega 'features' y 'pain_points_addressed' a portfolio.json
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Mapa Pain Point → Solución ────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="kx-section-title">◈ Dolor del Cliente → Solución Propuesta</div>', unsafe_allow_html=True)

pain_raw = web_data.get("pain_points", []) or []
pains    = [p.get("snippet", "") if isinstance(p, dict) else str(p) for p in pain_raw[:3]]

if pains and products:
    for j, pain in enumerate(pains):
        product_match = products[j % len(products)].get("name", "—")
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:center;margin-bottom:0.8rem;">
            <div class="kx-card kx-card-red" style="margin:0;padding:0.8rem 1rem;">
                <div style="font-size:0.7rem;color:#FF3B5C;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Pain Point</div>
                <div style="font-size:0.82rem;color:#C9D1D9;line-height:1.5;">{pain[:200]}</div>
            </div>
            <div style="text-align:center;color:#00FFB2;font-size:1.2rem;">→</div>
            <div class="kx-card kx-card-accent" style="margin:0;padding:0.8rem 1rem;">
                <div style="font-size:0.7rem;color:#00FFB2;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Solución</div>
                <div style="font-size:0.82rem;font-weight:700;color:#FFF;">{product_match}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Ejecuta el análisis completo para ver el mapeo dolor → solución.")
    
page_footer()