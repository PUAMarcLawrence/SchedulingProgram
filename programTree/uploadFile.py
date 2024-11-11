import streamlit as st
import os

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
