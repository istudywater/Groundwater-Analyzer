import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Export')
    return output.getvalue()

def max_detection_app():
    st.title("📈 Max Detection Analyzer")

    uploaded_file = st.file_uploader("Upload your historical groundwater dataset (.xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        columns = df.columns.tolist()

        with st.expander("🔧 Select column mappings"):
            col1, col2, col3 = st.columns(3)
            with col1:
                well_col = st.selectbox("Select Well ID column", options=columns)
            with col2:
                date_col = st.selectbox("Select Sample Date column", options=columns)
            with col3:
                constituent_col = st.selectbox("Select Constituent Name column", options=columns)
            result_col = st.selectbox("Select Result/Detection column", options=columns)

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[result_col] = pd.to_numeric(df[result_col], errors='coerce')

        df_clean = df.dropna(subset=[constituent_col, result_col, well_col, date_col]).copy()

        if not df_clean.empty:
            idx_max = df_clean.groupby(constituent_col)[result_col].idxmax()
            max_df = df_clean.loc[idx_max, [constituent_col, result_col, well_col, date_col]].copy()
            max_df.columns = ["Constituent", "Max Detection", "Location of Max Detection", "Date of Max Detection"]
            max_df["Date of Max Detection"] = max_df["Date of Max Detection"].dt.strftime("%Y-%m-%d")

            two_years_ago = datetime.now() - timedelta(days=730)
            recent_df = df_clean[df_clean[date_col] >= two_years_ago].copy()

            if not recent_df.empty:
                idx_recent = recent_df.groupby(constituent_col)[result_col].idxmax()
                recent_max_df = recent_df.loc[idx_recent, [constituent_col, result_col, well_col, date_col]].copy()
                recent_max_df.columns = ["Constituent", "Max Detection within 2 Years", "Location of Max Detection within 2 Years", "Date of Max Detection within 2 Years"]
                recent_max_df["Date of Max Detection within 2 Years"] = recent_max_df["Date of Max Detection within 2 Years"].dt.strftime("%Y-%m-%d")
            else:
                recent_max_df = pd.DataFrame(columns=["Constituent", "Max Detection within 2 Years", "Location of Max Detection within 2 Years", "Date of Max Detection within 2 Years"])

            summary_df = pd.merge(max_df, recent_max_df, on="Constituent", how="left")
            summary_df["Max Detection within 2 Years"] = summary_df["Max Detection within 2 Years"].fillna("ND")
            summary_df["Location of Max Detection within 2 Years"] = summary_df["Location of Max Detection within 2 Years"].fillna("Not Applicable")
            summary_df["Date of Max Detection within 2 Years"] = summary_df["Date of Max Detection within 2 Years"].fillna("Not Applicable")

            st.dataframe(summary_df, use_container_width=True)
            st.download_button("📥 Download Excel File", to_excel(summary_df), "max_detection_summary.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("No valid data rows found after cleaning. Please check the column mappings and data values.")
