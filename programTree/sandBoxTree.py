import streamlit as st

if "curiculum_temp" not in st.session_state:
    st.session_state['curiculum_temp'] = None

if st.session_state['curiculum_temp'] == None:
    
    sandName = st.text_input("Enter a SandBox Name")