import streamlit as st
import pandas as pd

# Define schedule parameters
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]

# Initialize session state if not already present
if "selected_cells" not in st.session_state:
    st.session_state.selected_cells = set()

# Function to toggle cell selection
def toggle_cell(day, time_slot):
    cell = (day, time_slot)
    if cell in st.session_state.selected_cells:
        st.session_state.selected_cells.remove(cell)
    else:
        st.session_state.selected_cells.add(cell)

# Create table-like layout
st.title("Interactive Schedule Selector")
st.write("Click on a cell to select/deselect a time slot.")

# Create table
schedule_df = pd.DataFrame("⬜", index=time_slots, columns=days)
for day, time_slot in st.session_state.selected_cells:
    schedule_df.at[time_slot, day] = "✅"

# Display schedule as a table
st.dataframe(schedule_df.style.applymap(lambda x: "background-color: lightgreen" if x == "✅" else ""))

# Clickable buttons for selection
for time_slot in time_slots:
    cols = st.columns(len(days))
    for idx, day in enumerate(days):
        if cols[idx].button(schedule_df.at[time_slot, day], key=f"{day}_{time_slot}"):
            toggle_cell(day, time_slot)
            st.rerun()

# Display selected slots
st.subheader("Selected Time Slots:")
if st.session_state.selected_cells:
    st.write(pd.DataFrame(list(st.session_state.selected_cells), columns=["Day", "Time Slot"]))
else:
    st.write("No slots selected.")
