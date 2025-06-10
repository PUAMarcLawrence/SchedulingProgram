import sqlite3
import os
import hashlib
import pandas as pd

db_path = './data'
university_db = db_path +'/university.db'

#===========================Account Creation/Modification===========================
def initialize_db():
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION;')
            cursor.execute('PRAGMA foreign_keys = ON;')
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    color TEXT NOT NULL UNIQUE
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS departments (
                    department_id INTEGER PRIMARY KEY,
                    department_name TEXT NOT NULL UNIQUE,
                    dean_id INTEGER UNIQUE,
                    FOREIGN KEY (dean_id) REFERENCES users(user_id) ON DELETE SET NULL
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS programs (
                    program_id INTEGER PRIMARY KEY,
                    program_name TEXT NOT NULL UNIQUE,
                    chair_id INTEGER UNIQUE,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (chair_id) REFERENCES users(user_id) ON DELETE SET NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS curriculum (
                    curriculum_id INTEGER PRIMARY KEY,
                    program_year TEXT NOT NULL UNIQUE,
                    program_id INTEGER NOT NULL,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE SET NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY,
                    code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    lec_hrs REAL,
                    lab_hrs REAL,
                    units INTEGER NOT NULL,
                    deptartment_id INTEGER,
                    FOREIGN KEY (deptartment_id) REFERENCES departments(department_id) ON DELETE SET NULL
                )'''
            )
            cursor.execute(
                ''' CREATE TABLE IF NOT EXISTS subjects (
                    curriculum_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    term INTEGER NOT NULL,
                    year_standing INTEGER,
                    subject_id TEXT NOT NULL,
                    pre_requisites TEXT,
                    co_requisites TEXT,
                    FOREIGN KEY (curriculum_id) REFERENCES curriculum(curriculum_id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES courses(course_id) ON DELETE CASCADE

                )'''
            )
            
            conn.commit()
        except sqlite3.OperationalError as e:
            conn.rollback()
            print(f"Error creating tables: {e}")

def admin_registeration_check():
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
        count = cursor.fetchone()[0]
    return count == 0

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username,password,role,department,program,color):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION;')
            cursor.execute(
                '''
                INSERT INTO users (username, password, role, color) 
                VALUES (?, ?, ?, ?)
                ''',
                (username, hash_password(password), role, color,)
            )
            if department is not None:
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO departments (department_name)
                    VALUES (?)
                    ''',
                    (department,)
                )
            if role == "Dean":
                cursor.execute(
                    '''
                    UPDATE departments
                    SET dean_id = (SELECT user_id FROM users WHERE username = ?)
                    WHERE department_name = ? AND (dean_id IS NULL)
                    ''',
                    (username, department,)
                )
                if cursor.rowcount == 0:
                    raise sqlite3.IntegrityError("Department already has a dean.")
            if program is not None:
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO programs (program_name, department_id)
                    VALUES (?, (SELECT department_id FROM departments WHERE department_name = ?))
                    ''',
                    (program, department,)
                )
            if role == "Subject Chair":
                cursor.execute(
                    '''
                    UPDATE programs
                    SET chair_id = (SELECT user_id FROM users WHERE username = ?)
                    WHERE program_name = ? AND (chair_id IS NULL)
                    ''',
                    (username, program,)
                )
                if cursor.rowcount == 0:
                    raise sqlite3.IntegrityError("Program already has a chair person.")
            conn.commit()
            if role == "Admin":
                return {"status": True, "message": f"Admin {username} created successfully."}
            else:
                return {"status": True, "message": f"{role} {username} created successfully."}
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "users.color" in str(e):
                return {"status": False, "message": "Color already in use."}
            elif "users.username" in str(e):
                return {"status": False, "message": "Username already in use."}
            elif "users.password" in str(e):
                return {"status": False, "message": "Enter a UNIQUE password."}
            return {"status": False, "message": f"Error: {e}"}

def get_departments():
    try:
        with sqlite3.connect(university_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department_name FROM departments")
            departments = [row[0] for row in cursor.fetchall()]
        return departments
    except sqlite3.Error as e:
        return []

def get_no_dean_departments():
    try:
        with sqlite3.connect(university_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department_name FROM departments WHERE (dean_id is NULL)")
            departments = [row[0] for row in cursor.fetchall()]
        return departments
    except sqlite3.Error as e:
        return []

def check_user(username,password):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.execute(
            '''
            SELECT role FROM users
            WHERE username = ? AND password = ?
            ''',
            (username, hash_password(password),)
        )
        role = cursor.fetchone()
        if role:
            if role[0] == 'Subject Chair':
                cursor = conn.execute(
                    '''
                    SELECT user_id, username, role, color, department_name, program_name FROM users
                    INNER JOIN departments ON programs.department_id = departments.department_id
                    LEFT JOIN programs ON users.user_id = programs.chair_id
                    WHERE username = ? AND password = ?
                    ''',
                    (username, hash_password(password),)
                )
            else:
                cursor = conn.execute(
                    '''
                    SELECT user_id, username, role, color, department_name, program_name FROM users
                    LEFT JOIN departments ON users.user_id = departments.dean_id
                    LEFT JOIN programs ON users.user_id = programs.chair_id
                    WHERE username = ? AND password = ?
                    ''',
                    (username, hash_password(password),)
                )
            return cursor.fetchone()
        else:
            return None

def change_password_to_new(username,old_password,new_password):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION;')
            cursor.execute(
                '''
                SELECT password FROM users
                WHERE username = ?
                ''',
                (username,)
            )
            stored_password = cursor.fetchone()[0]
            if hash_password(old_password) != stored_password:
                raise sqlite3.IntegrityError("Incorrect old Password, please try again.")
            cursor.execute(
                '''
                UPDATE users
                SET password = ?
                WHERE username = ?
                ''',
                (hash_password(new_password), username,)
            )
            if cursor.rowcount == 0:
                raise sqlite3.IntegrityError("Password change failed.")
            conn.commit()
            return {"status": True, "message": "Password Successfully Changed."}
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "users.password" in str(e):
                return {"status": False, "message": "Enter a UNIQUE password."}
            return {"status": False, "message": str(e)}

#========================Upload Curriculum=========================

def subjects_to_IDs(cursor,pre_requisites):
    subjects = [s.strip().upper() for s in pre_requisites.split(',')]
    placeholders = ', '.join('?' for _ in subjects)
    cursor.execute(
        f'''
        SELECT course_id FROM courses WHERE code IN ({placeholders})
        ''',
        subjects
    )
    numbered_subjects = [f'{item[0]}' for item in cursor.fetchall()]
    return ', '.join(numbered_subjects)

def upload_to_database(data,department_name,program_name,program_year):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION;')
            cursor.execute(
                '''
                INSERT OR IGNORE INTO curriculum (program_year,program_id,department_id)
                VALUES (?,(SELECT program_id FROM programs WHERE program_name = ?),(SELECT department_id FROM departments WHERE department_name = ?))
                ''',
                (program_year,program_name,department_name)
            )
            if cursor.rowcount == 0:
                raise sqlite3.IntegrityError("Curriculum already exists")
            for i in range(data.shape[0]):
                if data.loc[i,'Care Taker'] is not None:
                    cursor.execute(
                        '''
                        INSERT OR IGNORE INTO departments (department_name)
                        VALUES (?)
                        ''',
                        (data.loc[i,'Care Taker'].replace(" ",""),)
                    )
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO courses (code, title, lec_hrs, lab_hrs, units, deptartment_id)
                    VALUES (?, ?, ?, ?, ?, (SELECT department_id FROM departments WHERE department_name = ?))
                    ''',
                    (
                        data.loc[i,'Code'].strip().upper().replace(" ",""),
                        data.loc[i,'Title'],
                        data.loc[i,'Lec Hrs'],
                        data.loc[i,'Lab Hrs'],
                        int(data.loc[i,'Credit Units']),
                        data.loc[i,'Care Taker'].strip().upper()
                    )
                )
                
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO subjects (curriculum_id, year, term, year_standing, subject_id, pre_requisites, co_requisites)
                    VALUES ((SELECT curriculum_id FROM curriculum WHERE program_year = ?), ?, ?, ?, (SELECT course_id FROM courses WHERE code = ?), ?, ?)
                    ''',
                    (
                        program_year,  # curriculum_id from the last insert
                        int(data.loc[i,'Year']),
                        int(data.loc[i,'Term']),
                        int(data.loc[i,'Req_Year_Standing']) if pd.notna(data.loc[i,'Req_Year_Standing']) else None,
                        data.loc[i,'Code'].strip().upper().replace(" ",""),
                        subjects_to_IDs(cursor,data.loc[i,'Pre_requisites']) if pd.notna(data.loc[i,'Pre_requisites']) else None,
                        subjects_to_IDs(cursor,data.loc[i,'Co_requisites']) if pd.notna(data.loc[i,'Co_requisites']) else None
                    )
                )
            conn.commit()
            return {"status": True, "message": f"Curriculum uploaded successfully."}
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return {"status": False, "message": f"Error1: {e}"}

#===========================Curriculum Editor===========================
def get_department_curriculum_list(department):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT program_year FROM curriculum
            WHERE department_id = (SELECT department_id FROM departments WHERE department_name = ?)
            ''',
            (department,)
        )
        curriculum_list = [row[0] for row in cursor.fetchall()]
    return curriculum_list

def get_curriculum_data(program,department,program_year):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT subjects.year, subjects.term, subjects.year_standing, courses.code, courses.title, 
                   courses.lec_hrs, courses.lab_hrs, courses.units, subjects.pre_requisites, subjects.co_requisites
            FROM curriculum
            JOIN subjects ON curriculum.curriculum_id = subjects.curriculum_id
            JOIN courses ON courses.course_id = subjects.subject_id =
            WHERE curriculum.program_year = ?
            ''',
            (program_year,)
        )
        data = cursor.fetchall()
    return pd.DataFrame(data, columns=[
        'Year', 'Term', 'Req_Year_Standing', 'Code', 'Title', 
        'Lec Hrs', 'Lab Hrs', 'Credit Units', 'Pre_requisites', 'Co_requisites'
    ])