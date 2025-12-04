import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Daily organizer", page_icon="📊", layout="centered")
st.title("Organize Away 📊")
st.write("Feel too overwhelmed with tasks?")
st.write("Let us take do one small thing first and let momentum do the rest.")

# --- Simple username login ---
username = st.text_input("Enter your username")

if username:
    task_file = f"tasks_{username}.csv"

    # Load or create dataframe
    if os.path.exists(task_file):
        df = pd.read_csv(task_file)
    else:
        df = pd.DataFrame(columns=["task", "completed", "deadline", "completed_date"])

    # Make sure completed_date column exists
    if "completed_date" not in df.columns:
        df["completed_date"] = ""

    # --- Add New Task ---
    new_task = st.text_input("Add a new task:")

    d = st.date_input("Due date (optional):")
    t = st.time_input("Time (optional):")

    # combine date + time
    deadline = datetime.combine(d, t)

    if st.button("Add task") and new_task.strip() != "":
        df = df._append(
            {
                "task": new_task,
                "completed": False,
                "deadline": deadline,
                "completed_date": ""
            },
            ignore_index=True
        )
        df.to_csv(task_file, index=False)
        st.success("Task Added!")

    # --- Display Tasks ---
    st.subheader("Your Tasks")

    if len(df) == 0:
        st.write("No tasks yet.")
    else:

        # Split into active and completed
        active_tasks = df[df["completed"] == False]
        completed_tasks = df[df["completed"] == True]

        # ============================
        # ACTIVE TASKS SECTION
        # ============================
        st.markdown("### 📝 Active Tasks")

        if len(active_tasks) == 0:
            st.write("No active tasks.")
        else:
            for i, row in active_tasks.iterrows():
                cols = st.columns([3, 2])

                # Checkbox for active task
                checked = cols[0].checkbox(
                    row["task"],
                    value=row["completed"],
                    key=f"active_{i}"
                )

                # If checked off, move to completed & timestamp
                if checked:
                    df.at[i, "completed"] = True
                    df.at[i, "completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    df.to_csv(task_file, index=False)
                    st.experimental_rerun()

                # Deadline display
                if pd.notna(row["deadline"]):
                    dl = pd.to_datetime(row["deadline"])
                    time_left = dl - datetime.now()

                    if time_left.total_seconds() < 0:
                        cols[1].write("⏰ **Overdue!**")
                    else:
                        hours_left = int(time_left.total_seconds() // 3600)
                        cols[1].write(f"⏳ {hours_left} hrs left")
                else:
                    cols[1].write("No timer")

        # ============================
        # COMPLETED TASKS SECTION
        # ============================
        st.markdown("### ✔️ Completed Tasks")

        if len(completed_tasks) == 0:
            st.write("No completed tasks yet.")
        else:
            for i, row in completed_tasks.iterrows():
                completed_date = row["completed_date"]
                st.write(f"✔ **{row['task']}** — completed on **{completed_date}**")

        # Save any updates
        df.to_csv(task_file, index=False)

    # --- Show progress ---
    completed_count = df["completed"].sum()
    total = len(df)
    st.progress(completed_count / total if total else 0)
    st.write(f"Completed {completed_count}/{total} tasks")

else:
    st.warning("Please enter a username to continue.")
