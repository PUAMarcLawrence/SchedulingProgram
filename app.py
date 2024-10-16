import streamlit as st
import graphviz as gv
import sqlite3
# # Sample data: Dictionary where the keys are subjects and the values include both pre-requisites and co-requisites
# subjects = {
#     "Year 1 - Semester 1": {
#         "Math 101": {"prerequisites": [], "corequisites": []},
#         "Physics 101": {"prerequisites": [], "corequisites": []},
#         "Programming 101": {"prerequisites": [], "corequisites": []}
#     },
#     "Year 1 - Semester 2": {
#         "Math 102": {"prerequisites": ["Math 101"], "corequisites": []},
#         "Physics 102": {"prerequisites": ["Physics 101"], "corequisites": ["Math 102"]},
#         "Programming 102": {"prerequisites": ["Programming 101", "Physics 101"], "corequisites": []}
#     },
#     "Year 2 - Semester 1": {
#         "Math 201": {"prerequisites": ["Math 102"], "corequisites": []},
#         "Physics 201": {"prerequisites": ["Physics 102"], "corequisites": []},
#         "Data Structures": {"prerequisites": ["Programming 102"], "corequisites": []}
#     },
#     "Year 2 - Semester 2": {
#         "Math 202": {"prerequisites": ["Math 201"], "corequisites": []},
#         "Physics 202": {"prerequisites": ["Physics 201"], "corequisites": []},
#         "Algorithms": {"prerequisites": ["Data Structures"], "corequisites": ["Math 202"]}
#     }
# }

def load_subjects_from_db(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to fetch data from the database
    query = """
    SELECT Year, Term, Code, Prerequisites, Co_requisites 
    FROM ECE2021;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Create a dictionary to store the subjects
    subjects = {}
    
    for row in rows:
        year = row[0]
        term = row[1]
        subject_code = row[2]
        prerequisites = row[3].split(',') if row[3] else []
        corequisites = row[4].split(',') if row[4] else []
        
        # Create a semester key
        semester_key = f"{year} - {term}"
        
        # If the semester does not exist in the dictionary, create it
        if semester_key not in subjects:
            subjects[semester_key] = {}
        
        # Add the subject to the semester
        subjects[semester_key][subject_code] = {
            "prerequisites": [prereq.strip() for prereq in prerequisites],
            "corequisites": [coreq.strip() for coreq in corequisites]
        }
    
    # Close the database connection
    conn.close()
    
    return subjects

# Function to build the graph with co-requisites
def build_subject_graph(subjects):
    dot = gv.Digraph()
    dot.attr(rankdir='LR', size='20,10', nodesep='0.05', ranksep='0.5')
    # Iterate over semesters and subjects to add nodes and edges
    for semester, semester_subjects in subjects.items():
        with dot.subgraph() as s:
            s.attr(rank='same')  # Set rank for subjects in the same semester
            for subject, details in semester_subjects.items():
                s.node(subject, subject, shape='box', style='rounded',fontsize='10', width='0.001', height='0.0001')  # Add node with rounded box

                # Add edges for prerequisites
                for prereq in details['prerequisites']:
                    dot.edge(prereq, subject)

                # Add edges for corequisites (using dashed lines with arrows on both ends)
                for coreq in details['corequisites']:
                    dot.edge(coreq, subject, style='dashed', dir='both', constraint="false")

    return dot

# Build and render the graph
db_path = 'ece.db'  # Change this to your database path
subjects = load_subjects_from_db(db_path)
graph = build_subject_graph(subjects)
st.graphviz_chart(graph)
