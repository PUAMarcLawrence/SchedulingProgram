import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from utils.auth_utils import hash_password
import io
import time

# Database setup
conn = sqlite3.connect('data/school.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT,
                color TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS curricula (
                curriculum_id INTEGER PRIMARY KEY AUTOINCREMENT,
                curriculum_name TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS school_years (
                year_id INTEGER PRIMARY KEY AUTOINCREMENT,
                year_name TEXT,
                curriculum_id INTEGER,
                FOREIGN KEY (curriculum_id) REFERENCES curricula (curriculum_id))''')

c.execute('''CREATE TABLE IF NOT EXISTS schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT,
                start_time TEXT,
                end_time TEXT,
                days TEXT,
                username TEXT,
                year_id INTEGER,
                FOREIGN KEY (year_id) REFERENCES school_years (year_id))''')

# If the table already exists, add the role and color columns to users and username and year_id columns to schedules
c.execute("PRAGMA table_info(users)")
columns = [column[1] for column in c.fetchall()]
if 'role' not in columns:
    c.execute("ALTER TABLE users ADD COLUMN role TEXT")
if 'color' not in columns:
    c.execute("ALTER TABLE users ADD COLUMN color TEXT")

c.execute("PRAGMA table_info(schedules)")
columns = [column[1] for column in c.fetchall()]
if 'username' not in columns:
    c.execute("ALTER TABLE schedules ADD COLUMN username TEXT")
if 'year_id' not in columns:
    c.execute("ALTER TABLE schedules ADD COLUMN year_id INTEGER")

conn.commit()

class School:
    def __init__(self):
        self.class_duration = timedelta(hours=1, minutes=10)  # Adjusted class duration to 1 hour and 10 minutes
        self.time_slots = self.generate_time_slots()
        self.days_options = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "MWF", "TTHS"]

    def generate_time_slots(self):
        start_time = datetime.strptime("7:00 AM", "%I:%M %p")  # Adjusted start time to 7:00 AM
        end_time = datetime.strptime("9:00 PM", "%I:%M %p")  # Adjusted end time to 9:00 PM
        slots = []
        while start_time + self.class_duration <= end_time:
            end_slot_time = (start_time + self.class_duration).strftime("%I:%M %p")
            slots.append(f"{start_time.strftime('%I:%M %p')} - {end_slot_time}")
            start_time += self.class_duration
        return slots

    def add_class(self, class_name, selected_slots, selected_days, username, year_id):
        if not class_name.strip():
            st.error("Class name cannot be empty.")
            return False

        class_name = class_name.lower()

        # Check if the class already exists for the given year
        c.execute("SELECT * FROM schedules WHERE class_name = ? AND year_id = ?", (class_name, year_id))
        if c.fetchone():
            st.error(f"Class '{class_name}' already exists for the selected year.")
            return False

        for time_slot in selected_slots:
            try:
                start_time_str, end_time_str = time_slot.split(" - ")
                start_time = datetime.strptime(start_time_str, "%I:%M %p")
                end_time = datetime.strptime(end_time_str, "%I:%M %p")
            except ValueError:
                st.error("Invalid time slot selected.")
                return False

            for day in selected_days:
                if not self.is_time_slot_available(start_time, end_time, day, year_id):
                    st.error(f"Time slot {time_slot} on {day} is already booked. Please choose a different time.")
                    return False

        for time_slot in selected_slots:
            start_time_str, end_time_str = time_slot.split(" - ")
            start_time = datetime.strptime(start_time_str, "%I:%M %p")
            end_time = datetime.strptime(end_time_str, "%I:%M %p")
            for day in selected_days:
                c.execute("INSERT INTO schedules (class_name, start_time, end_time, days, username, year_id) VALUES (?, ?, ?, ?, ?, ?)",
                          (class_name, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), day, username, year_id))
        conn.commit()
        return True

    def is_time_slot_available(self, start_time, end_time, day, year_id):
        c.execute("SELECT * FROM schedules WHERE days = ? AND year_id = ?", (day, year_id))
        for row in c.fetchall():
            existing_start = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            existing_end = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
            if (start_time < existing_end and end_time > existing_start):
                return False
        return True

    def display_schedule(self, year_id):
        c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules WHERE year_id = ?", (year_id,))
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
            end_time_str = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            time_slot_str = f"{start_time_str} - {end_time_str}"
            day_mapping = {
                "MWF": ["Mon", "Wed", "Fri"],
                "TTHS": ["Tues", "Thurs", "Sat"]
            }
            days_to_display = day_mapping.get(day, [day])
            for display_day in days_to_display:
                c.execute("SELECT color FROM users WHERE username = ?", (username,))
                user_color = c.fetchone()[0]
                display_text = f"{class_name}"
                df.loc[df["Time"] == time_slot_str, display_day] = display_text

        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    def export_schedule_to_excel(self, year_id):
        try:
            c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules WHERE year_id = ?", (year_id,))
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
                end_time_str = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                time_slot_str = f"{start_time_str} - {end_time_str}"
                day_mapping = {
                    "MWF": ["Mon", "Wed", "Fri"],
                    "TTHS": ["Tues", "Thurs", "Sat"]
                }
                days_to_display = day_mapping.get(day, [day])
                for display_day in days_to_display:
                    c.execute("SELECT color FROM users WHERE username = ?", (username,))
                    user_color = c.fetchone()[0]
                    display_text = f"{class_name}"
                    df.loc[df["Time"] == time_slot_str, display_day] = display_text

            # Convert DataFrame to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Schedule')
            output.seek(0)

            # Create a download button
            st.download_button(
                label="Download Schedule as Excel",
                data=output,
                file_name="schedules.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Schedules exported successfully.")
        except Exception as e:
            st.error(f"An error occurred while exporting schedules: {e}")

def list_classes(self, year_id):
        if st.session_state.role == "Dean":
            c.execute("SELECT DISTINCT class_name FROM schedules WHERE year_id = ?", (year_id,))
        else:
            c.execute("SELECT DISTINCT class_name FROM schedules WHERE username = ? AND year_id = ?", (st.session_state.username, year_id))
        classes = c.fetchall()
        return [class_name[0] for class_name in classes]

def delete_class(self, class_name, year_id):
        if st.session_state.role == "Dean":
            c.execute("DELETE FROM schedules WHERE class_name = ? AND year_id = ?", (class_name, year_id))
        else:
            c.execute("DELETE FROM schedules WHERE class_name = ? AND username = ? AND year_id = ?", (class_name, st.session_state.username, year_id))
        conn.commit()
        st.success(f"Class '{class_name}' has been deleted from the schedule.")

def register():
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]

    username = st.text_input("Username").lower()
    password = st.text_input("Password", type="password")
    color = st.color_picker("Pick a color to represent your account")
    role = "Dean" if user_count == 0 else "Subject Chair"
    if st.button("Register"):
        if not username:
            st.error("Username cannot be empty")
        elif not password:
            st.error("Password cannot be empty")
        elif not color:
            st.error("Please pick a color")
        else:
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                st.error("Username already exists.")
            else:
                hashed_password = hash_password(password)
                c.execute("INSERT INTO users (username, password, role, color) VALUES (?, ?, ?, ?)", (username, hashed_password, role, color))
                conn.commit()
                st.success(f"User registered successfully as {role}.")
                st.experimental_set_query_params()

# Database setup
conn = sqlite3.connect('data/school.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT,
                color TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS curricula (
                curriculum_id INTEGER PRIMARY KEY AUTOINCREMENT,
                curriculum_name TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS school_years (
                year_id INTEGER PRIMARY KEY AUTOINCREMENT,
                year_name TEXT,
                curriculum_id INTEGER,
                FOREIGN KEY (curriculum_id) REFERENCES curricula (curriculum_id))''')

c.execute('''CREATE TABLE IF NOT EXISTS schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT,
                start_time TEXT,
                end_time TEXT,
                days TEXT,
                username TEXT,
                year_id INTEGER,
                curriculum_id INTEGER,
                FOREIGN KEY (year_id) REFERENCES school_years (year_id),
                FOREIGN KEY (curriculum_id) REFERENCES curricula (curriculum_id))''')

# If the table already exists, add the role and color columns to users and username and year_id columns to schedules
c.execute("PRAGMA table_info(users)")
columns = [column[1] for column in c.fetchall()]
if 'role' not in columns:
    c.execute("ALTER TABLE users ADD COLUMN role TEXT")
if 'color' not in columns:
    c.execute("ALTER TABLE users ADD COLUMN color TEXT")

c.execute("PRAGMA table_info(schedules)")
columns = [column[1] for column in c.fetchall()]
if 'username' not in columns:
    c.execute("ALTER TABLE schedules ADD COLUMN username TEXT")
if 'year_id' not in columns:
    c.execute("ALTER TABLE schedules ADD COLUMN year_id INTEGER")
if 'curriculum_id' not in columns:
    c.execute("ALTER TABLE schedules ADD COLUMN curriculum_id INTEGER")

conn.commit()

class School:
    def __init__(self):
        self.class_duration = timedelta(hours=1, minutes=10)  # Adjusted class duration to 1 hour and 10 minutes
        self.time_slots = self.generate_time_slots()
        self.days_options = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "MWF", "TTHS"]

    def generate_time_slots(self):
        start_time = datetime.strptime("7:00 AM", "%I:%M %p")  # Adjusted start time to 7:00 AM
        end_time = datetime.strptime("9:00 PM", "%I:%M %p")  # Adjusted end time to 9:00 PM
        slots = []
        while start_time + self.class_duration <= end_time:
            end_slot_time = (start_time + self.class_duration).strftime("%I:%M %p")
            slots.append(f"{start_time.strftime('%I:%M %p')} - {end_slot_time}")
            start_time += self.class_duration
        return slots

    def add_class(self, class_name, selected_slots, selected_days, username, year_id, curriculum_id):
        if not class_name.strip():
            st.error("Class name cannot be empty.")
            return False

        class_name = class_name.lower()

        # Check if the class already exists for the given year and curriculum
        c.execute("SELECT * FROM schedules WHERE class_name = ? AND year_id = ? AND curriculum_id = ?", (class_name, year_id, curriculum_id))
        if c.fetchone():
            st.error(f"Class '{class_name}' already exists for the selected year and curriculum.")
            return False

        for time_slot in selected_slots:
            try:
                start_time_str, end_time_str = time_slot.split(" - ")
                start_time = datetime.strptime(start_time_str, "%I:%M %p")
                end_time = datetime.strptime(end_time_str, "%I:%M %p")
            except ValueError:
                st.error("Invalid time slot selected.")
                return False

            for day in selected_days:
                if not self.is_time_slot_available(start_time, end_time, day, year_id, curriculum_id):
                    st.error(f"Time slot {time_slot} on {day} is already booked. Please choose a different time.")
                    return False

        for time_slot in selected_slots:
            start_time_str, end_time_str = time_slot.split(" - ")
            start_time = datetime.strptime(start_time_str, "%I:%M %p")
            end_time = datetime.strptime(end_time_str, "%I:%M %p")
            for day in selected_days:
                c.execute("INSERT INTO schedules (class_name, start_time, end_time, days, username, year_id, curriculum_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (class_name, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), day, username, year_id, curriculum_id))
        conn.commit()
        return True

    def is_time_slot_available(self, start_time, end_time, day, year_id, curriculum_id):
        c.execute("SELECT * FROM schedules WHERE days = ? AND year_id = ? AND curriculum_id = ?", (day, year_id, curriculum_id))
        for row in c.fetchall():
            existing_start = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            existing_end = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
            if (start_time < existing_end and end_time > existing_start):
                return False
        return True

    def display_schedule(self, year_id, curriculum_id):
        c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules WHERE year_id = ? AND curriculum_id = ?", (year_id, curriculum_id))
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
            end_time_str = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            time_slot_str = f"{start_time_str} - {end_time_str}"
            day_mapping = {
                "MWF": ["Mon", "Wed", "Fri"],
                "TTHS": ["Tues", "Thurs", "Sat"]
            }
            days_to_display = day_mapping.get(day, [day])
            for display_day in days_to_display:
                c.execute("SELECT color FROM users WHERE username = ?", (username,))
                user_color = c.fetchone()[0]
                display_text = f"{class_name}"
                df.loc[df["Time"] == time_slot_str, display_day] = display_text

        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    def export_schedule_to_excel(self, year_id, curriculum_id):
        try:
            c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules WHERE year_id = ? AND curriculum_id = ?", (year_id, curriculum_id))
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
                end_time_str = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                time_slot_str = f"{start_time_str} - {end_time_str}"
                day_mapping = {
                    "MWF": ["Mon", "Wed", "Fri"],
                    "TTHS": ["Tues", "Thurs", "Sat"]
                }
                days_to_display = day_mapping.get(day, [day])
                for display_day in days_to_display:
                    c.execute("SELECT color FROM users WHERE username = ?", (username,))
                    user_color = c.fetchone()[0]
                    display_text = f"{class_name}"
                    df.loc[df["Time"] == time_slot_str, display_day] = display_text

            # Convert DataFrame to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Schedule')
            output.seek(0)

            # Create a download button
            st.download_button(
                label="Download Schedule as Excel",
                data=output,
                file_name="schedules.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Schedules exported successfully.")
        except Exception as e:
            st.error(f"An error occurred while exporting schedules: {e}")

    def list_classes(self, year_id, curriculum_id):
        if st.session_state.role == "Dean":
            c.execute("SELECT DISTINCT class_name FROM schedules WHERE year_id = ? AND curriculum_id = ?", (year_id, curriculum_id))
        else:
            c.execute("SELECT DISTINCT class_name FROM schedules WHERE username = ? AND year_id = ? AND curriculum_id = ?", (st.session_state.username, year_id, curriculum_id))
        classes = c.fetchall()
        return [class_name[0] for class_name in classes]

    def delete_class(self, class_name, year_id, curriculum_id):
        if st.session_state.role == "Dean":
            c.execute("DELETE FROM schedules WHERE class_name = ? AND year_id = ? AND curriculum_id = ?", (class_name, year_id, curriculum_id))
        else:
            c.execute("DELETE FROM schedules WHERE class_name = ? AND username = ? AND year_id = ? AND curriculum_id = ?", (class_name, st.session_state.username, year_id, curriculum_id))
        conn.commit()
        st.success(f"Class '{class_name}' has been deleted from the schedule.")

    # def delete_curriculum(self, year_id, curriculum_id):
    #     if st.session_state.role = "Dean":
    #         c.execute("DELETE FROM WHERE AND",(year_id, curriculum_id))
    #     else:
    #         c.execute("DELETE FROM WHERE AND",(st.session_state.username, year_id, curriculum_id))  
        
        #hello
        #i do not know where to get the uhhh, delete from where and for curriculum and years

# def hash_password(password):
#     return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# def register():
#     c.execute("SELECT COUNT(*) FROM users")
#     user_count = c.fetchone()[0]

#     username = st.text_input("Username").lower()
#     password = st.text_input("Password", type="password")
#     color = st.color_picker("Pick a color to represent your account")
#     role = "Dean" if user_count == 0 else "Subject Chair"
#     if st.button("Register"):
#         if not username:
#             st.error("Username cannot be empty")
#         elif not password:
#             st.error("Password cannot be empty")
#         elif not color:
#             st.error("Please pick a color")
#         else:
#             c.execute("SELECT * FROM users WHERE username = ?", (username,))
#             if c.fetchone():
#                 st.error("Username already exists.")
#             else:
#                 hashed_password = hash_password(password)
#                 c.execute("INSERT INTO users (username, password, role, color) VALUES (?, ?, ?, ?)", (username, hashed_password, role, color))
#                 conn.commit()
#                 st.success(f"User registered successfully as {role}.")
#                 st.experimental_set_query_params()

# def login():
#     username = st.text_input("Username").lower()
#     password = st.text_input("Password", type="password")
#     if st.button("Login"):
#         c.execute("SELECT * FROM users WHERE username = ?", (username,))
#         user = c.fetchone()
#         if user and bcrypt.checkpw(password.encode(), user[1].encode()):
#             st.session_state.logged_in = True
#             st.session_state.username = username
#             st.session_state.role = user[2]
#             st.session_state.color = user[3]
#             st.session_state.delete_mode = False
#             st.success("Login successful!")
#             st.experimental_set_query_params()
#         else:
#             st.error("Invalid username or password.")

def main_program():
    school = School()
    st.title("School Scheduling Program")

    st.sidebar.header("Menu")
    menu_option = st.sidebar.selectbox("Choose an option", ["Add Curriculum", "Add School Year", "Add Class", "Show Schedule", "Export Schedule to Excel", "Delete Class", "Delete Curriculum"])

    if menu_option == "Add Curriculum":
        st.header("Add a Curriculum")
        curriculum_name = st.text_input("Curriculum Name")
        if st.button("Add Curriculum"):
            if not curriculum_name:
                st.error("Curriculum name cannot be empty.")
            else:
                c.execute("INSERT INTO curricula (curriculum_name) VALUES (?)", (curriculum_name,))
                conn.commit()
                st.success(f"Curriculum '{curriculum_name}' added successfully.")

    elif menu_option == "Add School Year":
        st.header("Add a School Year")
        c.execute("SELECT curriculum_id, curriculum_name FROM curricula")
        curricula = c.fetchall()
        curriculum_dict = {name: id for id, name in curricula}
        selected_curriculum = st.selectbox("Select Curriculum", list(curriculum_dict.keys()))
        year_name = st.text_input("School Year (e.g., 2024)")
        if st.button("Add School Year"):
            if not year_name:
                st.error("School year cannot be empty.")
            else:
                curriculum_id = curriculum_dict[selected_curriculum]
                c.execute("INSERT INTO school_years (year_name, curriculum_id) VALUES (?, ?)", (year_name, curriculum_id))
                conn.commit()
                st.success(f"School year '{year_name}' added to curriculum '{selected_curriculum}' successfully.")

    elif menu_option == "Add Class":
        st.header("Add a Class")
        c.execute("SELECT curriculum_id, curriculum_name FROM curricula")
        curricula = c.fetchall()
        curriculum_dict = {name: id for id, name in curricula}
        selected_curriculum = st.selectbox("Select Curriculum", list(curriculum_dict.keys()))

        c.execute("SELECT year_id, year_name FROM school_years WHERE curriculum_id = ?", (curriculum_dict[selected_curriculum],))
        school_years = c.fetchall()
        year_dict = {name: id for id, name in school_years}
        selected_year = st.selectbox("Select School Year", list(year_dict.keys()))

        class_name = st.text_input("Class Name")
        st.write("Select the desired time slots by clicking on the schedule below:")
        schedule_df = school.display_schedule(year_dict[selected_year], curriculum_dict[selected_curriculum])
        selected_slots = st.multiselect("Select Time Slots", school.time_slots)
        selected_days = st.multiselect("Select Days", school.days_options)
        

        if st.button("Add Class"):
            if not class_name:
                st.error("Class name cannot be empty.")
            elif not selected_slots:
                st.error("Please select at least one time slot.")
            elif not selected_days:
                st.error("Please select at least one day.")
            else:
                if school.add_class(class_name, selected_slots, selected_days, st.session_state.username, year_dict[selected_year], curriculum_dict[selected_curriculum]):
                    st.success(f"Class '{class_name}' scheduled successfully.")
                else:
                    st.error(f"Failed to schedule class '{class_name}'. Please check the selected time slots and try again.")

        st.rerun() #refreshes the schedule table after clicking on "Add class" button

    elif menu_option == "Show Schedule":
        st.header("Class Schedule")
        c.execute("SELECT curriculum_id, curriculum_name FROM curricula")
        curricula = c.fetchall()
        curriculum_dict = {name: id for id, name in curricula}
        selected_curriculum = st.selectbox("Select Curriculum", list(curriculum_dict.keys()))

        c.execute("SELECT year_id, year_name FROM school_years WHERE curriculum_id = ?", (curriculum_dict[selected_curriculum],))
        school_years = c.fetchall()
        year_dict = {name: id for id, name in school_years}
        selected_year = st.selectbox("Select School Year", list(year_dict.keys()))

        school.display_schedule(year_dict[selected_year], curriculum_dict[selected_curriculum])

    elif menu_option == "Export Schedule to Excel":
        st.header("Export Schedule to Excel")
        c.execute("SELECT curriculum_id, curriculum_name FROM curricula")
        curricula = c.fetchall()
        curriculum_dict = {name: id for id, name in curricula}
        selected_curriculum = st.selectbox("Select Curriculum", list(curriculum_dict.keys()))

        c.execute("SELECT year_id, year_name FROM school_years WHERE curriculum_id = ?", (curriculum_dict[selected_curriculum],))
        school_years = c.fetchall()
        year_dict = {name: id for id, name in school_years}
        selected_year = st.selectbox("Select School Year", list(year_dict.keys()))

        school.export_schedule_to_excel(year_dict[selected_year], curriculum_dict[selected_curriculum])

    elif menu_option == "Delete Class":
        st.header("Delete a Class")
        c.execute("SELECT curriculum_id, curriculum_name FROM curricula")
        curricula = c.fetchall()
        curriculum_dict = {name: id for id, name in curricula}
        selected_curriculum = st.selectbox("Select Curriculum", list(curriculum_dict.keys()))

        c.execute("SELECT year_id, year_name FROM school_years WHERE curriculum_id = ?", (curriculum_dict[selected_curriculum],))
        school_years = c.fetchall()
        year_dict = {name: id for id, name in school_years}
        selected_year = st.selectbox("Select School Year", list(year_dict.keys()))

        if st.button("Start Deleting Classes"):
            st.session_state.delete_mode = True

        if st.session_state.delete_mode:
            classes = school.list_classes(year_dict[selected_year], curriculum_dict[selected_curriculum])
            if classes:
                delete_class_name = st.selectbox("Select Class to Delete", classes)
                if st.button("Confirm Delete"):
                    school.delete_class(delete_class_name, year_dict[selected_year], curriculum_dict[selected_curriculum])
                    st.session_state.delete_mode = False
                    st.experimental_set_query_params(refresh=True)
                    st.success(f"Class '{delete_class_name}' has been deleted.")
                    time.sleep(2)
                    st.rerun()
                    
            else:
                st.info("No classes available to delete.")

    # elif menu_option == "Delete Curriculum":
    #     st.header("Delete a Curriculum Year")
    #     c.execute("SELECT curriculum_id, curriculum_name FROM curricula")
    #     curricula = c.fetchall()
    #     curriculum_dict = {name: id for id, name in curricula}
    #     selected_curriculum = st.selectbox("Select Curriculum", list(curriculum_dict.keys()))

    #     c.execute("SELECT year_id, year_name FROM school_years WHERE curriculum_id = ?", (curriculum_dict[selected_curriculum],))
    #     school_years = c.fetchall()
    #     year_dict = {name: id for id, name in school_years}
    #     selected_year = st.selectbox("Select School Year", list(year_dict.keys()))
        
        # if st.button("Delete Curriculum Year"):
        #     st.session_state.delete_mode = True
        
        # if st.session_state.delete.mode:
        #     year_toDelete = school.list_classes(year_dict[selected_year], curriculum_dict[selected_curriculum])
        #     if year_toDelete:
        #         delete_year = st.selectbox("Select Curriculum and Year to delete", year_toDelete)
        #         if st.buttom("Confirm Delete"):
        #             school.delete_curriculumYear(delete_year, year_dict[selected_year])
        #             st.session_state.delete_mode = False
        #             st.experimental_set_query_params(refresh=True)
        #             st.success(f"Curriculum '{delete_year}' and has been deleted")



# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'delete_mode' not in st.session_state:
    st.session_state.delete_mode = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'color' not in st.session_state:
    st.session_state.color = ""

# if not st.session_state.logged_in:
#     login()
# else:
main_program()

# Close the database connection when the program ends
conn.close()