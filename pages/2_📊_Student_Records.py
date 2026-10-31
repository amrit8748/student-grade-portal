import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Student Records | Grade Portal",
    page_icon="📊",
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

    /* Pill-Shaped Download Button Matching Mockup */
    [data-testid="stDownloadButton"] > button {
        background-color: #162a64 !important;
        color: #ffffff !important;
        border: 1.5px solid #7ab8ff !important;
        border-radius: 999px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        transition: 0.2s ease-in-out;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #1f3a8a !important;
        border-color: #a8c7fa !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE FILE PATH ---
CSV_FILE = "saved_grades.csv"

# --- PAGE HEADER BANNER ---
st.markdown("""
    <div class="dashboard-header">
        <h1>📊 Student and Course Records</h1>
        <p>Filter and search student course entries across branches and semesters</p>
    </div>
""", unsafe_allow_html=True)

# --- CHECK IF DATABASE EXISTS ---
if not os.path.exists(CSV_FILE):
    st.warning("⚠️ No grade records found yet! Please go to **Page 1 (Data Entry)** in the sidebar and save at least one student record first.")
    st.stop()

# Load master dataset
df = pd.read_csv(CSV_FILE)

if df.empty:
    st.warning("⚠️ The database is currently empty. Add student records on Page 1 to view the record.")
    st.stop()

# --- 1. SUMMARY BAR CONTAINER ---
# This keeps the summary bar visually at the top while allowing filters below to control its numbers
summary_container = st.container(border=True)

# --- 2. SEARCH & FILTER CONTROLS ---
with st.container(border=True):
    st.subheader("🔍 Filter Record")

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_query = st.text_input(
            "Search by Roll Number or Student Name",
            placeholder="e.g., 2026CS101 or Alex"
        )
    with f_col2:
        selected_branches = st.multiselect(
            "Branch / Degree",
            options=sorted(df["Branch"].dropna().unique()),
            default=[]
        )
    with f_col3:
        selected_semesters = st.multiselect(
            "Semester",
            options=sorted(df["Semester"].dropna().unique()),
            default=[]
        )

    f_col4, f_col5 = st.columns(2)
    with f_col4:
        selected_subjects = st.multiselect(
            "Subject",
            options=sorted(df["Subject"].dropna().unique()),
            default=[]
        )
    with f_col5:
        selected_status = st.multiselect(
            "Course Status",
            options=sorted(df["Status"].dropna().unique()),
            default=[]
        )

# --- 3. APPLY FILTERS TO DATAFRAME ---
filtered_df = df.copy()

# Text search (matches Roll_No or Student_Name case-insensitively)
if search_query.strip():
    q = search_query.strip()
    filtered_df = filtered_df[
        filtered_df["Roll_No"].astype(str).str.contains(q, case=False, na=False) |
        filtered_df["Student_Name"].astype(str).str.contains(q, case=False, na=False)
    ]

# Dropdown filters (only filter if user selects at least one option)
if selected_branches:
    filtered_df = filtered_df[filtered_df["Branch"].isin(selected_branches)]

if selected_semesters:
    filtered_df = filtered_df[filtered_df["Semester"].isin(selected_semesters)]

if selected_subjects:
    filtered_df = filtered_df[filtered_df["Subject"].isin(selected_subjects)]

if selected_status:
    filtered_df = filtered_df[filtered_df["Status"].isin(selected_status)]

# --- 4. POPULATE TOP DYNAMIC SUMMARY BAR (NESTED METRIC CARDS) ---
with summary_container:
    st.subheader("📌 Record Summary")
    
    total_unique_students = filtered_df["Roll_No"].nunique()
    total_subject_entries = len(filtered_df)
    passed_count = int((filtered_df["Status"] == "Pass").sum())
    backlog_fail_count = int((filtered_df["Status"] != "Pass").sum())

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("Total Unique Students", total_unique_students)
    with m2:
        with st.container(border=True):
            st.metric("Total Subject Entries", total_subject_entries)
    with m3:
        with st.container(border=True):
            st.metric("Passed Entries", passed_count)
    with m4:
        with st.container(border=True):
            st.metric("Backlog / Fails", backlog_fail_count)

# --- 5. MASTER DATA TABLE & EXPORT (CARD BOX) ---
with st.container(border=True):
    header_col, download_col = st.columns([3, 1])
    with header_col:
        st.subheader(f"📋 Filtered Records ({len(filtered_df)} entries)")
    with download_col:
        csv_export = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_export,
            file_name="filtered_student_record.csv",
            mime="text/csv",
            use_container_width=True
        )

    if filtered_df.empty:
        st.info("No matching records found for the active filters.")
    else:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )