import sqlite3
import pandas as pd
from utils.db_utils import schoolAddrDB, get_program

def get_all_program_in_department(department_ID):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT program_ID, program
                FROM programs
                WHERE department_ID = :departmentID
                ''',
                {
                    'departmentID':department_ID
                }
            )
            return pd.DataFrame(cursor.fetchall(),columns=['program_ID','program'])
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

def get_all_subjectChairs_in_department(role,department_ID):
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
            return pd.DataFrame(cursor.fetchall(),columns=['program','username'])
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

# ===================================== dean pages ======================================

def get_subjectChair_Dean(role,department_ID):
    Subject_Chair_list = get_all_subjectChairs_in_department(role,department_ID)
    programID_column = Subject_Chair_list['program']
    program_column = programID_column.apply(get_program)
    Subject_Chair_list['program']=program_column
    Subject_list = get_all_program_in_department(department_ID)
    result = Subject_Chair_list.merge(Subject_list,how='right')
    return result

def delete_program_dean(program):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                '''
                DELETE FROM programs
                WHERE program = :program
                ''',
                {
                    'program':program
                }
            )
            return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False

def modify_program_dean(old_program,new_program):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                '''
                UPDATE programs
                SET program = :new_program
                WHERE program = :old_program
                ''',
                {
                    'new_program':new_program.upper(),
                    'old_program':old_program
                }
            )
            return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False