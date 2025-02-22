import sqlite3
import pandas as pd
from utils.db_utils import path_curriculum,path_sandBox
pd.set_option('future.no_silent_downcasting', True)

def copy_table(department,program, userID, source_table_name, new_table_name):
    source_db = f'{path_curriculum}/{department}/{program}_curriculum.db'
    dest_db = f'{path_sandBox}/{userID}_sandBox.db'
    try:
        with sqlite3.connect(source_db) as source_conn, sqlite3.connect(dest_db) as dest_conn:
            source_cursor = source_conn.cursor()
            dest_cursor = dest_conn.cursor()

            source_cursor.execute(
                f"""
                SELECT sql 
                FROM sqlite_master 
                WHERE type ='table' AND name='{source_table_name}'
                """
                )
            schema_result = source_cursor.fetchone()
            if schema_result:
                schema = schema_result[0]
                new_schema = schema.replace(source_table_name, new_table_name,1)
                dest_cursor.execute(new_schema)
                source_cursor.execute(
                    f"""
                    SELECT * 
                    FROM {source_table_name}
                    """
                )
                rows = source_cursor.fetchall()
                column_names = [desc[0] for desc in source_cursor.description]
                columns_str = "[" + "], [".join(column_names) + "]"
                placeholders = ", ".join(["?"] * len(column_names))
                dest_cursor.executemany(
                    f"""
                    INSERT INTO {new_table_name} ({columns_str}) 
                    VALUES ({placeholders})
                    """, 
                    rows
                )
                return True
            else:
                return False
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False

def create_scratch_sandbox(userID,new_table_name):
    sand_db = f'{path_sandBox}/{userID}_sandBox.db'
    try:
        with sqlite3.connect(sand_db) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {new_table_name}(
                Year INTEGER,
                Term INTEGER,
                Code TEXT,
                Title TEXT,
                [Lec Hrs] INTEGER,
                [Lab Hrs] INTEGER,
                [Credit Units] INTEGER,
                Prerequisite TEXT,
                Co_requisite TEXT,
                [Care Taker] TEXT)
                """)
            conn.execute(
                f"""
                INSERT INTO {new_table_name}(Year,Term,Code,Title,[Lec Hrs],[Lab Hrs],[Credit Units],Prerequisite,Co_requisite,[Care Taker])
                VALUES (:Year,:Term,:Code,:Title,:lec_hrs,:lab_hrs,:credit_units,:prereque,:coreque,:care_taker)""",
                {
                    'Year': 1,
                    'Term': 1,
                    'Code': 'MATH165',
                    'Title': 'COLLEGE ALGEBRA WITH ANALYTIC GEOMETRY',
                    'lec_hrs': 3.7,
                    'lab_hrs': None,
                    'credit_units': 3,
                    'prereque': None,
                    'coreque': None,
                    'care_taker':'MATH'
                }
                )
            return True
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False

def get_sand_names(userID):
    sand_db = f'{path_sandBox}/{userID}_sandBox.db'
    try:
        with sqlite3.connect(sand_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

def load_from_sand_db(userID,sandBox_name):
    sand_db = f'{path_sandBox}/{userID}_sandBox.db'
    try:
        with sqlite3.connect(sand_db) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {sandBox_name}")
            subjects = cursor.fetchall()
           
            return subjects
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return {}

def format_data_to_Graph(data):
    subjects_dict = {}
    for row in data:
        year,term,subject_code,title,lec_hrs,lab_hrs,credit_units,prerequisites,corequisites,care_taker = row
        if pd.isna(year) != True and pd.isna(term) != True and pd.isna(subject_code) != True:
            prerequisites = prerequisites.split(',') if prerequisites else []
            corequisites = corequisites.split(',') if corequisites else []
            if year != None or year:
                year = int(year)
            if term != None:
                term = int(term)
            semester_key = (year, term)
            if semester_key not in subjects_dict:
                subjects_dict[semester_key] = {}

            subjects_dict[semester_key][subject_code] = {
                "title": title,
                "lec_hrs":lec_hrs,
                "lab_hrs":lab_hrs,
                "prerequisites": [prereq.strip() for prereq in prerequisites],
                "corequisites": [coreq.strip() for coreq in corequisites],
                "credit_unit": credit_units,
                "care_taker": care_taker
            }
    return subjects_dict

def save_data_to_sand_db(data,userID,sandBox_name):
    sand_db = f'{path_sandBox}/{userID}_sandBox.db'
    try:
        with sqlite3.connect(sand_db) as conn:
            conn.execute(f"DELETE FROM {sandBox_name};")
            # print(data)
            conn.executemany(
                f"""
                INSERT INTO {sandBox_name}(Year,Term,Code,Title,[Lec Hrs],[Lab Hrs],[Credit Units],Prerequisites,Co_requisites,[Care Taker])
                VALUES(?,?,?,?,?,?,?,?,?,?)""",data)
            return True
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False
