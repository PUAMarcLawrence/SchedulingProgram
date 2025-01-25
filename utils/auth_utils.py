# Functions for authentication and password hashing
import sqlite3
import hashlib

userAddrDB = 'data/school.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    c.execute(
        '''SELECT * FROM users WHERE username = :username AND password = :password''',
        {
            'username': username, 
            'password': hash_password(password)
        }
    )
    result = c.fetchone()
    conn.close()
    return result

def user_counts():
    try:
        with sqlite3.connect(userAddrDB) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            return c.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
