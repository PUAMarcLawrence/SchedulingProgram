import streamlit as st
import os
import pandas as pd
from datetime import datetime
from utils.db_utils import upload_to_sqlite

# Set the name of the template file
template_file_name = "template/Curiculum.xlsx"

# Display a title and some instructions
# st.title("Download Template Excel File")


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
    program = st.selectbox("Choose a Program",st.session_state['editable_list'])
    years = list(range(datetime.now().year - 15, datetime.now().year + 15))
    selected_year = st.selectbox("Select Year:", years, index=len(years) - 1)
    if st.button("Upload Curiculum"):
        if upload_to_sqlite(uploaded_file,program,str(selected_year)):
           st.write("Uploaded")
        else:
            st.eror("Data Upload Failed")
    # Load data from the uploaded Excel file
    try:
        data = pd.read_excel(uploaded_file)
        # Display data preview
        st.write("Preview of Excel data:")
        st.dataframe(data)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
    
