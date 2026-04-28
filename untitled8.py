import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------- DATABASE SETUP ---------------- #

conn = sqlite3.connect("school.db", check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute("""CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )""")

c.execute("""CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                date_added TEXT
            )""")

c.execute("""CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_name TEXT,
                score REAL,
                letter_grade TEXT,
                date TEXT
            )""")

conn.commit()

# ---------------- AUTH SYSTEM ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def auth_page():
    st.title("🔐 Student Grade Analyzer")

    choice = st.radio("Select Option", ["Login", "Sign Up"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

    else:
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if new_pass != confirm:
                st.warning("Passwords do not match")
            else:
                try:
                    c.execute("INSERT INTO users VALUES (?,?)", (new_user, new_pass))
                    conn.commit()
                    st.success("Account created! Login now ✅")
                except:
                    st.error("Username already exists ❌")

if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ---------------- MAIN APP ---------------- #

st.set_page_config(page_title="Student Grade Analyzer", layout="wide")
st.title("📚 Student Grade Analyzer")

# Sidebar
with st.sidebar:
    page = st.radio("Navigation", ["Add Student", "Record Grade", "Dashboard", "Analytics"])
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Helper functions
def calculate_grade(score):
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"

# Add Student
if page == "Add Student":
    st.header("➕ Add Student")

    sid = st.text_input("Student ID")
    fname = st.text_input("First Name")
    lname = st.text_input("Last Name")
    email = st.text_input("Email")

    if st.button("Add"):
        try:
            c.execute("INSERT INTO students VALUES (?,?,?,?,?)",
                      (sid, fname, lname, email, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("Student added ✅")
        except:
            st.error("Student ID exists ❌")

    df = pd.read_sql("SELECT * FROM students", conn)
    st.dataframe(df)

# Record Grade
elif page == "Record Grade":
    st.header("📝 Record Grade")

    students = pd.read_sql("SELECT * FROM students", conn)

    if students.empty:
        st.warning("Add students first")
    else:
        sid = st.selectbox("Student", students["student_id"])
        assignment = st.text_input("Assignment")
        score = st.number_input("Score", 0.0, 100.0)

        if st.button("Save"):
            c.execute("INSERT INTO grades (student_id, assignment_name, score, letter_grade, date) VALUES (?,?,?,?,?)",
                      (sid, assignment, score, calculate_grade(score), datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("Saved ✅")

        df = pd.read_sql("SELECT * FROM grades", conn)
        st.dataframe(df)

# Dashboard
elif page == "Dashboard":
    st.header("👤 Student Dashboard")

    students = pd.read_sql("SELECT * FROM students", conn)

    if not students.empty:
        sid = st.selectbox("Select Student", students["student_id"])

        grades = pd.read_sql(f"SELECT * FROM grades WHERE student_id='{sid}'", conn)

        if not grades.empty:
            avg = grades["score"].mean()
            st.metric("Average", f"{avg:.1f}%")
            st.line_chart(grades.set_index("date")["score"])
        else:
            st.info("No grades yet")

# Analytics
elif page == "Analytics":
    st.header("📊 Class Analytics")

    grades = pd.read_sql("SELECT * FROM grades", conn)

    if not grades.empty:
        st.metric("Class Average", f"{grades['score'].mean():.1f}%")
        st.bar_chart(grades["letter_grade"].value_counts())

# Footer
st.markdown("---")
st.markdown("*Database Enabled Streamlit App*")
