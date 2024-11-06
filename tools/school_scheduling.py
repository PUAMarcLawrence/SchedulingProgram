import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import hashlib

# Database setup
conn = sqlite3.connect('data/school.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS schedules (
                class_name TEXT,
                start_time TEXT,
                end_time TEXT,
                days TEXT,
                username TEXT)''')

# If the table already exists, add the role column to users and username column to schedules
c.execute("PRAGMA table_info(users)")
columns = [column[1] for column in c.fetchall()]
if 'role' not in columns:
    c.execute("ALTER TABLE users ADD COLUMN role TEXT")

c.execute("PRAGMA table_info(schedules)")
columns = [column[1] for column in c.fetchall()]
if 'username' not in columns:
    c.execute("ALTER TABLE schedules ADD COLUMN username TEXT")

conn.commit()

class School:
    def __init__(self):
        self.class_duration = timedelta(hours=1, minutes=15)
        self.time_slots = self.generate_time_slots()
        self.days_options = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "MWF", "TTHS"]

    def generate_time_slots(self):
        start_time = datetime.strptime("7:30 AM", "%I:%M %p")
        end_time = datetime.strptime("9:15 PM", "%I:%M %p")
        slots = []
        while start_time + self.class_duration <= end_time:
            slots.append(start_time.strftime("%I:%M %p"))
            start_time += self.class_duration
        return slots

    def add_class(self, class_name, time_slot, days, username):
        if not class_name.strip():
            st.error("Class name cannot be empty.")
            return False

        class_name = class_name.lower()

        # Check if the class already exists
        c.execute("SELECT * FROM schedules WHERE class_name = ?", (class_name,))
        if c.fetchone():
            st.error(f"Class '{class_name}' already exists.")
            return False
        
        try:
            start_time = datetime.strptime(time_slot, "%I:%M %p")
        except ValueError:
            st.error("Invalid time slot selected.")
            return False
        
        end_time = start_time + self.class_duration

        day_mapping = {
            "MWF": ["Mon", "Wed", "Fri"],
            "TTHS": ["Tues", "Thurs", "Sat"]
        }

        if days in day_mapping:
            days_list = day_mapping[days]
        else:
            days_list = [days]

        for day in days_list:
            if not self.is_time_slot_available(start_time, end_time, day):
                st.error(f"Time slot {time_slot} on {day} is already booked. Please choose a different time.")
                return False

        for day in days_list:
            c.execute("INSERT INTO schedules (class_name, start_time, end_time, days, username) VALUES (?, ?, ?, ?, ?)",
                      (class_name, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), day, username))
        conn.commit()
        return True

    def is_time_slot_available(self, start_time, end_time, day):
        c.execute("SELECT * FROM schedules WHERE days = ?", (day,))
        for row in c.fetchall():
            existing_start = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            existing_end = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            if (start_time < existing_end and end_time > existing_start):
                return False
        return True

    def display_schedule(self):
        c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules")
        schedules = c.fetchall()
        if not schedules:
            st.info("No schedules to display.")
            return

        columns = ["Time", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
        df = pd.DataFrame(columns=columns)

        for time_slot in self.time_slots:
            df = pd.concat([df, pd.DataFrame([[time_slot] + [""] * (len(columns) - 1)], columns=columns)], ignore_index=True)

        for class_name, start_time, end_time, day, username in schedules:
            start_time_str = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            day_mapping = {
                "MWF": ["Mon", "Wed", "Fri"],
                "TTHS": ["Tues", "Thurs", "Sat"]
            }
            days_to_display = day_mapping.get(day, [day])
            for display_day in days_to_display:
                display_text = f"{class_name}\n(Added by: {username})"
                df.loc[df["Time"] == start_time_str, display_day] = display_text

        st.dataframe(df, use_container_width=True, height=425)

    def export_schedule_to_excel(self):
        try:
            c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules")
            schedules = c.fetchall()
            if not schedules:
                st.info("No schedules to export.")
                return

            columns = ["Time", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
            df = pd.DataFrame(columns=columns)

            for time_slot in self.time_slots:
                df = pd.concat([df, pd.DataFrame([[time_slot] + [""] * (len(columns) - 1)], columns=columns)], ignore_index=True)

            for class_name, start_time, end_time, day, username in schedules:
                start_time_str = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                day_mapping = {
                    "MWF": ["Mon", "Wed", "Fri"],
                    "TTHS": ["Tues", "Thurs", "Sat"]
                }
                days_to_display = day_mapping.get(day, [day])
                for display_day in days_to_display:
                    display_text = f"{class_name}\n(Added by: {username})"
                    df.loc[df["Time"] == start_time_str, display_day] = display_text

            file_path = "schedules.xlsx"
            df.to_excel(file_path, index=False)
            st.success(f"Schedules exported to {file_path}")
        except Exception as e:
            st.error(f"An error occurred while exporting schedules: {e}")

    def list_classes(self):
        c.execute("SELECT DISTINCT class_name FROM schedules WHERE username = ?", (st.session_state.username,))
        classes = c.fetchall()
        return [class_name[0] for class_name in classes]

    def delete_class(self, class_name):
        if st.session_state.role == "Dean":
            c.execute("DELETE FROM schedules WHERE class_name = ?", (class_name,))
        else:
            c.execute("DELETE FROM schedules WHERE class_name = ? AND username = ?", (class_name, st.session_state.username))
        conn.commit()
        st.success(f"Class '{class_name}' has been deleted from the schedule.")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]

    username = st.text_input("Username").lower()
    password = st.text_input("Password", type="password")
    role = "Dean" if user_count == 0 else "Subject chair"
    if st.button("Register"):
        if not username:
            st.error("Username cannot be empty")
        elif not password:
            st.error("Password cannot be empty")
        else:
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                st.error("Username already exists.")
            else:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hash_password(password), role))
                conn.commit()
                st.success(f"User registered successfully as {role}.")
                st.experimental_set_query_params()

def login():
    username = st.text_input("Username").lower()
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
        user = c.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user[2]  # Store the role in session state
            st.session_state.delete_mode = False
            st.success("Login successful!")
            st.experimental_set_query_params()
        else:
            st.error("Invalid username or password.")

def main_program():
    school = School()
    st.title("School Scheduling Program")

    st.sidebar.header("Menu")
    if st.session_state.role == "Dean":
        menu_option = st.sidebar.selectbox("Choose an option", ["Add Class", "Show Schedule", "Export Schedule to Excel", "Delete Class"])
    else:
        menu_option = st.sidebar.selectbox("Choose an option", ["Add Class", "Show Schedule", "Export Schedule to Excel", "Delete Class"])

    if menu_option == "Add Class":
        st.header("Add a Class")
        class_name = st.text_input("Class Name")
        time_slot = st.selectbox("Time Slot", school.time_slots)
        days = st.selectbox("Days", school.days_options)

        if st.button("Add Class"):
            if school.add_class(class_name, time_slot, days, st.session_state.username):
                st.success(f"Class '{class_name}' scheduled successfully.")
            else:
                st.error(f"Time slot {time_slot} on {days} is already booked. Please choose a different time.")

    elif menu_option == "Show Schedule":
        st.header("Class Schedule")
        school.display_schedule()

    elif menu_option == "Export Schedule to Excel":
        st.header("Export Schedule to Excel")
        if st.button("Export"):
            school.export_schedule_to_excel()

    elif menu_option == "Delete Class":
        st.header("Delete a Class")
        if st.button("Start Deleting Classes"):
            st.session_state.delete_mode = True

        if st.session_state.delete_mode:
            classes = school.list_classes()
            if classes:
                delete_class_name = st.selectbox("Select Class to Delete", classes)
                if st.button("Confirm Delete"):
                    school.delete_class(delete_class_name)
                    st.session_state.delete_mode = False  # Exit delete mode after deletion
                    st.experimental_set_query_params(refresh=True)  # Refresh the app to update the schedule display
                    st.success(f"Class '{delete_class_name}' has been deleted.")
            else:
                st.info("No classes available to delete.")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'delete_mode' not in st.session_state:
    st.session_state.delete_mode = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""

# Start the program with the login or register window
if not st.session_state.logged_in:
    st.title("Welcome to the School Scheduling Program")
    option = st.selectbox("Choose an option", ["Login", "Register"])

    if option == "Login":
        login()
    elif option == "Register":
        register()
else:
    main_program()

# Close the database connection when the program ends
conn.close()
