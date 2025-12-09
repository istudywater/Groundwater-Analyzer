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

            df.columns = df.columns.str.strip()  # Clean column headers
            st.success("File uploaded successfully.")

            st.subheader("Step 1: Assign Column Roles")

            well_col = st.selectbox("Select Well ID Column", df.columns)
            date_col = st.selectbox("Select Date Column", df.columns)

            st.markdown("Select the columns that contain constituent data:")
            constituent_cols = st.multiselect(
                "Select Constituent Columns",
                [col for col in df.columns if col not in [well_col, date_col]]
            )

            if well_col and date_col and constituent_cols:

                # ✅ SAFE melt using temporary column name
                long_df = df.melt(
                    id_vars=[well_col, date_col],
                    value_vars=constituent_cols,
                    var_name="Constituent",
                    value_name="Result_Value"   # ✅ temporary safe name
                )

                # ✅ Rename back to Result AFTER melt
                long_df = long_df.rename(columns={"Result_Value": "Result"})

                st.success("Dataset formatted successfully!")
                st.dataframe(long_df.head(), use_container_width=True)

                st.download_button(
                    label="📥 Download Long Format Excel",
                    data=to_excel(long_df),
                    file_name="long_format_dataset.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            else:
                st.info("Please select all column roles to proceed.")

        except Exception as e:
            st.error(f"Error formatting dataset: {e}")