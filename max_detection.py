import streamlit as st
import pandas as pd
from io import BytesIO

def clean_result_column(df, result_col):
    """Clean the 'Result' column."""
    df[result_col] = df[result_col].astype(str).str.strip()
    df[result_col] = df[result_col].str.replace("<<", "<", regex=False)
    df[result_col] = df[result_col].replace("", "NR")
    return df

def extract_numeric(value):
    """Extract numeric value for comparison."""
    try:
        if pd.isna(value):
            return None
        value_str = str(value).strip()
        if value_str.startswith("<"):
            return float(value_str[1:])
        elif value_str.upper() in ["ND", "NS", "NR", ""]:
            return None
        else:
            return float(value_str)
    except:
        return None

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Summary")
    output.seek(0)
    return output

def max_detection_app():
    st.header("🧪 Max & Min Detection Summary")

    uploaded_file = st.file_uploader("Upload formatted long-format Excel file", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully.")

            with st.expander("Step 1: Select Columns"):
                date_col = st.selectbox("Select Date Column", df.columns)
                well_col = st.selectbox("Select Well ID Column", df.columns)
                constituent_col = st.selectbox("Select Constituent Column", df.columns)
                result_col = st.selectbox("Select Result Column", df.columns)

            df = clean_result_column(df, result_col)
            summary_data = []

            for constituent in df[constituent_col].unique():
                subset = df[df[constituent_col] == constituent].copy()
                subset["Numeric"] = subset[result_col].apply(extract_numeric)

                # Max detection
                max_row = subset.loc[subset["Numeric"].idxmax()] if subset["Numeric"].notna().any() else None
                max_val = max_row[result_col] if max_row is not None else "No Data"
                max_loc = max_row[well_col] if max_row is not None else "Not Applicable"
                max_date = pd.to_datetime(max_row[date_col]).date() if max_row is not None else "Not Applicable"

                # Min detection logic (refined)
                numeric_vals = subset["Numeric"].dropna()
                if not numeric_vals.empty:
                    min_val_numeric = numeric_vals.min()
                    min_row = subset[subset["Numeric"] == min_val_numeric].iloc[0]
                    min_val = min_row[result_col]
                    min_loc = min_row[well_col]
                    min_date = pd.to_datetime(min_row[date_col]).date()
                else:
                    min_val = "No Data"
                    min_loc = "Not Applicable"
                    min_date = "Not Applicable"

                summary_data.append({
                    "Constituent": constituent,
                    "Max Value": max_val,
                    "Well ID of Max": max_loc,
                    "Date of Max": max_date,
                    "Min Value": min_val,
                    "Well ID of Min": min_loc,
                    "Date of Min": min_date,
                })

            summary_df = pd.DataFrame(summary_data)

            st.success("Summary generated successfully.")
            st.dataframe(summary_df, use_container_width=True)

            st.download_button(
                label="📅 Download Summary Excel",
                data=to_excel(summary_df),
                file_name="max_detection_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"Error generating summary: {e}")
