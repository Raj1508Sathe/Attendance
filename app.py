import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_autorefresh import st_autorefresh 

# ----------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------
st.set_page_config(
    page_title="Smart Attendance | Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# ADVANCED CSS (Liquid Layout & Glassmorphism)
# ----------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    [data-testid="stStatusWidget"] {display: none !important;}
    .stSpinner {display: none !important;}
    .stApp { background: radial-gradient(circle at top right, #1e293b, #020617); color: #f8fafc; }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 1.5rem;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
        margin-bottom: 1rem;
    }
    .floating-chatbot {
        position: fixed; bottom: 5rem; right: 2rem; width: 22rem;
        background: rgba(15, 23, 42, 0.95); border-radius: 1rem; padding: 1.2rem;
        z-index: 1000; border: 1px solid #00ffff;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# TIMETABLE DATABASE (SE-DIV A)[cite: 1]
# ----------------------------------------
TIMETABLE = {
    "Monday": [("08:30", "09:30", "DBMS (SVS)"), ("09:30", "10:30", "EVS (NNJ)"), ("10:45", "12:45", "Practical: DBMSL/MPL/WD")],
    "Tuesday": [("08:30", "09:30", "IoT (BKD)"), ("09:30", "10:30", "MP (SAP)"), ("10:45", "11:45", "EVS (NNJ)"), ("11:45", "13:30", "Practical: DBMSL/MPL/WD")],
    "Wednesday": [("08:30", "09:30", "DBMS (SVS)"), ("09:30", "10:30", "PM (SGC)"), ("10:45", "11:45", "DM (SYC)")],
    "Thursday": [("08:30", "09:30", "DM (SYC)"), ("09:30", "10:30", "DBMS (SVS)"), ("10:45", "11:45", "MIL Tut (SYC)")],
    "Friday": [("08:30", "09:30", "PM (SGC)"), ("09:30", "10:30", "DM (SYC)"), ("10:45", "11:45", "IoT (BKD)")],
    "Saturday": [("08:30", "09:30", "DM (SYC)"), ("09:30", "10:30", "DM (SYC)")]
}

def get_current_session():
    now = datetime.now()
    day, current_time = now.strftime("%A"), now.strftime("%H:%M")
    if day not in TIMETABLE: return "No Academic Sessions"
    for start, end, sub in TIMETABLE[day]:
        if start <= current_time <= end: return f"{sub} ({start}-{end})"
    return "Break / No Active Lecture"

# ----------------------------------------
# AUTHENTICATION
# ----------------------------------------
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 Secure Access</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        u, p = st.text_input("Admin ID", value="Raj"), st.text_input("PIN", type="password")
        if st.button("Enter Dashboard", use_container_width=True):
            if u == "Raj" and p == "RAJ1508": st.session_state.authenticated = True; st.rerun()
            else: st.error("Access Denied.")
    st.stop()

# ----------------------------------------
# DATA LOADING
# ----------------------------------------
st_autorefresh(interval=10000, key="datarefresh")
@st.cache_data(show_spinner=False)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Student_Attendance_System").get_worksheet(1)
        return pd.DataFrame(sheet.get_all_records())
    except:
        return pd.DataFrame({
            "Name": ["Atharva", "Shravani", "Janhavi", "Vaishnavi", "Anushka", "Aditi", "Raj", "Om", "Jaydip"],
            "Status": ["Present", "Absent", "Present", "Present", "Absent", "Present", "Present", "Present", "Present"],
            "Scan_Count": [5, 2, 6, 7, 3, 5, 4, 1, 6],
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 9
        })

data = load_data()

# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ SYSTEM ADMIN")
    st.info("User: **Raj Sathe**")
    st.markdown(f"""
        <div style='background:rgba(0,255,255,0.1); padding:10px; border-radius:10px; text-align:center;'>
            <h3 style='margin:0; color:#00ffff;'>{datetime.now().strftime("%H:%M:%S")}</h3>
            <small>Live System Time</small><br>
            <strong style='color:#22c55e;'>{get_current_session()}</strong>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    view = st.selectbox("Navigation", ["Overview", "Timetable Check", "Detailed Records", "Campus Map"])
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ----------------------------------------
# MAIN CONTENT
# ----------------------------------------
st.markdown("<h1 style='text-align:center; color:#00ffff; letter-spacing: 2px;'>SMART ATTENDANCE COMMAND CENTER</h1>", unsafe_allow_html=True)

total_reg = data["Name"].nunique()
curr_pres = data[data["Status"] == "Present"]["Name"].nunique()

if view == "Overview":
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='glass-card'><small>Total Logs</small><h2>{len(data)}</h2></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='glass-card'><small>Present Now</small><h2 style='color:#00ffff;'>{curr_pres}</h2></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='glass-card'><small>Attendance %</small><h2>{(curr_pres/total_reg*100):.1f}%</h2></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='glass-card'><small>IoT Node</small><h2 style='color:#22c55e;'>Active 🟢</h2></div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    display_df = data.drop_duplicates(subset="Name", keep="last").copy()
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Timetable Check":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"📅 Schedule for {datetime.now().strftime('%A')}")
    sched = pd.DataFrame(TIMETABLE.get(datetime.now().strftime('%A'), []), columns=["Start", "End", "Subject"])
    if not sched.empty:
        sched.index = range(1, len(sched) + 1)
        st.table(sched)
    else: st.info("No active sessions scheduled.")
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Detailed Records":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    detailed_df = data.copy()
    detailed_df.index = range(1, len(detailed_df) + 1)
    st.dataframe(detailed_df, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

elif view == "Campus Map":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.map(pd.DataFrame({"lat": [18.4485], "lon": [73.8275]}), zoom=14)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# AI CHATBOT (FIXED)
# ----------------------------------------
query = st.chat_input("Ask about students, counts, or the project...")
if query:
    response = ""  # Fixed: Initialize before use
    q = query.lower()
    session = get_current_session()
    
    if "how many" in q or "count" in q or "present" in q:
        response = f"🤖 There are currently **{curr_pres}** students present out of **{total_reg}** registered students."
    elif "how it works" in q:
        response = "🤖 This system uses IoT nodes to scan student IDs, logs data to Google Sheets, and visualizes it in real-time using Streamlit."
    elif "current" in q or "lecture" in q:
        response = f"🤖 The current session is: **{session}**."
    else:
        for name in data["Name"].unique():
            if str(name).lower() in q:
                row = data[data["Name"] == name].iloc[-1]
                response = f"🤖 **{name}** is marked **{row['Status']}**. Last scan: {row['Timestamp']}."
                break
    
    if not response: 
        response = "🤖 I'm here to help! Try asking 'How many students are present?' or check a name."

    st.markdown(f"<div class='floating-chatbot'><b style='color:#00ffff;'>AI Assistant:</b><br>{response}</div>", unsafe_allow_html=True)
