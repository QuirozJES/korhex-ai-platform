import streamlit as st

st.set_page_config(page_title="Sales Toolkit", page_icon="💼", layout="wide")

if not st.session_state.get('current_analysis'):
    st.warning("⚠️ Realiza un análisis en la página principal primero.")
    st.stop()

data = st.session_state['current_analysis']
# Usamos .get() para todo
name = data.get('company_name', 'Client')
analysis = data.get('analysis', {})
products = data.get('products', [])

st.title(f"💼 Sales Toolkit: {name}")

st.subheader("🎯 Recommended Solutions")
if products:
    cols = st.columns(len(products))
    for i, product in enumerate(products):
        with cols[i]:
            with st.container(border=True):
                # Blindaje en los atributos del producto
                st.markdown(f"**{product.get('name', 'Product')}**")
                st.caption(f"Category: {product.get('category', 'General')}")
                st.write(product.get('description', 'No description available.'))
else:
    st.info("No hay productos específicos para esta industria.")

st.divider()

st.subheader("📢 AI-Generated Sales Pitch")
with st.chat_message("assistant"):
    # Si no hay speech, evitamos el error
    st.markdown(analysis.get('sales_speech', 'No sales pitch generated yet.'))

with st.expander("🛡️ Objection Handling"):
    st.info(analysis.get('audit_notes', 'No audit notes available.'))