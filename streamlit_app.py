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

    # --- Load or create dataframe ---
    if os.path.exists(task_file):
        df = pd.read_csv(task_file)
    else:
        df = pd.DataFrame(columns=["task", "completed", "deadline", "completed_date"])

    # --- FIX missing columns ---
    required_cols = ["task", "completed", "deadline", "completed_date"]
    for col in required_cols:
        if col not in df.columns:
            if col == "completed":
                df[col] = False
            else:
                df[col] = ""

    df["completed"] = df["completed"].astype(bool)

    # --- AUTO CLEANUP: remove completed tasks older than 2 days ---
    now = datetime.now()

    def too_old(row):
        try:
            if row["completed"] and row["completed_date"]:
                completed_dt = datetime.strptime(row["completed_date"], "%Y-%m-%d %H:%M")
                return (now - completed_dt).days >= 2
            return False
        except:
            return False

    df = df[~df.apply(too_old, axis=1)]
    df.to_csv(task_file, index=False)

    # --- Add New Task ---
    new_task = st.text_input("Add a new task:")

    d = st.date_input("Due date (optional):")
    t = st.time_input("Time (optional):")
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
        active_tasks = df[df["completed"] == False]
        completed_tasks = df[df["completed"] == True]

        # ACTIVE TASKS
        st.markdown("### 📝 Active Tasks")
        if len(active_tasks) == 0:
            st.write("No active tasks.")
        else:
            for i, row in active_tasks.iterrows():
                cols = st.columns([3, 2])
                checked = cols[0].checkbox(
                    row["task"], value=row["completed"], key=f"active_{i}"
                )

                if checked:
                    df.at[i, "completed"] = True
                    df.at[i, "completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    df.to_csv(task_file, index=False)
                    st.rerun()

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

        # COMPLETED TASKS
        st.markdown("### ✔️ Completed Tasks")
        if len(completed_tasks) == 0:
            st.write("No completed tasks yet.")
        else:
            for i, row in completed_tasks.iterrows():
                st.write(f"✔ **{row['task']}** — completed on **{row['completed_date']}**")

        df.to_csv(task_file, index=False)

    # --- FINAL SAFETY CHECK (INSIDE USERNAME BLOCK!) ---
    for col in ["task", "completed", "deadline", "completed_date"]:
        if col not in df.columns:
            if col == "completed":
                df[col] = False
            else:
                df[col] = ""
    df["completed"] = df["completed"].astype(bool)

    # --- Show progress ---
    completed_count = df["completed"].sum()
    total = len(df)
    st.progress(completed_count / total if total else 0)
    st.write(f"Completed {completed_count}/{total} tasks")

else:
    st.warning("Please enter a username to continue.")
