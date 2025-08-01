import streamlit as st
import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Export')
    return output.getvalue()

def format_dataset_app():
    st.title("🧰 Format Wide-to-Long Dataset")

    uploaded_file = st.file_uploader("Upload a wide-format Excel dataset (.xlsx)", type=["xlsx"], key="format")
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        columns = df.columns.tolist()

        with st.expander("🔧 Select column mappings"):
            col1, col2 = st.columns(2)
            with col1:
                well_col = st.selectbox("Select Well ID column", options=columns, key="format_well")
            with col2:
                date_col = st.selectbox("Select Sample Date column", options=columns, key="format_date")

        exclude_cols = [well_col, date_col]
        constituent_cols = [col for col in columns if col not in exclude_cols]

        long_df = df.melt(id_vars=[well_col, date_col], value_vars=constituent_cols,
                          var_name="Constituent", value_name="Result")

        st.dataframe(long_df, use_container_width=True)
        st.download_button("📥 Download Long Format Excel", to_excel(long_df),
                           "long_format_dataset.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
