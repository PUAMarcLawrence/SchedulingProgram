import streamlit as st
from utils.db_utils import initialize_db, admin_registered

if "role" not in st.session_state:
    st.session_state.role = None
if "loggedIn" not in st.session_state:
    st.session_state.loggedIn = False
if "pageLogin" not in st.session_state:
    st.session_state.pageLogin = True

ROLES = [None, "Admin", "Dean", "Subject CHair"]

def AdminRegistration():
    st.set_page_config(layout="centered")
    st.title("Admin Registration")
    st.warning("Please register as an admin to use the system.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password == confirm_password:
            # Here you would typically save the username and password to a database
            st.success("Admin registered successfully!")
        else:
            st.error("Passwords do not match.")

def register():
    st.set_page_config(layout="centered")
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password == confirm_password:
            # Here you would typically save the username and password to a database
            st.success("User registered successfully!")
        else:
            st.error("Passwords do not match.")

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
    if admin_registered():
        pg = st.navigation([st.Page(AdminRegistration)])
        pg.run()
    else:
        st.title("Welcome to the School Scheduling System")
    #     if st.session_state['pageLogin']==True:
    #         pg = st.navigation([st.Page(login)])
    #     else:
    #         pg = st.navigation([st.Page(register)])
# pg.run()
