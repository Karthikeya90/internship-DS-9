import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------- DATABASE ---------------- #
conn = sqlite3.connect("school.db", check_same_thread=False)
c = conn.cursor()

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

# ---------------- AUTH ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def auth():
    st.title("🔐 Student Grade Analyzer")
    choice = st.radio("Select", ["Login", "Sign Up"])

    if choice == "Login":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
            if c.fetchone():
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid login")

    else:
        u = st.text_input("New Username")
        p = st.text_input("Password", type="password")
        cp = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if p != cp:
                st.warning("Passwords mismatch")
            else:
                try:
                    c.execute("INSERT INTO users VALUES (?,?)", (u, p))
                    conn.commit()
                    st.success("Account created")
                except:
                    st.error("User exists")

if not st.session_state.logged_in:
    auth()
    st.stop()

# ---------------- APP ---------------- #
st.set_page_config(layout="wide")
st.title("📚 Student Grade Analyzer")

with st.sidebar:
    page = st.radio("Navigation", ["Add Student", "Record Grade", "Dashboard", "Analytics"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Helper
def grade(score):
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"

# ---------------- ADD STUDENT ---------------- #
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
            st.success("Added ✅")
        except:
            st.error("ID exists ❌")

    df = pd.read_sql("SELECT * FROM students", conn)
    st.dataframe(df)

# ---------------- RECORD GRADE ---------------- #
elif page == "Record Grade":
    st.header("📝 Record Grade")

    students = pd.read_sql("SELECT * FROM students", conn)

    if students.empty:
        st.warning("Add students first")
    else:
        students["name"] = students["first_name"] + " " + students["last_name"]

        selected_name = st.selectbox("Select Student", students["name"])

        # Get ID from name
        sid = students[students["name"] == selected_name]["student_id"].values[0]

        assignment = st.text_input("Assignment")
        score = st.number_input("Score", 0.0, 100.0)

        if st.button("Save"):
            c.execute("INSERT INTO grades (student_id, assignment_name, score, letter_grade, date) VALUES (?,?,?,?,?)",
                      (sid, assignment, score, grade(score), datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("Saved ✅")

        st.dataframe(pd.read_sql("SELECT * FROM grades", conn))

# ---------------- DASHBOARD ---------------- #
elif page == "Dashboard":
    st.header("👤 Student Dashboard")

    students = pd.read_sql("SELECT * FROM students", conn)

    if not students.empty:
        students["name"] = students["first_name"] + " " + students["last_name"]

        selected_name = st.selectbox("Select Student", students["name"])
        sid = students[students["name"] == selected_name]["student_id"].values[0]

        grades = pd.read_sql(f"SELECT * FROM grades WHERE student_id='{sid}'", conn)

        if not grades.empty:
            st.metric("Average", f"{grades['score'].mean():.1f}%")
            st.line_chart(grades.set_index("date")["score"])
        else:
            st.info("No grades")

# ---------------- ANALYTICS ---------------- #
elif page == "Analytics":
    st.header("📊 Class Analytics")

    grades = pd.read_sql("SELECT * FROM grades", conn)

    if not grades.empty:
        st.metric("Class Average", f"{grades['score'].mean():.1f}%")

        st.subheader("Grade Distribution (Bar Chart)")
        bar_data = grades["letter_grade"].value_counts()
        st.bar_chart(bar_data)

        st.subheader("Grade Distribution (Pie Chart)")
        st.pyplot(bar_data.plot.pie(autopct='%1.1f%%').figure)
