import streamlit as st
import pandas as pd
from utils.programTree_db_utils import load_subjects_from_db, get_table_names
from programTree.quick_view import build_interactive_subject_graph, format_subjects_for_legend

if "tabs" not in st.session_state:
    st.session_state.tabs = ["Home", "About"]

# Select a tab
selected_tab = st.tabs(st.session_state.tabs)

# tables = get_table_names()
# if tables:
#     select_table = st.selectbox("Select a curriculum:",tables)
#     subjects = load_subjects_from_db(select_table)

#     if subjects:
#         st.components.v1.html(
#             build_interactive_subject_graph(subjects).generate_html(),
#             height=800
#         )
#         semester_tables = format_subjects_for_legend(subjects)
#         for semester, df in semester_tables.items():
#             st.subheader(f"Subjects and Requirements for {semester}")
#             main,sub = st.columns([3,0.3])
#             Total = pd.DataFrame(df)["Credit Units"].sum(axis=0)
#             Total_sum = pd.DataFrame([{"Total Units":Total}])
#             main.dataframe(
#                 df,
#                 hide_index=True,
#                 use_container_width=True
#             )
#             sub.dataframe(
#                 Total_sum,
#                 hide_index=True,
                
#             )