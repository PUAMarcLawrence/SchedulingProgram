import sqlite3
import pandas as pd

def upload_to_database(file_path,department,program,year):
    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False
    
    try:
        curriculum = f'./data/curriculum/{department}/{program}_curriculum.db'
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            columns = data.columns
            column_definitions = ", ".join([f"{col} TEXT" for col in columns])
            table_name = f"{program.upper()}_{year}"
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