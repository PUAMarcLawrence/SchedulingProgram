import streamlit as st

from utils.scheduling_db_utils import initialize_db, School, get_curriculum_school_year_combinations

def main_program():
    school = School()
    st.title("School Scheduling Program")

    st.sidebar.header("Menu")
    menu_option = st.sidebar.selectbox("Choose an option", ["Add Class", "Show Schedule", "Export Schedule to Excel", "Delete Class", "Edit Class"])

    # Fetch all curriculum and school year combinations
    curriculum_school_year_combinations = get_curriculum_school_year_combinations()
    
    # Filter out None (None) combinations
    curriculum_school_year_options = [
        f"{row['curriculum']} ({row['school_year']})"
        for row in curriculum_school_year_combinations
        if row['curriculum'] is not None and row['school_year'] is not None
    ]

    if menu_option == "Add Class":
        st.header("Add a Class")
        class_name = st.text_input("Class Name")
        section = st.text_input("Section")

        # Add "Add New Curriculum and School Year" to the dropdown list
        add_new_option = "Add New Curriculum and School Year"
        dropdown_options = [add_new_option] + curriculum_school_year_options
        # Dropdown for curriculum and school year
        selected_curriculum_school_year = st.selectbox(
            "Select Curriculum and School Year",
            dropdown_options,
            index=0,  # Set "Add New Curriculum and School Year" as the default option
            disabled = curriculum_school_year_options == []
        )

        if selected_curriculum_school_year == add_new_option:
            curriculum = st.text_input("Enter Curriculum")
            school_year = st.text_input("Enter School Year")
        else:
            curriculum, school_year = selected_curriculum_school_year.split(" (")
            school_year = school_year[:-1]  # Remove the closing parenthesis

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
        if curriculum_school_year_options:
            selected_curriculum_school_year = st.selectbox(
                "Select Curriculum and School Year",
                curriculum_school_year_options
            )
            curriculum, school_year = selected_curriculum_school_year.split(" (")
            school_year = school_year[:-1]  # Remove the closing parenthesis
            school.display_schedule(curriculum, school_year)
        else:
            st.warning("No curriculum and school year combinations found. Please add a class first.")

    elif menu_option == "Export Schedule to Excel":
        st.header("Export Schedule to Excel")
        if curriculum_school_year_options:
            selected_curriculum_school_year = st.selectbox(
                "Select Curriculum and School Year",
                curriculum_school_year_options
            )
            curriculum, school_year = selected_curriculum_school_year.split(" (")
            school_year = school_year[:-1]  # Remove the closing parenthesis
            school.export_schedule_to_excel(curriculum, school_year)
        else:
            st.warning("No curriculum and school year combinations found. Please add a class first.")

    elif menu_option == "Delete Class":
        st.header("Delete a Class")
        if curriculum_school_year_options:
            selected_curriculum_school_year = st.selectbox(
                "Select Curriculum and School Year",
                curriculum_school_year_options
            )
            curriculum, school_year = selected_curriculum_school_year.split(" (")
            school_year = school_year[:-1]  # Remove the closing parenthesis

            if st.button("Start Deleting Classes"):
                st.session_state.delete_mode = True

            if st.session_state.delete_mode:
                classes = school.list_classes(curriculum, school_year)  # Pass curriculum and school year
                if classes:
                    delete_class_name = st.selectbox("Select Class to Delete", classes)
                    if st.button("Confirm Delete"):
                        school.delete_class(delete_class_name, curriculum, school_year)  # Pass curriculum and school year
                        st.session_state.delete_mode = False
                        st.experimental_set_query_params(refresh=True)
                        st.success(f"Class '{delete_class_name}' has been deleted from {curriculum} ({school_year}).")
                else:
                    st.info("No classes available to delete.")
        else:
            st.warning("No curriculum and school year combinations found. Please add a class first.")

    elif menu_option == "Edit Class":
        st.header("Edit a Class")
        if curriculum_school_year_options:
            selected_curriculum_school_year = st.selectbox(
                "Select Curriculum and School Year",
                curriculum_school_year_options
            )
            curriculum, school_year = selected_curriculum_school_year.split(" (")
            school_year = school_year[:-1]  # Remove the closing parenthesis

            classes = school.list_classes(curriculum, school_year)
            if classes:
                class_to_edit = st.selectbox("Select Class to Edit", classes)
                section_to_edit = st.text_input("Enter Section to Edit")
                new_class_name = st.text_input("New Class Name")
                new_section = st.text_input("New Section")

                if st.button("Edit Class"):
                    if school.edit_class(class_to_edit, section_to_edit, new_class_name, new_section, st.session_state.username, curriculum, school_year):
                        st.success(f"Class '{class_to_edit}' (Section: {section_to_edit}) updated to '{new_class_name}' (Section: {new_section}) for {curriculum} ({school_year}).")
                    else:
                        st.error("Failed to edit class. Please check your inputs and permissions.")
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
