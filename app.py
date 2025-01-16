import streamlit as st
from components.login_component import login, register

# initializing session states
if "role" not in st.session_state:
    st.session_state['role'] = None
if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False

# Roles declaration
ROLES = [None, "Subject Chair", "Dean"]

# Logout Functions
def logout():
    st.session_state['loggedIn'] = False
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

# ============================ Account Pages ===========================
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

# =========================== ProgramTree Pages ========================
quickView = st.Page("programTree/quickView.py", title="Quick View", icon=":material/account_tree:", 
    default=(role == "Subject Chair" or role == "Dean"),)
# sandbox_programTree = st.Page("programTree/sandBoxTree.py", title="SandBox", icon=":material/handyman:")

# Page Dictionary
account_pages = [logout_page, settings]
programTree_pages = [quickView]

# Logo on the Side Bar
st.logo("images/Scheduling Tools.PNG", icon_image="images/scheduler.png",size = "large")

page_dict = {}
# Taging pages to thier ROLE restrictions
if st.session_state.role in ["Subject Chair","Dean"]:
    page_dict["Program Tree"] = programTree_pages

#========================== Main Program ======================================
if st.session_state['loggedIn'] and len(page_dict) > 0 :
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