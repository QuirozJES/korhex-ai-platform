"""
02_analysis.py — The 6 Elements of Account Analysis
Owner: Engineer 5 (UI)
"""
import time
import streamlit as st
from modules.ui_theme import page_header, badge, no_data_state, get_analysis, page_footer

try:
    from modules.ui_theme import page_header, badge, no_data_state, get_analysis
except ImportError:
    st.error("⚠️ modules/ui_theme.py not found.")
    st.stop()

st.set_page_config(page_title="Analysis · KORHEX.AI", page_icon="🔬", layout="wide")

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

# ── Account header ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kx-card kx-card-accent" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
    <div>
        <div style="font-size:1.18rem;font-weight:800;color:#FFF;letter-spacing:0.02em;">{company}</div>
        <div style="color:#6B7280;font-size:0.8rem;font-family:'Share Tech Mono',monospace;">
            {industry} &nbsp;|&nbsp; {years} yr(s) inactive
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
    st.warning(f"⚠️ **Audit:** {audit_notes}")

st.markdown("---")
st.markdown('<div class="kx-section-title">◈ 6 Account Intelligence Blocks</div>', unsafe_allow_html=True)

# ── 6 analysis sections ───────────────────────────────────────────────────────
SECTIONS = [
    ("1. Company Snapshot & Strategy",  "strategy_background",  "🏢", "kx-card-accent"),
    ("2. Technology Environment",       "tech_environment",     "💻", "kx-card-blue"),
    ("3. IT Pain Points",               "pain_points",          "⚡", "kx-card-red"),
    ("4. Key Decision Makers",          "decision_makers",      "👤", "kx-card-yellow"),
    ("5. Financial Signals",            "financial_signals",    "💰", "kx-card-accent"),
    ("6. Competitive Context",          "competitive_context",  "🎯", "kx-card-blue"),
]

# Attempt to parse numbered sections from the agent output
def extract_section(full_text: str, section_num: int) -> str:
    """Extract a numbered section from the agent output."""
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
            clean = ' '.join(section_text.split())
            st.markdown(f'<div class="kx-card {card_class}" style="margin-bottom:0.8rem;"><div class="kx-section-title">◈ AI Agent Analysis</div><div style="font-size:0.9rem;line-height:1.7;color:#C9D1D9;">{clean}</div></div>', unsafe_allow_html=True)

        elif raw_snippets:
            st.markdown(f'<div class="kx-section-title">◈ Collected Web Sources</div>', unsafe_allow_html=True)
            for item in raw_snippets[:4]:
                if isinstance(item, dict):
                    snippet = item.get("snippet") or item.get("title") or item.get("content") or str(item)
                    source  = item.get("url") or item.get("source") or ""
                else:
                    snippet = str(item)
                    source  = ""
                st.markdown(f"""
                <div class="kx-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem;">
                    <div style="font-size:0.85rem;color:#C9D1D9;line-height:1.6;">{snippet}</div>
                    {f'<div style="font-size:0.7rem;color:#00B4FF;margin-top:0.3rem;font-family:monospace;">{source}</div>' if source else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="color:#6B7280;font-size:0.85rem;font-family:'Share Tech Mono',monospace;padding:1rem 0;">
                No data available for this section. The scraper found no information for '{web_key}'.
            </div>
            """, unsafe_allow_html=True)

# ── Audit notes ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="kx-section-title">◈ Compliance Agent Audit Report</div>', unsafe_allow_html=True)
audit_color = "kx-card-accent" if audit_ok else "kx-card-red"
st.markdown(f"""
<div class="kx-card {audit_color}">
    <div style="display:flex;align-items:center;gap:0.8rem;">
        <div style="font-size:1.5rem;">{"✅" if audit_ok else "⚠️"}</div>
        <div>
            <div style="font-weight:700;color:#FFF;">
                {"Analysis verified — no hallucinations detected" if audit_ok else "Possible inaccuracies detected"}
            </div>
            <div style="color:#C9D1D9;font-size:0.85rem;margin-top:0.3rem;">{audit_notes}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

page_footer()