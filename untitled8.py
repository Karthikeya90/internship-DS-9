import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Student Grade Analyzer", page_icon="📚", layout="wide")

# ---------------- LOGIN SYSTEM ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login - Student Grade Analyzer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid username or password ❌")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- APP STARTS AFTER LOGIN ---------------- #

# Initialize session state
if 'students' not in st.session_state:
    st.session_state.students = {}

if 'grades' not in st.session_state:
    st.session_state.grades = []

# Helper functions
def calculate_grade_letter(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def get_student_stats(student_id):
    student_grades = [g for g in st.session_state.grades if g['student_id'] == student_id]
    if not student_grades:
        return None
    
    scores = [g['score'] for g in student_grades]
    return {
        'average': sum(scores) / len(scores),
        'highest': max(scores),
        'lowest': min(scores),
        'total_assignments': len(scores)
    }

def get_class_stats():
    if not st.session_state.grades:
        return None
    
    scores = [g['score'] for g in st.session_state.grades]
    return {
        'class_average': sum(scores) / len(scores),
        'highest_score': max(scores),
        'lowest_score': min(scores),
        'total_grades': len(scores)
    }

# App title
st.title("📚 Student Grade Analyzer")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select Page", ["Add Student", "Record Grade", "Student Dashboard", "Class Analytics"])
    
    st.markdown("---")
    st.subheader("Quick Stats")
    if st.session_state.students:
        st.metric("Total Students", len(st.session_state.students))
    if st.session_state.grades:
        st.metric("Total Grades", len(st.session_state.grades))
        class_stats = get_class_stats()
        if class_stats:
            st.metric("Class Average", f"{class_stats['class_average']:.1f}%")

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Add Student Page
if page == "Add Student":
    st.header("➕ Add New Student")
    
    col1, col2 = st.columns(2)
    
    with col1:
        student_id = st.text_input("Student ID", placeholder="e.g., S001")
        first_name = st.text_input("First Name")
    
    with col2:
        last_name = st.text_input("Last Name")
        email = st.text_input("Email", placeholder="student@example.com")
    
    if st.button("Add Student", type="primary"):
        if student_id and first_name and last_name:
            if student_id not in st.session_state.students:
                st.session_state.students[student_id] = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'date_added': datetime.now().strftime("%Y-%m-%d")
                }
                st.success(f"✅ Student {first_name} {last_name} added successfully!")
                st.rerun()
            else:
                st.error("❌ Student ID already exists!")
        else:
            st.warning("⚠️ Please fill in all required fields!")
    
    if st.session_state.students:
        st.markdown("---")
        st.subheader("Registered Students")
        students_df = pd.DataFrame.from_dict(st.session_state.students, orient='index')
        students_df.index.name = 'Student ID'
        st.dataframe(students_df, use_container_width=True)

# Record Grade Page
elif page == "Record Grade":
    st.header("📝 Record Grade")
    
    if not st.session_state.students:
        st.warning("⚠️ Please add students first before recording grades!")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.selectbox(
                "Select Student",
                options=list(st.session_state.students.keys()),
                format_func=lambda x: f"{x} - {st.session_state.students[x]['first_name']} {st.session_state.students[x]['last_name']}"
            )
            assignment_name = st.text_input("Assignment Name", placeholder="e.g., Midterm Exam")
        
        with col2:
            score = st.number_input("Score (%)", min_value=0.0, max_value=100.0, step=0.5)
            assignment_type = st.selectbox("Assignment Type", ["Exam", "Quiz", "Homework", "Project", "Other"])
        
        date = st.date_input("Date")
        notes = st.text_area("Notes (Optional)")
        
        if st.button("Record Grade", type="primary"):
            if assignment_name:
                grade_entry = {
                    'student_id': student_id,
                    'assignment_name': assignment_name,
                    'score': score,
                    'letter_grade': calculate_grade_letter(score),
                    'assignment_type': assignment_type,
                    'date': date.strftime("%Y-%m-%d"),
                    'notes': notes
                }
                st.session_state.grades.append(grade_entry)
                st.success(f"✅ Grade recorded: {score}% ({calculate_grade_letter(score)})")
                st.rerun()
            else:
                st.warning("⚠️ Please enter assignment name!")
        
        if st.session_state.grades:
            st.markdown("---")
            st.subheader("Recent Grades")
            recent_grades = st.session_state.grades[-10:][::-1]
            grades_df = pd.DataFrame(recent_grades)
            st.dataframe(grades_df, use_container_width=True)

# Student Dashboard
elif page == "Student Dashboard":
    st.header("👤 Student Dashboard")
    
    if not st.session_state.students:
        st.warning("⚠️ No students registered yet!")
    else:
        student_id = st.selectbox(
            "Select Student",
            options=list(st.session_state.students.keys()),
            format_func=lambda x: f"{x} - {st.session_state.students[x]['first_name']} {st.session_state.students[x]['last_name']}"
        )
        
        student = st.session_state.students[student_id]
        st.subheader(f"{student['first_name']} {student['last_name']}")
        
        stats = get_student_stats(student_id)
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Average", f"{stats['average']:.1f}%")
            col2.metric("Highest", f"{stats['highest']:.1f}%")
            col3.metric("Lowest", f"{stats['lowest']:.1f}%")
            col4.metric("Assignments", stats['total_assignments'])

            student_grades = [g for g in st.session_state.grades if g['student_id'] == student_id]
            df = pd.DataFrame(student_grades)
            st.line_chart(df.set_index('date')['score'])

# Class Analytics
elif page == "Class Analytics":
    st.header("📊 Class Analytics")
    
    if st.session_state.grades:
        class_stats = get_class_stats()
        st.metric("Class Average", f"{class_stats['class_average']:.1f}%")
