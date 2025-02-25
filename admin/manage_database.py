import streamlit as st
from utils.admin_db_utils import get_table_names, load_data, update_data

# st.title("SQLite Database Viewer & Editor")
    
# tables = get_table_names()
# if not tables:
#     st.error("No tables found in the database.")
# else:
#     table_name = st.selectbox("Select Table", tables)
#     df = load_data(table_name)

#     edited_df = st.data_editor(df, num_rows="dynamic")

#     if st.button("Save Changes"):
#         update_data(table_name, edited_df)
#         st.success("Database updated successfully!")