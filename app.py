import sqlite3
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from graphviz import Digraph

# Function to retrieve data from the SQLite database
def get_data_from_db(db_path, query):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Retrieve data using the provided query
    df = pd.read_sql_query(query, conn)
    
    # Close the database connection
    conn.close()
    
    return df

def create_graph(data):
    dot = Digraph(format='png')

    # Add nodes and edges
    for index, row in data.iterrows():
        code = row['Code']  # Assuming the column for the code is named 'code'
        prerequisites = row['Prerequisites']  # Assuming a column for prerequisites
        requisites = row['Co_requisites']  # Assuming a column for requisites
        
        # Add the main code node
        dot.node(code)

        # Add prerequisite edges
        if isinstance(prerequisites, str):  # Check if it's a string
            for prereq in prerequisites.split(','):
                prereq = prereq.strip()
                dot.node(prereq)  # Ensure prerequisite node exists
                dot.edge(prereq, code)  # Create edge from prerequisite to code

        # Add requisite edges
        if isinstance(requisites, str):  # Check if it's a string
            for req in requisites.split(','):
                req = req.strip()
                dot.node(req)  # Ensure requisite node exists
                dot.edge(code, req)  # Create edge from code to requisite

    return dot

# Database path and query (you can modify these as needed)
db_path = 'ece.db'  # Path to your SQLite database
query = 'SELECT * FROM ECE2021'  # SQL query to fetch data from the table

 # Connect to SQLite database to get list of tables
conn = sqlite3.connect(db_path)  # Replace with your database file
table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
conn.close()

# Dropdown for selecting a table
selected_table = st.selectbox("Select a table:", table_names['name'].tolist())

if selected_table:
    # Streamlit app
    st.title(selected_table)

    # Get data from the database
    data = get_data_from_db(db_path, 'SELECT * FROM '+selected_table)

    # Assuming there is a 'year_column' in the table, we will filter by year 1, 2, 3, and 4
    year_column = 'Year'  # Replace with the actual column name representing year categories
    years = ['1', '2', '3', '4']  # List of years 1, 2, 3, 4 to separate data into

    # Loop through each year and create a separate table
    for year in years:
        st.subheader(f"Data for Year {year}")
        
        # Filter the data for the current year
        data_for_year = data[data[year_column] == year]
        
        # Insert a drag column for each table
        data_for_year.insert(0, 'Drag', '⇅')
        
        # Drop the year column from the DataFrame before displaying it
        data_for_year = data_for_year.drop(columns=[year_column])
        
        # Build the grid options to enable row dragging
        gb = GridOptionsBuilder.from_dataframe(data_for_year)
        gb.configure_default_column(editable=True)  # Makes columns editable (optional)
        gb.configure_grid_options(rowDragManaged=True)  # Enables row drag management
        gb.configure_column('Drag', rowDrag=True, width=50)  # Set rowDrag on the Drag column with specified width
        
        grid_options = gb.build()

        # Display the data in an AgGrid table with row dragging enabled
        AgGrid(data_for_year, gridOptions=grid_options, enable_enterprise_modules=True,height=500, fit_columns_on_grid_load=True)

        # Adjust the layout of the AgGrid table
        st.markdown(
            """
            <style>
            .ag-theme-alpine {
                --ag-grid-header-background-color: #f7f7f7;
                --ag-grid-header-color: #000;
                --ag-grid-row-height: 30px; /* Adjust row height */
                --ag-grid-font-size: 14px; /* Adjust font size */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Create the Graphviz graph
    graph = create_graph(data)

    graph_string=graph.source

    st.graphviz_chart(graph_string, use_container_width=False)
