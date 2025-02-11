import sqlite3
import hashlib
import os

db_path = './data'
path_sandBox = './data/sandBox'
path_curriculum = './data/curriculum'
schoolAddrDB = 'data/school.db'

def initialize_db():
    if not os.path.exists(db_path):
        os.mkdir(db_path)
    if not os.path.exists(path_sandBox):
        os.mkdir(path_sandBox)
    if not os.path.exists(path_curriculum):
        os.mkdir(path_curriculum)
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

def initialize_department_dir(department):
    if not os.path.exists(f'./data/curriculum/{department}'):
        os.mkdir(f'./data/curriculum/{department}')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_department(department):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                    '''
                    INSERT OR IGNORE INTO departments (department) 
                    VALUES (:department)
                    ''', 
                    {
                        'department': department
                    }
                )
    except sqlite3.Error as e:
       print(f"An error occurred: {e}")

def get_departmentID(department):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT department_ID 
                FROM departments WHERE department = :department
                ''',
                {'department':department})
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
def get_programID(program):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT program_ID
                FROM programs WHERE program = :program
                ''',
                {'program':program})
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
def get_program(program_ID):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT program
                FROM programs WHERE program_ID = :program_ID
                ''',
                {'program_ID':program_ID})
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

def add_program(program,department):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO programs (program, department_ID) VALUES (:program, :department_ID)
                ''',
                {'program':program.upper(),
                 'department_ID':department})
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    
def get_department(department_ID):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT department 
                FROM departments WHERE department_ID = :department_ID
                ''',
                {'department_ID':department_ID})
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
def get_department_programs(department_ID):
    if department_ID == None:
        return []
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT program FROM programs WHERE department_ID = :department", {'department': department_ID})
            programs = [row[0] for row in cursor.fetchall()]
        return programs
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

