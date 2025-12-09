import streamlit as st
import pandas as pd
from io import BytesIO

def extract_numeric(value):
    try:
        value_str = str(value).strip()
        if value_str.startswith("<"):
            return float(value_str[1:])
        elif value_str.upper() == "ND":
            return None
        else:
            val = float(value_str)
            return val if val > 0 else None
    except:
        return None

def is_non_detect(value):
    value_str = str(value).strip().upper()
    return value_str == "ND" or value_str.startswith("<")

def clean_result_column(df, result_col):
    df[result_col] = df[result_col].astype(str).str.strip()
    df[result_col] = df[result_col].str.replace("<<", "<", regex=False)
    df[result_col] = df[result_col].replace("", "ND")
    return df

def get_lowest_non_detect(subset, result_col, well_col, date_col):
    nd_values = subset[result_col].astype(str).str.strip()
    nd_values = nd_values[nd_values.str.startswith("<")]

    if not nd_values.empty:
        nd_numeric = nd_values.str[1:].astype(float)
        min_index = nd_numeric.idxmin()
        return (
            subset.loc[min_index, result_col],
            subset.loc[min_index, well_col],
            pd.to_datetime(subset.loc[min_index, date_col]).date(),
        )
    else:
        return "BDL", "Not Applicable", "Not Applicable"

def generate_max_min_summary(df, date_col, well_col, constituent_col, result_col):
    df = clean_result_column(df, result_col)
    summary_data = []
    nd_constituents = []

    for constituent in df[constituent_col].unique():
        subset = df[df[constituent_col] == constituent].copy()
        subset["Numeric"] = subset[result_col].apply(extract_numeric)
        subset["Is_ND"] = subset[result_col].apply(is_non_detect)

        # ✅ CORRECT 100% ND LOGIC
        all_nd = subset["Is_ND"].all()

        if all_nd:
            min_val, min_loc, min_date = get_lowest_non_detect(
                subset, result_col, well_col, date_col
            )
            nd_constituents.append(constituent)

            summary_data.append({
                "Constituent": constituent,
                "Max Value": "BDL",
                "Well ID of Max": "Not Applicable",
                "Date of Max": "Not Applicable",
                "Min Value": min_val,
                "Well ID of Min": min_loc,
                "Date of Min": min_date,
                "100% NDs": "Yes"
            })
            continue

        # ✅ MAX (true detection only)
        max_row = subset.loc[subset["Numeric"].idxmax()]
        max_val = max_row[result_col]
        max_loc = max_row[well_col]
        max_date = pd.to_datetime(max_row[date_col]).date()

        # ✅ MIN (true numeric min or lowest < value)
        valid_min_df = subset[subset["Numeric"].notna() & (subset["Numeric"] > 0)]

        if not valid_min_df.empty:
            min_row = valid_min_df.loc[valid_min_df["Numeric"].idxmin()]
            min_val = min_row[result_col]
            min_loc = min_row[well_col]
            min_date = pd.to_datetime(min_row[date_col]).date()
        else:
            min_val, min_loc, min_date = get_lowest_non_detect(
                subset, result_col, well_col, date_col
            )

        summary_data.append({
            "Constituent": constituent,
            "Max Value": max_val,
            "Well ID of Max": max_loc,
            "Date of Max": max_date,
            "Min Value": min_val,
            "Well ID of Min": min_loc,
            "Date of Min": min_date,
            "100% NDs": ""
        })

    summary_df = pd.DataFrame(summary_data)

    # ✅ 100% ND SUMMARY STATEMENT
    if nd_constituents:
        nd_list = ", ".join(nd_constituents)
        nd_summary = f"The following constituents resulted in 100% non-detect values: {nd_list}."
    else:
        nd_summary = "No constituents resulted in 100% non-detects."

    return summary_df, nd_summary

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Summary")
    output.seek(0)
    return output

def max_detection_app():
    st.header("🧪 Max & Min Detection Summary")

    uploaded_file = st.file_uploader("Upload long-format Excel/CSV file", type=["xlsx", "xls", "csv"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("File uploaded successfully.")

            with st.expander("Step 1: Select Columns"):
                date_col = st.selectbox("Select Date Column", df.columns)
                well_col = st.selectbox("Select Well ID Column", df.columns)
                constituent_col = st.selectbox("Select Constituent Column", df.columns)
                result_col = st.selectbox("Select Result Column", df.columns)

            summary_df, nd_summary = generate_max_min_summary(
                df, date_col, well_col, constituent_col, result_col
            )

            st.success("Summary generated successfully.")
            st.dataframe(summary_df, use_container_width=True)
            st.info(nd_summary)

            st.download_button(
                label="📥 Download Summary Excel",
                data=to_excel(summary_df),
                file_name="max_detection_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"Error generating summary: {e}")