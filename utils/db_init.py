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
                
            )