import streamlit as st
from utils.programTree_db_utils import get_table_names
from utils.db_utils import get_department_programs

st.set_page_config(layout="wide")

if st.session_state['role'] == 'Dean':
    program = st.selectbox("Select a program:",get_department_programs(st.session_state['department_ID']))
tables = get_table_names(st.session_state['department_ID'],program)
if tables:
    select_table = st.selectbox('Select a curriculum:',tables)
else:
    st.warning(f"No curriculum found in the database.")
    select_table = None