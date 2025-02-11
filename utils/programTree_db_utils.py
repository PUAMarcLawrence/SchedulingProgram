import sqlite3
from utils.db_utils import get_department
import os

department_path = './data/curriculum/'

def get_table_names(department_ID,program):
    department = get_department(department_ID)
    if not os.path.exists(f'./data/curriculum/{department}'):
        os.mkdir(f'./data/curriculum/{department}')
    curriculum = f'./data/curriculum/{department}/{program}_curriculum.db'
    try:
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []