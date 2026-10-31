import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Analytics & Marksheet | Grade Portal",
    page_icon="📈",
    layout="wide"
)

# --- CUSTOM UI  ---
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

# ---  PAGE HEADER BANNER ---
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

# --- 1. TOP STUDENT & SEMESTER SELECTOR BAR ---
with st.container(border=True):
    st.subheader("🔍 Select Student Record")

    df["Student_Label"] = df["Roll_No"].astype(str) + " - " + df["Student_Name"]

    # Line 1: Branch / Degree and Semester side-by-side
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        branches = sorted(df["Branch"].dropna().unique())
        selected_branch = st.selectbox(
            "Branch / Degree",
            options=branches,
            index=None,
            placeholder="Select Branch / Degree..."
        )

    branch_df = df[df["Branch"] == selected_branch] if selected_branch else df

    with sel_col2:
        semesters = sorted(branch_df["Semester"].dropna().unique())
        selected_semester = st.selectbox(
            "Semester",
            options=semesters,
            index=None,
            placeholder="Select Semester..."
        )

    filtered_selector_df = (
        branch_df[branch_df["Semester"] == selected_semester]
        if selected_semester else branch_df
    )

    # Line 2: Student Name / Roll No box on the next line
    unique_students = sorted(filtered_selector_df["Student_Label"].dropna().unique())
    selected_student_label = st.selectbox(
        "Student Name / Roll Number",
        options=unique_students,
        index=None,
        placeholder="Select Student (Roll No & Name)..."
    )

# Keep the rest of the page empty until all 3 are selected
if not (selected_branch and selected_semester and selected_student_label):
    st.info("Select a **Branch**, **Semester**, and **Student** above to view their Marksheet and Analytics.")
    st.stop()

# Filter final dataset for the selected student AND semester
selected_roll = selected_student_label.split(" - ")[0]
sem_df = df[
    (df["Roll_No"].astype(str) == selected_roll) &
    (df["Semester"] == selected_semester)
].copy()

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
overall_status = "PASS" if active_backlogs == 0 else f" {active_backlogs} BACKLOG"

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

# --- 3. DETAILED SEMESTER MARKSHEET TABLE  ---
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

# --- 4. VISUAL PERFORMANCE ANALYTICS  ---
import altair as alt

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    with st.container(border=True):
        st.markdown("##### 🎯 Assessment Split by Subject (Max 100)")
        marks_melted = sem_df.melt(
            id_vars=["Subject"],
            value_vars=["Mid_Sem", "Assignments", "End_Sem"],
            var_name="Component",
            value_name="Marks"
        )
        marks_chart = (
            alt.Chart(marks_melted)
            .mark_bar()
            .encode(
                x=alt.X("Subject:N", title=None, axis=alt.Axis(labelAngle=-90)),
                y=alt.Y("Marks:Q", scale=alt.Scale(domain=[0, 100]), title="Marks (Out of 100)"),
                color=alt.Color("Component:N", title="Assessment")
            )
            .properties(height=320)
        )
        st.altair_chart(marks_chart, use_container_width=True)

with chart_col2:
    with st.container(border=True):
        st.markdown("##### 📅 Attendance Percentage by Subject (%)")
        att_chart = (
            alt.Chart(sem_df)
            .mark_bar(color="#7ab8ff")
            .encode(
                x=alt.X("Subject:N", title=None, axis=alt.Axis(labelAngle=-90)),
                y=alt.Y("Attendance:Q", scale=alt.Scale(domain=[0, 100]), title="Attendance (%)")
            )
            .properties(height=320)
        )
        st.altair_chart(att_chart, use_container_width=True)
# --- 5. GRADE DISTRIBUTION SUMMARY  ---
with st.container(border=True):
    st.markdown("##### 🏅 Letter Grade Tally (This Semester)")
    grade_counts = sem_df["Letter_Grade"].value_counts().reset_index()
    grade_counts.columns = ["Letter Grade", "Number of Subjects"]
    st.dataframe(grade_counts, use_container_width=True, hide_index=True)