# Functions for authentication and password hashing
import sqlite3
import hashlib
import os

path = './data'
userAddrDB = 'data/school.db'

def initialize_db():
    if not os.path.exists(path):
        os.mkdir(path)
    try:
        with sqlite3.connect(userAddrDB) as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS departments (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         department TEXT NOT NULL UNIQUE
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT NOT NULL UNIQUE, 
                         password TEXT NOT NULL UNIQUE,
                         department foriegn key REFERENCES departments(department),
                         role TEXT NOT NULL, 
                         program foriegn key REFERENCES programs(program),
                         color TEXT NOT NULL UNIQUE
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS programs (
                         ID INTEGER PRIMARY KEY AUTOINCREMENT,
                         program TEXT NOT NULL UNIQUE,
                         department foriegn key REFERENCES departments(department)
                )
            ''')

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                conn.execute(
                    '''
                    INSERT INTO users (username, password, department, role, program, color) 
                    VALUES (:username, :password, :department, :role, :program, :color)
                    ''',
                    {
                        'username': 'MapuaAdmin',
                        'password': hash_password('Mapua01251925'),
                        'department': 'NA',
                        'role': 'Admin',
                        'program': 'NA',
                        'color': '#000000'
                    })

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def create_user(username, password,department, role, program, color):
    try:
        # Open database connection
        with sqlite3.connect(userAddrDB) as conn:
            conn.execute(
                '''
                INSERT INTO users (username, password, department, role, program, color) 
                VALUES (:username, :password, :department, :role, :program, :color)
                ''', 
                {
                    'username': username, 
                    'password': hash_password(password),
                    'department': department,
                    'role': role, 
                    'program': program,
                    'color': color
                }
            )
        return {"success": True, "message": f"{role} Registration successful! You can now log in."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Username already exists/Color already used. Please choose a different one."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    try:
        with sqlite3.connect(userAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT username, password, department, role, color
                FROM users 
                WHERE username = :username AND password = :password
                ''',
                {
                    'username': username, 
                    'password': hash_password(password)
                }
            )
            result = cursor.fetchone()
            return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None 

def user_counts():
    try:
        with sqlite3.connect(userAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
