# Login form components
import time
import streamlit as st
from utils.db_utils import create_user, initialize_user_table
from utils.auth_utils import check_login, user_counts

def login():
    initialize_user_table()
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_result = check_login(username, password)
        if login_result:
            st.session_state.update({
                'loggedIn': True,
                'username': username,
                'role': login_result[2],
                'color': login_result[3],
                'delete_mode': False
            })
            st.success("Logged in successfully!")
            time.sleep(1.5)
            st.rerun()
        else:
            st.error("Invalid username or password")
    if st.button("Register New User"):
        st.session_state['pageLogin'] = False
        st.rerun()


def register():
    user_count = user_counts()
    st.title("Register New User")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    color = st.color_picker("Pick a color to represent your account")
    role = "Dean" if user_count == 0 else "Subject Chair"
    if st.button("Register"):
        if username and password and confirm_password and color and role:
            if password == confirm_password:
                reg_result = create_user(username, password, role, color)
                st.success(reg_result.get("message"))
                if reg_result.get("success"):
                    st.session_state['pageLogin'] = True
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("Passwords do not match. Please try again.")
        else:
            st.error("All fields are required.")
    if st.button("Back to Login"):
        st.session_state['pageLogin'] = True
        st.rerun()