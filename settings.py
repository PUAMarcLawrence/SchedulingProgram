import streamlit as st
import time
from utils.login_db_utils import check_old_password, change_password_to_new

def change_password():
    old_password = st.text_input("Old Password", type="password")
    column1, column2 = st.columns(2)
    new_password = column1.text_input("New Password", type="password")
    confirm_password = column2.text_input("Confirm Password", type="password")
    if st.button("Change Password"):
        if old_password and new_password and confirm_password:
            if new_password == confirm_password:
                if check_old_password(st.session_state['username'],old_password):
                    if change_password_to_new(st.session_state['username'],new_password):
                        st.success("Password changed successfully.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Password change failed. Please try again.")
                else:
                    st.error("Old password is incorrect.")
            else:
                st.error("Passwords do not match. Please try again.")
        else:
            st.error("All fields are required.")





option = st.selectbox("Settings", ["Change Password"])
if option == "Change Password":
    change_password()