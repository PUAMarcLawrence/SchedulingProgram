import streamlit as st
from components.login_component import login,register_page

def navigation():
    if "role" not in st.session_state:
        st.session_state.role = None

    


    # if st.session_state.get('logged_in'):
    #     if st.sidebar.button("Logout"):
    #         st.session_state.logged_in = False
    #         st.session_state.username = ""
    #         st.success("Logged out successfully!")
    # st.sidebar.title("Navigation")
    # if st.session_state.get('logged_in'):
    #     page = st.sidebar.selectbox("Select a page", ["Home", "Another Page"])
    #     if page == "Home":
    #         from pages.home import home_page
    #         home_page()
    #     # elif page == "Another Page":
    #     #     from pages.another_page import another_page
    #     #     another_page()
    # else:
    #     option = st.sidebar.selectbox("Choose an action", ["Login", "Register"])
    #     if option == "Login":
    #         st.sidebar.write("Please log in to access other pages.")
    #         login()
    #     elif option == "Register":
    #         register_page()
