import sqlite3
import pandas as pd

eceAddrDB = 'data/ece.db'

# ===================================== Quickview page ======================================
def get_table_names():
    try:
        with sqlite3.connect(eceAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
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
        print(f"Database connection error: {e}")
        return {}

    subjects = {}
    for row in rows:
        year, term, subject_code, title, prerequisites, corequisites, credit_unit= row
        prerequisites = prerequisites.split(',') if prerequisites else []
        corequisites = corequisites.split(',') if corequisites else []
        if year != None:
            year = int(year)
        if term != None:
            term = int(term)
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
            table_name = program.upper() + year
            # create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
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