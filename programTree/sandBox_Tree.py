import streamlit as st

st.set_page_config(layout="wide")

First, Second = st.columns(2)
with First.popover("New Sandbox"):
    option = st.selectbox("Sandbox Options", ("Open Existing Sandbox", "Create New Sandbox"))