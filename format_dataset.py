import streamlit as st
import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Formatted")
    output.seek(0)
    return output

def to_matrix_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=True, sheet_name="Matrix")
    output.seek(0)
    return output

def format_dataset_app():
    st.header("📊 Format Dataset to Long & Matrix")

    uploaded_file = st.file_uploader("Upload raw lab dataset (Excel or CSV)", type=["xlsx", "xls", "csv"])

    if uploaded_file:
        try:
            # Read file depending on type
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("File uploaded successfully.")
            st.subheader("Step 1: Select Column Headers")

            well_col = st.selectbox("Select Well ID Column", df.columns)
            date_col = st.selectbox("Select Date Column", df.columns)
            analyte_col = st.selectbox("Select Constituent/Analyte Column", df.columns)
            result_col = st.selectbox("Select Result Column", df.columns)

            long_df = df[[well_col, date_col, analyte_col, result_col]].copy()
            long_df.columns = ["Well ID", "Date", "Constituent", "Result"]

            st.subheader("Step 2: Preview and Download Long-Format Table")
            st.dataframe(long_df, use_container_width=True)

            st.download_button(
                label="📥 Download Long Format Excel",
                data=to_excel(long_df),
                file_name="long_format_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # Generate matrix format (pivot table)
            st.subheader("Step 3: Preview and Download Matrix Format Table")
            matrix_df = long_df.pivot_table(
                index=["Well ID", "Date"],
                columns="Constituent",
                values="Result",
                aggfunc="first"
            ).reset_index()

            st.dataframe(matrix_df, use_container_width=True)

            st.download_button(
                label="📥 Download Matrix Format Excel",
                data=to_matrix_excel(matrix_df),
                file_name="matrix_format_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"Error formatting dataset: {e}")