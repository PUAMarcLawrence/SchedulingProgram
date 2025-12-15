import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = ["Admin", "Dean", "Professor"]

def login():
    st.title("Login")
    role = st.selectbox("Select your role", ROLES)
    if st.button("Login"):
        st.session_state.role = role
        st.rerun()

def logout():
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
dashboard_page = st.Page("pages/01_dashboard.py", title="Dashboard", icon=":material/dashboard:", default=(role=="Admin"))



account_pages = [logout_page, settings, dashboard_page]



st.title("Request manager")
st.logo("assets/Scheduling_Tools.PNG", icon_image="assets/scheduler.png")

page_dict = {}
if st.session_state.role in ["Admin", "Dean", "Professor"]:
    page_dict["Account"] = account_pages
# if st.session_state.role in ["Responder", "Admin"]:
#     page_dict["Respond"] = respond_pages
# if st.session_state.role == "Admin":
#     page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()