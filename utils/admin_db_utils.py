import sqlite3
import pandas as pd

# Database connection
DB_PATH = "/data/school.db"  # Change this to your database path

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def load_data(table_name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            return df
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def get_table_names():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def update_data(table_name, df):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

