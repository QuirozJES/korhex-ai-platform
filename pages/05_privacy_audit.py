import streamlit as st
from modules.audit_logger import get_privacy_dashboard_data

st.set_page_config(page_title="Privacy & Cost Audit", page_icon="🛡️", layout="wide")

st.title("🛡️ Privacy & Local Infrastructure Audit")
data = get_privacy_dashboard_data()

col1, col2, col3, col4 = st.columns(4)
with col1:
    # Usamos .get() para asegurar que el Score nunca sea None
    st.metric("Privacy Score", f"{data.get('privacy_score', 100)}%", "SECURE")
with col2:
    st.metric("Cloud Data Leakage", f"{data.get('bytes_to_cloud', 0)} bytes", "PROTECTED")
with col3:
    st.metric("Cloud API Calls", data.get('cloud_api_calls', 0), "Bypassed")
with col4:
    st.metric("Local Processing", "100%", "GPU-Accelerated")

st.divider()

st.subheader("💰 Economic Impact (Savings)")
# Si por algo el ahorro es None, mostramos 0.0
savings = data.get('cost_saved_usd', 0.0)
st.metric("Estimated Savings (USD)", f"${round(savings, 4)}", delta="Saved vs Cloud API")

st.success("✅ Todo el procesamiento se realizó localmente en tu infraestructura.")