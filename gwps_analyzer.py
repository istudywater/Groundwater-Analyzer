# app.py

import streamlit as st
import pandas as pd
import io
from core import generate_gw_summary

st.set_page_config(page_title="GW Analyzer", layout="wide")

def gwps_analyzer_app():
    st.title("🌊 Groundwater Monitoring Summary Tool")

    # --------------------------------------------------------------
    # 1) Downloadable Sample Templates (place your sample .xlsx files
    #    in the same folder as this script: lab_data_template.xlsx,
    #    gwps_template.xlsx, wells_template.xlsx)
    # --------------------------------------------------------------
    st.markdown("## 🔍 Download Sample Lab Data")
    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            with open("lab_data_sample.xlsx", "rb") as f:
                lab_bytes = f.read()
            st.download_button(
                label="📥 Lab Data Sample",
                data=lab_bytes,
                file_name="lab_data_sample.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except FileNotFoundError:
            st.error("`lab_data_sample.xlsx` not found.")

    with col2:
        try:
            with open("gwps.xlsx", "rb") as f:
                gwps_bytes = f.read()
            st.download_button(
                label="📥 GWPS Example",
                data=gwps_bytes,
                file_name="gwps.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except FileNotFoundError:
            st.error("`gwps.xlsx` not found.")

    with col3:
        try:
            with open("wells_example.xlsx", "rb") as f:
                wells_bytes = f.read()
            st.download_button(
                label="📥 Wells List Example",
                data=wells_bytes,
                file_name="wells_example.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except FileNotFoundError:
            st.error("`wells_example.xlsx` not found.")

    st.markdown("---")

    # --------------------------------------------------------------
    # 2) Instructions
    # --------------------------------------------------------------
    st.markdown("### 📝 Instructions")
    st.markdown("""
    1. **Download** and populate the templates above.  
    2. **Upload** your completed Lab Data, GWPS table, and (optionally) Wells List.  
    3. Click **Run Summary** to process and view results.  
    4. **Download** or **copy/paste** the summary table below.
    """)

    # --------------------------------------------------------------
    # 3) File Uploaders
    # --------------------------------------------------------------
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        st.markdown("#### 1. Upload Lab Data (.xlsx/.xls)")
        lab_file = st.file_uploader(
            label="",
            type=["xlsx", "xls"],
            key="lab"
        )

    with col2:
        st.markdown("#### 2. Upload GWPS Table (.xlsx/.xls)")
        gwps_file = st.file_uploader(
            label="",
            type=["xlsx", "xls"],
            key="gwps"
        )

    with col3:
        st.markdown("#### 3. Upload Wells List (optional)")
        wells_file = st.file_uploader(
            label="",
            type=["xlsx", "xls", "csv"],
            key="wells"
        )

    # --------------------------------------------------------------
    # 4) Run Summary
    # --------------------------------------------------------------
    if st.button("🚀 Run Summary"):
        if not lab_file or not gwps_file:
            st.error("Please upload both Lab Data and GWPS files.")
        else:
            try:
                # Read uploads into in-memory buffers
                lab_buffer  = io.BytesIO(lab_file.read())
                gwps_buffer = io.BytesIO(gwps_file.read())
                wells_buffer = None
                if wells_file:
                    wells_buffer = io.BytesIO(wells_file.read())

                # Generate summary DataFrame (no file write)
                df_summary = generate_gw_summary(
                    lab_source=lab_buffer,
                    gwps_source=gwps_buffer,
                    output_path=None,
                    wells=None,
                    wells_source=wells_buffer,
                    sheet_name=None
                )

                st.success("✅ Summary generated below!")
                # --------------------------------------------------------------
                # 5) Display for copy/paste
                # --------------------------------------------------------------
                st.markdown("#### Summary Table (copy/paste below)")
                st.dataframe(df_summary, use_container_width=True)

                # --------------------------------------------------------------
                # 6) Download as Excel
                # --------------------------------------------------------------
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    df_summary.to_excel(writer, index=True, sheet_name="Summary")
                excel_buffer.seek(0)

                st.download_button(
                    label="📥 Download Summary as Excel",
                    data=excel_buffer,
                    file_name="GW_Summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Error generating summary: {e}")

    st.markdown("---")

    # --------------------------------------------------------------
    # 7) Footer Links
    # --------------------------------------------------------------
    # ——— Links ———
    st.markdown("To report issues, please contact me via [🔗 LinkedIn](https://www.linkedin.com/in/istudywater/).")
    st.markdown("To share your opinion of this webapp, please use the [feedback form](https://docs.google.com/forms/d/e/1FAIpQLSee-rxz_gHT8JACxRr62wHWgb8np3qBsZIGMP8GM9R3NnUv_g/viewform?usp=header)")
    st.markdown("Vibe coded by Bryan B. Smith  "  
        "[🔗 GitHub](https://github.com/istudywater/groundwater-analyzer) | "
        "[🔗 LinkedIn](https://www.linkedin.com/in/istudywater/)")