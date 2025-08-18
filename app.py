import streamlit as st
import time
from utils.db_utils import initialize_db, admin_registeration_check, create_user, check_user, get_departments, get_no_dean_departments

if "role" not in st.session_state:
    st.session_state["role"] = None
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
if "is_page_login" not in st.session_state:
    st.session_state.is_page_login = True

ROLES = [None, "Admin", "Dean", "Subject Chair"]

def admin_registration():
    with st.form("Admin Registration"):
        st.header("Admin Registration")
        st.info("Please register an admin account to initialize the system.")
        admin_username = st.text_input("Username")
        first, second = st.columns(2)
        admin_password = first.text_input("Password", type="password")
        admin_confirm_password = second.text_input("Confirm Password", type="password")
        role = "Admin"
        department = None
        program = None
        color = "#000000"
        if st.form_submit_button("Register"):
            if admin_username and admin_password and admin_confirm_password:
                if admin_password != admin_confirm_password:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Registering..."):
                        reg_result = create_user(admin_username,admin_password,role,department,program,color)
                        if reg_result.get("status"):
                            st.success(reg_result.get("message"))
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(reg_result.get("message"))
            else:
                st.error("Please enter both username and password.")

def login():
    st.set_page_config(layout="centered")
    st.header("Welcome to the School Scheduling System")
    with st.form("Login"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if username and password:
                with st.spinner("Logging in..."):
                    login_result = check_user(username,password)
                    if login_result:
                        st.session_state.update({
                            'is_logged_in': True,
                            'user_id': login_result[0],
                            'username': login_result[1],
                            'role': login_result[2],
                            'color': login_result[3],
                            'department': login_result[4],
                            'program': login_result[5],
                        })
                        st.success("Login successful!")
                        st.session_state['is_logged_in'] = True
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            else:
                st.error("Please enter both username and password.")
        if st.form_submit_button("Register New User"):
            st.session_state['is_page_login'] = False
            st.rerun()

def general_registration():
    st.header("Register")
    username = st.text_input("Username")
    first, second = st.columns(2)
    password = first.text_input("Password", type="password")
    confirm_password = second.text_input("Confirm Password", type="password")
    role = st.selectbox("Select your role",["Dean","Subject Chair"],index=None,placeholder="Select a role")
    third, forth = st.columns(2,vertical_alignment="bottom")
    match role:
        case "Dean":
            department_found = forth.toggle("Not in the List?", value = False)
            if department_found:
                department = third.text_input("Department", value = None, help="e.g. EECE, CEGE, CBMES, etc.")
            else:
                department = third.selectbox(
                    "Department",
                    get_no_dean_departments(),
                    index = None,
                    placeholder = "Select or Enter the your department",
                )
            program = None
        case "Subject Chair":
            department_found = forth.toggle("Not in the List?", value = False)
            if department_found:
                department = third.text_input("Department", value = None, help="e.g. EECE, CEGE, CBMES, etc.")
            else:
                department = third.selectbox(
                    "Department",
                    get_departments(),
                    index = None,
                    placeholder = "Select or Enter the your department",
                )
            program = st.text_input(
                "Program",
                value = None,
                help="e.g. CPE,ECE,EE etc.",
                )
    if role != None:
        color = st.color_picker("Pick a color to represent your account")
    if st.button("Register",disabled=role is None):
        if username and password and confirm_password and department:
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                if department != None:
                    department = department.upper()
                if program != None:
                    program = program.upper()
                with st.spinner("Registering..."):
                    reg_result = create_user(username.strip(),password.strip(),role,department,program,color)
                    if reg_result.get("status"):
                        st.success(reg_result.get("message"))
                        time.sleep(2)
                        st.session_state['is_page_login'] = True
                        st.rerun()
                    else:
                        st.error(reg_result.get("message"))
        else:
            st.error("Please enter all required fields.")
    if st.button("Already have an account? Login"):
        st.session_state['is_page_login'] = True
        st.rerun()

def logout():
    st.session_state.update({
                        'is_logged_in': False,
                        'user_id': None,
                        'username': None,
                        'role': None,
                        'color': None,
                        'department': None,
                        'program': None,
                    })
    st.cache_data.clear()
    st.rerun()

def main():
    role = st.session_state["role"]

    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("settings.py", title="Settings", icon=":material/settings:")


    manage_users = st.Page(
        "admin/manage_users.py", 
        title="Manage Users", 
        icon=":material/people:", 
        default=(role == "Admin"),)
    curriculum_editor= st.Page(
        "programTree/curriculum_editor.py",
        title="Curriculum Editor",
        icon=":material/account_tree:",
    )
    upload_curiculum = st.Page(
        "programTree/curriculum_uploader.py",
        title="Upload Curiculum",
        icon=":material/upload:",
        default=(role == "Dean"or role == "Subject Chair"),
    )

    account_pages = [logout_page, settings]
    admin_pages = [manage_users]
    program_tree_pages = [upload_curiculum,curriculum_editor]
    st.logo("images/Scheduling_Tools.PNG", icon_image="images/scheduler.png",size = "large")
    page_dict = {}
    if st.session_state.role in ["Admin"]:
        page_dict["Admin"] = admin_pages
    if st.session_state.role in ["Dean", "Subject Chair"]:
        page_dict["Curriculum Builder"] = program_tree_pages
    if st.session_state['is_logged_in'] and len(page_dict) > 0 :
        pg = st.navigation({"Account": account_pages} | page_dict)
    else:
        initialize_db()
        if admin_registeration_check():
            pg = st.navigation([st.Page(admin_registration)])
        elif st.session_state['is_page_login']==True:
                pg = st.navigation([st.Page(login,title="Login")])
        else:
            pg = st.navigation([st.Page(general_registration,title="Register")])
    pg.run()
    if st.session_state['is_logged_in']:
        match st.session_state['role']:
            case "Admin":
                st.sidebar.badge(f"[{st.session_state['role']}] {st.session_state['username']} ")
            case "Dean":
                st.sidebar.badge(f"[{st.session_state['department']} {st.session_state['role']}] {st.session_state['username']} ")
            case "Subject Chair":
                st.sidebar.badge(f"[{st.session_state['program']} {st.session_state['role']}] {st.session_state['username']} ")
            case _:
                st.sidebar.badge(f"[{st.session_state['role']}] {st.session_state['username']} ")

if __name__ == "__main__":
    main()