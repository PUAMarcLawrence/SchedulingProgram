import streamlit as st
import pandas as pd
from utils.db_utils import get_department_curriculum_list,get_curriculum_data

st.set_page_config(layout="wide", page_title="Quick View", page_icon=":material/account_tree:")

if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = True
if "edited_data" not in st.session_state:
    st.session_state["edited_data"] = None

curriculum = st.selectbox(
    "Select Curriculum",
    get_department_curriculum_list(st.session_state["department"]),
    index=0,
    help="Select the curriculum you want to view or edit."
)



with st.container(border = True):
    df = pd.DataFrame(get_curriculum_data(st.session_state["program"],st.session_state["department"],curriculum))
    if st.button("Edit Mode"):
        if st.session_state["edit_mode"] == False:
            st.session_state["edit_mode"] = True
        else:
            st.session_state["edit_mode"] = False
    st.session_state["edited_data"] = st.data_editor(
        df,
        column_config={
            "Year": st.column_config.NumberColumn("Year", help="Year of the course"),
            "Term": st.column_config.NumberColumn("Term", help="Term of the course"),
            "Code": st.column_config.TextColumn("Course Code", help="Code of the course"),
            "Title": st.column_config.TextColumn("Course Name", help="Name of the course"),
            "Credit Units": st.column_config.NumberColumn("Credit Units", help="Credits for the course"),
        },
        disabled=st.session_state["edit_mode"],
        use_container_width=True,
        hide_index=True,
    )
