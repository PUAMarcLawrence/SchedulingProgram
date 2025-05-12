import sqlite3
import os
import hashlib

db_path = './data'
university_db = db_path +'/university.db'

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
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    color TEXT NOT NULL UNIQUE
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS departments (
                    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    department TEXT NOT NULL UNIQUE,
                    daen_id INTEGER UNIQUE,
                    FOREIGN KEY (daen_id) REFERENCES users(user_id) ON DELETE SET NULL
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS programs (
                    program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program TEXT NOT NULL UNIQUE,
                    chair_id INTEGER UNIQUE,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (chair_id) REFERENCES users(user_id) ON DELETE SET NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
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
            cursor.execute("SELECT 1 FROM departments WHERE department = ? LIMIT 1", (department,))
            department_exists = False
            program_exists = False
            if cursor.fetchone():
                department_exists = True
            cursor.execute("SELECT 1 FROM programs WHERE program = ? LIMIT 1", (program,))
            if cursor.fetchone():
                program_exists = True
            cursor.execute('BEGIN TRANSACTION;')
            cursor.execute(
                '''INSERT INTO users (username, password, role, color) VALUES (?, ?, ?, ?)''',
                (username, hash_password(password), role, color)
            )
            conn.commit()
            return {"status": True, "message": f"Admin {username} created successfully."}
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return {"status": False, "message": f"Error: {e}"}

def get_departments():
    try:
        with sqlite3.connect(university_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department FROM departments")
            departments = [row[0] for row in cursor.fetchall()]
        return departments
    except sqlite3.Error as e:
        return []