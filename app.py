import streamlit as st
from components.login_component import login,register
from utils.db_utils import create_user_table

st.set_page_config(layout="wide")
if "role" not in st.session_state:
    st.session_state.role = None

create_user_table()

ROLES = [None, "Program Chair", "Dean"]

def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

tool_1 = st.Page(
    "tools/school_scheduling.py",
    title="School Scheduling",
    icon=":material/computer:",
    default=(role == "Program Chair" or role == "Dean"),
)

tool_2 = st.Page(
    "tools/programTree.py",
    title="Program Tree",
    icon=":material/account_tree:",
)

account_pages = [logout_page, settings]
tool_pages = [tool_1, tool_2]


st.logo("images/Scheduling Tools.PNG", icon_image="images/scheduler.png")

page_dict = {}
# if st.session_state.role in ["Requester", "Admin"]:
#     page_dict["Request"] = request_pages
if st.session_state.role in ["Program Chair", "Dean"]:
    page_dict["Tools"] = tool_pages
# if st.session_state.role == "Dean":
#     page_dict["Dean"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
    pg.run()
else:
    st.title("Welcome to the School Scheduling Program")
    option = st.selectbox("Choose an option", ["Login", "Register"])

    if option == "Login":
        login()
    elif option == "Register":
        register()



# import yaml
# import streamlit as st
# from yaml.loader import SafeLoader
# import streamlit_authenticator as stauth
# from streamlit_authenticator.utilities import CredentialsError,ForgotError,Hasher,LoginError,RegisterError,ResetError,UpdateError

# # Loading config file
# with open('./config.yaml', 'r', encoding='utf-8') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# #Creating the authenticator object
# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days']
# )

# # Creating a login widget
# try:
#     authenticator.login()
# except LoginError as e:
#     st.error(e)

# # Creating a guest login button
# try:
#     authenticator.experimental_guest_login('Login with Google', provider='google',
#                                             oauth2=config['oauth2'])
#     authenticator.experimental_guest_login('Login with Microsoft', provider='microsoft',
#                                             oauth2=config['oauth2'])
# except LoginError as e:
#     st.error(e)

# # Authenticating user
# if st.session_state['authentication_status']:
#     authenticator.logout()
#     st.write(f'Welcome *{st.session_state["name"]}*')
#     st.title('Some content')
# elif st.session_state['authentication_status'] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state['authentication_status'] is None:
#     st.warning('Please enter your username and password')

# # Creating a password reset widget
# if st.session_state['authentication_status']:
#     try:
#         if authenticator.reset_password(st.session_state['username']):
#             st.success('Password modified successfully')
#     except (CredentialsError, ResetError) as e:
#         st.error(e)

# # Creating a new user registration widget
# try:
#     (email_of_registered_user,
#         username_of_registered_user,
#         name_of_registered_user) = authenticator.register_user()
#     if email_of_registered_user:
#         st.success('User registered successfully')
# except RegisterError as e:
#     st.error(e)

# # Creating a forgot password widget
# try:
#     (username_of_forgotten_password,
#         email_of_forgotten_password,
#         new_random_password) = authenticator.forgot_password()
#     if username_of_forgotten_password:
#         st.success('New password sent securely')
#         # Random password to be transferred to the user securely
#     elif not username_of_forgotten_password:
#         st.error('Username not found')
# except ForgotError as e:
#     st.error(e)

# # Creating a forgot username widget
# try:
#     (username_of_forgotten_username,
#         email_of_forgotten_username) = authenticator.forgot_username()
#     if username_of_forgotten_username:
#         st.success('Username sent securely')
#         # Username to be transferred to the user securely
#     elif not username_of_forgotten_username:
#         st.error('Email not found')
# except ForgotError as e:
#     st.error(e)

# # Creating an update user details widget
# if st.session_state['authentication_status']:
#     try:
#         if authenticator.update_user_details(st.session_state['username']):
#             st.success('Entry updated successfully')
#     except UpdateError as e:
#         st.error(e)

# # Saving config file
# with open('../config.yaml', 'w', encoding='utf-8') as file:
#     yaml.dump(config, file, default_flow_style=False)