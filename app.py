import streamlit as st
from components.login_component import login, register
from utils.db_utils import create_user_table

create_user_table()
st.set_page_config(layout="wide")

if "role" not in st.session_state:
    st.session_state['role'] = None

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

ROLES = [None, "Requester", "Responder", "Admin"]

def logout():
    st.session_state['logged_in'] = False
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

school_scheduling = st.Page(
    "scheduling/school_scheduling.py",
    title="School Scheduling",
    icon=":material/computer:",
    default=(role == "Program Chair" or role == "Dean"),
)

quickView = st.Page(
    "programTree/quickView.py",
    title="Quick View",
    icon=":material/account_tree:",
)

upload_curiculum = st.Page(
    "programTree/uploadFile.py",
    title="Upload Curiculum",
    icon=":material/upload:"
)

account_pages = [logout_page, settings]
scheduling_pages = [school_scheduling]
programTree_pages = [quickView,upload_curiculum]

st.logo("images/Scheduling Tools.PNG", icon_image="images/scheduler.png",size = "large")

page_dict = {}
if st.session_state.role in ["Program Chair","Dean"]:
    page_dict["Scheduling"] = scheduling_pages
if st.session_state.role in ["Program Chair","Dean"]:
    page_dict["Program Tree"] = programTree_pages

if st.session_state['logged_in']: # or len(page_dict) > 0 :
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    option = st.selectbox("Choose an Option",["Login","Register"])
    match option:
        case "Login":
            pg = st.navigation([st.Page(login)])
        case "Register":
            pg = st.navigation([st.Page(register)])

pg.run()

# import streamlit as st
# import streamlit.components.v1 as components
# import hashlib
# import time

# # Function to handle login
# def login(username, password):
#     # Dummy credentials
#     if username == "admin" and password == "password":
#         # Set a secure hash as a token for demonstration purposes
#         token = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()
#         st.session_state['token'] = token
#         # Set a cookie for login persistence
#         components.html(f"<script>document.cookie = 'token={token};path=/'</script>")
#         return True
#     return False

# # Check if there's a saved token in cookies
# def check_token():
#     token = st.session_state.get('token', None)
#     if token:
#         # Use your backend to verify if the token is valid here
#         return True
#     return False

# # Logout function
# def logout():
#     st.session_state['token'] = None
#     # Clear the cookie
#     components.html("<script>document.cookie = 'token=; Max-Age=0; path=/'</script>")
#     st.rerun()

# # Display the login form
# def show_login():
#     st.title("Login Page")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     login_button = st.button("Login")

#     if login_button:
#         if login(username, password):
#             st.success("Login successful!")
#             st.rerun()
#         else:
#             st.error("Invalid username or password")

# # Main app
# def show_main_app():
#     st.title("Main Application")
#     st.write("Welcome to the main application page.")
#     if st.button("Logout"):
#         logout()

# # Application logic
# if check_token():
#     show_main_app()
# else:
#     show_login()
