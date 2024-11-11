# Login form components
import time
import streamlit as st
from utils.db_utils import create_user
from utils.auth_utils import check_login, hash_password, user_counts

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state['logged_in'] = True
            st.session_state.username = username
            st.session_state.role = check_login(username,password)[2]  # Store the role in session state
            st.session_state.color = check_login(username,password)[3] # Store the role color
            st.session_state.delete_mode = False
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")
        time.sleep(1)
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
                if create_user(username, password, role, color):
                    st.success(f"{role} Registration successful! You can now log in.")
                else:
                    st.error("Username already exists. Please choose a different one.")
            else:
                st.error("Passwords do not match. Please try again.")
        else:
            st.error("All fields are required.")
        time.sleep(1)
        st.rerun()