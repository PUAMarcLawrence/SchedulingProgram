# Functions for database interactions
import streamlit as st
import sqlite3
import pandas as pd
from utils.auth_utils import hash_password

userAddrDB = 'data/school.db'
eceAddrDB = 'data/ece.db'
progAddrDB = 'data/programs.db'

# initialize creation of users db
def create_user_table():
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
              username TEXT PRIMARY KEY, 
              password TEXT, 
              role TEXT, 
              color Text)''')
    
    conn.commit()
    conn.close()

# creates new user
def create_user(username, password, role, color):
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role, color) VALUES (?, ?, ?, ?)', (username, hash_password(password), role, color))
        conn.commit()
        conn.close()
        return True  # Return True if user creation was successful
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Return False if username already exists
    
# Function to retrieve all table names in the database
def get_table_names():
    try:
        with sqlite3.connect(eceAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        return tables
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
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
        st.error(f"Database connection error: {e}")
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

def programs_to_db(data_list):
    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(progAddrDB)
    cursor = conn.cursor()
    
    # Create table (if it doesn't already exist)
    cursor.execute("CREATE TABLE IF NOT EXISTS programs (id INTEGER PRIMARY KEY, item TEXT)")
    
    # Clear any existing data
    cursor.execute("DELETE FROM programs")
    
    # Insert list items into the table
    cursor.executemany("INSERT INTO programs (item) VALUES (?)", [(item,) for item in data_list])
    
    # Commit and close the connection
    conn.commit()
    conn.close()

def programs_to_list():
    # Connect to SQLite database
    conn = sqlite3.connect(progAddrDB)
    cursor = conn.cursor()

    # Create table (if it doesn't already exist)
    cursor.execute("CREATE TABLE IF NOT EXISTS programs (id INTEGER PRIMARY KEY, item TEXT)")

    # Retrieve all items from the table
    cursor.execute("SELECT item FROM programs")
    data_list = [row[0] for row in cursor.fetchall()]
    
    # Close the connection
    conn.close()
    
    return data_list

# Define function to upload data into SQLite
def upload_to_sqlite(file_path,program,year):
    # Load data from Excel file
    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return False
    
    # Connect to the SQLite database
    conn = sqlite3.connect(eceAddrDB)
    cursor = conn.cursor()
    
    # Create a table with columns based on the Excel data
    columns = data.columns
    column_definitions = ", ".join([f"{col} TEXT" for col in columns])
    table_name = program+year
    
    # Create table if it doesn't exist
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
    cursor.execute(create_table_query)
    
    # Insert data into the SQLite database
    try:
        data.to_sql(table_name, conn, if_exists="replace", index=False)
        st.success(f"Data successfully uploaded to SQLite database '{eceAddrDB}' in table '{table_name}'.")
    except Exception as e:
        st.error(f"Error uploading data to SQLite: {e}")
        conn.close()
        return False
    
    # Close the connection
    conn.close()
    return True

def del_curiculum_db(table):
    # Connect to the SQLite database
    conn = sqlite3.connect(eceAddrDB)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP TABLE {table}")
    except Exception as e:
        conn.close()
        return False
    conn.close()
    return True

def create_sandTable(table_name,template):

    sandAddrDB = 'data/'+ st.session_state.username + '_sandBox'
    conn = sqlite3.connect(sandAddrDB)

    conn.execute(f'CREATE TABLE IF NOT EXISTS {table_name}')
    conn.close()
