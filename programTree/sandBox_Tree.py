import streamlit as st
import pandas as pd
import time
from utils.programTree_db_utils import load_subjects_from_db, get_table_names
from utils.sandBox_db_utils import copy_table   

st.set_page_config(layout="wide")
with st.popover("New Sandbox"):
    option = st.selectbox("Options", ("From Scratch", "Copy from existing curriculum"))
    if st.button("Create"):
        if option == "Copy from existing curriculum":
            if copy_table('data/ece.db',st.session_state['ID'],'ECE2024','ECE2025'):
                st.success("Table copied successfully")
            else:
                st.error("Curriculum name in use.")
        else:
            st.session_state['ID'] = str(int(time.time()))
            st.success("New Sandbox created successfully")

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

# Create dynamic tabs
open_tables = (get_table_names())
tabs = st.tabs(open_tables)

# Add content to each tab dynamically
for i, tab in enumerate(tabs):
    with tab:
        st.write(f"Data for {open_tables[i]}")
        subjects = load_subjects_from_db(open_tables[i])
        # print(subjects)
        if subjects:
            # st.components.v1.html(
            #     build_interactive_subject_graph(subjects).generate_html(),
            #     height=800
            # )
            semester_tables = format_subjects_for_legend(subjects)
            Edit = {}
            for (year,semester), df in semester_tables.items():
                semester_key = (year,semester)
                st.subheader(f"Year {year} - Semester {semester}")
                main,sub = st.columns([3,0.3])
                Edited_table=main.data_editor(
                    df,
                    num_rows="dynamic",
                    hide_index=True,
                    column_config={
                        "Subject Code": st.column_config.TextColumn(
                        "Subject Code",
                        width="small",
                        ),
                        "Title": st.column_config.TextColumn(
                        "Title",
                        width="medium",
                        ),
                        "Pre-requisites": st.column_config.ListColumn(
                        "Prerequisites",
                        width="medium",
                        ),
                        "Co-requisites":st.column_config.ListColumn(
                            "Co-requisites",
                            width="small",
                        ),
                        "Credit Units":st.column_config.NumberColumn(
                            "Credit Units",
                            width="small",
                        )
                    },
                    height=len(df) * 35 + 70,
                    use_container_width=True
                )
                # for subject_code,title,prerequisite,corequisite,credit_units in zip(Edited_table["Subject Code"],Edited_table["Title"],Edited_table["Pre-requisites"],Edited_table["Co-requisites"],Edited_table["Credit Units"]):
                    # print(f"Year:{year} Semester:{semester} Subject Code: {subject_code}, Title: {title}, Prerequisites: {prerequisite}, Co-requisites: {corequisite}, Credit Units: {credit_units}")
                # Edit[semester_key] = Edited_table.to_dict('records')
                # print(Edit[semester_key] = Edited_table.to_dict())
                # Edited_table.concact(edit)

                Total = pd.DataFrame(Edited_table)["Credit Units"].sum(axis=0)
                Total_sum = pd.DataFrame([{"Total Units":Total}])
                sub.dataframe(
                    Total_sum,
                    column_config={
                        "Total Units": st.column_config.ProgressColumn(
                            "Total Units",
                            min_value=0,
                            max_value=20,
                            width="small",
                            format="%i"
                        )
                    },
                    hide_index=True,
                )
            # print(Edit)