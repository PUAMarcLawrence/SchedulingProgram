import sqlite3
import os

db_path = './data'
users_db = db_path +'/users.db'
departments_db = db_path +'/departments.db'
programs_db = db_path +'/programs.db'
courses_db = db_path +'/courses.db'
schedules_db = db_path +'/schedules.db'

def initialize_db():
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    if not os.path.exists(users_db):
        os.makedirs(users_db)
    if not os.path.exists(departments_db):
        os.makedirs(departments_db)
    if not os.path.exists(programs_db):
        os.makedirs(programs_db)
    if not os.path.exists(courses_db):
        os.makedirs(courses_db)
    if not os.path.exists(schedules_db):
        os.makedirs(schedules_db)
    try:
        with sqlite3.connect(users_db) as conn:
            conn.execute('PRAGMA foreign_keys = ON;')
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )'''
            )
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS departments (
                    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                    daen_id INTEGER NOT NULL,
                    FOREIGN KEY (dean_id) REFERENCES users (user_id) ON DELETE CASCADE
                )'''
            )
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS programs (
                    program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    chair_id INTEGER NOT NULL,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (chair_id) REFERENCES users (user_id) ON DELETE CASCADE,
                    FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE CASCADE
                )'''
            )
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    lec_hrs INTEGER,
                    lab_hrs INTEGER,
                    credits INTEGER NOT NULL,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE CASCADE
                )'''
            )
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    semester TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
                )'''
            )
    except sqlite3.OperationalError as e:
        print(f"Error initializing database: {e}")