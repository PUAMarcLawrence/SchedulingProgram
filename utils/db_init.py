import sqlite3
import os

db_path = './data'
university_db = db_path +'/university.db'

def initialize_db():
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    with sqlite3.connect(university_db) as conn:
        try:
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
                    name TEXT NOT NULL UNIQUE,
                    daen_id INTEGER UNIQUE,
                    FOREIGN KEY (daen_id) REFERENCES users(user_id) ON DELETE SET NULL
                )'''
            )
            
        except sqlite3.OperationalError as e:
            print(f"Error creating tables: {e}")