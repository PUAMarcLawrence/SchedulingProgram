import streamlit as st
import webbrowser

def help(label: str, url: str):

    try:
        st.link_button(label, url)
    except AttributeError:
        if st.button(label):
            webbrowser.open_new_tab(url)

help("Go to google", "https://www.google.com")asdasd