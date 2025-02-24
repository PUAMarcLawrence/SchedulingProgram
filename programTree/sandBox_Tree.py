import streamlit as st
import time
from utils.sandBox_db_utils import copy_table, get_sand_names,load_from_sand_db,format_data_to_Graph,save_data_to_sand_db, create_scratch_sandbox, rename_sandBox,delete_sandBox
from utils.db_utils import get_department_programs,get_program,get_department
from utils.quickView_db_utils import get_table_names
from utils.graph_utils import build_interactive_subject_graph

st.set_page_config(layout="wide")

opentabs,createtabs = st.columns([4,1])
with createtabs.popover("Create Sandbox"):
    option = st.selectbox("Options", ("From Scratch", "Copy from existing curriculum"))
    match option:
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
                if select_table == None:
                    st.error("Requires a curriculum to copy from.")
                elif sand_name == None:
                    st.error("Requires a name for the sandBox")
                else:
                    if copy_table(department,program,st.session_state['ID'],select_table,sand_name):
                        st.success("Curriculum copied successfully")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Sandbox name in use.")
        case "From Scratch":
            sand_name = st.text_input("Enter the sandbox name:",  )
            if st.button("Create Sandbox"):
                if sand_name == "":
                    st.error("Requires a name for the sandBox")
                else:
                    if create_scratch_sandbox(st.session_state['ID'],sand_name):
                        st.success("sandbox creation Successfully")
                    else:
                        st.error("Sandbox creation failed")
        
open_sandBox = opentabs.multiselect(
    "SandBoxes",
    get_sand_names(st.session_state["ID"]),
    placeholder="Select sandboxes to open",
    help="You can select multiple sandboxes to open"
)
Edited_data = {}
if open_sandBox:
    tabs = st.tabs(open_sandBox)
    for i, tab in enumerate(tabs):
        with tab:
            main,save,settings = st.columns([4.5,0.5,0.3])
            subjects = load_from_sand_db(st.session_state['ID'],open_sandBox[i])
            if subjects:
                st.info('In entering year standings as a pre-requisite use the entire spelling with spaces ex.(2nd year standing)', icon="ℹ️")
                Edited_data[i] = st.data_editor(
                    subjects,
                    column_config={
                        "0":st.column_config.NumberColumn(
                            "Year",
                            width='small'
                        ),
                        "1":st.column_config.NumberColumn(
                            "Sem",
                            width='small'
                        ),
                        "2":st.column_config.TextColumn(
                            "Code",
                            width='small'
                        ),
                        "3":st.column_config.TextColumn(
                            "Title",
                            width='medium'
                        ),
                        "4":st.column_config.NumberColumn(
                            "Lec Hrs",
                            width='small'
                        ),
                        "5":st.column_config.NumberColumn(
                            "Lab Hrs",
                            width='small'
                        ),
                        "6":st.column_config.NumberColumn(
                            "Credit",
                            width='small'
                        ),
                        "7":st.column_config.TextColumn(
                            "Pre-Requisite",
                            width='medium'
                        ),
                        "8":st.column_config.TextColumn(
                            "Co-Requisite",
                            width='medium'
                        ),
                        "9":st.column_config.TextColumn(
                            "Care Taker",
                            width='small'
                        ),
                    },
                    height=len(subjects) * 35 + (70),
                    num_rows='dynamic',
                    use_container_width=True,
                    key=f"Editor_{open_sandBox[i]}"
                    )
                if save.button("Save",key=f"Button_{open_sandBox[i]}"):
                    if save_data_to_sand_db(Edited_data[i],st.session_state['ID'],open_sandBox[i]):
                        st.success("Saved")
                    else:
                        st.error("Error occured sandBox not saved")
                converted_data = format_data_to_Graph(Edited_data[i])
                st.components.v1.html(
                    build_interactive_subject_graph(converted_data).generate_html(),
                    height=800
                )
            with settings.popover("",icon="⚙️"):
                st.write("Settings")
                option = st.selectbox(
                    "Options",
                    ("Transfer to Active","Rename","Delete"),
                    label_visibility='collapsed',
                    key=f"SettingBox_{open_sandBox[i]}"
                )
                match option:
                    # case "Transfer to Active":
                    #     sub_option = st.selectbox("SubOptions",("Existing","New Curriculum"),label_visibility='collapsed',key=f"Transfer_setting_{open_sandBox[i]}")
                    #     match sub_option:
                    #         case "Existing":
                    #             selected_exist_curriculum = st.selectbox("Existing Curriculum",)
                    #         case "New Curriculum":
                    case "Rename":
                        new_sandbox_name = st.text_input("New SandBox Name",label_visibility='collapsed',placeholder=open_sandBox[i],key=f"new_name_textBox_{open_sandBox[i]}")
                        if st.button("Rename",key=f"rename_button_{open_sandBox[i]}"):
                            rename_sandBox(st.session_state['ID'],open_sandBox[i],new_sandbox_name)
                            st.rerun()
                    case "Delete":
                        if st.button("Delete",key=f"delete_button_{open_sandBox[i]}"):
                            delete_sandBox(st.session_state['ID'],open_sandBox[i])
                            st.rerun()
                        st.warning("This action cannot be UNDONE!", icon="⚠️")