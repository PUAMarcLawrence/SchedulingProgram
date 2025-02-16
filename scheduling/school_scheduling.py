
import streamlit as st
from utils.scheduling_db_utils import initialize_db, School, get_curriculum_school_year_combinations, fetch_current_class_details

def main_program():
    school = School()
    st.title("School Scheduling Program")

    st.sidebar.header("Menu")
    menu_option = st.sidebar.selectbox("Choose an option", ["Add Class", "Show Schedule", "Export Schedule to Excel", "Delete Class", "Edit Class"])

    # Fetch all curriculum and school year combinations
    curriculum_school_year_combinations = get_curriculum_school_year_combinations()
    
    # Extract unique curriculum and school year options
    curriculum_options = list(set(row['curriculum'] for row in curriculum_school_year_combinations if row['curriculum'] is not None))
    school_year_options = list(set(row['school_year'] for row in curriculum_school_year_combinations if row['school_year'] is not None))

    if menu_option == "Add Class":
        st.header("Add a Class")
        class_name = st.text_input("Class Name", placeholder="Enter the class name (e.g., Mathematics)")
        section = st.text_input("Section", placeholder="Enter the section (e.g., E01)")

        # Input for Curriculum
        curriculum = st.selectbox(
            "Select or Enter Curriculum",
            options=curriculum_options + ["Add New Curriculum"],
            index=0,  # Default to the first option
            help="Select an existing curriculum or choose 'Add New Curriculum' to create a new one."
        )
        if curriculum == "Add New Curriculum":
            curriculum = st.text_input("Enter New Curriculum", placeholder="Enter the new curriculum name (e.g., COE)")

        # Input for School Year
        school_year = st.selectbox(
            "Select or Enter School Year",
            options=school_year_options + ["Add New School Year"],
            index=0,  # Default to the first option
            help="Select an existing school year or choose 'Add New School Year' to create a new one."
        )
        if school_year == "Add New School Year":
            school_year = st.text_input("Enter New School Year", placeholder="Enter the new school year (e.g., 2025)")

        st.write("Select the desired time slots by clicking on the schedule below:")
        if curriculum and school_year:
            school.display_schedule(curriculum, school_year)
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
                st.error("School year cannot be empty.")
            elif not selected_slots:
                st.error("Please select at least one time slot.")
            elif not selected_days:
                st.error("Please select at least one day.")
            else:
                if school.add_class(class_name, section, selected_slots, selected_days, st.session_state.username, curriculum, school_year):
                    st.success(f"Class '{class_name}' (Section: {section}) scheduled successfully for {curriculum} ({school_year}).")
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
                "Select School Year",
                options=school_year_options,
                index=0
            )
            school.display_schedule(selected_curriculum, selected_school_year)
        else:
            st.warning("No curriculum and school year combinations found. Please add a class first.")

    elif menu_option == "Export Schedule to Excel":
        st.header("Export Schedule to Excel")
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
            school.export_schedule_to_excel(selected_curriculum, selected_school_year)
        else:
            st.warning("No curriculum and school year combinations found. Please add a class first.")

    elif menu_option == "Delete Class":
        st.header("Delete a Class")
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

            if st.button("Start Deleting Classes"):
                st.session_state.delete_mode = True

            if st.session_state.delete_mode:
                classes = school.list_classes(selected_curriculum, selected_school_year)
                if classes:
                    delete_class_name = st.selectbox("Select Class to Delete", classes)
                    if st.button("Confirm Delete"):
                        school.delete_class(delete_class_name, selected_curriculum, selected_school_year)
                        st.session_state.delete_mode = False
                        st.experimental_set_query_params(refresh=True)
                        st.success(f"Class '{delete_class_name}' has been deleted from {selected_curriculum} ({selected_school_year}).")
                else:
                    st.info("No classes available to delete.")
        else:
            st.warning("No curriculum and school year combinations found. Please add a class first.")

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

            classes = school.list_classes(selected_curriculum, selected_school_year)
            if classes:
                class_to_edit = st.selectbox("Select Class to Edit", classes)
                current_class_details = fetch_current_class_details(class_to_edit, selected_curriculum, selected_school_year)
                if current_class_details:
                    current_class_name, current_section = current_class_details

                    # Pre-fill the current class details
                    new_class_name = st.text_input("New Class Name", value=current_class_name)
                    new_section = st.text_input("New Section", value=current_section)

                    if st.button("Edit Class"):
                        if school.edit_class(current_class_name, current_section, new_class_name, new_section, st.session_state.username, selected_curriculum, selected_school_year):
                            st.success(f"Class '{current_class_name}' (Section: {current_section}) updated to '{new_class_name}' (Section: {new_section}) for {selected_curriculum} ({selected_school_year}).")
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
    st.session_state.delete_mode = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'color' not in st.session_state:
    st.session_state.color = ""

initialize_db()
main_program()
