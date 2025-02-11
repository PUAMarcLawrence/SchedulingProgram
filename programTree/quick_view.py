import streamlit as st
import pandas as pd
from pyvis.network import Network
from utils.programTree_db_utils import get_table_names,load_subjects_from_db
from utils.db_utils import get_department_programs,get_program

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
                f_title += f"Pre-Req: {c_req}\n"
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

def format_subjects_for_legend(subjects):
    semester_tables = {}
    for semester, semester_subjects in subjects.items():
        legend_data = []
        for subject, details in semester_subjects.items():
            title = details['title']
            prerequisites = ', '.join(details['prerequisites']) if details['prerequisites'] else "None"
            corequisites = ', '.join(details['corequisites']) if details['corequisites'] else "None"
            credit_unit = details['credit_unit']
            legend_data.append([subject, title, prerequisites, corequisites,credit_unit])

        # Create a DataFrame for the semester
        df = pd.DataFrame(
            legend_data, 
            columns=["Subject Code", "Title", "Pre-requisites", "Co-requisites","Credit Units"]
        )
        semester_tables[semester] = df  # Store DataFrame in a dictionary with semester as the key
    return semester_tables

if st.session_state['role'] == "Dean":
    program = st.selectbox(
        "Select Program to view:",
        get_department_programs(st.session_state['department_ID'])
    )
else:
    program = st.session_state['program_ID']
    program = get_program(program)

tables = get_table_names(st.session_state['department_ID'],program)
if tables:
    select_table = st.selectbox('Select a curriculum:',tables)
    subjects = load_subjects_from_db(st.session_state['department_ID'],program,select_table)
    if subjects:
        st.components.v1.html(
            build_interactive_subject_graph(subjects).generate_html(),
            height=800
        )
        with st.popover("Show Legend",use_container_width=True):
            st.markdown(
                """
                ### Legend
                - ─── **Solid Line**: Pre-Requisite
                - \- - - **Broken Line**: Co-Requisite
                - ⭐ **Star Node**: Year Standing Prerequisite
                """
                )
        semester_tables = format_subjects_for_legend(subjects)
        for (year,semester), df in semester_tables.items():
            st.subheader(f"Year {year} - Semester {semester}")
            main,sub = st.columns([3,0.4])
            Total = pd.DataFrame(df)["Credit Units"].sum(axis=0)
            Total_sum = pd.DataFrame([{"Total Units":Total}])
            main.dataframe(
                df,
                hide_index=True,
                column_config={
                    "Subject Code": st.column_config.TextColumn(
                       "Subject Code",
                       width="small",
                    ),
                    "Title": st.column_config.TextColumn(
                       "Title",
                       width="medium",
                    ),
                    "Pre-requisites": st.column_config.ListColumn(
                       "Prerequisites",
                       width="medium",
                    ),
                    "Co-requisites":st.column_config.ListColumn(
                        "Co-requisites",
                        width="small",
                    ),
                    "Credit Units":st.column_config.Column(
                        "Credit Units",
                        width="small",
                    )
                },
                height=len(df) * 35 + 35,
                use_container_width=True
            )
            sub.dataframe(
                Total_sum,
                hide_index=True,  
            )
else:
    st.warning(f"No curriculum found in the database.")
    select_table = None