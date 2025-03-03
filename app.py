import streamlit as st
from components.login_component import login, register, AdminRegistration
from utils.login_db_utils import check_anyUser
from utils.db_utils import initialize_db

# initializing session states
if "role" not in st.session_state:
    st.session_state['role'] = None
if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False
if 'pageLogin' not in st.session_state:
    st.session_state['pageLogin'] = True
if 'delete_mode' not in st.session_state:
    st.session_state['delete_mode'] = False

# Roles declaration
ROLES = [None,"Admin", "Subject Chair", "Dean"]

# Logout Functions
def logout():
    st.session_state['loggedIn'] = False
    st.session_state.role = None
    st.rerun()

role = st.session_state.role
# ============================ Account Pages ===========================
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

#============================ Admin Pages ==============================
manage_users = st.Page(
    "admin/manage_database.py", 
    title="Manage Database", 
    icon=":material/people:", 
    default=(role == "Admin"),)

# ============================ Dean Pages ==============================
subject_chair_management = st.Page(
    "dean/subject_chair_management.py",
    title="Subject Chair Management",
    icon=":material/people:",)
    # default=(role == "Dean"),)

# ============================ Program Tree Pages =======================
quickView = st.Page(
    "programTree/quick_view.py", 
    title="Quick View", 
    icon=":material/account_tree:",)
    # default=(role == "Subject Chair" or role == "Dean"),)

sandbox_programTree = st.Page(
    "programTree/sandBox_Tree.py", 
    title="SandBox", 
    icon=":material/handyman:")

upload_curiculum = st.Page(
    "programTree/upload_file.py",
    title="Upload Curiculum",
    icon=":material/upload:")

# ============================ Scheduling Pages ========================
school_scheduling = st.Page(
    "scheduling/school_scheduling.py",
    title="School Scheduling",
    icon=":material/computer:",
    default=(role == "Subject Chair" or role == "Dean"),)

# scheduling_subjects = st.Page(
#     "scheduling/scheduling_subjects.py",
#     title="School Sched",
#     icon=":material/computer:",
# )


# ============================ Page Dictionary ==========================
account_pages = [logout_page, settings]
dean_pages = [subject_chair_management]
admin_pages = [manage_users]
programTree_pages = [upload_curiculum, quickView, sandbox_programTree]
scheduling_pages = [school_scheduling,] # scheduling_subjects]


# ========================== Main Program ===============================
st.logo("images/Scheduling_Tools.PNG", icon_image="images/scheduler.png",size = "large")

page_dict = {}
if st.session_state.role in ["Admin"]:
    page_dict["Admin"] = admin_pages
if st.session_state.role in ["Dean"]:
    page_dict["Subject Chair"] = dean_pages
if st.session_state.role in ["Subject Chair","Dean"]:
    page_dict["Program Tree"] = programTree_pages
if st.session_state.role in ["Subject Chair","Dean"]:
    page_dict["Scheduling"] = scheduling_pages


if st.session_state['loggedIn'] and len(page_dict) > 0 :
    pg = st.navigation( {"Account": account_pages} | page_dict)
else:
    initialize_db()
    if check_anyUser():
        pg = st.navigation([st.Page(AdminRegistration)])
    else:
        if st.session_state['pageLogin']==True:
            pg = st.navigation([st.Page(login)])
        else:
            pg = st.navigation([st.Page(register)])
pg.run()
