import streamlit as st
import pandas as pd
from pyvis.network import Network
from utils.programTree_db_utils import get_table_names, load_subjects_from_db

st.set_page_config(layout="wide")

def build_interactive_subject_graph(subjects):
    net = Network(
        height="600px", 
        width="100%", 
        bgcolor="#222222", 
        font_color="white", 
        # directed=True, 
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
                    "treeSpacing": 200,
                    "direction": "LR",
                    "sortMethod": "hubsize"
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

    semester_color_map = {
        "1 - 1": "#800000", "1 - 2": "#006400", "1 - 3": "#00008B", "1 - 4": "#A9A9A9",
        "2 - 1": "#FF0000", "2 - 2": "#008000", "2 - 3": "#00FF00", "2 - 4": "#696969",
        "3 - 1": "#FF4500", "3 - 2": "#0000FF", "3 - 3": "#6A5ACD", "3 - 4": "#2F4F4F",
        "4 - 1": "#A9A9A9", "4 - 2": "#696969", "4 - 3": "#2F4F4F", "4 - 4": "#000000"
    }

    all_subjects = set()
    for semester, semester_subjects in subjects.items():
        for subject in semester_subjects.keys():
            all_subjects.add(subject)
    level_map = {
    "1 - 1": 1, "1 - 2": 2, "1 - 3": 3, "1 - 4": 4,
    "2 - 1": 5, "2 - 2": 6, "2 - 3": 7, "2 - 4": 8,
    "3 - 1": 9, "3 - 2": 10, "3 - 3": 11, "3 - 4": 12,
    "4 - 1": 13, "4 - 2": 14, "4 - 3": 15, "4 - 4": 16,
    }
    for semester, semester_subjects in subjects.items():
        semester_color = semester_color_map.get(semester, "black")
        for subject in semester_subjects.keys():
            f_title = f"{subject}\n"
            if semester_subjects[subject]['prerequisites'] != []:
                p_req = ", ".join(semester_subjects[subject]['prerequisites'])
                f_title += f"Pre-Req: {p_req}\n"
            if semester_subjects[subject]['corequisites'] != []:
                c_req = ", ".join(semester_subjects[subject]['corequisites'])
                f_title += f"Pre-Req: {c_req}\n"
            f_title += f"Credit: {semester_subjects[subject]['credit_unit']}"
            # Set the node level to ensure vertical alignment
            net.add_node(
                subject, 
                title = f_title,
                label = subject,
                # color = semester_color, 
                level = level_map.get(semester, 0), 
            )
    
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            for prereq in details['prerequisites']:
                if prereq in all_subjects:
                    net.add_edge(
                        prereq, 
                        subject, 
                        # color=semester_color_map.get(semester, "black"),
                        width=2
                    )
            for coreq in details['corequisites']:
                if coreq in all_subjects:
                    net.add_edge(
                        coreq, 
                        subject, 
                        # color="#0082c8", 
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
        total=0
        for subject, details in semester_subjects.items():
            title = details['title']
            prerequisites = ', '.join(details['prerequisites']) if details['prerequisites'] else "None"
            corequisites = ', '.join(details['corequisites']) if details['corequisites'] else "None"
            credit_unit = details['credit_unit']
            total = total + credit_unit
            legend_data.append([subject, title, prerequisites, corequisites,credit_unit])
        legend_data.append(['','','','TOTAL',total])

        df = pd.DataFrame(legend_data, columns=["Subject Code", "Title", "Prerequisites", "Co-requisites","Credit Units"])

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
            height=600
        )
        semester_tables = format_subjects_for_legend(subjects)
        for semester, df in semester_tables.items():
            st.subheader(f"Subjects and Requirements for {semester}")
            st.table(df)  # Display each semester's table
else:
    st.error("No Curriculum found in the database")
