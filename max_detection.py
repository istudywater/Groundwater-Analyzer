import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Max Detection Summary", layout="wide")

def max_detection_app():
    st.title("📊 Max Detection Summary")

    # Upload raw lab data
    uploaded_file = st.file_uploader("Upload your formatted lab dataset (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            # Select required columns
            st.markdown("### 🔧 Column Selection")
            well_col = st.selectbox("Select Well ID Column", df.columns, index=0)
            date_col = st.selectbox("Select Sample Date Column", df.columns, index=1)
            analyte_col = st.selectbox("Select Constituent/Analyte Column", df.columns, index=2)
            result_col = st.selectbox("Select Result Column", df.columns, index=3)

            if st.button("▶️ Generate Max Detection Summary"):
                # Clean up and flag ND
                df['Analyte'] = df[analyte_col].astype(str).str.strip()
                df['Well'] = df[well_col].astype(str).str.strip()
                df['ResultRaw'] = df[result_col].astype(str).str.strip()

                # Flag non-detects: "ND" or values starting with "<"
                df['Is_ND'] = df['ResultRaw'].str.upper().eq("ND") | df['ResultRaw'].str.startswith("<")

                # Effective value: for ND values, use the numeric portion after "<" or NaN; else float(ResultRaw)
                def extract_effective(val, is_nd):
                    try:
                        if is_nd:
                            if val.startswith("<"):
                                return float(val.replace("<", "").strip())
                            return float("nan")  # For plain ND
                        else:
                            return float(val)
                    except:
                        return float("nan")

                df['Effective'] = df.apply(lambda row: extract_effective(row['ResultRaw'], row['Is_ND']), axis=1)

                # Aggregate
                summary = df.groupby('Analyte').agg(
                    Min_Effective=('Effective', 'min'),
                    Max_Effective=('Effective', 'max'),
                    Count=('Effective', 'count'),
                    ND_Count=('Is_ND', 'sum')
                ).reset_index()

                # Add ND flag and formatted columns
                summary["100% NDs"] = summary["Count"] == summary["ND_Count"]
                summary["100% NDs"] = summary["100% NDs"].apply(lambda x: "Yes" if x else "")
                summary["Min"] = summary.apply(
                    lambda row: f"<{row.Min_Effective:.2f}" if row["100% NDs"] == "Yes" or row.Min_Effective == row.Max_Effective else f"{row.Min_Effective:.2f}", axis=1
                )
                summary["Max"] = summary.apply(
                    lambda row: "BDL" if row["100% NDs"] == "Yes" else f"{row.Max_Effective:.2f}", axis=1
                )

                # Reorder and clean
                summary_df = summary[["Analyte", "Min", "Max", "100% NDs"]]

                st.success("✅ Summary generated below:")
                st.dataframe(summary_df, use_container_width=True)

                # Output statement
                all_nd = summary_df[summary_df["100% NDs"] == "Yes"]["Analyte"].tolist()
                if all_nd:
                    nd_statement = "The following constituents resulted in 100% non-detect values: " + ", ".join(all_nd) + "."
                    st.markdown(f"📌 **{nd_statement}**")
                else:
                    st.markdown("📌 **All constituents had at least one detected value.**")

                # Download button
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Max Summary")
                excel_buffer.seek(0)

                st.download_button(
                    label="📥 Download Summary as Excel",
                    data=excel_buffer,
                    file_name="Max_Summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ Error: {e}")

# Run the app if executed as main
if __name__ == "__main__":
    max_detection_app()