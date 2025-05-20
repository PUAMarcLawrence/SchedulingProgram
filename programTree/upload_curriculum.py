import streamlit as st
import os
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# Set the name of the template file
template_file_name = "template/Curiculum.xlsx"

if 'editable_list' not in st.session_state:
    st.session_state['editable_list'] = []

st.write("Click the button below to download the template Excel file.")

# Check if the template file exists in the program directory
if os.path.exists(template_file_name):
    # Button to download the template Excel file
    with open(template_file_name, "rb") as file:
        file_bytes = file.read()
        st.download_button(
            label="Download Template Excel File",
            data=file_bytes,
            file_name=template_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.error(f"Template file '{template_file_name}' not found in the program directory.")

uploaded_file = st.file_uploader(
    "Choose a xlsx file", 
    accept_multiple_files=False,
    type=["xlsx","xls"]
)

if uploaded_file is not None:
    with st.form("Upload"):
        program_select, year_select = st.columns(2)
        program_code = program_select.text_input("Program Code",help="e.g. ECE, CPE, EE, etc.",value=None,placeholder=st.session_state['program'])
        batch_year = year_select.number_input("Batch Year", min_value=1900, value=2025, step=1)
        if st.form_submit_button("Upload"):
            st.success("File uploaded successfully!")
            