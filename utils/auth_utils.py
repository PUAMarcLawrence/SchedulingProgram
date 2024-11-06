# Functions for authentication and password hashing
import sqlite3
import hashlib

userAddrDB = 'data/users.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

def user_counts():
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    result = c.fetchone()[0]
    conn.close()
    return result