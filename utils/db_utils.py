# Functions for database interactions
import sqlite3
import pandas as pd
from utils.auth_utils import hash_password, userAddrDB
import os

path = './data'
# eceAddrDB = 'data/ece.db'
# progAddrDB = 'data/programs.db'

def initialize_db():
    if not os.path.exists(path):
        os.mkdir(path)
    try:
        with sqlite3.connect(userAddrDB) as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS departments (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         department TEXT NOT NULL UNIQUE
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT NOT NULL UNIQUE, 
                         password TEXT NOT NULL UNIQUE,
                         department foriegn key REFERENCES departments(department),
                         role TEXT NOT NULL, 
                         program foriegn key REFERENCES programs(program),
                         color TEXT NOT NULL UNIQUE
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS programs (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         program TEXT NOT NULL UNIQUE,
                         department foriegn key REFERENCES departments(department)
                )
            ''')

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                conn.execute(
                    '''
                    Insert into users (username, password, department, role, program, color) 
                    values (:username, :password, :department, :role, :program, :color)
                    ''',
                    {
                        'username': 'MapuaAdmin',
                        'password': hash_password('Mapua01251925'),
                        'department': 'NA',
                        'role': 'Admin',
                        'program': 'NA',
                        'color': '#000000'
                    })

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def create_user(username, password, role, color):
    try:
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

# ============================ Program Tree Sqlite Functions ============================
# def get_table_names():
#     try:
#         with sqlite3.connect(eceAddrDB) as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#             tables = [row[0] for row in cursor.fetchall()]
#         return tables
#     except sqlite3.Error as e:
#         print(f"Database connection error: {e}")
#         return []

# # Function to load subjects from the selected table
# def load_subjects_from_db(table_name):
#     try:
#         with sqlite3.connect(eceAddrDB) as conn:
#             query = f"""
#             SELECT Year, Term, Code, Title, Prerequisites, Co_requisites, [Credit Units]
#             FROM "{table_name}";
#             """
#             rows = conn.execute(query).fetchall()
#     except sqlite3.Error as e:
#         print(f"Database connection error: {e}")
#         return {}

#     subjects = {}
#     for row in rows:
#         year, term, subject_code, title, prerequisites, corequisites, credit_unit= row
#         prerequisites = prerequisites.split(',') if prerequisites else []
#         corequisites = corequisites.split(',') if corequisites else []

#         semester_key = f"{year} - {term}"
#         if semester_key not in subjects:
#             subjects[semester_key] = {}

#         subjects[semester_key][subject_code] = {
#             "title": title,
#             "prerequisites": [prereq.strip() for prereq in prerequisites],
#             "corequisites": [coreq.strip() for coreq in corequisites],
#             "credit_unit": credit_unit
#         }
#     return subjects
