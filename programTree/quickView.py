import streamlit as st
import pandas as pd
from pyvis.network import Network
from utils.db_utils import get_table_names, load_subjects_from_db

# Main app logic

def build_subject_graph_interactive(subjects):
    net = Network(height="550px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
    # Set hierarchical layout options for vertical alignment
    net.set_options("""
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
    }""")

    # Define a color map for semesters (customize colors as needed)
    semester_color_map = {
        "1 - 1": "#800000", "1 - 2": "#006400", "1 - 3": "#00008B", "1 - 4": "#A9A9A9",
        "2 - 1": "#FF0000", "2 - 2": "#008000", "2 - 3": "#00FF00", "2 - 4": "#696969",
        "3 - 1": "#FF4500", "3 - 2": "#0000FF", "3 - 3": "#6A5ACD", "3 - 4": "#2F4F4F",
        "4 - 1": "#A9A9A9", "4 - 2": "#696969", "4 - 3": "#2F4F4F", "4 - 4": "#000000"
    }

    # Step 1: Add nodes with level based on semester
    all_subjects = set()
    for semester, semester_subjects in subjects.items():
        for subject in semester_subjects.keys():
            all_subjects.add(subject)

    for semester, semester_subjects in subjects.items():
        semester_color = semester_color_map.get(semester, "black")
        match semester:
            case "1 - 1":
                level = 1
            case "1 - 2":
                level = 2
            case "1 - 3":
                level = 3
            case "1 - 4":
                level = 4
            case "2 - 1":
                level = 5
            case "2 - 2":
                level = 6
            case "2 - 3":
                level = 7
            case "2 - 4":
                level = 8
            case "3 - 1":
                level = 9
            case "3 - 2":
                level = 10
            case "3 - 3":
                level = 11
            case "3 - 4":
                level = 12
            case "4 - 1":
                level = 13
            case "4 - 2":
                level = 14
            case "4 - 3":
                level = 15
            case "4 - 4":
                level = 16
            
            
        # level = int(semester.replace(" - ",""))  # Determine level by the year part of "Year - Term"
        for subject in semester_subjects.keys():
            # Set the node level to ensure vertical alignment
            net.add_node(subject, label=subject, color=semester_color, level=level, font={"size": 100, "color": "black"})

    # Step 2: Add edges for prerequisites and corequisites
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            for prereq in details['prerequisites']:
                if prereq in all_subjects:
                    net.add_edge(prereq, subject, color=semester_color_map.get(semester, "black"),width=2)
            for coreq in details['corequisites']:
                if coreq in all_subjects:
                    net.add_edge(coreq, subject, color="#0082c8", width=3, dashes=True)

    return net

# Format subjects for legend with Title and color coding
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
    selected_table = st.selectbox("Select a curriculum:", tables)
    subjects = load_subjects_from_db(selected_table)

    if subjects:
        net = build_subject_graph_interactive(subjects)
        st.components.v1.html(net.generate_html(), height=560)

        # Display the subjects table as separate tables for each semester
        semester_tables = format_subjects_for_legend(subjects)
        for semester, df in semester_tables.items():
            st.subheader(f"Subjects and Requirements for {semester}")
            st.table(df)  # Display each semester's table
else:
    st.error("No tables found in the database.")
