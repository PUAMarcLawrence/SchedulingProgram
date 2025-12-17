import streamlit as st
import pandas as pd

# st.set_page_config(page_title="Weekly Timetable Scheduler", layout="wide")


# st.caption("Assign subjects to time slots for each day of the week")



# --- Configuration ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
time_slots = [
    "07:00AM - 09:00AM",
    "09:00AM - 10:30AM",
    "10:30AM - 12:00PM",
    "12:00PM - 01:30PM",
    "01:30PM - 03:00PM",
    "03:00PM - 04:30PM",
    "04:30PM - 06:00PM",
    "06:00PM - 07:30PM",
    "07:30PM - 09:00PM",
]

subjects = ["", "Math", "Science", "English", "History", "Programming", "Electronics"]

# # --- Initialize timetable ONCE ---
# if "timetable" not in st.session_state:
#     st.session_state.timetable = pd.DataFrame(
#         "", index=time_slots, columns=days
#     )


# st.title("📅 Weekly Timetable Scheduler")

# # --- Timetable Editor (NO reassignment, NO rerun) ---
# st.subheader("🗓️ Weekly Schedule")

# st.data_editor(
#     st.session_state.timetable,
#     key="timetable_editor",
#     width = 'stretch',
#     column_config={
#         day: st.column_config.SelectboxColumn(
#             label=day,
#             options=subjects
#         ) for day in days
#     },
#     num_rows="fixed"
# )

# # --- Assign via Form (isolated rerun) ---
# st.subheader("➕ Assign Subject to Slot")

# with st.form("assign_form"):
#     col1, col2, col3 = st.columns(3)

#     with col1:
#         day = st.selectbox("Day", days)
#     with col2:
#         time = st.selectbox("Time Slot", time_slots)
#     with col3:
#         subject = st.selectbox("Subject", subjects)

#     submitted = st.form_submit_button("Assign")

# if submitted:
#     st.session_state.timetable.loc[time, day] = subject
#     st.success(f"Assigned {subject or 'Empty'} on {day} at {time}")

# # --- Export / Reset ---
# st.subheader("💾 Actions")

# col1, col2 = st.columns(2)

# with col1:
#     csv = st.session_state.timetable.to_csv()
#     st.download_button("Download CSV", csv, "timetable.csv", "text/csv")

# with col2:
#     if st.button("Reset Timetable"):
#         st.session_state.timetable[:] = ""


