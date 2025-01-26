# Functions for database interactions
import sqlite3
import pandas as pd
from utils.login_utils import hash_password



eceAddrDB = 'data/ece.db'
# progAddrDB = 'data/programs.db'


# ============================ Program Tree Sqlite Functions ============================
def get_table_names():
    try:
        with sqlite3.connect(eceAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        return tables
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

# Function to load subjects from the selected table
def load_subjects_from_db(table_name):
    try:
        with sqlite3.connect(eceAddrDB) as conn:
            query = f"""
            SELECT Year, Term, Code, Title, Prerequisites, Co_requisites, [Credit Units]
            FROM "{table_name}";
            """
            rows = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return {}

    subjects = {}
    for row in rows:
        year, term, subject_code, title, prerequisites, corequisites, credit_unit= row
        prerequisites = prerequisites.split(',') if prerequisites else []
        corequisites = corequisites.split(',') if corequisites else []

        semester_key = f"{year} - {term}"
        if semester_key not in subjects:
            subjects[semester_key] = {}

        subjects[semester_key][subject_code] = {
            "title": title,
            "prerequisites": [prereq.strip() for prereq in prerequisites],
            "corequisites": [coreq.strip() for coreq in corequisites],
            "credit_unit": credit_unit
        }
    return subjects
