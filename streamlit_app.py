import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Daily organizer", page_icon="📊", layout="centered")
st.title("Organize Away 📊")
st.write(
    "Feel too overwhelmed with tasks?"
)
st.write("Let us take do one small thing first and let momentum do the rest. ")

task_file="tasks.csv"
if os.path.exists(task_file):
    df = pd.read_csv(task_file)
else:
    df= pd.DataFrame(columns=["task", "completed"])

new_task= st.text_input("Add a new task: ")

if st.button ("Add task") and new_task.strip() != "":
    df = df._append({"task": new_task, "completed": False}, ignore_index=True)
    df.to_csv(task_file, index=False)
    st.success("Task Added!")

# Display tasks
st.subheader("Your Tasks")

if len(df) ==0:
    st.write("No tasks yet.")

else:
    for i, row in df.iterrows():
        done = st.checkbox(row["task"], value=row["completed"], key=i)
        df.at[i, "completed"] = done
    
    # save updated states
    df.to_csv(task_file, index=False)

#show progress
completed_count = df["completed"].sum()
total = len(df)
st.progress(completed_count /total if total else 0)
st.write (f"Completed {completed_count}/{total} tasks")
