"""
03_recommendations.py — Recommended Product Portfolio (RAG)
Owner: Engineer 5 (UI)
FIXED: uses modules.ui_theme, not streamlit_app.ui_utils
"""
import streamlit as st
import re
from modules.ui_theme import page_header, badge, no_data_state, get_analysis, page_footer

try:
    from modules.ui_theme import page_header, badge, no_data_state, score_bar, get_analysis
except ImportError:
    st.error("⚠️ modules/ui_theme.py not found. Make sure you are running from the korhex-ai/ root folder.")
    st.stop()

st.set_page_config(page_title="Recommendations · KORHEX.AI", page_icon="🎯", layout="wide")

page_header(
    title="🎯 Portfolio Recommendations",
    subtitle="Products selected by local RAG — semantic matching against portfolio.json with no external APIs."
)

current = get_analysis()

if not current:
    no_data_state(
        msg="No active analysis in this session.",
        hint="← Run an analysis from the main page first."
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
        <span class="kx-badge badge-green">{len(products)} SOLUTION MATCHES</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Product grid ───────────────────────────────────────────────────────────────
if not products:
    no_data_state(
        msg="No recommended products found.",
        hint="Verify that modules/rag.py and data/portfolio.json are correctly configured."
    )
    st.stop()

st.markdown('<div class="kx-section-title">◈ RAG-Recommended Solutions</div>', unsafe_allow_html=True)

import html as _html  # kept for &amp; in static HTML only

def _strip_tags(text: str) -> str:
    """Strip HTML tags, escape sequences, and collapse whitespace to single spaces."""
    t = str(text or '')
    # Remove HTML tags
    t = re.sub(r'<[^>]+>', '', t)
    # Convert literal escape sequences that survive JSON parsing
    t = t.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
    # Collapse all real whitespace (newlines, tabs, spaces) into single spaces
    t = ' '.join(t.split())
    return t.strip()

for i, product in enumerate(products):
    name        = _strip_tags(product.get("name", f"Product {i+1}"))
    category    = _strip_tags(product.get("category", ""))
    description = _strip_tags(product.get("description", ""))
    roi_pitch   = _strip_tags(product.get("roi_pitch", ""))
    match_score = int(product.get("match_score", 0))
    features    = product.get("features", []) or []
    pain_points = product.get("pain_points_addressed", []) or []

    card_classes = ["kx-card-accent", "kx-card-blue", "kx-card-yellow"]
    card_class   = card_classes[i % len(card_classes)]

    col_main, col_side = st.columns([3, 1])

    with col_main:
        cat_html   = f'<div style="color:#6B7280;font-size:0.75rem;font-family:monospace;margin-top:0.2rem;">{_html.escape(category)}</div>' if category else ''
        badge_html = f'<span class="kx-badge badge-green">MATCH {match_score}%</span>' if match_score else ''
        desc_html  = f'<div style="color:#C9D1D9;font-size:0.88rem;line-height:1.6;margin-bottom:0.8rem;">{_html.escape(description)}</div>' if description else ''
        roi_html   = (
            f'<div style="background:#050A0E;border-radius:4px;padding:0.8rem;border-left:2px solid #00FFB2;'
            f'font-size:0.85rem;color:#C9D1D9;line-height:1.6;">'
            f'<span style="color:#00FFB2;font-family:monospace;font-size:0.7rem;letter-spacing:0.1em;">◈ ROI PITCH &nbsp;</span>'
            f'<br>{_html.escape(roi_pitch)}</div>'
        ) if roi_pitch else ''

        card_html = f"""
<div class="kx-card {card_class}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
    <div>
      <div style="font-size:1.05rem;font-weight:700;color:#FFF;">{_html.escape(name)}</div>
      {cat_html}
    </div>
    {badge_html}
  </div>
  {desc_html}
  {roi_html}
</div>""".strip()
        st.markdown(card_html, unsafe_allow_html=True)


    with col_side:
        if features:
            st.markdown('<div class="kx-section-title" style="margin-top:0.5rem;">◈ Key Features</div>', unsafe_allow_html=True)
            for f in features[:5]:
                st.markdown(f'<div style="font-size:0.78rem;color:#C9D1D9;padding:0.2rem 0;border-bottom:1px solid #1E2A35;">✓ {f}</div>', unsafe_allow_html=True)
        if pain_points:
            st.markdown('<div class="kx-section-title" style="margin-top:0.8rem;">◈ Pain Points Addressed</div>', unsafe_allow_html=True)
            for pp in pain_points[:3]:
                st.markdown(f'<div style="font-size:0.78rem;color:#FF3B5C;padding:0.2rem 0;">⚡ {pp}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Mapping Pain Point → Solution ─────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="kx-section-title">◈ Client Pain Point → Proposed Solution</div>', unsafe_allow_html=True)

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
                <div style="font-size:0.7rem;color:#00FFB2;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Solution</div>
                <div style="font-size:0.82rem;font-weight:700;color:#FFF;">{product_match}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Run a full analysis to view the pain point → solution mapping.")

page_footer()