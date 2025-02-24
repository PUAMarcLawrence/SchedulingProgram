import streamlit as st
import pandas as pd
from utils.quickView_db_utils import get_table_names,load_subjects_from_db,format_for_graph
from utils.db_utils import get_department_programs,get_program
from utils.graph_utils import build_interactive_subject_graph

st.set_page_config(layout="wide")

def format_subjects_for_legend(subjects):
    semester_tables = {}

    for semester, semester_subjects in subjects.items():
        legend_data = []
        for subject,details in semester_subjects.items():
            year = details['year']
            sem = details['term']
            title = details['title']
            lec_hrs = details['lec_hrs'] if details['lec_hrs'] else None
            lab_hrs = details['lab_hrs'] if details['lab_hrs'] else None
            prerequisites = ', '.join(details['prerequisites']) if details['prerequisites'] else None
            corequisites = ', '.join(details['corequisites']) if details['corequisites'] else None
            credit_unit = details['credit_unit']
            care_taker = details['care_taker']
            legend_data.append([year,sem,subject, title, lec_hrs, lab_hrs, credit_unit, prerequisites, corequisites, care_taker])
        df = pd.DataFrame(
            legend_data,
            columns=["Yr","Term","Subject Code", "Course Title", "Lec Hrs","Lab Hrs","Credit Units","Pre-requisites", "Co-requisites","Care Taker"]
        )
        semester_tables[semester] = df
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
    curriculum = load_subjects_from_db(st.session_state['department_ID'],program,select_table)
    curriculum_graph = format_for_graph(st.session_state['department_ID'],program,select_table)
    if curriculum:
        st.components.v1.html(
            build_interactive_subject_graph(curriculum_graph).generate_html(),
            height=800
        )
        with st.popover("Show Legend",use_container_width=True):
            st.markdown(
                """
                ### Legend
                - ─── **Solid Line**: Pre-Requisite
                - \ - - - **Broken Line**: Co-Requisite
                - ⭐ **Star Node**: Year Standing Prerequisite
                """
                )
        year_tabs = []
        for year, year_subjects in curriculum.items():
            year_tabs.append("Year " + str(year))
        tabs = st.tabs(year_tabs)
        for i, tab in enumerate(tabs):
            with tab:
                semester_tables = format_subjects_for_legend(curriculum[i+1])
                for semester,subjects in semester_tables.items():
                    st.subheader(f"Year {i+1} - Semester {semester}")
                    main,sub = st.columns([6,0.4])
                    subjects = pd.DataFrame(subjects)
                    total_lec = pd.DataFrame(subjects)["Lec Hrs"].sum(axis=0)
                    total_lab = pd.DataFrame(subjects)["Lab Hrs"].sum(axis=0)
                    total_cred = pd.DataFrame(subjects)["Credit Units"].sum(axis=0)
                    Total_row = pd.DataFrame(
                        {
                            'Course Title': ['TOTAL'],
                            'Lec Hrs': [total_lec],
                            'Lab Hrs': [total_lab],
                            'Credit Units': [total_cred]
                            
                        }
                    )
                    df = pd.concat([subjects, Total_row], ignore_index=True)
                    st.dataframe(
                        df,
                        column_config={
                            "Subject Code": st.column_config.TextColumn(
                            "Course Code",
                            width="small",
                            ),
                            "Course Title": st.column_config.TextColumn(
                            "Course Title",
                            width="medium",
                            ),
                            "Pre-requisites": st.column_config.ListColumn(
                            "Pre-Requisites",
                            width="medium",
                            ),
                            "Co-requisites":st.column_config.ListColumn(
                                "Co-Requisites",
                                width="medium",
                            ),
                            "Credit Units":st.column_config.Column(
                                "Credit Units",
                                width="small",
                            )
                        },
                        hide_index=True,
                        use_container_width=True,
                        height=len(df) * 35 + 38,
                    )
else:
    st.warning(f"No curriculum found in the database.")
    select_table = None