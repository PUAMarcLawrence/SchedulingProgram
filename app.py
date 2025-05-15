import streamlit as st
import time
from utils.db_utils import initialize_db, admin_registeration_check,create_user,get_departments,check_user

if "role" not in st.session_state:
    st.session_state.role = None
if "loggedIn" not in st.session_state:
    st.session_state.loggedIn = False
if "pageLogin" not in st.session_state:
    st.session_state.pageLogin = True

ROLES = [None, "Admin", "Dean", "Subject Chair"]

def admin_registration():
    st.title("Admin Registration")
    st.info("Please register an admin account to initialize the system.")
    username = st.text_input("Username")
    first, second = st.columns(2)
    password = first.text_input("Password", type="password")
    confirm_password = second.text_input("Confirm Password", type="password")
    role = "Admin"
    department = None
    program = None
    color = "#000000"
    if st.button("Register"):
        if username and password and confirm_password:
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                reg_result = create_user(username,password,role,department,program,color)
                if reg_result.get("status"):
                    st.success(reg_result.get("message"))
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(reg_result.get("message"))
        else:
            st.error("Please enter both username and password.")

def login():
    st.title("Welcome to the School Scheduling System")
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        with st.spinner("Logging in..."):
            if username and password:
                login_result = check_user(username,password)
                if login_result:
                    st.session_state.update({
                        'loggedIn': True,
                        'user_id': login_result[0],
                        'username': login_result[1],
                        'role': login_result[2],
                        'color': login_result[3],
                        'department': login_result[4],
                        'program': login_result[5],
                    })
                    st.success("Login successful!")
                    st.session_state['loggedIn'] = True
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter both username and password.")
    if st.button("Register New User"):
        st.session_state['pageLogin'] = False
        st.rerun()

def general_registration():
    st.header("Register")
    username = st.text_input("Username")
    first, second = st.columns(2)
    password = first.text_input("Password", type="password")
    confirm_password = second.text_input("Confirm Password", type="password")
    role = st.selectbox("Select your role",["Dean","Subject Chair"],index=None,placeholder="Select a role")
    third, forth = st.columns(2,vertical_alignment="bottom")
    if role == "Dean":
        department = third.text_input("Department", value = None, help="e.g. EECE, CEGE, CBMES, etc.")
        program = None
    elif role == "Subject Chair":
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
                reg_result = create_user(username,password,role,department,program,color)
                if reg_result.get("status"):
                    st.success(reg_result.get("message"))
                    time.sleep(2)
                    st.session_state['pageLogin'] = True
                    st.rerun()
                else:
                    st.error(reg_result.get("message"))
        else:
            st.error("Please enter all required fields.")
    if st.button("Already have an account? Login"):
        st.session_state['pageLogin'] = True
        st.rerun()

def logout():
    st.session_state.update({
                        'loggedIn': False,
                        'user_id': None,
                        'username': None,
                        'role': None,
                        'color': None,
                        'department': None,
                        'program': None,
                    })
    st.rerun()

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

manage_users = st.Page(
    "admin/manage_users.py", 
    title="Manage Users", 
    icon=":material/people:", 
    default=(role == "Admin"),)

quick_view = st.Page(
    "programTree/quick_view.py",
    title="Program Tree",
    icon=":material/account_tree:",
    default=(role == "Dean"or role == "Subject Chair"),
)

account_pages = [logout_page, settings]
admin_pages = [manage_users]
program_tree_pages = [quick_view]
# ========================== Main Program ===============================
st.logo("images/Scheduling_Tools.PNG", icon_image="images/scheduler.png",size = "large")

page_dict = {}
if st.session_state.role in ["Admin"]:
    page_dict["Admin"] = admin_pages
if st.session_state.role in ["Dean", "Subject Chair"]:
    page_dict["Curriculum Builder"] = program_tree_pages

if st.session_state['loggedIn'] and len(page_dict) > 0 :
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    initialize_db()
    if admin_registeration_check():
        pg = st.navigation([st.Page(admin_registration)])
    else:
        if st.session_state['pageLogin']==True:
            pg = st.navigation([st.Page(login,title="Login")])
        else:
            pg = st.navigation([st.Page(general_registration,title="Register")])
pg.run()
st.sidebar.text(f"[{st.session_state['role']}] {st.session_state['username']} ")
