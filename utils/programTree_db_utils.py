import sqlite3
import pandas as pd

eceAddrDB = 'data/ece.db'

def get_table_names():
    try:
        with sqlite3.connect(eceAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

# ===================================== Upload page ======================================
def upload_to_database(file_path,program,year):
    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False
    
    try:
        with sqlite3.connect(eceAddrDB) as conn:
            cursor = conn.cursor()
            columns = data.columns
            column_definitions = ", ".join([f"{col} TEXT" for col in columns])
            table_name = program + year
            # create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS :table_name (:column_definitions)
                ''',
                {
                    'table_name': table_name,
                    'column_definitions': column_definitions
                })
        try:
            data.to_sql(table_name, conn, if_exists="replace", index=False)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    except sqlite3.Error as e:
        print(f"Error uploading data to SQLite: {e}")
        return False