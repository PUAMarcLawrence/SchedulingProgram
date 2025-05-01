import sqlite3
import os

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
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    color TEXT NOT NULL UNIQUE
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS departments (
                    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    daen_id INTEGER UNIQUE,
                    FOREIGN KEY (daen_id) REFERENCES users(user_id) ON DELETE SET NULL
                )'''
            )
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS programs (
                    program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
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

def admin_registered():
    with sqlite3.connect(university_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
        count = cursor.fetchone()[0]
    return count == 0