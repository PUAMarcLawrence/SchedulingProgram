import streamlit as st
from components.login_component import login, register
from utils.db_utils import create_user_table

create_user_table()
st.set_page_config(layout="wide")

#initializing session states
if "role" not in st.session_state:
    st.session_state['role'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ROLES
ROLES = [None, "Subject Chair", "Dean"]

# Logout Functions
def logout():
    st.session_state['logged_in'] = False
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

# Options in the Side Bar to the Pages
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

school_scheduling = st.Page(
    "scheduling/school_scheduling.py",
    title="School Scheduling",
    icon=":material/computer:",
    default=(role == "Subject Chair" or role == "Dean"),
)

quickView = st.Page(
    "programTree/quickView.py",
    title="Quick View",
    icon=":material/account_tree:",
)

upload_curiculum = st.Page(
    "programTree/uploadFile.py",
    title="Upload Curiculum",
    icon=":material/upload:"
)

sandbox_programTree = st.Page(
    "programTree/sandBoxTree.py",
    title="SandBox",
    icon=":material/handyman:"
)

settings_programTree = st.Page(
    "programTree/programTreeSettings.py",
    title="Settings",
    icon=":material/settings:"
)

# Page Dictionary
account_pages = [logout_page, settings]
scheduling_pages = [school_scheduling]
programTree_pages = [quickView,upload_curiculum,sandbox_programTree,settings_programTree]

# Logo on the Side Bar
st.logo("images/Scheduling Tools.PNG", icon_image="images/scheduler.png",size = "large")

page_dict = {}
# Taging pages to thier ROLE restrictions
if st.session_state.role in ["Subject Chair","Dean"]:
    page_dict["Scheduling"] = scheduling_pages
if st.session_state.role in ["Subject Chair","Dean"]:
    page_dict["Program Tree"] = programTree_pages

#main body of Display
if st.session_state['logged_in'] and len(page_dict) > 0 :
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    st.title("Welcome to the School Scheduling Program")
    option = st.selectbox("Choose an Option",["Login","Register"])
    match option:
        case "Login":
            pg = st.navigation([st.Page(login)])
        case "Register":
            pg = st.navigation([st.Page(register)])

pg.run()
