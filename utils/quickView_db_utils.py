import sqlite3
from utils.db_utils import get_department,initialize_department_dir

department_path = './data/curriculum/'

def get_table_names(department_ID,program):
    department = get_department(department_ID)
    initialize_department_dir(department)
    curriculum = f'./data/curriculum/{department}/{program}_curriculum.db'
    try:
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

def load_subjects_from_db(department_ID,program,table):
    department = get_department(department_ID)
    initialize_department_dir(department)
    curriculum = f'./data/curriculum/{department}/{program}_curriculum.db'
    try:
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            subjects = cursor.fetchall()
            subjects_dict = {}
            for row in subjects:
                year,term,subject_code,title,lec_hrs,lab_hrs,credit_units,prerequisites,corequisites,care_taker = row
                prerequisites = prerequisites.split(',') if prerequisites else []
                corequisites = corequisites.split(',') if corequisites else []
                if year != None:
                    year = int(year)
                if term != None:
                    term = int(term)
                # semester_key = (year, term)
                if year not in subjects_dict:
                    subjects_dict[year] = {}
                if term not in subjects_dict[year]:
                    subjects_dict[year][term] = {}
                subjects_dict[year][term][subject_code] = {
                    "year": year,
                    "term": term,
                    "title": title,
                    "lec_hrs":lec_hrs,
                    "lab_hrs":lab_hrs,
                    "prerequisites": [prereq.strip() for prereq in prerequisites],
                    "corequisites": [coreq.strip() for coreq in corequisites],
                    "credit_unit": credit_units,
                    "care_taker": care_taker
                }
            return subjects_dict
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return {}

def format_for_graph(department_ID,program,table):
    department = get_department(department_ID)
    initialize_department_dir(department)
    curriculum = f'./data/curriculum/{department}/{program}_curriculum.db'
    try:
        with sqlite3.connect(curriculum) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            subjects = cursor.fetchall()
            subjects_dict = {}
            for row in subjects:
                year,term,subject_code,title,lec_hrs,lab_hrs,credit_units,prerequisites,corequisites,care_taker = row
                prerequisites = prerequisites.split(',') if prerequisites else []
                corequisites = corequisites.split(',') if corequisites else []
                if year != None:
                    year = int(year)
                if term != None:
                    term = int(term)
                semester_key = (year, term)
                if semester_key not in subjects_dict:
                    subjects_dict[semester_key] = {}
                subjects_dict[semester_key][subject_code] = {
                    "year": year,
                    "term": term,
                    "title": title,
                    "lec_hrs":lec_hrs,
                    "lab_hrs":lab_hrs,
                    "prerequisites": [prereq.strip() for prereq in prerequisites],
                    "corequisites": [coreq.strip() for coreq in corequisites],
                    "credit_unit": credit_units,
                    "care_taker": care_taker
                }
            print(subjects_dict)
            return subjects_dict
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return {}
