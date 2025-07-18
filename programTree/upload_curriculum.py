import streamlit as st
import os
import pandas as pd
from utils.db_utils import upload_to_database

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
    try:
        data = pd.read_excel(uploaded_file)
        st.warning("Please make sure that you double check the data before uploading.")
        st.warning("If YEAR, TERM, COURSE CODE are NONE/Blank would NOT be recorded", icon="⚠️")
        st.write("Editable preview of Excel data:")
        Edited_data = st.data_editor(
            data,
            use_container_width=True,
            height=len(data) * 35 + 70,
            num_rows='dynamic'
        )
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
    with st.form("Upload"):
        st.subheader("Upload Curriculum to Database")
        program_select, year_select = st.columns(2)
        program_code = program_select.text_input("Program Code",help="e.g. ECE, CPE, EE, etc.",value=None,placeholder=st.session_state['program'])
        if program_code:
            program_code = program_code.upper().replace(" ", "")
        batch_year = year_select.number_input("Batch Year", min_value=1900, value=2025, step=1)
        program_batch = f"{program_code}_{str(batch_year)}"
        if st.form_submit_button("Upload"):
            if program_code and batch_year:
                upload_result = upload_to_database(Edited_data, st.session_state['department'], st.session_state['program'], program_batch)
                if upload_result.get("status"):
                    st.success(upload_result.get("message"))
                else:
                    st.error(upload_result.get("message"))
            else:
                st.error("Enter a VALID program code and batch year")

            