# Description: This file contains the code for the subject chair management system.
import streamlit as st
from utils.dean_db_utils import get_subjectChair_Dean, delete_program_dean, modify_program_dean
from utils.db_utils import add_program

def add_DepartmentProgram():
    if st.session_state['new_program']:
        if add_program(st.session_state['new_program'],st.session_state['department_ID']):
            st.success("Program added successfully.")
        else:
            st.error("Program already exists.")

# Main app layout
st.title("Subject Chair List")
text_box,button,modify = st.columns([3,0.3,0.6])
text_box.text_input(
    "Add new Program:", 
    help="Enter a Program Code Example(ECE,CPE,EE etc)",
    value=None,
    key="new_program",
    label_visibility="visible",)
button.button(
    "➕", 
    on_click=add_DepartmentProgram,
    disabled=st.session_state['new_program'] == None)
original_data = get_subjectChair_Dean("Subject Chair",st.session_state['department_ID'])
st.dataframe(
    original_data,
    column_config={
        "program": st.column_config.Column(
            "Program",
        ),
        "username": st.column_config.Column(
            "Program Chair",
        ),
        "program_ID": None
    },
    use_container_width=True,
    hide_index=True)

with modify.popover("Modify"):
    option = st.selectbox(
        "Select",
        ("Modify","Delete"),
        label_visibility="collapsed"
    )
    program = st.selectbox(
        "Select a program to modify/delete",
        (original_data[original_data['username'].isna()]['program']),
        help="If the program is not in the list, that means a user is already assigned to it.",
    )
    if option == "Modify":
        new_program = st.text_input(
            "New Program Name",
            label_visibility="visible",
            help="Enter a Program Code Example(ECE,CPE,EE etc)"
        )
    if st.button(option):
        if option == "Modify":
            if modify_program_dean(program,new_program):
                st.success("Modified")
                st.rerun()
            else:
                st.error("Program name already exists.")
        else:
            if delete_program_dean(program):
                st.success("Deleted")
                st.rerun()
            else:
                st.error("An error occurred.")
    st.warning("This action cannot be UNDONE!")

