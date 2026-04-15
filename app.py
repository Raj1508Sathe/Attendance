import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh 

# ----------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------
st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# CUSTOM UI: CYBERPUNK DARK THEME + GLASSMORPHISM
# ----------------------------------------
st.markdown("""
    <style>
    [data-testid="stStatusWidget"] {display: none !important;}
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #e0e0e0;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .floating-chatbot {
        position: fixed;
        bottom: 80px;
        right: 30px;
        width: 300px;
        background: rgba(15, 23, 42, 0.95);
        border-radius: 15px;
        padding: 15px;
        z-index: 10000;
        border: 1px solid #00ffff;
        box-shadow: 0 0 15px rgba(0,255,255,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# SESSION MANAGEMENT
# ----------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Smart Attendance System Login")
    username = st.text_input("Username")
    pin = st.text_input("PIN", type="password")
    
    if st.button("Login"):
        if username == "Raj" and pin == "RAJ1508":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")
    st.stop()

# ----------------------------------------
# DATA LOADING
# ----------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Student_Attendance_System").get_worksheet(1)
        return pd.DataFrame(sheet.get_all_records())
    except:
        # Emergency Demo Data
        return pd.DataFrame({
            "Name": ["Atharva", "Shravani", "Janhavi", "Vaishnavi", "Anushka", "Aditi", "Raj", "Om", "Jaydip"],
            "Status": ["Present", "Absent", "Present", "Present", "Absent", "Present", "Present", "Present", "Present"],
            "Scan_Count": [5, 2, 6, 7, 3, 5, 4, 1, 6],
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 9
        })

st_autorefresh(interval=10000, key="datarefresh")
data = load_data()

# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.markdown(f"### 🛡 Admin: {st.session_state.get('username', 'Raj')}")
    st.success("System: **Online** 🟢")
    st.divider()
    view = st.radio("Choose View", ["📝 Students Record", "📍 College Location"])
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ----------------------------------------
# MAIN DASHBOARD
# ----------------------------------------
st.markdown(f"<h1 style='text-align:center; color:#00ffff;'>Computer Engineering Command Center</h1>", unsafe_allow_html=True)

# Monitoring Hub (Friends word removed)
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("👥 Student Monitoring Hub")

student_list = ["Atharva", "Shravani", "Janhavi", "Vaishnavi", "Anushka", "Aditi", "Raj", "Om", "Jaydip"]
df_monitor = data[data["Name"].isin(student_list)]

if not df_monitor.empty:
    summary = df_monitor.groupby("Name").agg({"Status": "last", "Scan_Count": "sum"}).reset_index()
    st.table(summary)
else:
    st.warning("No monitoring data available currently.")
st.markdown("</div>", unsafe_allow_html=True)

# KPI Metrics
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
total_logs = len(data)
active_count = df_monitor[df_monitor["Status"] == "Present"].shape[0]
iot_health = "🟢 Optimal" if active_count > 4 else "🟡 Moderate"

col1.metric("📊 Total Logs", total_logs)
col2.metric("👥 Active Students", active_count)
col3.metric("🤖 IoT Health", iot_health)
st.markdown("</div>", unsafe_allow_html=True)

# Area Chart
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
chart_data = data.copy()
chart_data["Timestamp"] = pd.to_datetime(chart_data["Timestamp"], errors="coerce")
chart_data = chart_data.groupby(chart_data["Timestamp"].dt.minute)["Name"].count().reset_index()
chart_data.rename(columns={"Name": "Check-ins", "Timestamp": "Minute"}, inplace=True)
fig = px.area(chart_data, x="Minute", y="Check-ins", template="plotly_dark", color_discrete_sequence=["#00ffff"])
fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, width='stretch')
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# SIDEBAR NAVIGATION LOGIC
# ----------------------------------------
if view == "📝 Students Record":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.dataframe(data, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)
elif view == "📍 College Location":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.map(pd.DataFrame({"lat": [18.4485], "lon": [73.8275]}))
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# FLOATING AI CHATBOT (Friends word removed)
# ----------------------------------------
query = st.chat_input("Ask your AI Assistant about attendance or location...")
if query:
    response = ""
    query_lower = query.lower()

    if "location" in query_lower or "college" in query_lower:
        response = "📍 JSPM NTC is in Narhe, Pune (18.4485, 73.8275). It's a premier institute for Engineering."
    else:
        for name in student_list:
            if name.lower() in query_lower:
                record = df_monitor[df_monitor["Name"].str.contains(name, case=False, na=False)]
                if not record.empty:
                    status = record["Status"].iloc[-1]
                    scans = record["Scan_Count"].iloc[-1]
                    response = f"{name} is currently **{status}** with {scans} scans recorded."
                else:
                    response = f"No attendance record found for {name}."
                break

    if response == "":
        response = "🤖 Sorry, I can answer only about Narhe campus or student attendance."
    
    st.markdown(f"""
        <div class='floating-chatbot'>
            <b style='color:#00ffff;'>🤖 AI Assistant:</b><br>
            <span style='color:white;'>{response}</span>
        </div>
    """, unsafe_allow_html=True)
