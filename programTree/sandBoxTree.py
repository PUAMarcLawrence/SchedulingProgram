import streamlit as st
from utils.db_utils import create_sandTable,get_table_names,get_sandTable_names

if 'sand_Create' not in st.session_state:
    st.session_state['sand_Create'] = False

if st.button("Create SandBox"):
    if not st.session_state['sand_Create']:
        st.session_state['sand_Create'] = True
    else:
        st.session_state['sand_Create'] = False

if st.session_state['sand_Create']:
    col1,col2 = st.columns(2)
    sandTableName = col1.text_input("Sandbox Name")
    tables = get_table_names()
    selected_temp = col2.selectbox("Choose a curiculum template",tables)
    if st.button("Create"):
        create_sandTable(sandTableName,selected_temp)
else:
    sandTables = get_sandTable_names()
    selected_temp = st.selectbox("Choose an Option",sandTables)
        
