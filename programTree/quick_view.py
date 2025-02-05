import streamlit as st
import pandas as pd
from pyvis.network import Network
from utils.programTree_db_utils import get_table_names, load_subjects_from_db

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
 
                    "direction": "LR"
                   
                }
            },
            "physics": {
                "hierarchicalRepulsion": {
                    "centralGravity": 7
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

            # Set the node level to ensure vertical alignment
            net.add_node(
                subject, 
                title = f_title,
                label = subject,
                # color = semester_color, 
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

    for semester, semester_subjects in subjects.items():
        for node in net.nodes:
            node["value"] = len(neighbor_map[node["id"]])
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
        df = pd.DataFrame(legend_data, columns=["Subject Code", "Title", "Prerequisites", "Co-requisites","Credit Units"])
        semester_tables[semester] = df  # Store DataFrame in a dictionary with semester as the key
    return semester_tables

tables = get_table_names()
if tables:
    select_table = st.selectbox("Select a curriculum:",tables)
    subjects = load_subjects_from_db(select_table)

    if subjects:
        st.components.v1.html(
            build_interactive_subject_graph(subjects).generate_html(),
            height=800
        )
        semester_tables = format_subjects_for_legend(subjects)
        for semester, df in semester_tables.items():
            st.subheader(f"Subjects and Requirements for {semester}")
            main,sub = st.columns([3,0.5])
            Total = pd.DataFrame(df)["Credit Units"].sum(axis=0)
            Total_sum = pd.DataFrame([{"Total Credit Units":Total}])
            main.dataframe(
                df,
                hide_index=True,
                use_container_width=True
            )
            sub.dataframe(
                Total_sum,
                hide_index=True,
                
            )

            

else:
    st.error("No Curriculum found in the database")
