import streamlit as st
from utils.db_init import initialize_db

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Admin", "Dean", "Subject CHair"]

def login():
    st.set_page_config(layout="centered")
    st.title("Welcome to the School Scheduling System")
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

def logout():
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")



# ========================== Main Program ===============================
st.logo("images/Scheduling_Tools.PNG", icon_image="images/scheduler.png",size = "large")

account_pages = [logout_page, settings]

page_dict = {}


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
