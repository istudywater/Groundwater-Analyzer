import streamlit as st
import pandas as pd
from io import BytesIO

from core import load_data
from max_min_analysis import analyze_max_min_nd

def max_detection_app():

    st.title("📈 Max Detection Summary Tool")

    uploaded_file = st.file_uploader("📥 Upload lab data file", type=["xlsx"])

    if uploaded_file:
        try:
            df = load_data(uploaded_file)
            st.success("✅ File loaded successfully.")

            st.markdown("### 🔧 Select Columns")
            col1, col2 = st.columns(2)

            with col1:
                well_col = st.selectbox("Well ID Column", df.columns)
                analyte_col = st.selectbox("Analyte Column", df.columns)

            with col2:
                result_col = st.selectbox("Result Column", df.columns)
                date_col = st.selectbox("Date Column", df.columns)

            if st.button("🚀 Run Max/Min Detection Summary"):
                summary_df, nd_only, nd_statement = analyze_max_min_nd(
                    df,
                    well_col=well_col,
                    analyte_col=analyte_col,
                    result_col=result_col,
                    date_col=date_col
                )

                st.subheader("📊 Summary Table")
                st.dataframe(summary_df, use_container_width=True)

                st.markdown(f"**{nd_statement}**")

                st.download_button(
                    "📥 Download as CSV",
                    summary_df.to_csv(index=False),
                    file_name="max_detection_summary.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ Error: {e}")