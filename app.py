import streamlit as st
import graphviz as gv
import sqlite3

def get_table_names(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return []

def load_subjects_from_db(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return {}

    cursor = conn.cursor()
    
    query = f"""
    SELECT Year, Term, Code, Prerequisites, Co_requisites 
    FROM {table_name};
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    subjects = {}
    
    for row in rows:
        year, term, subject_code, prerequisites, corequisites = row
        prerequisites = prerequisites.split(',') if prerequisites else []
        corequisites = corequisites.split(',') if corequisites else []

        semester_key = f"{year} - {term}"
        if semester_key not in subjects:
            subjects[semester_key] = {}
        
        subjects[semester_key][subject_code] = {
            "prerequisites": [prereq.strip() for prereq in prerequisites],
            "corequisites": [coreq.strip() for coreq in corequisites]
        }
    
    conn.close()
    
    return subjects

def build_subject_graph(subjects):
    dot = gv.Digraph()
    dot.attr(splines='true')
    dot.attr(rankdir='LR', size='10,5', nodesep='0.1', ranksep='0.5', dpi='70')
    
    for semester, semester_subjects in subjects.items():
        with dot.subgraph() as s:
            s.attr(rank='same')
            for subject, details in semester_subjects.items():
                s.node(subject, subject, shape='box', style='rounded', fontsize='10', width='0.001', height='0.0001')

                for prereq in details['prerequisites']:
                    dot.edge(prereq, subject)

                for coreq in details['corequisites']:
                    dot.edge(coreq, subject, style='dashed', dir='none', constraint="false", color='blue')

    return dot

# Main app logic
db_path = 'ece.db'  # Change this to your database path
tables = get_table_names(db_path)

if tables:
    selected_table = st.selectbox("Select a table:", tables)

    subjects = load_subjects_from_db(db_path, selected_table)

    graph = build_subject_graph(subjects)
    st.graphviz_chart(graph)
else:
    st.error("No tables found in the database.")
