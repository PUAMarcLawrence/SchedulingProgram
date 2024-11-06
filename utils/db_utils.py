# Functions for database interactions
import sqlite3
from utils.auth_utils import hash_password

userAddrDB = 'data/users.db'

def create_user_table():
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    conn.commit()
    conn.close()

def create_user(username, password, role):
    conn = sqlite3.connect(userAddrDB)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hash_password(password),role))
        conn.commit()
        conn.close()
        return True  # Return True if user creation was successful
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Return False if username already exists
