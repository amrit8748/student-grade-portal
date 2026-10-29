import streamlit as st
import pandas as pd
import os
from catalog_data import COURSE_CATALOG

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Data Entry | Grade Portal",
    page_icon="📝",
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

    /* Pill-Shaped Submit Button Matching Mockup */
    .stButton > button {
        background-color: #162a64 !important;
        color: #ffffff !important;
        border: 1.5px solid #7ab8ff !important;
        border-radius: 999px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #1f3a8a !important;
        border-color: #a8c7fa !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE FILE PATH ---
CSV_FILE = "saved_grades.csv"

# --- HELPER FUNCTION: 10-POINT GRADING ENGINE ---
def calculate_grade_and_points(marks):
    if marks >= 90:
        return "O", 10
    elif marks >= 80:
        return "A+", 9
    elif marks >= 70:
        return "A", 8
    elif marks >= 60:
        return "B+", 7
    elif marks >= 50:
        return "B", 6
    elif marks >= 40:
        return "P", 5
    else:
        return "F", 0

# --- CENTER-ALIGNED PAGE HEADER BANNER ---
st.markdown("""
    <div class="dashboard-header">
        <h1>🎓 Grade Management Portal — Student Marks & Course Entry</h1>
        <p>Select a student's branch and semester to dynamically load their curriculum and enter marks</p>
    </div>
""", unsafe_allow_html=True)

# --- DATA ENTRY PANEL (REACTIVE CARD BOXES) ---
with st.container(border=True):
    top_box1, top_box2 = st.columns([2, 1])
    
    # Box 1: Student Details
    with top_box1:
        with st.container(border=True):
            st.markdown("#### 👤 Student Details")
            col1, col2 = st.columns(2)
            with col1:
                roll_no = st.text_input("Registration / Roll Number", placeholder="e.g., 2026CS101")
                student_name = st.text_input("Student Full Name", placeholder="e.g., Alex Johnson")
            with col2:
                branch = st.selectbox(
                    "Branch / Degree",
                    options=list(COURSE_CATALOG.keys())
                )
                semester = st.selectbox(
                    "Semester",
                    options=list(COURSE_CATALOG[branch].keys())
                )

    # Box 2: Dynamic Course Selection & Attendance
    with top_box2:
        with st.container(border=True):
            st.markdown("#### 📚 Course & Attendance")
            available_courses = COURSE_CATALOG[branch][semester]
            selected_course_label = st.selectbox(
                f"Select Subject ({branch} • {semester})",
                options=list(available_courses.keys())
            )
            attendance = st.slider(
                "Attendance Percentage (%)",
                min_value=0,
                max_value=100,
                value=85,
                help="Minimum 75% attendance is required to pass the course."
            )

    # Box 3: Performance Metrics
    with st.container(border=True):
        st.markdown("#### 📊 Performance Metrics (Out of 100)")
        col3, col4, col5 = st.columns(3)
        with col3:
            mid_sem = st.number_input("Mid-Sem Exam (Max 30)", min_value=0.0, max_value=30.0, value=22.0, step=0.5)
        with col4:
            assignments = st.number_input("Continuous Evaluation / Quizzes (Max 20)", min_value=0.0, max_value=20.0, value=16.0, step=0.5)
        with col5:
            end_sem = st.number_input("End-Sem Exam (Max 50)", min_value=0.0, max_value=50.0, value=40.0, step=0.5)

    # Submit Button
    submitted = st.button("💾 Calculate Grade & Save to Database", use_container_width=True)

# --- PROCESSING & CSV STORAGE LOGIC ---
if submitted:
    if not roll_no.strip() or not student_name.strip():
        st.error("⚠️ Please enter both the Registration/Roll Number and Student Full Name.")
    else:
        # 1. Unpack Subject Name, Course Type, and Credits from the nested catalog
        subject_name, course_type, credits = COURSE_CATALOG[branch][semester][selected_course_label]

        # 2. Compute Marks, Grade, and Credit Points
        total_marks = round(mid_sem + assignments + end_sem, 2)
        letter_grade, grade_point = calculate_grade_and_points(total_marks)
        credit_points = grade_point * credits

        # 3. Determine Course Status
        if attendance < 75:
            status = "Detained (Low Attendance)"
        elif letter_grade == "F":
            status = "Fail / Backlog"
        else:
            status = "Pass"

        # 4. Prepare Record Dictionary
        clean_roll = roll_no.strip().upper()
        new_record = {
            "Roll_No": clean_roll,
            "Student_Name": student_name.strip().title(),
            "Branch": branch,
            "Semester": semester,
            "Subject": subject_name,
            "Course_Type": course_type,
            "Credits": credits,
            "Mid_Sem": mid_sem,
            "Assignments": assignments,
            "End_Sem": end_sem,
            "Total_Marks": total_marks,
            "Letter_Grade": letter_grade,
            "Grade_Point": grade_point,
            "Credit_Points": credit_points,
            "Attendance": attendance,
            "Status": status
        }

        # 5. Save or Update in CSV
        if not os.path.exists(CSV_FILE):
            df = pd.DataFrame([new_record])
            df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Created database and saved **{subject_name}** record for **{new_record['Student_Name']}** ({clean_roll})!")
        else:
            df = pd.read_csv(CSV_FILE)
            
            # Check if this student already has a grade entered for this exact subject
            duplicate_mask = (df["Roll_No"].astype(str) == clean_roll) & (df["Subject"] == subject_name)
            
            if duplicate_mask.any():
                # Update existing subject record for that student instead of creating a duplicate row
                for key, val in new_record.items():
                    df.loc[duplicate_mask, key] = val
                df.to_csv(CSV_FILE, index=False)
                st.info(f"🔄 Updated existing **{subject_name}** record for **{new_record['Student_Name']}** ({clean_roll}).")
            else:
                # Append brand new record
                df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success(f"✅ Saved **{subject_name}** record for **{new_record['Student_Name']}** ({clean_roll})!")

        # 6. Instant Summary Card (Nested Metric Cards Matching Mockup)
        with st.container(border=True):
            st.markdown("#### 📌 Calculated Result Summary")
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                with st.container(border=True):
                    st.metric("Course Type", f"{course_type} ({credits} Cr)")
            with m2:
                with st.container(border=True):
                    st.metric("Total Score", f"{total_marks} / 100")
            with m3:
                with st.container(border=True):
                    st.metric("Letter Grade", letter_grade)
            with m4:
                with st.container(border=True):
                    st.metric("Credit Points", f"{credit_points} pts")
            with m5:
                with st.container(border=True):
                    st.metric("Course Status", status)