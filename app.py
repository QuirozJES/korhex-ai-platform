import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))

st.set_page_config(
    page_title="KORHEX.AI Account Intelligence",
    page_icon="🤖",
    layout="wide"
)

if 'accounts_analyzed' not in st.session_state:
    st.session_state['accounts_analyzed'] = []
if 'web_data' not in st.session_state:
    st.session_state['web_data'] = {}

def main():
    st.title("🤖 KORHEX.AI — Account Intelligence Platform")
    st.caption("Local AI | Zero Data Leakage | Powered by Llama 3")

    with st.sidebar:
        st.header("⚙️ Account Input")

        company_url = st.text_input(
            "🔗 Company URL *",
            placeholder="https://www.example.com"
        )

        company_name = st.text_input(
            "Company Name *",
            placeholder="e.g. Toyota Motor Corp"
        )

        industry = st.selectbox(
            "Industry",
            ["Technology", "Finance", "Healthcare",
             "Manufacturing", "Retail", "Energy",
             "Telecommunications"]
        )

        years_inactive = st.slider(
            "Years since last purchase",
            0, 10, 3
        )

        analyze_btn = st.button(
            "🚀 Execute Analysis",
            type="primary",
            use_container_width=True
        )

        st.divider()

        with st.expander("🛡️ Solution Viability"):
            st.markdown("""
**✅ No commercial AI licenses required**

**✅ Open-source tools only**
Ollama · Streamlit · Python · Tavily free tier

**✅ Simulated/example accounts**
No real client data stored or transmitted

**✅ Full data confidentiality**
100% local processing. Zero external data transmission.

---
**Components:**
- Sources: Tavily API (public web)
- Processing: Llama 3 via Ollama (local)
- Output: Streamlit UI (local network)

**Minimum Requirements:**
- GPU: 8GB VRAM
- RAM: 16GB
- Python 3.11 | Ollama | Streamlit
            """)

    if analyze_btn:
        if not company_name or not company_url:
            st.warning("⚠️ Please enter both Company Name and URL.")
            return

        try:
            from modules.scraper import search_account, calculate_net_new_score
            from modules.rag import get_relevant_products
            from modules.agent import generate_analysis
            from modules.ui_components import render_tabs
        except ImportError as e:
            st.error(f"Module missing: {e}")
            st.info("Make sure all .py files are in the modules/ folder.")
            return

        prog = st.progress(0, text="🔍 Searching public information...")
        web_data = search_account(company_name, company_url, industry)
        st.session_state['web_data'] = web_data

        prog.progress(33, text="💡 Matching portfolio solutions...")
        products = get_relevant_products(industry, web_data)

        prog.progress(66, text="🤖 Generating AI analysis and speech...")
        analysis = generate_analysis(company_name, web_data, products, years_inactive)

        prog.progress(100, text="✅ Analysis complete!")

        score_data = calculate_net_new_score(years_inactive, web_data)
        entry = {
            "name": company_name,
            "url": company_url,
            "industry": industry,
            "score": score_data['total_score'],
            "priority": score_data['priority'],
            "years_inactive": years_inactive,
            "is_net_new": score_data['is_net_new']
        }

        st.session_state['accounts_analyzed'] = [
            a for a in st.session_state['accounts_analyzed']
            if a['name'] != company_name
        ]
        st.session_state['accounts_analyzed'].append(entry)
        st.session_state['accounts_analyzed'].sort(
            key=lambda x: x['score'], reverse=True
        )
        st.session_state['accounts_analyzed'] = \
            st.session_state['accounts_analyzed'][:5]

        render_tabs(company_name, analysis, products, years_inactive, web_data)

    else:
        st.info("👈 Enter a company URL and name in the sidebar to begin.")

        if st.session_state['accounts_analyzed']:
            st.header("🏆 Top 5 Priority Accounts")
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, acc in enumerate(st.session_state['accounts_analyzed']):
                badge = "🏷️ NET NEW" if acc['is_net_new'] else "🔄 RE-ENGAGEMENT"
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.markdown(f"{medals[i]} **{acc['name']}** — {badge}")
                    st.caption(f"{acc['url']} | {acc['industry']}")
                with col2:
                    st.metric("Score", f"{acc['score']}/100")
                with col3:
                    st.caption(acc['priority'])
                st.divider()

if __name__ == "__main__":
    main()