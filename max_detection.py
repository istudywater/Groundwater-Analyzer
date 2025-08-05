import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64

def max_detection_app():
    st.title("🔍 Max Detection App")
    st.write("Upload a cleaned long-format groundwater monitoring dataset to calculate min/max detections and identify exceedances.")

    uploaded_file = st.file_uploader("Upload Long Format Dataset (.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            # Standardize column names
            df.columns = [col.strip() for col in df.columns]
            required_cols = ['Well ID', 'Date', 'Constituent', 'Result']
            if not all(col in df.columns for col in required_cols):
                st.error(f"Dataset must contain the following columns: {required_cols}")
                return

            # Clean the 'Result' column
            df['Result'] = df['Result'].astype(str).str.strip()
            df['Result'] = df['Result'].str.replace('<<', '<', regex=False)
            df['Result'] = df['Result'].replace('', 'NR')

            # Create new numeric result column
            def parse_numeric(val):
                try:
                    if val in ["ND", "NR"]:
                        return np.nan
                    if isinstance(val, str) and val.startswith('<'):
                        return float(val.replace('<', '').strip())
                    return float(val)
                except:
                    return np.nan

            df['Numeric Result'] = df['Result'].apply(parse_numeric)

            if df['Numeric Result'].dropna().empty:
                st.error("No valid data rows found after cleaning. Please check the column mappings and data values.")
                return

            # Compute min/max for each constituent and well
            grouped = df.groupby(['Constituent', 'Well ID'])['Numeric Result'].agg(['min', 'max']).reset_index()
            grouped = grouped.rename(columns={'min': 'Min Detection', 'max': 'Max Detection'})

            st.success("Summary statistics generated successfully.")
            st.dataframe(grouped)

            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Summary')
                processed_data = output.getvalue()
                return processed_data

            st.download_button(
                label="📥 Download Summary Excel",
                data=to_excel(grouped),
                file_name='max_detection_summary.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.error(f"Error processing file: {e}")
