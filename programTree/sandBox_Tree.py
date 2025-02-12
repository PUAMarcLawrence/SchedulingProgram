import streamlit as st
import time
from pyvis.network import Network
from utils.sandBox_db_utils import copy_table, get_sand_names,load_from_sand_db,format_data_to_Graph,save_data_to_sand_db
from utils.db_utils import get_department_programs,get_program,get_department
from utils.programTree_db_utils import get_table_names

st.set_page_config(layout="wide")

def build_interactive_subject_graph(subjects):
    net = Network(
        height="700px", 
        width="100%", 
        bgcolor="#222222", 
        font_color="white", 
        directed=True, 
        # filter_menu=True,
        select_menu=True,
        cdn_resources='remote'
        )

    net.set_options(
        '''
        {
            "edges": {
                "color": {"inherit": true},
                "smooth": true
            },
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "levelSeparation": 250,
                    "direction": "LR"
                   
                }
            },
            "physics": {
                "hierarchicalRepulsion": {
                    "centralGravity": 8
                },
                "minVelocity": 0.75,
                "solver": "hierarchicalRepulsion"
            }
        }
        '''
    )

    all_subjects = set()
    for semester, semester_subjects in subjects.items():
        for subject in semester_subjects.keys():
            all_subjects.add(subject)
    
    level_map = 1
    for semester, semester_subjects in subjects.items():
        for subject in semester_subjects.keys():
            f_title = f"""[{semester}]
                            {subject}\n"""
            if semester_subjects[subject]['prerequisites'] != []:
                p_req = ", ".join(semester_subjects[subject]['prerequisites'])
                f_title += f"Pre-Req: {p_req}\n"
            if semester_subjects[subject]['corequisites'] != []:
                c_req = ", ".join(semester_subjects[subject]['corequisites'])
                f_title += f"Co-Req: {c_req}\n"
            f_title += f"""Credit: {semester_subjects[subject]['credit_unit']}
                            Care Taker: {semester_subjects[subject]['care_taker']}"""
            net.add_node(
                subject, 
                title = f_title,
                label = subject,
                level = level_map, 
            )
        level_map += 1
    
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            for prereq in details['prerequisites']:
                if prereq in all_subjects:
                    net.add_edge(
                        prereq, 
                        subject, 
                        width=4
                    )
            for coreq in details['corequisites']:
                if coreq in all_subjects:
                    net.add_edge(
                        coreq, 
                        subject, 
                        width=3, 
                        dashes=True)
    
    neighbor_map = net.get_adj_list()

    color_map = {
        0:"#e0f7ff", 1:"#b3e5ff", 2:"#80d4ff", 3:"#4dc3ff", 4:"#1ab2ff", 
        5:"#00aaff", 6:"#ff9966", 7:"#ff6633", 8:"#ff3300", 9:"#ff0000", 
        10:"#ff073a", 
    } #e0f7ff, #b3e5ff, #80d4ff, #4dc3ff, #1ab2ff, #00aaff, #ff9966, #ff6633, #ff3300, #ff0000, #ff073a
    
    subjects_only = {}
    for semester_subjects in subjects.values():
        subjects_only.update(semester_subjects)

    phrases=["2nd year standing","3rd year standing","4th year standing"]
    
    for node in net.nodes:
        for prerequisite in subjects_only[node['id']]['prerequisites']:
            for phrase in phrases:
                if phrase.lower() == prerequisite.lower():
                    node["shape"] = "star"
        node["value"] = len(neighbor_map[node["id"]])
        node["color"] = color_map[node["value"]]
        node["labelHighlightBold"] = "true"
    return net

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
                if select_table == "":
                    st.error("Rquires a curriculum to copy from.")
                else:
                    if copy_table(department,program,st.session_state['ID'],select_table,sand_name):
                        st.success("Table copied successfully")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Sandbox name in use.")
        case "From Scratch":
            sand_name = st.text_input("Enter the sandbox name:",  )
        
open_sandBox = opentabs.multiselect(
    "SandBoxes",
    get_sand_names(st.session_state["ID"]),
    placeholder="Select sandboxes to open",
    help="You can select multiple sandboxes to open"
)
if open_sandBox:
    tabs = st.tabs(open_sandBox)
    for i, tab in enumerate(tabs):
        with tab:
            main,save,settings = st.columns([4.5,0.3,0.3])
            main.write(f"Data for {open_sandBox[i]}")
            subjects = load_from_sand_db(st.session_state['ID'],open_sandBox[i])
            if subjects:
                # semester_tables = format_subjects_for_legend(subjects)
                Edited_data = st.data_editor(
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
                    height=len(subjects) * 35 + 70,
                    num_rows='dynamic',
                    use_container_width=True
                    )
                if save.button("Save"):
                    if save_data_to_sand_db(Edited_data,st.session_state['ID'],open_sandBox[i]):
                        st.success("Saved")
                    else:
                        st.error("Error occured sandBox not saved")
                converted_data = format_data_to_Graph(Edited_data)
                st.components.v1.html(
                    build_interactive_subject_graph(converted_data).generate_html(),
                    height=800
                )
            with settings.popover("",icon="🔧"):
                st.write("Settings")
            