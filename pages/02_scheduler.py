import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Multi-Year Scheduler", layout="wide")

# ---------------------------------
# CONFIGURATION
# ---------------------------------
YEAR_TERM_CONFIG = {
    1: 3,
    2: 3,
    3: 4,
    4: 4,
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

START_TIME = "07:30"
END_TIME = "21:15"
SLOT_MINUTES = 75

# ---------------------------------
# Generate time slots
# ---------------------------------
def generate_time_slots(start, end, interval_minutes):
    slots = []
    current = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")

    while current < end_time:
        next_time = current + timedelta(minutes=interval_minutes)
        slots.append(
            f"{current.strftime('%I:%M %p')} - {next_time.strftime('%I:%M %p')}"
        )
        current = next_time

    return slots

TIME_SLOTS = generate_time_slots(
    START_TIME,
    END_TIME,
    SLOT_MINUTES
)

# ---------------------------------
# Schedule template
# ---------------------------------
def make_empty_schedule():
    return pd.DataFrame(
        "",
        index=TIME_SLOTS,
        columns=DAYS
    )

# ---------------------------------
# Initialize session state
# ---------------------------------
for year, term_count in YEAR_TERM_CONFIG.items():
    for term in range(1, term_count + 1):
        key = f"year_{year}_term_{term}_df"
        if key not in st.session_state:
            st.session_state[key] = make_empty_schedule()

# ---------------------------------
# Term renderer
# ---------------------------------
def render_term(year: int, term: int):
    st.subheader(f"Year {year} — Term {term}")

    df_key = f"year_{year}_term_{term}_df"
    editor_key = f"editor_year_{year}_term_{term}"

    edited_df = st.data_editor(
        st.session_state[df_key],
        width = 'stretch',
        num_rows="fixed",
        height='content',
        key=editor_key
    )

    # Persist edits
    st.session_state[df_key] = edited_df

    if st.button(
        "Save Term",
        key=f"save_year_{year}_term_{term}"
    ):
        st.success(f"Year {year}, Term {term} saved!")

# ---------------------------------
# UI: Year tabs
# ---------------------------------
year_tabs = st.tabs([f"Year {y}" for y in YEAR_TERM_CONFIG.keys()])

for year_tab, (year, term_count) in zip(year_tabs, YEAR_TERM_CONFIG.items()):
    with year_tab:

        # ---------------------------------
        # UI: Term tabs
        # ---------------------------------
        term_tabs = st.tabs(
            [f"Term {t}" for t in range(1, term_count + 1)]
        )

        for term_tab, term in zip(term_tabs, range(1, term_count + 1)):
            with term_tab:
                render_term(year, term)
