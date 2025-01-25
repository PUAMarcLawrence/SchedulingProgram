# Functions for database interactions
import streamlit as st
import sqlite3
import pandas as pd
from utils.auth_utils import hash_password, userAddrDB

eceAddrDB = 'data/ece.db'
progAddrDB = 'data/programs.db'

import sqlite3
import streamlit as st

# Initialize user table
def initialize_user_table():
    """
    Creates a 'users' table in the SQLite database if it doesn't exist.
    The table includes:
      - username: Unique identifier (Primary Key).
      - password: Stores the hashed password.
      - role: User role (e.g., admin, user).
      - color: Custom color preference for the user.
    """
    try:
        with sqlite3.connect(userAddrDB) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT NOT NULL UNIQUE, 
                         password TEXT NOT NULL, 
                         role TEXT NOT NULL, 
                         color TEXT NOT NULL UNIQUE
                )
            ''')
            # conn.execute('''
            #     CREATE UNIQUE INDEX IF NOT EXISTS idx_username_color ON users (color)
            # ''')
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")

def create_user(username, password, role, color):
    try:
        # Validate inputs
        if not username or not password or not role or not color:
            raise ValueError("All fields (username, password, role, color) are required.")

        # Open database connection
        with sqlite3.connect(userAddrDB) as conn:
            conn.execute(
                '''
                INSERT INTO users (username, password, role, color) 
                VALUES (:user, :password, :role, :color)
                ''', 
                {
                    'user': username, 
                    'password': hash_password(password),
                    'role': role, 
                    'color': color
                }
            )
        return {"success": True, "message": f"{role} Registration successful! You can now log in."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Username already exists/Color already used. Please choose a different one."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}

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
