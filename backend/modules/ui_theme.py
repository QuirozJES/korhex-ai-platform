"""
ui_theme.py — KORHEX.AI Global Theme & UI Utilities
LEGACY MODULE: Previously used with Streamlit frontend.
Kept for reference/backward-compatibility.
"""
try:
    import streamlit as st
except ImportError:
    st = None  # Streamlit not installed — module kept for reference only

KORHEX_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700;900&display=swap');

:root {
  --neon:       #00FFB2;
  --neon-dim:   #00FFB240;
  --neon-glow:  0 0 8px #00FFB2, 0 0 20px #00FFB260;
  --red:        #FF3B5C;
  --yellow:     #FFD600;
  --blue:       #00B4FF;
  --bg:         #050A0E;
  --bg2:        #0D1117;
  --bg3:        #161B22;
  --border:     #1E2A35;
  --text:       #C9D1D9;
  --text-dim:   #6B7280;
  --font-mono:  'Share Tech Mono', monospace;
  --font-main:  'Exo 2', sans-serif;
  --radius:     6px;
  --transition: all 0.2s ease;
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font-main) !important;
}

[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed; top:0; left:0; right:0; bottom:0;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px,
    rgba(0,255,178,0.012) 2px, rgba(0,255,178,0.012) 4px);
  pointer-events: none; z-index: 9999;
}

[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}

h1 { color: var(--neon) !important; font-family: var(--font-main) !important;
     font-weight:700 !important; text-shadow: var(--neon-glow) !important; }
h2 { color: #FFF !important; font-family: var(--font-main) !important; font-weight:700 !important; }
h3 { color: var(--text) !important; font-family: var(--font-main) !important; }

[data-testid="stMetric"] {
  background: var(--bg3) !important; border: 1px solid var(--border) !important;
  border-left: 3px solid var(--neon) !important; border-radius: var(--radius) !important;
  padding: 1rem 1.2rem !important; transition: var(--transition) !important;
}
[data-testid="stMetric"]:hover { border-left-color: var(--blue) !important;
  box-shadow: -4px 0 12px var(--neon-dim) !important; }
[data-testid="stMetricLabel"] { color: var(--text-dim) !important; font-size:0.75rem !important;
  text-transform:uppercase !important; letter-spacing:0.1em !important; }
[data-testid="stMetricValue"] { color: var(--neon) !important;
  font-family: var(--font-mono) !important; font-size:1.8rem !important; }

.stButton > button {
  background: transparent !important; border: 1px solid var(--neon) !important;
  color: var(--neon) !important; font-family: var(--font-mono) !important;
  font-size:0.85rem !important; letter-spacing:0.08em !important;
  border-radius: var(--radius) !important; transition: var(--transition) !important;
}
.stButton > button:hover { background: var(--neon) !important; color: var(--bg) !important;
  box-shadow: var(--neon-glow) !important; }
.stButton > button[kind="primary"] { background: var(--neon) !important;
  color: var(--bg) !important; font-weight:700 !important; }

.stTextInput > div > div > input {
  background: var(--bg3) !important; border: 1px solid var(--border) !important;
  color: var(--text) !important; border-radius: var(--radius) !important;
  font-family: var(--font-mono) !important;
}

[data-testid="stTabs"] button { font-family: var(--font-mono) !important;
  font-size:0.8rem !important; letter-spacing:0.06em !important; color: var(--text-dim) !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: var(--neon) !important;
  border-bottom: 2px solid var(--neon) !important; }

[data-testid="stExpander"] { border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; background: var(--bg3) !important; }

[data-testid="stProgress"] > div > div { background: var(--neon) !important;
  box-shadow: var(--neon-glow) !important; }

hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background: var(--neon); }

.kx-card {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.2rem 1.4rem;
  margin-bottom: 0.8rem; transition: var(--transition);
}
.kx-card:hover { border-color: var(--neon); box-shadow: 0 0 12px var(--neon-dim); }
.kx-card-accent { border-left: 3px solid var(--neon); }
.kx-card-red    { border-left: 3px solid var(--red); }
.kx-card-blue   { border-left: 3px solid var(--blue); }
.kx-card-yellow { border-left: 3px solid var(--yellow); }

.kx-badge { display:inline-block; padding:0.2rem 0.6rem; border-radius:3px;
  font-family: var(--font-mono); font-size:0.7rem; font-weight:700;
  letter-spacing:0.1em; text-transform:uppercase; }
.badge-green  { background:#00FFB220; color:var(--neon);   border:1px solid var(--neon); }
.badge-red    { background:#FF3B5C20; color:var(--red);    border:1px solid var(--red); }
.badge-yellow { background:#FFD60020; color:var(--yellow); border:1px solid var(--yellow); }
.badge-blue   { background:#00B4FF20; color:var(--blue);   border:1px solid var(--blue); }

.kx-section-title { font-family: var(--font-mono); font-size:0.7rem;
  letter-spacing:0.2em; text-transform:uppercase; color: var(--text-dim);
  border-bottom:1px solid var(--border); padding-bottom:0.4rem; margin-bottom:1rem; }

.kx-score-bar-bg { background:var(--bg2); border-radius:3px; height:6px;
  overflow:hidden; border:1px solid var(--border); margin: 0.3rem 0 0.8rem 0; }
.kx-score-bar-fill { height:100%; border-radius:3px;
  background: linear-gradient(90deg, var(--neon), var(--blue));
  box-shadow: var(--neon-glow); transition: width 0.6s ease; }

.kx-logo-header { font-family:var(--font-mono); font-size:1.1rem; color:var(--neon);
  letter-spacing:0.15em; text-shadow:var(--neon-glow); padding:0.5rem 0; }
.kx-logo-sub { font-size:0.65rem; color:var(--text-dim);
  letter-spacing:0.12em; text-transform:uppercase; }

.kx-privacy-pill { background:#00FFB210; border:1px solid var(--neon);
  border-radius:20px; padding:0.25rem 0.8rem; font-family:var(--font-mono);
  font-size:0.68rem; color:var(--neon); display:inline-block; margin:0.2rem; }

.kx-speech-block { background:var(--bg2); border:1px solid var(--border);
  border-left:3px solid var(--neon); border-radius:var(--radius); padding:1.4rem;
  font-family:var(--font-main); font-size:0.95rem; line-height:1.7; white-space:pre-wrap; }

.kx-audit-zero { font-family:var(--font-mono); font-size:3.5rem; font-weight:900;
  color:var(--neon); text-shadow:var(--neon-glow); text-align:center; line-height:1; }

/* --- Visual refinements & overrides --- */

:root {
  --radius: 8px;
}

html, body, [data-testid="stAppViewContainer"] {
  background-image:
    radial-gradient(circle at 0% 0%, rgba(0,255,178,0.05), transparent 55%),
    radial-gradient(circle at 100% 100%, rgba(0,180,255,0.08), transparent 55%);
  line-height: 1.6 !important;
}

h1 {
  font-weight: 800 !important;
}

h2 {
  letter-spacing: 0.03em !important;
}

.stTextInput > div > div > input:focus {
  outline: none !important;
  border-color: var(--neon) !important;
  box-shadow: 0 0 0 1px var(--neon-dim) !important;
}

hr {
  margin: 1.5rem 0 !important;
}

.kx-card {
  background:
    radial-gradient(circle at 0% 0%, rgba(0,255,178,0.06), transparent 55%),
    radial-gradient(circle at 100% 100%, rgba(0,180,255,0.04), transparent 55%),
    var(--bg3);
  border-radius: var(--radius);
  padding: 1.15rem 1.3rem;
  margin-bottom: 0.9rem;
}

.kx-card:hover {
  box-shadow: 0 0 16px var(--neon-dim);
  transform: translateY(-1px);
}

.kx-section-title {
  letter-spacing:0.18em;
  padding-bottom:0.35rem;
  margin-bottom:0.9rem;
}

</style>
"""

def apply_theme():
    st.markdown(KORHEX_CSS, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = "", icon: str = ""):
    apply_theme()
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                border-bottom:1px solid #1E2A35; padding-bottom:0.8rem; margin-bottom:1.5rem;">
        <div>
            <div class="kx-logo-header">{icon if icon else "◈"} KORHEX.AI</div>
            <div class="kx-logo-sub">Account Intelligence Platform &nbsp;|&nbsp; Local AI · Zero Data Leakage</div>
        </div>
        <div style="text-align:right;">
            <div class="kx-privacy-pill">🔒 LOCAL AI</div>
            <div class="kx-privacy-pill">0 BYTES → CLOUD</div>
        </div>
    </div>
    <h2 style="margin-bottom:0.2rem;">{title}</h2>
    {"<p style='color:#6B7280;font-size:0.85rem;margin-top:0;'>"+subtitle+"</p>" if subtitle else ""}
    """, unsafe_allow_html=True)

def badge(text: str, color: str = "green") -> str:
    return f'<span class="kx-badge badge-{color}">{text}</span>'

def score_bar(score: int, max_score: int = 100) -> str:
    pct = min(100, int((score / max_score) * 100)) if max_score else 0
    return f'<div class="kx-score-bar-bg"><div class="kx-score-bar-fill" style="width:{pct}%;"></div></div>'

def priority_badge(priority: str) -> str:
    color_map = {"HIGH":"red","MEDIUM":"yellow","LOW":"blue","CRITICAL":"red"}
    color = color_map.get((priority or "LOW").upper(), "blue")
    return badge(priority or "N/A", color)

def no_data_state(msg: str = "No hay datos disponibles.", hint: str = ""):
    st.markdown(f"""
    <div class="kx-card" style="text-align:center;padding:2.5rem;border-style:dashed;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">◈</div>
        <div style="color:#6B7280;font-family:'Share Tech Mono',monospace;font-size:0.85rem;">{msg}</div>
        {"<div style='color:#00FFB280;font-size:0.75rem;margin-top:0.5rem;'>"+hint+"</div>" if hint else ""}
    </div>
    """, unsafe_allow_html=True)

def get_analysis() -> dict | None:
    return st.session_state.get("current_analysis", None)

def page_footer():
    """Footer estándar con Solution Viability. Llamar al FINAL de cada página."""
    st.markdown("---")
    st.markdown("""
    <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;
                padding:0.8rem 0; border-top:1px solid #1E2A35;">
        <span style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#6B7280;">
            ✓ No commercial AI licenses
        </span>
        <span style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#6B7280;">
            ✓ Open-source only (Ollama · CrewAI · Streamlit · SQLite)
        </span>
        <span style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#6B7280;">
            ✓ No real client data
        </span>
        <span style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#00FFB2;">
            ✓ 0 bytes to cloud
        </span>
    </div>
    """, unsafe_allow_html=True)