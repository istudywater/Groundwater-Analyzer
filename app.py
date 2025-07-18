import streamlit as st
from gw_summary.core import generate_gw_summary
import io
import pandas as pd

st.title("Groundwater Monitoring Summary")

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
