import streamlit as st
import sqlite3
import pandas as pd
from pyvis.network import Network

# Function to retrieve all table names in the database
def get_table_names(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        return tables
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return []

# Function to load subjects from the selected table
def load_subjects_from_db(db_path, table_name):
    try:
        with sqlite3.connect(db_path) as conn:
            query = f"""
            SELECT Year, Term, Code, Title, Prerequisites, Co_requisites 
            FROM "{table_name}";
            """
            rows = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return {}

    subjects = {}
    for row in rows:
        year, term, subject_code, title, prerequisites, corequisites = row
        prerequisites = prerequisites.split(',') if prerequisites else []
        corequisites = corequisites.split(',') if corequisites else []

        semester_key = f"{year} - {term}"
        if semester_key not in subjects:
            subjects[semester_key] = {}

        subjects[semester_key][subject_code] = {
            "title": title,
            "prerequisites": [prereq.strip() for prereq in prerequisites],
            "corequisites": [coreq.strip() for coreq in corequisites]
        }
    return subjects

def build_subject_graph_interactive(subjects):
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
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
        for subject, details in semester_subjects.items():
            title = details['title']
            prerequisites = ', '.join(details['prerequisites']) if details['prerequisites'] else "None"
            corequisites = ', '.join(details['corequisites']) if details['corequisites'] else "None"
            legend_data.append([subject, title, prerequisites, corequisites])

        df = pd.DataFrame(legend_data, columns=["Subject Code", "Title", "Prerequisites", "Co-requisites"])

        # Create a DataFrame for the semester
        df = pd.DataFrame(legend_data, columns=["Subject Code", "Title", "Prerequisites", "Co-requisites"])
        semester_tables[semester] = df  # Store DataFrame in a dictionary with semester as the key

    return semester_tables

# Main app logic
db_path = 'ece.db'
tables = get_table_names(db_path)
st.set_page_config(layout="wide")  # Optional: Expands Streamlit to full width
if tables:
    selected_table = st.selectbox("Select a curriculum:", tables, index=tables.index('ECE2021'))
    subjects = load_subjects_from_db(db_path, selected_table)

    if subjects:
        net = build_subject_graph_interactive(subjects)
        st.components.v1.html(net.generate_html(), height=850)

        # Display the subjects table as separate tables for each semester
        semester_tables = format_subjects_for_legend(subjects)
        for semester, df in semester_tables.items():
            st.subheader(f"Subjects and Requirements for {semester}")
            st.table(df)  # Display each semester's table
else:
    st.error("No tables found in the database.")

st.write(st.session_state["shared"])


