# import os
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io
from utils.db_utils import schoolAddrDB

# Database setup
def get_db_connection():
    conn = sqlite3.connect(schoolAddrDB)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        color TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS schedules (
        class_name TEXT,
        section TEXT,
        start_time TEXT,
        end_time TEXT,
        days TEXT,
        username TEXT,
        curriculum TEXT,
        school_year TEXT,
        term TEXT)''')
    # If the table already exists, add the curriculum, school_year, and term columns to schedules
    c.execute("PRAGMA table_info(schedules)")
    columns = [column[1] for column in c.fetchall()]
    if 'curriculum' not in columns:
        c.execute("ALTER TABLE schedules ADD COLUMN curriculum TEXT")
    if 'school_year' not in columns:
        c.execute("ALTER TABLE schedules ADD COLUMN school_year TEXT")
    if 'term' not in columns:
        c.execute("ALTER TABLE schedules ADD COLUMN term TEXT")
    conn.commit()
    conn.close()

initialize_db()

class School:
    def __init__(self):
        self.class_duration = timedelta(hours=1, minutes=10) # Adjusted class duration to 1 hour and 10 minutes
        self.time_slots = self.generate_time_slots()
        self.days_options = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "MWF", "TTHS"]
        self.terms_options = ["1st Term", "2nd Term", "3rd Term"]

    def generate_time_slots(self):
        start_time = datetime.strptime("7:00 AM", "%I:%M %p") # Adjusted start time to 7:00 AM
        end_time = datetime.strptime("9:00 PM", "%I:%M %p") # Adjusted end time to 9:00 PM
        slots = []
        while start_time + self.class_duration <= end_time:
            end_slot_time = (start_time + self.class_duration).strftime("%I:%M %p")
            slots.append(f"{start_time.strftime('%I:%M %p')} - {end_slot_time}")
            start_time += self.class_duration
        return slots

    def add_class(self, class_name, section, selected_slots, selected_days, username, curriculum, school_year, term):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            if not class_name.strip():
                st.error("Class name cannot be empty.")
                return False
            class_name = class_name.lower()
            # Check if the class already exists for the same curriculum, school year, and term
            c.execute("SELECT * FROM schedules WHERE class_name = ? AND section = ? AND curriculum = ? AND school_year = ? AND term = ?",
                      (class_name, section, curriculum, school_year, term))
            if c.fetchone():
                st.error(f"Class '{class_name}' with section '{section}' already exists for {curriculum} ({school_year}, {term}).")
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
                    if not self.is_time_slot_available(start_time, end_time, day, curriculum, school_year, term):
                        st.error(f"Time slot {time_slot} on {day} is already booked for {curriculum} ({school_year}, {term}). Please choose a different time.")
                        return False
            for time_slot in selected_slots:
                start_time_str, end_time_str = time_slot.split(" - ")
                start_time = datetime.strptime(start_time_str, "%I:%M %p")
                end_time = datetime.strptime(end_time_str, "%I:%M %p")
                for day in selected_days:
                    c.execute("INSERT INTO schedules (class_name, section, start_time, end_time, days, username, curriculum, school_year, term) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              (class_name, section, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), day, username, curriculum, school_year, term))
            conn.commit()
            st.success(f"Class '{class_name}' (Section: {section}) scheduled successfully for {curriculum} ({school_year}, {term}).")
            return True
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return False
        finally:
            conn.close()

    def is_time_slot_available(self, start_time, end_time, day, curriculum, school_year, term):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM schedules WHERE days = ? AND curriculum = ? AND school_year = ? AND term = ?", (day, curriculum, school_year, term))
        for row in c.fetchall():
            existing_start = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            existing_end = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
            if (start_time < existing_end and end_time > existing_start):
                conn.close()
                return False
        conn.close()
        return True

    def display_schedule(self, curriculum, school_year, term):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT class_name, section, start_time, end_time, days, username FROM schedules WHERE curriculum = ? AND school_year = ? AND term = ?", (curriculum, school_year, term))
        schedules = c.fetchall()
        if not schedules:
            st.info(f"No schedules to display for {curriculum} ({school_year}, {term}).")
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
                c.execute("SELECT color FROM users WHERE username = ?", (username,))
                user_color = c.fetchone()[0]
                display_text = f"<span style='color:{user_color}'>{class_name} <br> {section}</span>"
                df.loc[df["Time"] == time_slot_str, display_day] = display_text
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        conn.close()

    def list_classes(self, curriculum, school_year, term):
        """Fetch all classes for a specific curriculum, school year, and term."""
        conn = get_db_connection()
        c = conn.cursor()
        if st.session_state.role == "Dean":
            c.execute("SELECT DISTINCT class_name FROM schedules WHERE curriculum = ? AND school_year = ? AND term = ?", (curriculum, school_year, term))
        else:
            c.execute("SELECT DISTINCT class_name FROM schedules WHERE curriculum = ? AND school_year = ? AND term = ? AND username = ?", (curriculum, school_year, term, st.session_state.username))
        classes = c.fetchall()
        conn.close()
        return [class_name[0] for class_name in classes]

    def delete_class(self, class_name, curriculum, school_year, term):
        """Delete a class for a specific curriculum, school year, and term."""
        try:
            conn = get_db_connection()
            c = conn.cursor()
            # Check if the user is the Dean or the creator of the class
            c.execute("SELECT username FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ? AND term = ?",
                      (class_name, curriculum, school_year, term))
            result = c.fetchone()
            if not result:
                st.error(f"Class '{class_name}' not found for {curriculum} ({school_year}, {term}).")
                return False
            creator_username = result[0]
            if st.session_state.role != "Dean" and st.session_state.username != creator_username:
                st.error("You do not have permission to delete this class.")
                return False
            # Delete the class
            if st.session_state.role == "Dean":
                c.execute("DELETE FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ? AND term = ?",
                          (class_name, curriculum, school_year, term))
            else:
                c.execute("DELETE FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ? AND term = ? AND username = ?",
                          (class_name, curriculum, school_year, term, st.session_state.username))
            conn.commit()
            st.success(f"Class '{class_name}' has been deleted from {curriculum} ({school_year}, {term}).")
            return True
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return False
        finally:
            conn.close()

    def edit_class(self, old_class_name, old_section, new_class_name, new_section, username, curriculum, school_year, term):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            # Check if the user is the Dean or the creator of the class
            c.execute("SELECT username FROM schedules WHERE class_name = ? AND section = ? AND curriculum = ? AND school_year = ? AND term = ?",
                      (old_class_name, old_section, curriculum, school_year, term))
            result = c.fetchone()
            if not result:
                st.error(f"Class '{old_class_name}' (Section: {old_section}) not found for {curriculum} ({school_year}, {term}).")
                return False
            creator_username = result[0]
            if st.session_state.role != "Dean" and st.session_state.username != creator_username:
                st.error("You do not have permission to edit this class.")
                return False
            # Update the class name and section
            c.execute("UPDATE schedules SET class_name = ?, section = ? WHERE class_name = ? AND section = ? AND curriculum = ? AND school_year = ? AND term = ?",
                      (new_class_name, new_section, old_class_name, old_section, curriculum, school_year, term))
            conn.commit()
            st.success(f"Class '{old_class_name}' (Section: {old_section}) updated to '{new_class_name}' (Section: {new_section}) for {curriculum} ({school_year}, {term}).")
            return True
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return False
        finally:
            conn.close()

    def export_schedule_to_excel(self, curriculum, school_year, term):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT class_name, start_time, end_time, days, username FROM schedules WHERE curriculum = ? AND school_year = ? AND term = ?", (curriculum, school_year, term))
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
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
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
            st.error(f"An error occurred while exporting schedules: {e}")
        finally:
            conn.close()

def get_curriculum_school_year_combinations():
    """Fetch all unique curriculum and school year combinations from the database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT curriculum, school_year FROM schedules")
    combinations = c.fetchall()
    conn.close()
    return combinations

def main_program():
    # if not st.session_state.logged_in:
    #     st.sidebar.header("Login / Register")
    #     menu_option = st.sidebar.selectbox("Choose an option", ["Login", "Register"])
    #     if menu_option == "Login":
    #         login()
    #     elif menu_option == "Register":
    #         register()
    # else:
        school = School()
        st.title("School Scheduling Program")
        st.sidebar.header("Menu")
        menu_option = st.sidebar.selectbox("Choose an option", ["Add Class", "Show Schedule", "Export Schedule to Excel", "Delete Class", "Edit Class"])
        # Fetch all curriculum and school year combinations
        curriculum_school_year_combinations = get_curriculum_school_year_combinations()
        
        # Extract unique curriculum and school year options
        curriculum_options = list(set(row["curriculum"] for row in curriculum_school_year_combinations if row["curriculum"] is not None))
        school_year_options = list(set(row["school_year"] for row in curriculum_school_year_combinations if row["school_year"] is not None))
        
        if menu_option == "Add Class":
            st.header("Add a Class")
            class_name = st.text_input("Class Name", placeholder="Enter the class name (e.g., Mathematics)")
            section = st.text_input("Section", placeholder="Enter the section (e.g., E01)")
            # Input for Curriculum
            curriculum = st.selectbox(
                "Select or Enter Curriculum",
                options=curriculum_options + ["Add New Curriculum"],
                index=0, # Default to the first option
                help="Select an existing curriculum or choose 'Add New Curriculum' to create a new one."
            )
            if curriculum == "Add New Curriculum":
                curriculum = st.text_input("Enter New Curriculum", placeholder="Enter the new curriculum name (e.g., COE)")
            # Input for School Year
            school_year = st.selectbox(
                "Select or Enter Batch",
                options=school_year_options + ["Add New Batch"],
                index=0, # Default to the first option
                help="Select an existing batch or choose 'Add New Batch' to create a new one."
            )
            if school_year == "Add New Batch":
                school_year = st.text_input("Enter New Batch", placeholder="Enter the new batch (e.g., 2025)")
            # Input for Term
            term = st.selectbox(
                "Select Term",
                options=school.terms_options,
                index=0, # Default to the first option
                help="Select the term for the class."
            )
            st.write("Select the desired time slots by clicking on the schedule below:")
            if curriculum and school_year and term:
                school.display_schedule(curriculum, school_year, term)
            selected_slots = st.multiselect("Select Time Slots", school.time_slots)
            selected_days = st.multiselect("Select Days", school.days_options)
            if st.button("Add Class"):
                if not class_name:
                    st.error("Class name cannot be empty.")
                elif not section:
                    st.error("Section cannot be empty.")
                elif not curriculum:
                    st.error("Curriculum cannot be empty.")
                elif not school_year:
                    st.error("Batch cannot be empty.")
                elif not selected_slots:
                    st.error("Please select at least one time slot.")
                elif not selected_days:
                    st.error("Please select at least one day.")
                else:
                    if school.add_class(class_name, section, selected_slots, selected_days, st.session_state.username, curriculum, school_year, term):
                        st.success(f"Class '{class_name}' (Section: {section}) scheduled successfully for {curriculum} ({school_year}, {term}).")
                    else:
                        st.error(f"Failed to schedule class '{class_name}'. Please check the selected time slots and try again.")
        
        elif menu_option == "Show Schedule":
            st.header("Class Schedule")
            if curriculum_options and school_year_options:
                selected_curriculum = st.selectbox(
                    "Select Curriculum",
                    options=curriculum_options,
                    index=0
                )
                selected_school_year = st.selectbox(
                    "Select Batch",
                    options=school_year_options,
                    index=0
                )
                selected_term = st.selectbox(
                    "Select Term",
                    options=school.terms_options,
                    index=0
                )
                school.display_schedule(selected_curriculum, selected_school_year, selected_term)
            else:
                st.warning("No curriculum and Batch combinations found. Please add a class first.")
        
        elif menu_option == "Export Schedule to Excel":
            st.header("Export Schedule to Excel")
            if curriculum_options and school_year_options:
                selected_curriculum = st.selectbox(
                    "Select Curriculum",
                    options=curriculum_options,
                    index=0
                )
                selected_school_year = st.selectbox(
                    "Select Batch",
                    options=school_year_options,
                    index=0
                )
                selected_term = st.selectbox(
                    "Select Term",
                    options=school.terms_options,
                    index=0
                )
                school.export_schedule_to_excel(selected_curriculum, selected_school_year, selected_term)
            else:
                st.warning("No curriculum and batch combinations found. Please add a class first.")
        
        elif menu_option == "Delete Class":
            st.header("Delete a Class")
            if curriculum_options and school_year_options:
                selected_curriculum = st.selectbox(
                    "Select Curriculum",
                    options=curriculum_options,
                    index=0
                )
                selected_school_year = st.selectbox(
                    "Select Batch",
                    options=school_year_options,
                    index=0
                )
                selected_term = st.selectbox(
                    "Select Term",
                    options=school.terms_options,
                    index=0
                )
                if st.button("Start Deleting Classes"):
                    st.session_state.delete_mode = True
                if st.session_state.delete_mode:
                    classes = school.list_classes(selected_curriculum, selected_school_year, selected_term)
                    if classes:
                        delete_class_name = st.selectbox("Select Class to Delete", classes)
                        if st.button("Confirm Delete"):
                            school.delete_class(delete_class_name, selected_curriculum, selected_school_year, selected_term)
                            st.session_state.delete_mode = False
                            st.experimental_set_query_params(refresh=True)
                            st.success(f"Class '{delete_class_name}' has been deleted from {selected_curriculum} ({selected_school_year}, {selected_term}).")
                    else:
                        st.info("No classes available to delete.")
            else:
                st.warning("No curriculum and batch combinations found. Please add a class first.")
        
        elif menu_option == "Edit Class":
            st.header("Edit a Class")
            if curriculum_options and school_year_options:
                selected_curriculum = st.selectbox(
                    "Select Curriculum",
                    options=curriculum_options,
                    index=0
                )
                selected_school_year = st.selectbox(
                    "Select School Year",
                    options=school_year_options,
                    index=0
                )
                selected_term = st.selectbox(
                    "Select Term",
                    options=school.terms_options,
                    index=0
                )

                classes = school.list_classes(selected_curriculum, selected_school_year, selected_term)

                if classes:
                    class_to_edit = st.selectbox("Select Class to Edit", classes)

                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("SELECT class_name, section FROM schedules WHERE class_name = ? AND curriculum = ? AND school_year = ? AND term = ? LIMIT 1",
                              (class_to_edit, selected_curriculum, selected_school_year, selected_term))
                    current_class_details = c.fetchone()
                    conn.close()
                    if current_class_details:
                        current_class_name, current_section = current_class_details
                        
                        new_class_name = st.text_input("New Class Name", value=current_class_name)
                        new_section = st.text_input("New Section", value=current_section)
                        if st.button("Edit Class"):
                            if school.edit_class(current_class_name, current_section, new_class_name, new_section, st.session_state.username, selected_curriculum, selected_school_year, selected_term):
                                st.success(f"Class '{current_class_name}' (Section: {current_section}) updated to '{new_class_name}' (Section: {new_section}) for {selected_curriculum} ({selected_school_year}, {selected_term}).")
                            else:
                                st.error("Failed to edit class. Please check your inputs and permissions.")
                    else:
                        st.error("Failed to fetch class details. Please try again.")
                else:
                    st.info("No classes available to edit.")
            else:
                st.warning("No curriculum and school year combinations found. Please add a class first.")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'delete_mode' not in st.session_state:
    st.session_state.delete_mode= False
if 'username' not in st.session_state:
    st.session_state.username= ""
if 'role' not in st.session_state:
    st.session_state.role= ""
if 'color' not in st.session_state:
    st.session_state.color= ""

main_program()
