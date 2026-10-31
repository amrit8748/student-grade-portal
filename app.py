import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="University Grade Portal",
    page_icon="🎓",
    layout="wide"
)

# --- DEFINE PAGES WITH CUSTOM SIDEBAR NAMES & ICONS ---
data_entry_page = st.Page(
    page="pages/1_Data_Entry.py", 
    title="Data Entry", 
    icon="📝", 
    default=True
)

record_page = st.Page(
    page="pages/2_📊_Student_Records.py", 
    title="Student Records", 
    icon="📊"
)

analytics_page = st.Page(
     page="pages/3_📈_Student_Analytics.py", 
     title="Analytics & Marksheet", 
     icon="📈"
 )

# --- SET UP NAVIGATION BAR ---
pg = st.navigation([data_entry_page, record_page, analytics_page])

# --- RUN THE SELECTED PAGE ---
pg.run()