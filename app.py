import streamlit as st
from components.login_component import login, register

# initializing session states
if "role" not in st.session_state:
    st.session_state['role'] = None
if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False
if 'pageLogin' not in st.session_state:
    st.session_state['pageLogin'] = True

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
    "admin/manage_users.py", 
    title="Manage Users", 
    icon=":material/people:", 
    default=(role == "Admin"),)

manage_departments = st.Page(
    "admin/manage_departments.py", 
    title="Manage Departments", 
    icon=":material/corporate_fare:",)

# ============================ Scheduling Pages ========================
school_scheduling = st.Page(
    "scheduling/school_scheduling.py",
    title="School Scheduling",
    icon=":material/computer:",
    default=(role == "Subject Chair" or role == "Dean" or role == "Admin"),)

# ============================ Page Dictionary ==========================
account_pages = [logout_page, settings]
admin_pages = [manage_users, manage_departments]
scheduling_pages = [school_scheduling]

#========================== Main Program ======================================
# Logo on the Side Bar
st.logo("images/Scheduling Tools.PNG", icon_image="images/scheduler.png",size = "large")

page_dict = {}
# # Taging pages to thier ROLE restrictions
if st.session_state.role in ["Admin"]:
    page_dict["Admin"] = admin_pages
if st.session_state.role in ["Subject Chair","Dean"]:
    page_dict["Scheduling"] = scheduling_pages
# if st.session_state.role in ["Subject Chair","Dean"]:
#     page_dict["Program Tree"] = programTree_pages

if st.session_state['loggedIn'] and len(page_dict) > 0 :
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    st.title("Welcome to the School Scheduling Program")
    if st.session_state['pageLogin']==True:
        pg = st.navigation([st.Page(login)])
    else:
        pg = st.navigation([st.Page(register)])

pg.run()