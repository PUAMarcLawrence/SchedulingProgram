import sqlite3


def copy_table(department,program, userID, source_table_name, new_table_name):
    source_db = f'./data/curriculum/{department}/{program}_curriculum.db'
    dest_db = f'./data/sandBox/{userID}_sandBox.db'
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

def get_sand_names(userID):
    sand_db = f'./data/sandBox/{userID}_sandBox.db'
    try:
        with sqlite3.connect(sand_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
