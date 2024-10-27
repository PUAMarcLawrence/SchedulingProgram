import streamlit as st
import sqlite3
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

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
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
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
                "levelSeparation": 300,
                "direction": "LR",
                "sortMethod": "directed"
            }
        },
        "physics": {
            "hierarchicalRepulsion": {
                "centralGravity": 2
            },
            "minVelocity": 0.75,
            "solver": "hierarchicalRepulsion"
        }
    }""")

    # Define a color map for semesters (customize colors as needed)
    semester_color_map = {
        "1 - 1": "#800000", "1 - 2": "#FF0000", "1 - 3": "#FF4500", "1 - 4": "#FF6347",
        "2 - 1": "#006400", "2 - 2": "#008000", "2 - 3": "#00FF00", "2 - 4": "#ADFF2F",
        "3 - 1": "#00008B", "3 - 2": "#0000FF", "3 - 3": "#6A5ACD", "3 - 4": "#00BFFF",
        "4 - 1": "#ffffcc", "4 - 2": "#ffff99", "4 - 3": "#ffff66", "4 - 4": "#ffff33"
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
            net.add_node(subject, label=subject, color=semester_color, level=level)

    # Step 2: Add edges for prerequisites and corequisites
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            for prereq in details['prerequisites']:
                if prereq in all_subjects:
                    net.add_edge(prereq, subject, color=semester_color_map.get(semester, "black"))
            for coreq in details['corequisites']:
                if coreq in all_subjects:
                    net.add_edge(coreq, subject, color="#0082c8", width=3, dashes=True)

    return net



# Format subjects for legend with Title and color coding
def format_subjects_for_legend(subjects):
    legend_data = []
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            title = details['title']
            prerequisites = ', '.join(details['prerequisites']) if details['prerequisites'] else "None"
            corequisites = ', '.join(details['corequisites']) if details['corequisites'] else "None"
            legend_data.append([semester, subject, title, prerequisites, corequisites])

    df = pd.DataFrame(legend_data, columns=["Semester", "Subject Code", "Title", "Prerequisites", "Co-requisites"])

    color_map = {
        "1 - 1": "background-color: lightblue", "1 - 2": "background-color: lightgreen",
        "1 - 3": "background-color: lightblue", "1 - 4": "background-color: lightgreen",
        "2 - 1": "background-color: lightblue", "2 - 2": "background-color: lightgreen",
        "2 - 3": "background-color: lightblue", "2 - 4": "background-color: lightgreen",
        "3 - 1": "background-color: lightblue", "3 - 2": "background-color: lightgreen",
        "3 - 3": "background-color: lightblue", "3 - 4": "background-color: lightgreen",
        "4 - 1": "background-color: lightblue", "4 - 2": "background-color: lightgreen",
        "4 - 3": "background-color: lightblue", "4 - 4": "background-color: lightgreen",
    }

    return df.style.map(lambda _: color_map.get(_, ""), subset=['Semester'])

# Function to display the graph in the app with a full-screen option
def display_graph_with_fullscreen_option(net, file_path="subject_graph.html"):
    # Save the graph to an HTML file
    net.save_graph(file_path)
    
    # Display the graph in Streamlit
    with open(file_path, "r") as f:
        components.html(f.read(), height=750, width=800, scrolling=True)
    
    # Add a button to open the graph in a new tab for full-screen mode
    if st.button("View Full Screen"):
        js_code = f"""
        <script>
            window.open("{file_path}", "_blank");
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)

# Example usage
db_path = 'ece.db'  # Change this to your database path
tables = get_table_names(db_path)

if tables:
    selected_table = st.selectbox("Select a curriculum:", tables, index=tables.index('ECE2021'))
    subjects = load_subjects_from_db(db_path, selected_table)

    if subjects:
        net = build_subject_graph_interactive(subjects)
        
        # Display the graph with a full-screen option
        display_graph_with_fullscreen_option(net)
        
        # Display the subjects table as a legend, including Title
        legend_df = format_subjects_for_legend(subjects)
        st.subheader(f"Subjects and Requirements from {selected_table}")
        st.table(legend_df)
else:
    st.error("No tables found in the database.")
