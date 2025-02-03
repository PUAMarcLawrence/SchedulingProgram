# Login form components
import time
import streamlit as st
from utils.login_db_utils import create_admin, create_user, check_login, get_departments, get_programs

def AdminRegistration():
    st.title("Admin Registration")
    admin_user = st.text_input("Enter the Admin Username")
    admin_pass = st.text_input("Enter the Admin Password",type="password")
    if st.button("Register"):
        if create_admin(admin_user,admin_pass):
            st.success("Admin account created successfully.")
            time.sleep(2)
            st.rerun()
        else:
            st.error("An Error occured!")

def register():
    st.title("Register New User")
    username = st.text_input("Choose a Username")
    first,second =st.columns(2)
    password = first.text_input("Choose a Password", type="password")
    confirm_password = second.text_input("Confirm Password", type="password")
    role = st.selectbox("Select your role",["Dean","Subject Chair"],index=None,placeholder="Select a role")
    third,fourth = st.columns(2)
    if role == "Dean":
        department = third.text_input("Department",value=None)
        program = None
    else:
        department = third.selectbox(
            "Department",
            get_departments(),
            index=None,
            placeholder="Select a department",
            disabled=role==None)
        program = fourth.selectbox(
            "Program",
            get_programs(department),
            index=None,
            placeholder="Select a program",
            disabled=department==None)
    color = st.color_picker("Pick a color to represent your account")
    if st.button("Register",disabled=role==None or department==None):
        if username and password and confirm_password and role and department and color:
            if role == "Subject Chair" and not program:
                st.error("Program is required for Subject Chair role.")
            if password == confirm_password:
                reg_result = create_user(username, password, department.upper(), role, program, color)
                if reg_result.get("success"):
                    st.session_state['pageLogin'] = True
                    st.success(reg_result.get("message"))
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(reg_result.get("message"))
            else:
                st.error("Passwords do not match. Please try again.")
        else:
            st.error("All fields are required.")
    if st.button("Back to Login"):
        st.session_state['pageLogin'] = True
        st.rerun()

def login():
    st.title("Welcome to the School Scheduling System")
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_result = check_login(username, password)
        if login_result:
            st.session_state.update({
                'loggedIn': True,
                'username': login_result[0],
                'department_ID':login_result[3],
                'role': login_result[2],
                'program_ID': login_result[4],
                'color': login_result[5],
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
