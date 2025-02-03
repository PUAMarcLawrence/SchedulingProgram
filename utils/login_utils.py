# Functions for authentication and password hashing
import sqlite3
import hashlib
import os
from utils.db_utils import schoolAddrDB,get_programID,get_departmentID,add_department

path = './data'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_db():
    if not os.path.exists(path):
        os.mkdir(path)
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute('PRAGMA foreign_keys = ON;')
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS departments(
                department_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL UNIQUE
                )
                '''
            )
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS programs (
                    program_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    program TEXT NOT NULL UNIQUE,
                    department_ID INTEGER NOT NULL,
                    FOREIGN KEY(department_ID) REFERENCES departments(department_ID)
                )
                '''
            )
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE, 
                    password TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    department_ID INTEGER,
                    program_ID INTEGER UNIQUE,
                    color TEXT NOT NULL UNIQUE,
                    FOREIGN KEY(department_ID) REFERENCES departments(department_ID),
                    FOREIGN KEY(program_ID) REFERENCES programs(program_ID)
                )
                '''
            )
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def check_anyUser():
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                return True
            return False
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False

def get_departments():
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department FROM departments")
            departments = [row[0] for row in cursor.fetchall()]
        return departments
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

def get_programs(department):
    if department == None:
        return []
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department_ID FROM departments WHERE department = :department", {'department': department})
            department_ID = cursor.fetchone()[0]
            cursor.execute("SELECT program FROM programs WHERE department_ID = :department", {'department': department_ID})
            programs = [row[0] for row in cursor.fetchall()]
        return programs
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

def create_admin(username, password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                    '''
                    INSERT INTO users (username, password, department_ID, role, program_ID, color) 
                    VALUES (:username, :password, :department, :role, :program, :color)
                    ''',
                    {
                        'username': username,
                        'password': hash_password(password),
                        'department': None,
                        'role': 'Admin',
                        'program': None,
                        'color': '#000000'
                    })
        return True
    except sqlite3.Error as e:
        return False


def create_user(username, password,department, role, program, color):
    try:
        # Open database connection
        with sqlite3.connect(schoolAddrDB) as conn:
            if role == 'Dean':
                add_department(department)
            else:
                program = get_programID(program)
            conn.execute(
                '''
                INSERT INTO users (username, password, department_ID, role, program_ID, color) 
                VALUES (:username, :password, :department, :role, :program, :color)
                ''', 
                {
                    'username': username, 
                    'password': hash_password(password),
                    'department': get_departmentID(department),
                    'role': role, 
                    'program': program,
                    'color': color
                }
            )
        return {"success": True, "message": f"{role} Registration successful! You can now log in."}
    except sqlite3.IntegrityError as ie:
        return {"success": False, "message": "Username already exists/Color already used. Please choose a different one."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}

def check_login(username, password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT username, password, role, department_ID, program_ID, color
                FROM users 
                WHERE username = :username AND password = :password
                ''',
                {
                    'username': username, 
                    'password': hash_password(password)
                }
            )
            result = cursor.fetchone()
            return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None 

def check_old_password(username,old_password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT password
                FROM users 
                WHERE username = :username
                ''',
                {
                    'username': username
                }
            )
            result = cursor.fetchone()
            if result[0] != hash_password(old_password):
                return False
            else:
                return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    
def change_password_to_new(username,new_password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                '''
                UPDATE users
                SET password = :password
                WHERE username = :username
                ''',
                {
                    'password': hash_password(new_password),
                    'username': username
                }
            )
            return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None