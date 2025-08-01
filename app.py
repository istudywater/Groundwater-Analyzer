# app.py

import streamlit as st
from core import generate_gw_summary
from max_detection    import max_detection_app
from format_dataset   import format_dataset_app
from gwps_analyzer    import gwps_analyzer_app

# ——— Initialize session state ———
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# ——— Sidebar with buttons ———
st.sidebar.title("🔎 GW Analyzer Navigation")
# Use full-width buttons. When clicked, they set session_state.page.
if st.sidebar.button("🏠 Home"):
    st.session_state.page = 'Home'
if st.sidebar.button("🧪 GWPS Analyzer"):
    st.session_state.page = 'GWPS Analyzer'
if st.sidebar.button("⚖️ Max Detection"):
    st.session_state.page = 'Max Detection'
if st.sidebar.button("🗂 Format Dataset"):
    st.session_state.page = 'Format Dataset'

# ——— Main content ———
page = st.session_state.page

if page == 'Home':
    st.set_page_config(page_title="GW Analyzer – Home", layout="wide")
    st.title("🌊 Groundwater Monitoring Analyzer")
    st.markdown("""
    Welcome to the GW Analyzer suite!  

    **Use the buttons on the left** to pick:
    - 🧪 **GWPS Analyzer**: Generate your groundwater protection summary  
    - ⚖️ **Max Detection**: Find the highest non-detect values  
    - 🗂 **Format Dataset**: Tidy up your raw lab output  

    Get started by clicking one of the navigation buttons.  
    """)
    st.markdown("---")
    st.markdown("👤 [GitHub](https://github.com/yourusername) | [LinkedIn](https://www.linkedin.com/in/yourprofile/)")

elif page == 'GWPS Analyzer':
    st.set_page_config(page_title="GWPS Analyzer", layout="wide")
    gwps_analyzer_app()

elif page == 'Max Detection':
    st.set_page_config(page_title="Max Detection", layout="wide")
    max_detection_app()

elif page == 'Format Dataset':
    st.set_page_config(page_title="Format Dataset", layout="wide")
    format_dataset_app()
