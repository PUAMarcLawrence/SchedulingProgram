import streamlit as st
from dataclasses import dataclass

if "role" not in st.session_state:
    st.session_state["role"] = None
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
if "is_page_login" not in st.session_state:
    st.session_state.is_page_login = True

def logout() -> None:
    st.session_state.update({
                        'is_logged_in': False,
                        'user_id': None,
                        'username': None,
                        'role': None,
                        'color': None,
                        'department': None,
                        'program': None,
                    })
    st.cache_data.clear()
    st.rerun()

def main() -> None:
    role = st.session_state["role"]

    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

    dashboard_page = st.Page("pages/01_dashboard.py", title="Dashboard", icon=":material/dashboard:")
    scheduler_page = st.Page("pages/02_scheduler.py", title="Scheduler", icon=":material/calendar_month:")
    curriculumTree_page = st.Page("pages/03_curriculumTree.py", title="Curriculum Tree", icon=":material/account_tree:")

    account_pages = [logout_page, settings]
    common_pages = [dashboard_page, scheduler_page, curriculumTree_page]
    st.logo("assets/Scheduling_Tools.PNG", icon_image="assets/scheduler.png",size = "large")
    page_dict = {}
    
    page_dict["Pages"] = common_pages
    pg = st.navigation({"Account": account_pages} | page_dict)
    pg.run()
    

if __name__ == "__main__":
    main()