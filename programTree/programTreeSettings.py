import streamlit as st
from utils.db_utils import programs_to_db,programs_to_list

# Initialize the list in session state if it doesn't already exist
if 'editable_list' not in st.session_state:
    st.session_state['editable_list'] = []
st.session_state['editable_list'] = programs_to_list()

# Function to add an item to the list
def add_item():
    if st.session_state['new_item']:
        st.session_state['editable_list'].append(st.session_state['new_item'])
        st.session_state['new_item'] = ""  # Clear the input box
        programs_to_db(st.session_state['editable_list'])

# Function to delete an item from the list
def delete_item(index):
    del st.session_state['editable_list'][index]

# Main app layout
st.title("Programs List")

# Input box for adding new items
st.text_input("Add new Program:", key="new_item")
st.button("Add", on_click=add_item)

# Display the editable list
if st.session_state['editable_list']:
    st.subheader("List of Programs")
    for i, item in enumerate(st.session_state['editable_list']):
        col1, col2, col3 = st.columns([6, 1, 1])
        
        # Editable text input for each item
        updated_item = col1.text_input("Edit item", item, key=f"item_{i}")
        
        # Update the item if it was edited
        if updated_item != item:
            st.session_state['editable_list'][i] = updated_item
        
        # Delete button for each item
        col2.button("Delete", key=f"delete_{i}", on_click=delete_item, args=(i,))

else:
    st.write("The list is currently empty.")
