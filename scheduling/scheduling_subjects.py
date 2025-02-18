import streamlit as st
import pandas as pd

# Define schedule parameters
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
time_slots = [
    "07:00-8:10", "08:10-09:20", "09:20-10:30", "10:30-11:40", "11:40-12:50","12:50-14:00",
    "14:00-15:10", "15:10-16:20", "16:20-17:30", "17:30-18:40", "18:40-19:50", "19:50-22:00"]

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
st.dataframe(
    schedule_df.style.map(lambda x: "background-color: lightgreen" if x == "✅" else ""),
    use_container_width=True,
    height=len(schedule_df) * 35 + 38,)

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

import streamlit as st

st.title("Vertical Pills Inside Table Cells")

# Function to create a row with vertical pills
def create_column(label, options):
    st.write(f"### {label}")  # Category header
    selected_option = None

    selected_option = st.pills(label, options, selection_mode="multi", label_visibility="collapsed")
    print(selected_option)
    return selected_option

# Create multiple categories and store selections
sun,mon,tue,wed,thur,fri,sat = st.columns(7)  # Split into two vertical sections

with mon:
    selected_1 = create_column("Category 1", ["A", "B", "C"])

with tue:
    selected_2 = create_column("Category 2", ["X", "Y", "Z"])

# Display selected pills in one output
st.write("### Selected Pills")
print(selected_1)
# selected_text = ", ".join(
# )

# st.write(selected_text if selected_text else "No selection made.")
