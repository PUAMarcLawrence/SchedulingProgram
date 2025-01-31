# Description: This file contains the code for the subject chair management system.
import streamlit as st
from utils.db_utils import get_subjectChair_Dean,add_program

def add_DepartmentProgram():
    if st.session_state['new_program']:
        if add_program(st.session_state['new_program'],st.session_state['department_ID']):
            st.success("Program added successfully.")
        else:
            st.error("Program already exists.")

# def remove_DepartmentProgram():

def add_new():
    # Input box for adding new items
    text_box,button = st.columns(2)
    text_box.text_input(
        "Add new Program:", 
        help="Enter a Program Code Example(ECE,CPE,EE etc)",
        key="new_program",
        label_visibility="visible")
    button.button(
        "Add", 
        on_click=add_DepartmentProgram)
    button.button(
        "Remove", 
        on_click=st.rerun)


# Main app layout
st.title("Subject Chair List")

add_new()

st.dataframe(
    get_subjectChair_Dean("Subject Chair",st.session_state['department_ID']),
        use_container_width=True,
        hide_index=True)
        # num_rows="dynamic")