import streamlit as st
import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Formatted")
    output.seek(0)
    return output

def format_dataset_app():
    st.header("📊 Format Raw Groundwater Dataset")

    uploaded_file = st.file_uploader(
        "Upload raw Excel or CSV file",
        type=["xlsx", "xls", "csv"]
    )

    if uploaded_file:
        try:
            file_name = uploaded_file.name.lower()

            if file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            df.columns = df.columns.astype(str).str.strip()

            st.success("File uploaded successfully.")

            st.subheader("Step 1: Assign Column Roles")

            well_col = st.selectbox("Select Well ID Column", df.columns)
            date_col = st.selectbox("Select Date Column", df.columns)
            analyte_col = st.selectbox("Select Analyte Name Column", df.columns)
            result_col = st.selectbox("Select Result Value Column", df.columns)

            # 🛑 Ensure user selections are not the same
            if len({well_col, date_col, analyte_col, result_col}) < 4:
                st.warning("Please select four unique columns for Well ID, Date, Analyte, and Result.")
                return

            long_df = df[[well_col, date_col, analyte_col, result_col]].copy()
            long_df.columns = ["Well ID", "Date", "Constituent", "Result"]

            st.success("✅ Dataset formatted successfully!")
            st.markdown("### Preview of Long-Format Output:")
            st.dataframe(long_df.head(50), use_container_width=True)

            st.download_button(
                label="📥 Download Long Format Excel",
                data=to_excel(long_df),
                file_name="long_format_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"Error formatting dataset: {e}")