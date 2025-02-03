import streamlit as st

from utils.programTree_db_utils import get_table_names

tables = get_table_names()
if tables:
    select_table = st.selectbox("Select a curriculum:",tables)
else:
    st.error("No Curriculum found in the database")

