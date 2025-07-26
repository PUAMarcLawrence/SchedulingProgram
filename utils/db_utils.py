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

    schema_statements = [
        '''PRAGMA foreign_keys = ON;''',

        '''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, 
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            color TEXT NOT NULL UNIQUE
        );''',

        '''CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY,
            department_name TEXT NOT NULL UNIQUE,
            dean_id INTEGER UNIQUE,
            FOREIGN KEY (dean_id) REFERENCES users(user_id) ON DELETE SET NULL
        );''',

        '''CREATE TABLE IF NOT EXISTS programs (
            program_id INTEGER PRIMARY KEY,
            program_name TEXT NOT NULL UNIQUE,
            chair_id INTEGER UNIQUE,
            department_id INTEGER NOT NULL,
            FOREIGN KEY (chair_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
        );''',

        '''CREATE TABLE IF NOT EXISTS curriculum (
            curriculum_id INTEGER PRIMARY KEY,
            curriculum_name TEXT NOT NULL UNIQUE,
            program_id INTEGER NOT NULL,
            department_id INTEGER NOT NULL,
            FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE SET NULL,
            FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
        );''',

        '''CREATE TABLE IF NOT EXISTS course (
            course_id INTEGER PRIMARY KEY,
            course_code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            lec_hrs REAL,
            lab_hrs REAL,
            units INTEGER NOT NULL,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
        );''',

        '''CREATE TABLE IF NOT EXISTS curriculum_course (
            curriculum_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            term INTEGER NOT NULL,
            year_standing INTEGER,
            PRIMARY KEY (curriculum_id, course_id),
            FOREIGN KEY (curriculum_id) REFERENCES curriculum(curriculum_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
        );''',

        '''CREATE TABLE IF NOT EXISTS course_prerequisite (
            curriculum_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            prerequisite_course_id INTEGER NOT NULL,
            PRIMARY KEY (curriculum_id, course_id, prerequisite_course_id),
            FOREIGN KEY (curriculum_id) REFERENCES curriculum(curriculum_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_course_id) REFERENCES course(course_id) ON DELETE CASCADE
        );''',

        ''' CREATE TABLE IF NOT EXISTS course_corequisite (
            curriculum_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            corequisite_course_id INTEGER NOT NULL,
            PRIMARY KEY (curriculum_id, course_id, corequisite_course_id),
            FOREIGN KEY (curriculum_id) REFERENCES curriculum(curriculum_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
            FOREIGN KEY (corequisite_course_id) REFERENCES course(course_id) ON DELETE CASCADE
        );''',
    ]

    try:
        with sqlite3.connect(university_db) as conn:
            cursor = conn.cursor()
            for stmt in schema_statements:
                cursor.execute(stmt)
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database initialization error: {e}")

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
                RETURNING user_id

                ''',
                (username, hash_password(password), role, color,)
            )
            user_id = cursor.fetchone()[0]
            
            if department is not None:
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO departments (department_name)
                    VALUES (?)
                    ''',
                    (department,)
                )
                cursor.execute(
                    '''
                    SELECT department_id FROM departments WHERE department_name = ?
                    ''',
                    (department,)
                )
                department_id = cursor.fetchone()[0]
            
            match role:
                case "Dean":
                    cursor.execute(
                        '''
                        UPDATE departments
                        SET dean_id = ?
                        WHERE department_id = ? AND (dean_id IS NULL)
                        ''',
                        (user_id, department_id,)
                    )
                    if cursor.rowcount == 0:
                        raise sqlite3.IntegrityError("Department already has a dean.")
                case "Subject Chair":
                    if program is not None:
                        cursor.execute(
                            '''
                            INSERT OR IGNORE INTO programs (program_name, department_id)
                            VALUES (?, ?)
                            ''',
                            (program, department_id,)
                        )
                    cursor.execute(
                        '''
                        UPDATE programs
                        SET chair_id = ?
                        WHERE program_name = ? AND (chair_id IS NULL)
                        ''',
                        (user_id, program,)
                    )
                    if cursor.rowcount == 0:
                        raise sqlite3.IntegrityError("Program already has a chair person.")
            conn.commit()
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
    hashed_pw = hash_password(password)
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                users.user_id,
                users.username,
                users.role,
                users.color,
                departments.department_name,
                programs.program_name
            FROM users
            LEFT JOIN programs ON users.user_id = programs.chair_id
            LEFT JOIN departments ON 
                (users.role = 'Subject Chair' AND programs.department_id = departments.department_id) 
                OR (users.role != 'Subject Chair' AND users.user_id = departments.dean_id)
            WHERE users.username = ? AND users.password = ?
            ''',
            (username, hashed_pw,)
        )
        return cursor.fetchone()

def change_password_to_new(username,old_password,new_password):
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION;')
            # Update only if the old password matches
            cursor.execute(
                '''
                UPDATE users
                SET password = ?
                WHERE username = ? AND password = ?
                ''',
                (hash_password(new_password), username, hash_password(old_password))
            )
            if cursor.rowcount == 0:
                raise sqlite3.IntegrityError("Incorrect old Password, please try again.")
            conn.commit()
            return {"status": True, "message": "Password Successfully Changed."}
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "users.password" in str(e):
                return {"status": False, "message": "Enter a UNIQUE password."}
            return {"status": False, "message": str(e)}

