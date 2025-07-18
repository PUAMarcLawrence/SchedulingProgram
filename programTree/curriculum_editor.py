import streamlit as st
import pandas as pd
from pyvis.network import Network
from utils.db_utils import get_department_curriculum_list,get_curriculum_data

def build_interactive_subject_graph(data):
    net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white")
    
    
    return net

st.set_page_config(layout="wide", page_icon=":material/account_tree:")

if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = True

curriculum = st.selectbox(
    "Select Curriculum",
    get_department_curriculum_list(st.session_state["department"]),
    index=0,
    help="Select the curriculum you want to view or edit."
)

container = st.container(border = True)

df = pd.DataFrame(get_curriculum_data(st.session_state["program"],st.session_state["department"],curriculum))
if st.button("Edit Mode"):
    if st.session_state["edit_mode"] == False:
        st.session_state["edit_mode"] = True
    else:
        st.session_state["edit_mode"] = False
edited_data = st.data_editor(
    df,
    column_config={
        "Year": st.column_config.NumberColumn("Year", help="Year of the course"),
        "Term": st.column_config.NumberColumn("Term", help="Term of the course"),
        "R.Y.S.": st.column_config.NumberColumn("R.Y.S.", help="Required Year Standing."),
        "Code": st.column_config.TextColumn("Code", help="Code of the course"),
        "Title": st.column_config.TextColumn("Course Name", help="Name of the course"),
        "Lec Hrs": st.column_config.NumberColumn("Lec Hrs", help="Lecture Hours"),
        "Lab Hrs": st.column_config.NumberColumn("Lab Hrs", help="Laboratory Hours"),
        "Credit Units": st.column_config.NumberColumn("Units", help="Credits for the course"),
        "Pre_requisites": st.column_config.ListColumn("Pre-requisites", help="Pre-requisites for the course",width="medium"),
        "Co_requisites": st.column_config.ListColumn("Co-requisites", help="Co-requisites for the course",width="medium"),
    },
    disabled=st.session_state["edit_mode"],
    use_container_width=True,
    hide_index=True,
    )
with container:
    st.components.v1.html(build_interactive_subject_graph(edited_data).generate_html())