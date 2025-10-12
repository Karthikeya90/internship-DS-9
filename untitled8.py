import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Student Grade Analyzer", page_icon="📚", layout="wide")

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
    
    # Display existing students
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
                st.success(f"✅ Grade recorded: {score}% ({calculate_grade_letter(score)}) for {assignment_name}")
                st.rerun()
            else:
                st.warning("⚠️ Please enter an assignment name!")
        
        # Display recent grades
        if st.session_state.grades:
            st.markdown("---")
            st.subheader("Recent Grades")
            recent_grades = st.session_state.grades[-10:][::-1]
            grades_df = pd.DataFrame(recent_grades)
            st.dataframe(grades_df, use_container_width=True)

# Student Dashboard Page
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Student ID:** {student_id}")
        with col2:
            st.write(f"**Email:** {student['email']}")
        with col3:
            st.write(f"**Registered:** {student['date_added']}")
        
        st.markdown("---")
        
        # Student statistics
        stats = get_student_stats(student_id)
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average", f"{stats['average']:.1f}%", delta=f"{calculate_grade_letter(stats['average'])}")
            with col2:
                st.metric("Highest Score", f"{stats['highest']:.1f}%")
            with col3:
                st.metric("Lowest Score", f"{stats['lowest']:.1f}%")
            with col4:
                st.metric("Total Assignments", stats['total_assignments'])
            
            # Student grades table
            st.markdown("---")
            st.subheader("All Grades")
            student_grades = [g for g in st.session_state.grades if g['student_id'] == student_id]
            student_grades_df = pd.DataFrame(student_grades)
            st.dataframe(student_grades_df, use_container_width=True)
            
            # Grade trend chart
            st.markdown("---")
            st.subheader("Grade Trend")
            chart_df = student_grades_df[['date', 'score']].copy()
            chart_df['date'] = pd.to_datetime(chart_df['date'])
            chart_df = chart_df.sort_values('date')
            st.line_chart(chart_df.set_index('date')['score'])
            
            # Grade distribution by assignment type
            st.markdown("---")
            st.subheader("Performance by Assignment Type")
            type_avg = student_grades_df.groupby('assignment_type')['score'].mean()
            st.bar_chart(type_avg)
        else:
            st.info("📊 No grades recorded for this student yet.")

# Class Analytics Page
elif page == "Class Analytics":
    st.header("📊 Class Analytics")
    
    if not st.session_state.grades:
        st.warning("⚠️ No grades recorded yet!")
    else:
        # Class statistics
        class_stats = get_class_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Class Average", f"{class_stats['class_average']:.1f}%")
        with col2:
            st.metric("Highest Score", f"{class_stats['highest_score']:.1f}%")
        with col3:
            st.metric("Lowest Score", f"{class_stats['lowest_score']:.1f}%")
        with col4:
            st.metric("Total Grades", class_stats['total_grades'])
        
        st.markdown("---")
        
        # Student averages
        st.subheader("Student Performance Overview")
        student_averages = []
        for sid in st.session_state.students:
            stats = get_student_stats(sid)
            if stats:
                student = st.session_state.students[sid]
                student_averages.append({
                    'Student ID': sid,
                    'Name': f"{student['first_name']} {student['last_name']}",
                    'Average': round(stats['average'], 1),
                    'Letter Grade': calculate_grade_letter(stats['average']),
                    'Assignments': stats['total_assignments']
                })
        
        if student_averages:
            avg_df = pd.DataFrame(student_averages)
            avg_df = avg_df.sort_values('Average', ascending=False)
            st.dataframe(avg_df, use_container_width=True)
            
            # Grade distribution chart
            st.markdown("---")
            st.subheader("Grade Distribution")
            grades_df = pd.DataFrame(st.session_state.grades)
            st.write("Distribution of all scores:")
            score_hist = pd.cut(grades_df['score'], bins=[0, 60, 70, 80, 90, 100], 
                               labels=['F (0-59)', 'D (60-69)', 'C (70-79)', 'B (80-89)', 'A (90-100)'])
            score_counts = score_hist.value_counts().sort_index()
            st.bar_chart(score_counts)
            
            # Letter grade distribution
            st.markdown("---")
            st.subheader("Letter Grade Distribution")
            letter_counts = grades_df['letter_grade'].value_counts()
            st.bar_chart(letter_counts)
            
            # Assignment type performance
            st.markdown("---")
            st.subheader("Average Score by Assignment Type")
            type_avg = grades_df.groupby('assignment_type')['score'].mean()
            st.bar_chart(type_avg)
        else:
            st.info("📊 No student performance data available yet.")

# Footer
st.markdown("---")
st.markdown("*Student Grade Analyzer - Built with Streamlit*")
