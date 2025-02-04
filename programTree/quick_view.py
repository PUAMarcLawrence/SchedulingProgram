import streamlit as st
from pyvis.network import Network
from utils.programTree_db_utils import get_table_names, load_subjects_from_db

st.set_page_config(layout="wide")

def build_interactive_subject_graph(subjects):
    net = Network(
        height="560px", 
        width="100%", 
        bgcolor="#ffffff", 
        font_color="black", 
        directed=True,) #filter_menu=True)

    net.set_options(
        '''
        {
            "edges": {
                "color": {"inherit": false},
                "smooth": true
        },
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "levelSeparation": 250,
                    "direction": "LR",
                    "sortMethod": "directed"
            }
        },
            "physics": {
                "hierarchicalRepulsion": {
                    "centralGravity": 5
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
    
    for semester, semester_subjects in subjects.items():
        semester_color = semester_color_map.get(semester, "black")
        level_map = {
            "1 - 1": 1, "1 - 2": 2, "1 - 3": 3, "1 - 4": 4,
            "2 - 1": 5, "2 - 2": 6, "2 - 3": 7, "2 - 4": 8,
            "3 - 1": 9, "3 - 2": 10, "3 - 3": 11, "3 - 4": 12,
            "4 - 1": 13, "4 - 2": 14, "4 - 3": 15, "4 - 4": 16,
            
        }
        for subject in semester_subjects.keys():
            # Set the node level to ensure vertical alignment
            net.add_node(
                subject, 
                label = subject,
                color = semester_color, 
                level = level_map.get(semester, 0), 
                font={
                    "size": 100, 
                    "color": "black"}
            )
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            for prereq in details['prerequisites']:
                if prereq in all_subjects:
                    net.add_edge(prereq, subject, color=semester_color_map.get(semester, "black"),width=2)
            for coreq in details['corequisites']:
                if coreq in all_subjects:
                    net.add_edge(coreq, subject, color="#0082c8", width=3, dashes=True)

    return net

tables = get_table_names()
if tables:
    select_table = st.selectbox("Select a curriculum:",tables)
    subjects = load_subjects_from_db(select_table)

    if subjects:
        st.components.v1.html(build_interactive_subject_graph(subjects).generate_html(),height=1000)


else:
    st.error("No Curriculum found in the database")
