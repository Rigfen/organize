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
        df = pd.DataFrame(columns=["task", "completed", "deadline"])

    # --- Add New Task ---
    new_task = st.text_input("Add a new task:")
    deadline = st.datetime_input("When should this be done? (optional)", value=None)

    if st.button("Add task") and new_task.strip() != "":
        df = df._append(
            {
                "task": new_task,
                "completed": False,
                "deadline": deadline if deadline else ""
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
        for i, row in df.iterrows():
            cols = st.columns([3, 2])
            
            # Checkbox
            done = cols[0].checkbox(row["task"], value=row["completed"], key=i)
            df.at[i, "completed"] = done

            # Display deadline
            if row["deadline"] != "":
                try:
                    dl = pd.to_datetime(row["deadline"])
                    time_left = dl - datetime.now()

                    if time_left.total_seconds() < 0:
                        cols[1].write(f"⏰ **Overdue!**")
                    else:
                        hours_left = int(time_left.total_seconds() // 3600)
                        cols[1].write(f"⏳ {hours_left} hrs left")
                except:
                    cols[1].write("—")
            else:
                cols[1].write("No timer")

        # Save updates
        df.to_csv(task_file, index=False)

    # --- Show Progress ---
    completed_count = df["completed"].sum()
    total = len(df)
    st.progress(completed_count / total if total else 0)
    st.write(f"Completed {completed_count}/{total} tasks")

else:
    st.warning("Please enter a username to continue.")
