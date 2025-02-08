import sqlite3

def copy_table(source_db, userID, source_table_name, new_table_name):
    dest_db = f'data/sandBox/{userID}_sandBox.db'
    try:
        with sqlite3.connect(source_db) as source_conn, sqlite3.connect(dest_db) as dest_conn:
            source_cursor = source_conn.cursor()
            dest_cursor = dest_conn.cursor()

            source_cursor.execute(
                f"""
                SELECT sql 
                FROM sqlite_master 
                WHERE type ='table' AND name='{source_table_name}'
                """
                )
            schema_result = source_cursor.fetchone()
            if schema_result:
                schema = schema_result[0]
                new_schema = schema.replace(source_table_name, new_table_name,1)
                dest_cursor.execute(new_schema)
                source_cursor.execute(
                    f"""
                    SELECT * 
                    FROM {source_table_name}
                    """
                )
                rows = source_cursor.fetchall()
                column_names = [desc[0] for desc in source_cursor.description]
                columns_str = "[" + "], [".join(column_names) + "]"
                placeholders = ", ".join(["?"] * len(column_names))
                dest_cursor.executemany(
                    f"""
                    INSERT INTO {new_table_name} ({columns_str}) 
                    VALUES ({placeholders})
                    """, 
                    rows
                )
                return True
            else:
                return False
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False

def create_sandTable(userID,table_name):
    sandAddrDB = f'data/sandBox/{userID}_sandBox.db'
    try:
        with sqlite3.connect(sandAddrDB) as conn:
            conn.execute(f'''CREATE TABLE IF NOT EXISTS sandBox_Dir (
                        table_name TEXT PRIMARY KEY,
                        userID INT,
                        userID FOREIGN KEY)''')
            
            conn.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                        username TEXT PRIMARY KEY, 
                        password TEXT, 
                        role TEXT, 
                        color Text)''')
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False