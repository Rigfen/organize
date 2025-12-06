import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.title("Task Organizer")

TASK_FILE = "tasks.csv"

# ---------------------------------------------------------
# Load tasks safely
# ---------------------------------------------------------
def load_tasks():
    if not os.path.exists(TASK_FILE):
        return pd.DataFrame(columns=["task", "completed", "created", "completed_date"])

    df = pd.read_csv(TASK_FILE)

    # Ensure required columns exist
    required_cols = ["task", "completed", "created", "completed_date"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Fix NaN values
    df["completed"] = df["completed"].fillna(False)
    return df

# ---------------------------------------------------------
# Save tasks
# ---------------------------------------------------------
def save_tasks(df):
    df.to_csv(TASK_FILE, index=False)

# ---------------------------------------------------------
# Remove completed tasks older than 2 days
# ---------------------------------------------------------
def clean_old_tasks(df):
    now = datetime.now()

    def keep_row(row):
        if row["completed"] and pd.notna(row["completed_date"]):
            try:
                comp_date = datetime.fromisoformat(row["completed_date"])
                return (now - comp_date) < timedelta(days=2)
            except:
                return False
        return True

    df = df[df.apply(keep_row, axis=1)]
    return df

# Load tasks
df = load_tasks()
df = clean_old_tasks(df)
save_tasks(df)

# ---------------------------------------------------------
# Add new task
# ---------------------------------------------------------
new_task = st.text_input("Add a new task:")

if st.button("Add"):
    if new_task.strip():
        new_row = {
            "task": new_task,
            "completed": False,
            "created": datetime.now().isoformat(),
            "completed_date": None
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_tasks(df)
        st.experimental_rerun()

# ---------------------------------------------------------
# Display active tasks
# ---------------------------------------------------------
st.subheader("Active Tasks")

for index, row in df[df["completed"] == False].iterrows():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(row["task"])
    with col2:
        if st.checkbox("✔", key=f"complete_{index}"):
            df.at[index, "completed"] = True
            df.at[index, "completed_date"] = datetime.now().isoformat()
            save_tasks(df)
            st.experimental_rerun()

# ---------------------------------------------------------
# Completed section
# ---------------------------------------------------------
st.subheader("Completed Tasks (last 2 days)")
completed_df = df[df["completed"] == True].copy()

# Count
completed_count = len(completed_df)
st.write(f"Completed: **{completed_count}**")

# Show completed tasks sorted by date
for index, row in completed_df.iterrows():
    comp_date = row["completed_date"][:16] if row["completed_date"] else "Unknown"
    st.write(f"✔ {row['task']} — **{comp_date}**")
