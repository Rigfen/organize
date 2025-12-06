import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Daily organizer", page_icon="📊", layout="centered")
st.title("Organize Away 📊")
st.write("Feel too overwhelmed with tasks?")
st.write("Let us do one small thing first and let momentum do the rest.")

# -------------------------
# Helpers
# -------------------------
def task_filename(username: str) -> str:
    return f"tasks_{username}.csv"

def now_iso() -> str:
    return datetime.now().isoformat(timespec="minutes")

def safe_read_tasks(path: str) -> pd.DataFrame:
    """Read CSV safely; if missing/corrupt, create proper empty DF."""
    cols = ["task", "completed", "created", "deadline", "completed_date"]
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            df = pd.read_csv(path)
        else:
            raise Exception("missing or empty")
    except:
        df = pd.DataFrame(columns=cols)
        df.to_csv(path, index=False)
    # Ensure required columns
    for c in cols:
        if c not in df.columns:
            df[c] = "" if c != "completed" else False
    # Normalize types
    df["completed"] = df["completed"].fillna(False).astype(bool)
    df["created"] = df["created"].fillna("")
    df["deadline"] = df["deadline"].fillna("")
    df["completed_date"] = df["completed_date"].fillna("")
    return df

def save_tasks(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)

def cleanup_completed_older_than(df: pd.DataFrame, days: int = 2) -> pd.DataFrame:
    """Return df with completed rows older than `days` removed."""
    keep_rows = []
    now = datetime.now()
    for _, row in df.iterrows():
        if row["completed"]:
            comp = row["completed_date"]
            try:
                comp_dt = datetime.fromisoformat(comp)
                if (now - comp_dt) < timedelta(days=days):
                    keep_rows.append(True)
                else:
                    keep_rows.append(False)  # too old -> drop
            except Exception:
                # If parsing fails, keep the row (safer) or drop? We'll drop to avoid junk.
                keep_rows.append(False)
        else:
            keep_rows.append(True)
    return df[keep_rows].reset_index(drop=True)

def fmt_dt(iso: str) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso

# -------------------------
# Login
# -------------------------
username = st.text_input("Enter your username (no password for now)")

if not username:
    st.warning("Please enter your username to continue.")
    st.stop()

# Build user file path and load data
task_file = task_filename(username)
df = safe_read_tasks(task_file)

# Auto-clean completed tasks older than 2 days
df = cleanup_completed_older_than(df, days=2)
save_tasks(df, task_file)

# -------------------------
# Add new task (with optional deadline date+time)
# -------------------------
st.markdown("## Add a task")
new_task = st.text_input("Task description", key="new_task_input")

# deadline inputs (optional)
col_date, col_time = st.columns(2)
with col_date:
    d = st.date_input("Due date (optional)", value=None)
with col_time:
    t = st.time_input("Time (optional)", value=None)

# combine deadline only if both provided (user may leave defaults)
deadline_iso = ""
try:
    if d is not None and t is not None:
        # If the UI returns today's default values even if user didn't change,
        # we still allow storing a deadline (it's optional). If you want 'no deadline'
        # when user hasn't touched it, you'd add an extra checkbox to enable deadline.
        deadline_dt = datetime.combine(d, t)
        deadline_iso = deadline_dt.isoformat(timespec="minutes")
except Exception:
    deadline_iso = ""

if st.button("Add task") and new_task.strip() != "":
    new_row = {
        "task": new_task.strip(),
        "completed": False,
        "created": now_iso(),
        "deadline": deadline_iso,
        "completed_date": ""
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_tasks(df, task_file)
    st.success("Task added.")
    st.experimental_rerun()

# -------------------------
# Display tasks: Active then Completed (completed sorted most-recent-first)
# -------------------------
st.markdown("## Your Tasks")

# Active tasks
active_df = df[df["completed"] == False].copy().reset_index()
if active_df.empty:
    st.write("No active tasks.")
else:
    st.markdown("### 📝 Active")
    for idx, row in active_df.iterrows():
        orig_index = row["index"]  # original index in df
        cols = st.columns([6, 2, 2])
        with cols[0]:
            st.write(row["task"])
            if row["created"]:
                st.caption(f"Created: {fmt_dt(row['created'])}")
            if row["deadline"]:
                st.caption(f"Deadline: {fmt_dt(row['deadline'])}")
        with cols[1]:
            # checkbox: when clicked, mark completed
            key = f"{username}_complete_{orig_index}"
            checked = st.checkbox("Mark done", key=key)
            if checked:
                df.at[orig_index, "completed"] = True
                df.at[orig_index, "completed_date"] = now_iso()
                save_tasks(df, task_file)
                st.experimental_rerun()
        with cols[2]:
            # optional: show a small note or leave empty
            pass

# Completed tasks (sorted by completed_date desc, most recent first)
completed_df = df[df["completed"] == True].copy()
if completed_df.empty:
    st.markdown("### ✔️ Completed")
    st.write("No completed tasks yet.")
else:
    # parse completed_date safely; rows with invalid/missing completed_date will be last
    try:
        completed_df["completed_parsed"] = pd.to_datetime(completed_df["completed_date"], errors="coerce")
        completed_df = completed_df.sort_values("completed_parsed", ascending=False)
    except Exception:
        # fallback: keep original order
        pass

    st.markdown("### ✔️ Completed (most recent first)")
    # show counter
    st.write(f"Completed: **{len(completed_df)}**")
    for _, row in completed_df.iterrows():
        st.write(f"✔ {row['task']} — completed on **{fmt_dt(row['completed_date'])}**")

# -------------------------
# Progress
# -------------------------
completed_count = int(df["completed"].sum())
total = len(df)
progress_value = completed_count / total if total else 0
st.progress(progress_value)
st.write(f"Completed {completed_count}/{total} tasks")
