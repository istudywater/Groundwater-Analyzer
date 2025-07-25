import streamlit as st
from gw_summary.core import generate_gw_summary
import io
import pandas as pd
import os

st.title("Groundwater Quality Analyzer")

st.markdown("This webapp takes two input files (laboratory results and facility-specific groundwater protection standards) and generates a summary table of detections and comparison to the GWPS values. For the laboratory data, the required header names are: Client Sample ID, Results and High Limit. Client Sample ID is the monitoring well ID, Result is for the detection and High Limit is the detection limit. The detection limit is used to convert ND values to < detection limit values. Additionally, monitoring well ID must be added manually. For the GWPS workbook, the webapp is looking for columns with the constituent name and another for the GWPS value.")

lab_file = st.file_uploader("Upload Lab Data (.xlsx)", type=["xlsx","xls"])
gwps_file = st.file_uploader("Upload GWPS Table (.xlsx)", type=["xlsx","xls"])
wells = st.text_input("Well IDs (comma separated)", "MW-1,MW-2,MW-3,MW-4,MW-5,MW-6")
run = st.button("Run Summary")

if run:
    if not lab_file or not gwps_file:
        st.error("Please upload both files before running the summary.")
    else:
        # 1) Read uploads into in-memory buffers
        lab_buffer  = io.BytesIO(lab_file.read())
        gwps_buffer = io.BytesIO(gwps_file.read())

        # 2) Prepare an in-memory output buffer
        output_buffer = io.BytesIO()

        # 3) Call your core function, passing file-like and in-memory buffer
        try:
            generate_gw_summary(
                lab_source=lab_buffer,
                gwps_source=gwps_buffer,
                output_path=output_buffer,  # pandas will write here
                wells=[w.strip() for w in wells.split(",") if w.strip()],
                sheet_name=None
            )
        except Exception as e:
            st.error(f"Error generating summary: {e}")
        else:
            # 4) Seek back to start of the buffer and offer download
            output_buffer.seek(0)
            st.success("Summary generated! Download below:")
            st.download_button(
                label="Download Summary",
                data=output_buffer,
                file_name="GW_Summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ——— Sample dataset downloads ———
st.markdown("### 🔍 Download Sample Datasets")

# 1) Lab data template
lab_template_path = os.path.join(os.getcwd(), "lab_data_sample.xlsx")
with open(lab_template_path, "rb") as f:
    lab_bytes = f.read()

st.download_button(
    label="📥 Download sample lab data",
    data=lab_bytes,
    file_name="lab_data_sample.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 2) GWPS template
gwps_template_path = os.path.join(os.getcwd(), "gwps.xlsx")
with open(gwps_template_path, "rb") as f:
    gwps_bytes = f.read()

st.download_button(
    label="📥 Download sample GWPS",
    data=gwps_bytes,
    file_name="gwps.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")

# … rest of your upload widgets and processing logic …

# ——— Links ———
st.markdown("To report issues, please contact me via LinkedIn.")
st.markdown("To share your opinion of this webapp, please use the [feedback form](https://docs.google.com/forms/d/e/1FAIpQLSee-rxz_gHT8JACxRr62wHWgb8np3qBsZIGMP8GM9R3NnUv_g/viewform?usp=header)")
st.markdown("Vibe coded by Bryan B. Smith  "  
    "[🔗 GitHub](https://github.com/istudywater/groundwater-analyzer) | "
    "[🔗 LinkedIn](https://www.linkedin.com/in/istudywater/)")