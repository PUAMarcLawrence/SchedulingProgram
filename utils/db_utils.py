# Functions for database interactions
import sqlite3
import pandas as pd

schoolAddrDB = 'data/school.db'

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

def remove_program(program,department_ID):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT program
                FROM programs
                WHERE department_ID = :departmentID
                ''',
                {
                    'departmentID':department_ID
                }
            )
            Subject_list = pd.DataFrame(cursor.fetchall(),columns=['program'])
            print(Subject_list)

            conn.execute(
                '''
                DELETE FROM programs WHERE program = :program
                ''',
                {'program':program.upper()})
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

def get_all_subjects_in_department(department_ID):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT program
                FROM programs
                WHERE department_ID = :departmentID
                ''',
                {
                    'departmentID':department_ID
                }
            )
            Subject_list = pd.DataFrame(cursor.fetchall(),columns=['program'])
            return Subject_list
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

# ===================================== dean pages ======================================

def get_subjectChair_Dean(role,department_ID):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                SELECT program_ID, username
                FROM users 
                WHERE role = :role AND department_ID =:departmentID
                ''',
                {
                    'role': role,
                    'departmentID':department_ID
                }
            )
            Subject_Chair_list = pd.DataFrame(cursor.fetchall(),columns=['program','username'])
            programID_column = Subject_Chair_list['program']
            program_column = programID_column.apply(get_program)
            Subject_Chair_list['program']=program_column
            cursor.execute(
                '''
                SELECT program
                FROM programs
                WHERE department_ID = :departmentID
                ''',
                {
                    'departmentID':department_ID
                }
            )
            Subject_list = pd.DataFrame(cursor.fetchall(),columns=['program'])
            result = Subject_Chair_list.merge(Subject_list,how='right')
            return result
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
