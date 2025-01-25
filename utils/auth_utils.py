# Functions for authentication and password hashing
import sqlite3
import hashlib

userAddrDB = 'data/school.db'

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
