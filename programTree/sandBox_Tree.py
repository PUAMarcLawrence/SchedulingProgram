import streamlit as st
import time
from utils.sandBox_db_utils import copy_table, get_sand_names
from utils.db_utils import get_department_programs,get_program,get_department
from utils.programTree_db_utils import get_table_names
st.set_page_config(layout="wide")

opentabs,createtabs = st.columns([4,1])
with createtabs.popover("New Sandbox"):
    option = st.selectbox("Sandbox Options", ("Open Existing Sandbox", "Create New Sandbox"))
    match option:
        case "Create New Sandbox":
            sub_option = st.selectbox("Options", ("From Scratch", "Copy from existing curriculum"))
            match sub_option:
                case "Copy from existing curriculum":
                    if st.session_state['role'] == "Dean":
                        program = st.selectbox(
                            "Select Program to view:",
                            get_department_programs(st.session_state['department_ID'])
                        )
                    else:
                        program = st.session_state['program_ID']
                        program = get_program(program)
                    department = get_department(st.session_state['department_ID'])
                    tables = get_table_names(st.session_state['department_ID'],program)
                    select_table = st.selectbox('Select a curriculum:',tables)
                    sand_name = st.text_input("Enter the sandbox name:",  )
                    if st.button("Create Sandbox"):
                        if select_table == "":
                            st.error("Rquires a curriculum to copy from.")
                        else:
                            if copy_table(department,program,st.session_state['ID'],select_table,sand_name):
                                st.success("Table copied successfully")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("Sandbox name in use.")
        case "Open Existing Sandbox":
            st.write("Open Existing Sandbox")
        case _:
            st.write("Invalid Option")

open_sandBox = opentabs.multiselect(
    "SandBoxes",
    get_sand_names(st.session_state["ID"]),
    placeholder="Select sandboxes to open",
    help="You can select multiple sandboxes to open"
)
if open_sandBox:
    tabs = st.tabs(open_sandBox)