# Description: This file contains the code for the subject chair management system.
import streamlit as st
from utils.db_utils import get_subjectChair_Dean,add_program

def add_DepartmentProgram():
    if st.session_state['new_program']:
        if add_program(st.session_state['new_program'],st.session_state['department_ID']):
            st.success("Program added successfully.")
        else:
            st.error("Program already exists.")

def remove_program():
    if st.session_state['selected_program']:
        if remove_program(st.session_state['selected_program']):
            st.success("Program removed successfully.")
        else:
            st.error("Program does not exist.")

def remove_DepartmentProgram():
    select_box,button = st.columns(2)
    selected_program = select_box.selectbox(
        "Select a Program to remove:",
        get_subjectChair_Dean("Subject Chair",st.session_state['department_ID'])['Program'].unique(),
        key="selected_program")
    button.button(
        "Remove", 
        on_click=remove_program)

def add_new():
    text_box,button = st.columns(2)
    text_box.text_input(
        "Add new Program:", 
        help="Enter a Program Code Example(ECE,CPE,EE etc)",
        key="new_program",
        label_visibility="visible",)
    button.button(
        "Add", 
        on_click=add_DepartmentProgram)

# Main app layout
st.title("Subject Chair List")
option = st.selectbox("Choose an option",["Add New Program","Remove Program"])
if option == "Add New Program":
    add_new()
else:
    remove_DepartmentProgram()
st.dataframe(
    get_subjectChair_Dean("Subject Chair",st.session_state['department_ID']),
        use_container_width=True,
        hide_index=True)