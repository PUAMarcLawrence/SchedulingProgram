import streamlit as st
import os
import pandas as pd
from datetime import datetime
from utils.upload_db_utils import upload_to_database,get_existing_curriculum
from utils.db_utils import get_department_programs,get_program

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
    prog_select,year_select = st.columns(2)
    program_name = prog_select.text_input("Enter the Program")
    years = list(range(datetime.now().year - 15, datetime.now().year + 15))
    selected_year = year_select.selectbox("Batch:", years, index=len(years) - 15)
    program_batch = f"{program_name.upper()}_{str(selected_year)}"
    if st.session_state['role'] == "Dean":
        program = st.selectbox(
            "Select Program to Uplaod to:",
            get_department_programs(st.session_state['department_ID'])
        )
    else:
        program = get_program(st.session_state['program_ID'])
    if get_existing_curriculum(st.session_state['department_ID'],program,program_batch):
        st.warning(f"{program_batch} already EXISTS, this would OVERWRITE the {program_batch} curriculum in the database", icon="⚠️")
    try:
        data = pd.read_excel(uploaded_file)
        st.write("Editable preview of Excel data:")
        Edited_data = st.data_editor(
            data,
            use_container_width=True,
            height=len(data) * 35 + 70,
            num_rows='dynamic'
        )
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
    st.warning(f"Please make sure that you double check the data before uploading. If YEAR, TERM, COURSE CODE are NONE/Blank would NOT be recorded", icon="⚠️")
    
    if st.button("Upload Curiculum",disabled= program_name == None or selected_year == None or program == None):
        if program_name and selected_year and program:
            if upload_to_database(Edited_data,st.session_state['department_ID'],program,program_batch):
                st.success("Uploaded")
            else:
                st.error("Failed to Upload Curiculum")
        else:
            st.error("Fill up the Required Fields")