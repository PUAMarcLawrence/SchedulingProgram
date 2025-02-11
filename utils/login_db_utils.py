import sqlite3
from utils.db_utils import schoolAddrDB, hash_password, add_department, get_departmentID, get_programID,get_program

def check_anyUser():
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                return True
            return False
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False

def create_admin(username, password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                    '''
                    INSERT INTO users (username, password, department_ID, role, program_ID, color) 
                    VALUES (:username, :password, :department, :role, :program, :color)
                    ''',
                    {
                        'username': username,
                        'password': hash_password(password),
                        'department': None,
                        'role': 'Admin',
                        'program': None,
                        'color': '#000000'
                    })
        return True
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False

def get_departments():
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department FROM departments")
            departments = [row[0] for row in cursor.fetchall()]
        return departments
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

def get_vacant_programs(department):
    if department == None:
        return []
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT department_ID 
                FROM departments 
                WHERE department = :department
                """, 
                {'department': department}
            )
            department_ID = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT program_ID 
                FROM users 
                WHERE department_ID = :department
                """, 
                {'department': department_ID}
            )
            registered_programs = [row[0] for row in cursor.fetchall()]
            cursor.execute(
                """
                SELECT program_ID, program 
                FROM programs 
                WHERE department_ID = :department
                """, 
                {'department': department_ID}
            )
            programs_in_department = [row[0] for row in cursor.fetchall()]
            unregistered_programs = [x for x in programs_in_department if x not in registered_programs]
            return [get_program(programID) for programID in unregistered_programs]
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return []

def create_user(username, password, department, role, program, color):
    try:
        # Open database connection
        with sqlite3.connect(schoolAddrDB) as conn:
            if role == 'Dean':
                add_department(department)
            else:
                program = get_programID(program)
            conn.execute(
                '''
                INSERT INTO users (username, password, department_ID, role, program_ID, color) 
                VALUES (:username, :password, :department, :role, :program, :color)
                ''', 
                {
                    'username': username, 
                    'password': hash_password(password),
                    'department': get_departmentID(department),
                    'role': role, 
                    'program': program,
                    'color': color
                }
            )
        return {"success": True, "message": f"{role} Registration successful! You can now log in."}
    except sqlite3.IntegrityError as ie:
        return {"success": False, "message": "Username already exists/Color already used. Please choose a different one."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    
def check_login(username, password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT ID, username, password, role, department_ID, program_ID, color
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
    
def check_old_password(username,old_password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT password
                FROM users 
                WHERE username = :username
                ''',
                {
                    'username': username
                }
            )
            result = cursor.fetchone()
            if result[0] != hash_password(old_password):
                return False
            else:
                return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    
def change_password_to_new(username,new_password):
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            conn.execute(
                '''
                UPDATE users
                SET password = :password
                WHERE username = :username
                ''',
                {
                    'password': hash_password(new_password),
                    'username': username
                }
            )
            return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None