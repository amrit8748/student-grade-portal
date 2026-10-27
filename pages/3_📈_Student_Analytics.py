import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Analytics & Marksheet | Grade Portal",
    page_icon="📈",
    layout="wide"
)

# --- CUSTOM UI STYLING (DARK DASHBOARD THEME & CARDS) ---
st.markdown("""
    <style>
    /* Main Page Background */
    .stApp {
        background-color: #0b0d12;
        color: #e6edf3;
    }
    
    /* Top Window-Style Centered Header Banner */
    .dashboard-header {
        background-color: #162a64;
        border: 2px solid #7ab8ff;
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .dashboard-header h1 {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        padding: 0;
    }
    .dashboard-header p {
        color: #a8c7fa;
        font-size: 0.95rem;
        margin: 6px 0 0 0;
    }

    /* Card Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #12151c;
        border: 1px solid #282d37 !important;
        border-radius: 12px !important;
        padding: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE FILE PATH ---
CSV_FILE = "saved_grades.csv"

# --- CENTER-ALIGNED PAGE HEADER BANNER ---
st.markdown("""
    <div class="dashboard-header">
        <h1>📈 Student Performance Analytics & Official Marksheet</h1>
        <p>Select a student and semester below to generate their complete grade report, SGPA, and visual breakdown</p>
    </div>
""", unsafe_allow_html=True)

# --- CHECK IF DATABASE EXISTS ---
if not os.path.exists(CSV_FILE):
    st.warning("⚠️ No grade records found! Please add student records on **Page 1 (Data Entry)** first.")
    st.stop()

df = pd.read_csv(CSV_FILE)

if df.empty:
    st.warning("⚠️ The database is currently empty. Add student records on Page 1 to view analytics.")
    st.stop()

# --- 1. TOP STUDENT & SEMESTER SELECTOR BAR (CARD BOX) ---
with st.container(border=True):
    st.subheader("🔍 Select Student Record")

    # Create a clean "Roll_No - Student_Name" label for the dropdown
    df["Student_Label"] = df["Roll_No"].astype(str) + " - " + df["Student_Name"]
    unique_students = sorted(df["Student_Label"].unique())

    sel_col1, sel_col2 = st.columns([2, 1])
    with sel_col1:
        selected_student_label = st.selectbox("Choose Student (Roll No & Name)", options=unique_students)

    # Extract the selected Roll_No and filter rows for that student
    selected_roll = selected_student_label.split(" - ")[0]
    student_df = df[df["Roll_No"].astype(str) == selected_roll]

    with sel_col2:
        available_semesters = sorted(student_df["Semester"].unique())
        selected_semester = st.selectbox("Choose Semester", options=available_semesters)

# Filter final dataset for the selected student AND semester
sem_df = student_df[student_df["Semester"] == selected_semester].copy()

# --- 2. STUDENT PROFILE & SGPA SUMMARY CARD (NESTED METRIC CARDS) ---
student_name = sem_df["Student_Name"].iloc[0]
student_branch = sem_df["Branch"].iloc[0]

# Calculate SGPA & Credit Metrics
total_credits = int(sem_df["Credits"].sum())
earned_credits = int(sem_df[sem_df["Status"] == "Pass"]["Credits"].sum())
total_credit_points = sem_df["Credit_Points"].sum()

sgpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0
avg_attendance = round(sem_df["Attendance"].mean(), 1)

# Check if student passed all subjects in this semester
active_backlogs = int((sem_df["Status"] != "Pass").sum())
overall_status = "PASS" if active_backlogs == 0 else f"⚠️ {active_backlogs} BACKLOG / DETAINED"

with st.container(border=True):
    # Profile Header Banner
    st.markdown(f"### 🎓 Official Semester Grade Report: **{student_name}**")
    st.caption(f"**Roll Number:** `{selected_roll}` &nbsp;|&nbsp; **Branch:** `{student_branch}` &nbsp;|&nbsp; **Term:** `{selected_semester}`")

    # 4 Big Nested Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("Semester GPA (SGPA)", f"{sgpa:.2f} / 10.0")
    with m2:
        with st.container(border=True):
            st.metric("Credits Earned", f"{earned_credits} / {total_credits} Cr")
    with m3:
        with st.container(border=True):
            st.metric("Mean Attendance", f"{avg_attendance}%")
    with m4:
        with st.container(border=True):
            st.metric("Semester Standing", overall_status)

# --- 3. DETAILED SEMESTER MARKSHEET TABLE (CARD BOX) ---
with st.container(border=True):
    st.subheader("📋 Subject-Wise Grade Breakdown")

    # Select and rename columns for a clean report card look
    marksheet_cols = [
        "Subject", "Course_Type", "Credits", 
        "Mid_Sem", "Assignments", "End_Sem", "Total_Marks", 
        "Letter_Grade", "Grade_Point", "Credit_Points", 
        "Attendance", "Status"
    ]

    st.dataframe(
        sem_df[marksheet_cols],
        use_container_width=True,
        hide_index=True
    )

# --- 4. VISUAL PERFORMANCE ANALYTICS (SIDE-BY-SIDE CARD BOXES) ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    with st.container(border=True):
        st.markdown("##### 🎯 Assessment Split by Subject (Max 100)")
        # Stacked bar chart showing Mid_Sem + Assignments + End_Sem adding up to Total_Marks
        marks_chart_df = sem_df.set_index("Subject")[["Mid_Sem", "Assignments", "End_Sem"]]
        st.bar_chart(marks_chart_df)

with chart_col2:
    with st.container(border=True):
        st.markdown("##### 📅 Attendance Percentage by Subject (%)")
        attendance_chart_df = sem_df.set_index("Subject")[["Attendance"]]
        st.bar_chart(attendance_chart_df)

# --- 5. GRADE DISTRIBUTION SUMMARY (CARD BOX) ---
with st.container(border=True):
    st.markdown("##### 🏅 Letter Grade Tally (This Semester)")
    grade_counts = sem_df["Letter_Grade"].value_counts().reset_index()
    grade_counts.columns = ["Letter Grade", "Number of Subjects"]
    st.dataframe(grade_counts, use_container_width=True, hide_index=True)