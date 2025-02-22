import sqlite3
import pandas as pd
from utils.db_utils import get_department, initialize_department_dir,path_curriculum

def upload_to_database(data,department_ID,program,program_batch):
    try:
        department = get_department(department_ID)
        initialize_department_dir(department)
        curriculum = f'{path_curriculum}/{department}/{program}_curriculum.db'
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            columns = data.columns
            column_definitions = ", ".join([f"{col} TEXT" for col in columns])
            table_name = program_batch
            cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})
                '''
            )
        try:
            data.to_sql(table_name, conn, if_exists="replace", index=False)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    except sqlite3.Error as e:
        print(f"Error uploading data to SQLite: {e}")
        return False
    
def get_existing_curriculum(department_ID,program,program_batch):
    department = get_department(department_ID)
    curriculum = f'{path_curriculum}/{department}/{program}_curriculum.db'
    try:
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (program_batch,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False