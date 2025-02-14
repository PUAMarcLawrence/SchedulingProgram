import streamlit as st
import pandas as pd
from pyvis.network import Network
from utils.programTree_db_utils import get_table_names,load_subjects_from_db
from utils.db_utils import get_department_programs,get_program
from utils.graph_utils import build_interactive_subject_graph

st.set_page_config(layout="wide")

def format_subjects_for_legend(subjects):
    semester_tables = {}
    for semester, semester_subjects in subjects.items():
        legend_data = []
        for subject, details in semester_subjects.items():
            title = details['title']
            prerequisites = ', '.join(details['prerequisites']) if details['prerequisites'] else "None"
            corequisites = ', '.join(details['corequisites']) if details['corequisites'] else "None"
            credit_unit = details['credit_unit']
            legend_data.append([subject, title, prerequisites, corequisites,credit_unit])

        # Create a DataFrame for the semester
        df = pd.DataFrame(
            legend_data, 
            columns=["Subject Code", "Title", "Pre-requisites", "Co-requisites","Credit Units"]
        )
        semester_tables[semester] = df  # Store DataFrame in a dictionary with semester as the key
    return semester_tables

if st.session_state['role'] == "Dean":
    program = st.selectbox(
        "Select Program to view:",
        get_department_programs(st.session_state['department_ID'])
    )
else:
    program = st.session_state['program_ID']
    program = get_program(program)

tables = get_table_names(st.session_state['department_ID'],program)
if tables:
    select_table = st.selectbox('Select a curriculum:',tables)
    subjects = load_subjects_from_db(st.session_state['department_ID'],program,select_table)
    if subjects:
        st.components.v1.html(
            build_interactive_subject_graph(subjects).generate_html(),
            height=800
        )
        with st.popover("Show Legend",use_container_width=True):
            st.markdown(
                """
                ### Legend
                - ─── **Solid Line**: Pre-Requisite
                - \- - - **Broken Line**: Co-Requisite
                - ⭐ **Star Node**: Year Standing Prerequisite
                """
                )
        semester_tables = format_subjects_for_legend(subjects)
        year_tabs = []
        for (year,semster), df in semester_tables.items():
            year_tabs.append("Year " + str(year))
        year_tabs = list(set(year_tabs))
        tabs = st.tabs(year_tabs)
        for i, tab in enumerate(tabs):
            with tab:
                st.write(f"Data for {year_tabs[i]}")
        
        for (year,semester), df in semester_tables.items():
            st.subheader(f"Year {year} - Semester {semester}")
            main,sub = st.columns([3,0.4])
            Total = pd.DataFrame(df)["Credit Units"].sum(axis=0)
            Total_sum = pd.DataFrame([{"Total Units":Total}])
            main.dataframe(
                df,
                hide_index=True,
                column_config={
                    "Subject Code": st.column_config.TextColumn(
                       "Course Code",
                       width="small",
                    ),
                    "Title": st.column_config.TextColumn(
                       "Course Title",
                       width="medium",
                    ),
                    "Pre-requisites": st.column_config.ListColumn(
                       "Pre-Requisites",
                       width="medium",
                    ),
                    "Co-requisites":st.column_config.ListColumn(
                        "Co-Requisites",
                        width="small",
                    ),
                    "Credit Units":st.column_config.Column(
                        "Credit Units",
                        width="small",
                    )
                },
                height=len(df) * 35 + 35,
                use_container_width=True
            )
            sub.dataframe(
                Total_sum,
                hide_index=True,  
            )
else:
    st.warning(f"No curriculum found in the database.")
    select_table = None