import io
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from utils.db_utils import schoolAddrDB

def initialize_db():
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()

            conn.execute('''CREATE TABLE IF NOT EXISTS schedules (
                            class_name TEXT,
                            section TEXT,
                            start_time TEXT,
                            end_time TEXT,
                            days TEXT,
                            username TEXT,
                            curriculum TEXT,
                            school_year TEXT)''')

            # If the table already exists, add the curriculum and school_year columns to schedules
            cursor.execute("PRAGMA table_info(schedules)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'curriculum' not in columns:
                conn.execute("ALTER TABLE schedules ADD COLUMN curriculum TEXT")
            if 'school_year' not in columns:
                conn.execute("ALTER TABLE schedules ADD COLUMN school_year TEXT")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

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

    def add_class(self, class_name, section, selected_slots, selected_days, username, curriculum, school_year):
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()

                if not class_name.strip():
                    # st.error("Class name cannot be empty.")
                    return False

                class_name = class_name.lower()

                # Check if the class already exists for the same curriculum and school year
                cursor.execute("SELECT * FROM schedules WHERE class_name = ? AND section = ? AND curriculum = ? AND school_year = ?",
                        (class_name, section, curriculum, school_year))
                if cursor.fetchone():
                    # st.error(f"Class '{class_name}' with section '{section}' already exists for {curriculum} ({school_year}).")
                    return False

                for time_slot in selected_slots:
                    try:
                        start_time_str, end_time_str = time_slot.split(" - ")
                        start_time = datetime.strptime(start_time_str, "%I:%M %p")
                        end_time = datetime.strptime(end_time_str, "%I:%M %p")
                    except ValueError:
                        # st.error("Invalid time slot selected.")
                        return False

                    for day in selected_days:
                        if not self.is_time_slot_available(start_time, end_time, day, curriculum, school_year):
                            # st.error(f"Time slot {time_slot} on {day} is already booked for {curriculum} ({school_year}). Please choose a different time.")
                            return False

                for time_slot in selected_slots:
                    start_time_str, end_time_str = time_slot.split(" - ")
                    start_time = datetime.strptime(start_time_str, "%I:%M %p")
                    end_time = datetime.strptime(end_time_str, "%I:%M %p")
                    for day in selected_days:
                        cursor.execute("INSERT INTO schedules (class_name, section, start_time, end_time, days, username, curriculum, school_year) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (class_name, section, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), day, username, curriculum, school_year))
                conn.commit()
                # st.success(f"Class '{class_name}' (Section: {section}) scheduled successfully for {curriculum} ({school_year}).")
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def is_time_slot_available(self, start_time, end_time, day, curriculum, school_year):
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM schedules WHERE days = ? AND curriculum = ? AND school_year = ?", (day, curriculum, school_year))
                for row in cursor.fetchall():
                    existing_start = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                    existing_end = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                    if (start_time < existing_end and end_time > existing_start):
                        conn.close()
                        return False
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def display_schedule(self, curriculum, school_year):
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()
        
                cursor.execute("SELECT class_name, section, start_time, end_time, days, username FROM schedules WHERE curriculum = ? AND school_year = ?", (curriculum, school_year))
                schedules = cursor.fetchall()
                if not schedules:
                    st.info(f"No schedules to display for {curriculum} ({school_year}).")
                    return

                columns = ["Time", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
                df = pd.DataFrame(columns=columns)

                for time_slot in self.time_slots:
                    df = pd.concat([df, pd.DataFrame([[time_slot] + [""] * (len(columns) - 1)], columns=columns)], ignore_index=True)

                for class_name, section, start_time, end_time, day, username in schedules:
                    start_time_str = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                    end_time_str = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                    time_slot_str = f"{start_time_str} - {end_time_str}"
                    day_mapping = {
                        "MWF": ["Mon", "Wed", "Fri"],
                        "TTHS": ["Tues", "Thurs", "Sat"]
                    }
                    days_to_display = day_mapping.get(day, [day])
                    for display_day in days_to_display:
                        cursor.execute("SELECT color FROM users WHERE username = ?", (username,))
                        user_color = cursor.fetchone()[0]
                        display_text = f"<span style='color:{user_color}'>{class_name} (Section: {section})</span>"
                        df.loc[df["Time"] == time_slot_str, display_day] = display_text

                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def edit_class(self, old_class_name, old_section, new_class_name, new_section, username, curriculum, school_year):
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()
                # Check if the user is the Dean or the creator of the class
                cursor.execute("SELECT username FROM schedules WHERE class_name = ? AND section = ? AND curriculum = ? AND school_year = ?",
                        (old_class_name, old_section, curriculum, school_year))
                result = cursor.fetchone()
                if not result:
                    st.error(f"Class '{old_class_name}' (Section: {old_section}) not found for {curriculum} ({school_year}).")
                    return False

                creator_username = result[0]
                if st.session_state.role != "Dean" and st.session_state.username != creator_username:
                    st.error("You do not have permission to edit this class.")
                    return False

                # Update the class name and section
                cursor.execute("UPDATE schedules SET class_name = ?, section = ? WHERE class_name = ? AND section = ? AND curriculum = ? AND school_year = ?",
                        (new_class_name, new_section, old_class_name, old_section, curriculum, school_year))
                conn.commit()
                st.success(f"Class '{old_class_name}' (Section: {old_section}) updated to '{new_class_name}' (Section: {new_section}) for {curriculum} ({school_year}).")
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def export_schedule_to_excel(self):
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT class_name, start_time, end_time, days, username FROM schedules")
                schedules = cursor.fetchall()
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
                        cursor.execute("SELECT color FROM users WHERE username = ?", (username,))
                        user_color = cursor.fetchone()[0]
                        display_text = f"{class_name}"
                        df.loc[df["Time"] == time_slot_str, display_day] = display_text

                # Convert DataFrame to Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Schedule')
                output.seek(0)

                # Create a download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"schedules_{timestamp}.xlsx"
                st.download_button(
                    label="Download Schedule as Excel",
                    data=output,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("Schedules exported successfully.")
        except Exception as e:
            print(f"An error occurred while exporting schedules: {e}")
            return False

    def list_classes(self, curriculum, school_year):
        """Fetch all classes for a specific curriculum and school year."""
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()
                if st.session_state.role == "Dean":
                    cursor.execute(
                        '''
                        SELECT DISTINCT class_name 
                        FROM schedules 
                        WHERE curriculum = :curriculum AND school_year = :school_year''', 
                        {
                            "curriculum": curriculum,
                            "school_year": school_year
                        }
                    )
                else:
                    cursor.execute("SELECT DISTINCT class_name FROM schedules WHERE curriculum = ? AND school_year = ? AND username = ?", (curriculum, school_year, st.session_state.username))
                return [class_name[0] for class_name in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def delete_class(self, class_name, curriculum, school_year):
        """Delete a class for a specific curriculum and school year."""
        try:
            with sqlite3.connect(schoolAddrDB) as conn:
                cursor = conn.cursor()
                # Check if the user is the Dean or the creator of the class
                cursor.execute("SELECT username FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ?",
                        (class_name, curriculum, school_year))
                result = cursor.fetchone()
                if not result:
                    st.error(f"Class '{class_name}' not found for {curriculum} ({school_year}).")
                    return False

                creator_username = result[0]
                if st.session_state.role != "Dean" and st.session_state.username != creator_username:
                    st.error("You do not have permission to delete this class.")
                    return False

                # Delete the class
                if st.session_state.role == "Dean":
                    cursor.execute("DELETE FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ?",
                        (class_name, curriculum, school_year))
                else:
                    cursor.execute("DELETE FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ? AND username = ?",
                        (class_name, curriculum, school_year, st.session_state.username))
                st.success(f"Class '{class_name}' has been deleted from {curriculum} ({school_year}).")
                return True
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return False

def get_curriculum_school_year_combinations():
    """Fetch all unique curriculum and school year combinations from the database."""
    try:
        with sqlite3.connect(schoolAddrDB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT curriculum, school_year FROM schedules")
            combinations = cursor.fetchall()
            return combinations
    except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return None