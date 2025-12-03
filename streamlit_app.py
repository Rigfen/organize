import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from pathlib import Path

# --- Define users ---
names = ["Alice", "Bob"]
usernames = ["alice", "bob"]
passwords = ["alice123", "bob123"]  # plain passwords

# Hash the passwords (important!)
hashed_passwords = stauth.Hasher(passwords).generate()

# Create the authenticator object
authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "my_cookie_name",          # cookie name
    "my_signature_key",        # any random string
    cookie_expiry_days=1       # days until cookie expires
)

# --- Login widget ---
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.success(f"Welcome {name}!")

    # --- User-specific tasks ---
    user_file = Path(f"tasks_{username}.csv")

    if user_file.exists():
        df = pd.read_csv(user_file)
    else:
        df = pd.DataFrame(columns=["task", "completed"])

    new_task = st.text_input("Add a new task:")

    if st.button("Add task") and new_task.strip() != "":
        df = df._append({"task": new_task, "completed": False}, ignore_index=True)
        df.to_csv(user_file, index=False)
        st.success("Task Added!")

    # Display tasks
    st.subheader("Your Tasks")
    if len(df) == 0:
        st.write("No tasks yet.")
    else:
        for i, row in df.iterrows():
            done = st.checkbox(row["task"], value=row["completed"], key=i)
            df.at[i, "completed"] = done
        df.to_csv(user_file, index=False)

    # Progress bar
    completed_count = df["completed"].sum()
    total = len(df)
    st.progress(completed_count / total if total else 0)
    st.write(f"Completed {completed_count}/{total} tasks")

elif authentication_status == False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please enter your username and password")
