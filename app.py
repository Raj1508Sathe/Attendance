import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ----------------------------------------
# PAGE CONFIG
# ----------------------------------------
st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# CSS — minimal, no complex HTML blocks
# ----------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
footer { display: none !important; }

html, body, .stApp {
    background: radial-gradient(circle at 20% 20%, #0c1a2e, #020617 60%) !important;
    color: #e2e8f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: rgba(6,182,212,0.04) !important;
    border-right: 1px solid rgba(6,182,212,0.15) !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

[data-testid="metric-container"] {
    background: rgba(6,182,212,0.06) !important;
    border: 1px solid rgba(6,182,212,0.2) !important;
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2rem !important;
    color: #06b6d4 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    letter-spacing: 1.5px !important;
    color: #64748b !important;
    text-transform: uppercase !important;
}

.stButton > button {
    background: rgba(6,182,212,0.08) !important;
    border: 1px solid rgba(6,182,212,0.3) !important;
    border-radius: 10px !important;
    color: #06b6d4 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(6,182,212,0.18) !important;
    border-color: #06b6d4 !important;
}

div[data-testid="stTextInput"] input {
    background: rgba(6,182,212,0.05) !important;
    border: 1px solid rgba(6,182,212,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(6,182,212,0.15) !important;
    border-radius: 12px !important;
}

.stRadio label { color: #94a3b8 !important; }
hr { border-color: rgba(6,182,212,0.15) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: rgba(6,182,212,0.04) !important;
    border-radius: 12px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 1.5px !important;
    border-radius: 10px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(6,182,212,0.15) !important;
    color: #06b6d4 !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# SESSION STATE
# ----------------------------------------
for key, val in [("authenticated", False), ("chat_history", []), ("students", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ----------------------------------------
# LOGIN
# ----------------------------------------
if not st.session_state.authenticated:
    st.markdown("""
        <h1 style='font-family:Orbitron,sans-serif;font-size:1.6rem;font-weight:900;
                   background:linear-gradient(135deg,#06b6d4,#8b5cf6);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   text-align:center;letter-spacing:3px;margin-top:4rem;'>
            ⬡ SMART ATTEND
        </h1>
        <p style='text-align:center;color:#475569;font-size:0.8rem;
                  letter-spacing:2px;margin-bottom:2rem;'>
            JSPM NTC · COMPUTER ENGINEERING
        </p>
    """, unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1, 1])
    with c:
        username = st.text_input("Username", placeholder="Enter username")
        pin      = st.text_input("PIN", type="password", placeholder="Enter PIN")
        if st.button("ENTER SYSTEM", use_container_width=True):
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
        scope  = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/drive"]
        creds  = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet  = client.open("Student_Attendance_System").get_worksheet(1)
        return pd.DataFrame(sheet.get_all_records())
    except Exception:
        return pd.DataFrame({
            "Name":       ["Atharva","Shravani","Janhavi","Vaishnavi",
                           "Anushka","Aditi","Raj","Om","Jaydip"],
            "Status":     ["Present","Absent","Present","Present",
                           "Absent","Present","Present","Present","Present"],
            "Scan_Count": [5, 2, 6, 7, 3, 5, 4, 1, 6],
            "Timestamp":  [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 9,
        })

if st.session_state.students is None:
    st.session_state.students = load_data().copy()

data         = st.session_state.students
STUDENT_LIST = ["Atharva","Shravani","Janhavi","Vaishnavi",
                "Anushka","Aditi","Raj","Om","Jaydip"]
df           = data[data["Name"].isin(STUDENT_LIST)].copy()

st_autorefresh(interval=30000, key="autorefresh")

# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.markdown("""
        <div style='text-align:center;padding:0.8rem 0;'>
            <span style='font-family:Orbitron,sans-serif;font-size:1rem;font-weight:900;
                         background:linear-gradient(135deg,#06b6d4,#8b5cf6);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         letter-spacing:2px;'>⬡ SMART ATTEND</span>
        </div>
    """, unsafe_allow_html=True)
    st.caption(f"🟢 ADMIN: RAJ  ·  {datetime.now().strftime('%d %b %Y  %H:%M')}")
    st.divider()
    if st.button("🔁  Reload Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.students = None
        st.rerun()
    st.download_button(
        "📤  Export CSV",
        data=df.to_csv(index=False),
        file_name=f"attendance_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.divider()
    if st.button("🚪  Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.students = None
        st.rerun()

# ----------------------------------------
# HEADER
# ----------------------------------------
st.markdown("""
    <h1 style='font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:900;
               background:linear-gradient(135deg,#06b6d4,#8b5cf6);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               text-align:center;letter-spacing:3px;margin-bottom:0.1rem;'>
        ⬡ COMPUTER ENGINEERING COMMAND CENTER
    </h1>
    <p style='text-align:center;color:#334155;font-size:0.72rem;
              letter-spacing:2px;margin-bottom:1.2rem;'>
        SMART ATTENDANCE · JSPM NTC · NARHE, PUNE
    </p>
""", unsafe_allow_html=True)

# ----------------------------------------
# COMPUTED STATS
# ----------------------------------------
present_n = int((df["Status"] == "Present").sum())
absent_n  = int((df["Status"] == "Absent").sum())
total_n   = len(df)
rate_n    = round(present_n / total_n * 100) if total_n else 0

# ----------------------------------------
# HELPER: donut chart
# ----------------------------------------
def make_donut(value, total, color, label):
    fig = go.Figure(go.Pie(
        values=[value, max(total - value, 0)],
        hole=0.72,
        marker_colors=[color, "rgba(255,255,255,0.04)"],
        textinfo="none",
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=8, b=8, l=8, r=8),
        height=150,
        annotations=[dict(
            text=f"<b>{value}</b>",
            x=0.5, y=0.5,
            font=dict(size=24, color=color, family="Orbitron"),
            showarrow=False,
        )],
    )
    return fig

# ----------------------------------------
# TABS
# ----------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "👥 Records", "📈 Analytics", "🤖 AI Assistant", "📍 Location"
])

# ══════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════
with tab1:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL STUDENTS",  total_n)
    k2.metric("PRESENT",         present_n)
    k3.metric("ABSENT",          absent_n)
    k4.metric("ATTENDANCE RATE", f"{rate_n}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Donut rings
    r1, r2, r3 = st.columns(3)
    with r1:
        st.plotly_chart(make_donut(present_n, total_n, "#06b6d4", "Present"),
                        use_container_width=True, key="d1")
        st.markdown("<p style='text-align:center;font-size:0.7rem;letter-spacing:2px;"
                    "color:#475569;'>PRESENT</p>", unsafe_allow_html=True)
    with r2:
        st.plotly_chart(make_donut(absent_n, total_n, "#f87171", "Absent"),
                        use_container_width=True, key="d2")
        st.markdown("<p style='text-align:center;font-size:0.7rem;letter-spacing:2px;"
                    "color:#475569;'>ABSENT</p>", unsafe_allow_html=True)
    with r3:
        st.plotly_chart(make_donut(rate_n, 100, "#10b981", "Rate"),
                        use_container_width=True, key="d3")
        st.markdown("<p style='text-align:center;font-size:0.7rem;letter-spacing:2px;"
                    "color:#475569;'>RATE %</p>", unsafe_allow_html=True)

    # Absent alerts
    absent_names = df[df["Status"] == "Absent"]["Name"].tolist()
    if absent_names:
        st.divider()
        st.markdown("**⚠ Absence Alerts**")
        acols = st.columns(len(absent_names))
        for i, name in enumerate(absent_names):
            acols[i].warning(f"⚠ {name}")

    st.divider()

    # Scan bar chart
    st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                "letter-spacing:2px;color:#06b6d4;'>SCAN ACTIVITY · TODAY</p>",
                unsafe_allow_html=True)
    bar_colors = ["#06b6d4" if s == "Present" else "#f87171" for s in df["Status"]]
    fig_bar = go.Figure(go.Bar(
        x=df["Name"], y=df["Scan_Count"],
        marker_color=bar_colors, marker_line_width=0,
        text=df["Scan_Count"], textposition="outside",
        textfont=dict(color="#94a3b8"),
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748b", family="Rajdhani"),
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
        height=240, bargap=0.4,
    )
    st.plotly_chart(fig_bar, use_container_width=True, key="bar")

# ══════════════════════════════════════════
# TAB 2 — RECORDS
# ══════════════════════════════════════════
with tab2:
    st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                "letter-spacing:2px;color:#06b6d4;'>STUDENT MONITORING HUB</p>",
                unsafe_allow_html=True)

    search   = st.text_input("Search", placeholder="Type student name...", label_visibility="collapsed")
    filtered = df[df["Name"].str.contains(search, case=False)] if search else df

    display_df = filtered[["Name","Status","Scan_Count","Timestamp"]].copy()
    display_df.columns = ["Name","Status","Scans","Last Seen"]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Scans": st.column_config.ProgressColumn(
                "Scan Count",
                min_value=0,
                max_value=int(df["Scan_Count"].max()) if not df.empty else 10,
                format="%d",
            ),
        },
    )

    st.divider()
    st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                "letter-spacing:2px;color:#06b6d4;'>MARK ATTENDANCE</p>",
                unsafe_allow_html=True)

    rows = [STUDENT_LIST[i:i+3] for i in range(0, len(STUDENT_LIST), 3)]
    for row in rows:
        cols = st.columns(3)
        for i, name in enumerate(row):
            match   = st.session_state.students["Name"] == name
            current = st.session_state.students.loc[match, "Status"].values
            if len(current):
                status = current[0]
                icon   = "✅" if status == "Present" else "❌"
                if cols[i].button(f"{icon} {name} ({status})",
                                  key=f"tog_{name}", use_container_width=True):
                    st.session_state.students.loc[match, "Status"] = (
                        "Absent" if status == "Present" else "Present"
                    )
                    st.rerun()

# ══════════════════════════════════════════
# TAB 3 — ANALYTICS
# ══════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                    "letter-spacing:2px;color:#06b6d4;'>WEEKLY TREND</p>",
                    unsafe_allow_html=True)
        days          = ["Mon","Tue","Wed","Thu","Fri","Sat","Today"]
        present_trend = [8, 7, 9, 6, 8, 7, present_n]
        absent_trend  = [1, 2, 0, 3, 1, 2, absent_n]
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=days, y=present_trend, name="Present",
            line=dict(color="#06b6d4", width=2),
            fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
            mode="lines+markers", marker=dict(size=6, color="#06b6d4"),
        ))
        fig_t.add_trace(go.Scatter(
            x=days, y=absent_trend, name="Absent",
            line=dict(color="#f87171", width=2, dash="dot"),
            fill="tozeroy", fillcolor="rgba(248,113,113,0.06)",
            mode="lines+markers", marker=dict(size=6, color="#f87171"),
        ))
        fig_t.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748b", family="Rajdhani"),
            legend=dict(orientation="h", y=1.15, x=0, font=dict(color="#94a3b8")),
            margin=dict(t=30, b=10, l=10, r=10), height=240,
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.07)", range=[0, 10]),
        )
        st.plotly_chart(fig_t, use_container_width=True, key="trend")

    with c2:
        st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                    "letter-spacing:2px;color:#06b6d4;'>DISTRIBUTION</p>",
                    unsafe_allow_html=True)
        fig_p = go.Figure(go.Pie(
            labels=["Present","Absent"],
            values=[present_n, absent_n],
            hole=0.70,
            marker=dict(
                colors=["rgba(6,182,212,0.75)","rgba(248,113,113,0.75)"],
                line=dict(color=["#06b6d4","#f87171"], width=2),
            ),
            textinfo="label+percent",
            textfont=dict(color="#94a3b8", family="Rajdhani"),
        ))
        fig_p.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748b"), showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10), height=240,
        )
        st.plotly_chart(fig_p, use_container_width=True, key="pie")

    st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                "letter-spacing:2px;color:#06b6d4;margin-top:0.5rem;'>SCAN LEADERBOARD</p>",
                unsafe_allow_html=True)
    top_df  = df.sort_values("Scan_Count", ascending=True)
    fig_top = go.Figure(go.Bar(
        x=top_df["Scan_Count"], y=top_df["Name"],
        orientation="h",
        marker=dict(
            color=top_df["Scan_Count"],
            colorscale=[[0,"rgba(139,92,246,0.5)"],[1,"rgba(6,182,212,0.9)"]],
            line_width=0,
        ),
        text=top_df["Scan_Count"], textposition="outside",
        textfont=dict(color="#94a3b8"),
    ))
    fig_top.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748b", family="Rajdhani"),
        margin=dict(t=10, b=10, l=10, r=10), height=280,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_top, use_container_width=True, key="lead")

# ══════════════════════════════════════════
# TAB 4 — AI ASSISTANT
# ══════════════════════════════════════════
with tab4:
    def ai_response(q, frame):
        ql = q.lower()
        if any(w in ql for w in ["location","college","campus","where"]):
            return "📍 JSPM NTC is in Narhe, Pune — 18.4485°N, 73.8275°E."
        if "who" in ql and "absent" in ql:
            names = frame[frame["Status"]=="Absent"]["Name"].tolist()
            return f"Currently absent: {', '.join(names)}." if names else "Nobody is absent! 🎉"
        if "who" in ql and "present" in ql:
            names = frame[frame["Status"]=="Present"]["Name"].tolist()
            return f"Currently present: {', '.join(names)}."
        if any(w in ql for w in ["rate","percentage","%"]):
            pct = round((frame["Status"]=="Present").sum() / len(frame) * 100)
            return f"Today's attendance rate is {pct}%."
        if any(w in ql for w in ["top","highest","most"]) and "scan" in ql:
            top = frame.sort_values("Scan_Count", ascending=False).iloc[0]
            return f"Highest scans: {top['Name']} with {int(top['Scan_Count'])} scans."
        if any(w in ql for w in ["summary","report","overview"]):
            p = (frame["Status"]=="Present").sum()
            a = (frame["Status"]=="Absent").sum()
            return f"Summary → Present: {p} | Absent: {a} | Rate: {round(p/len(frame)*100)}%"
        for name in frame["Name"].tolist():
            if name.lower() in ql:
                row = frame[frame["Name"].str.lower()==name.lower()].iloc[0]
                return f"{row['Name']} is {row['Status']} with {int(row['Scan_Count'])} scans today."
        return "Ask me: 'Who is absent?', 'Attendance rate?', a student name, or 'Give me a summary'."

    st.markdown("<p style='font-family:Orbitron,sans-serif;font-size:0.7rem;"
                "letter-spacing:2px;color:#06b6d4;'>AI ATTENDANCE ASSISTANT</p>",
                unsafe_allow_html=True)

    # Quick prompts
    qp_list = ["Who is absent?","Who is present?","Attendance rate?",
               "Top scanner?","Give me a summary","College location?"]
    qc = st.columns(3)
    for i, qp in enumerate(qp_list):
        if qc[i % 3].button(qp, key=f"qp_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role":"user","text":qp})
            st.session_state.chat_history.append({"role":"ai","text":ai_response(qp,df)})
            st.rerun()

    st.divid
/* Animated liquid blobs in background */
.stApp::before {
    content: '';
    position: fixed;
    top: -30%; left: -20%;
    width: 60vw; height: 60vw;
    background: radial-gradient(circle, rgba(6,182,212,0.07) 0%, transparent 70%);
    border-radius: 50%;
    animation: floatBlob 12s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: -20%; right: -10%;
    width: 50vw; height: 50vw;
    background: radial-gradient(circle, rgba(139,92,246,0.07) 0%, transparent 70%);
    border-radius: 50%;
    animation: floatBlob 16s ease-in-out infinite reverse;
    pointer-events: none;
    z-index: 0;
}
@keyframes floatBlob {
    0%, 100% { transform: translate(0,0) scale(1); }
    33%       { transform: translate(3vw,-2vh) scale(1.08); }
    66%       { transform: translate(-2vw,3vh) scale(0.94); }
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(6,182,212,0.04) !important;
    border-right: 1px solid rgba(6,182,212,0.15) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* Glass card utility */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(6,182,212,0.15);
    border-radius: 20px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.glass-card:hover { border-color: rgba(6,182,212,0.35); }

/* KPI metric cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: rgba(6,182,212,0.06);
    border: 1px solid rgba(6,182,212,0.18);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(6,182,212,0.4);
    background: rgba(6,182,212,0.12);
}
.kpi-val {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-label {
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    color: #64748b;
    text-transform: uppercase;
}
.kpi-cyan .kpi-val  { color: #06b6d4; }
.kpi-purple .kpi-val{ color: #8b5cf6; }
.kpi-green .kpi-val { color: #10b981; }
.kpi-amber .kpi-val { color: #f59e0b; }

/* Status pills */
.pill-present {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 12px; border-radius: 20px;
    background: rgba(16,185,129,0.12);
    color: #10b981;
    border: 1px solid rgba(16,185,129,0.25);
    font-size: 0.78rem; font-weight: 600; letter-spacing: 1px;
}
.pill-absent {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 12px; border-radius: 20px;
    background: rgba(248,113,113,0.12);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.25);
    font-size: 0.78rem; font-weight: 600; letter-spacing: 1px;
}
.dot-present {
    width: 6px; height: 6px;
    border-radius: 50%; background: #10b981;
    display: inline-block;
    animation: pulse 2s infinite;
}
.dot-absent { width:6px;height:6px;border-radius:50%;background:#f87171;display:inline-block; }
@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1);}
    50%{opacity:0.5;transform:scale(1.4);}
}

/* Alert badge */
.alert-warn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 10px;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: #f59e0b;
    font-size: 0.82rem; letter-spacing: 1px;
    margin: 4px;
}

/* Page title */
.page-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #06b6d4, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
    text-align: center;
    margin-bottom: 0.2rem;
}
.page-sub {
    text-align: center;
    color: #334155;
    font-size: 0.8rem;
    letter-spacing: 2px;
    margin-bottom: 2rem;
}

/* Card section title */
.card-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 2px;
    color: #06b6d4;
    margin-bottom: 1rem;
    text-transform: uppercase;
}

/* Student table */
.stu-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}
.stu-table th {
    text-align: left;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.62rem;
    letter-spacing: 2px;
    color: #475569;
    padding: 0 12px 10px;
    border-bottom: 1px solid rgba(6,182,212,0.1);
    text-transform: uppercase;
}
.stu-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    vertical-align: middle;
}
.stu-table tr:hover td { background: rgba(6,182,212,0.04); }

/* Avatar */
.avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.72rem; font-weight: 700;
}

/* Scan bar */
.scan-wrap { display:flex; align-items:center; gap:8px; }
.scan-bar {
    flex: 1; height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 10px; overflow: hidden;
}
.scan-fill {
    height: 100%; border-radius: 10px;
    background: linear-gradient(90deg, #06b6d4, #8b5cf6);
}

/* Chat */
.chat-bubble-ai {
    background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.2);
    border-radius: 16px 16px 16px 4px;
    padding: 10px 14px;
    color: #cbd5e1;
    font-size: 0.88rem;
    line-height: 1.5;
    margin-bottom: 10px;
    max-width: 85%;
}
.chat-bubble-user {
    background: linear-gradient(135deg, rgba(6,182,212,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    color: #e2e8f0;
    font-size: 0.88rem;
    line-height: 1.5;
    margin-bottom: 10px;
    max-width: 85%;
    margin-left: auto;
}
.ai-tag {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.62rem;
    color: #06b6d4;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

/* SVG ring animation */
.ring-circle { transition: stroke-dashoffset 1s ease; }

/* Streamlit widget overrides */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(6,182,212,0.05) !important;
    border: 1px solid rgba(6,182,212,0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,0.1) !important;
}
.stButton > button {
    background: linear-gradient(135deg, rgba(6,182,212,0.2), rgba(139,92,246,0.2)) !important;
    border: 1px solid rgba(6,182,212,0.35) !important;
    border-radius: 12px !important;
    color: #06b6d4 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 1.5px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(6,182,212,0.35), rgba(139,92,246,0.35)) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stSelectbox"] > div,
div[data-testid="stMultiSelect"] > div {
    background: rgba(6,182,212,0.05) !important;
    border: 1px solid rgba(6,182,212,0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}
.stRadio label { color: #cbd5e1 !important; }
[data-testid="metric-container"] {
    background: rgba(6,182,212,0.06) !important;
    border: 1px solid rgba(6,182,212,0.18) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "students" not in st.session_state:
    st.session_state.students = None

# ----------------------------------------
# LOGIN SCREEN
# ----------------------------------------
if not st.session_state.authenticated:
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;'>
        <div style='background:rgba(6,182,212,0.06);border:1px solid rgba(6,182,212,0.3);
                    border-radius:24px;padding:3rem 2.5rem;width:100%;max-width:400px;
                    backdrop-filter:blur(20px);'>
            <div style='font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;
                        color:#06b6d4;text-align:center;letter-spacing:2px;margin-bottom:0.3rem;'>
                ⬡ SMART ATTEND
            </div>
            <div style='text-align:center;color:#475569;font-size:0.8rem;letter-spacing:2px;margin-bottom:2rem;'>
                JSPM NTC · COMPUTER ENGINEERING
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("USERNAME", placeholder="Enter username")
        pin = st.text_input("PIN", type="password", placeholder="Enter PIN")
        if st.button("ENTER SYSTEM", use_container_width=True):
            if username == "Raj" and pin == "RAJ1508":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try again.")
    st.stop()

# ----------------------------------------
# DATA LOADING
# ----------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Student_Attendance_System").get_worksheet(1)
        return pd.DataFrame(sheet.get_all_records())
    except Exception:
        return pd.DataFrame({
            "Name": ["Atharva","Shravani","Janhavi","Vaishnavi",
                     "Anushka","Aditi","Raj","Om","Jaydip"],
            "Status": ["Present","Absent","Present","Present",
                       "Absent","Present","Present","Present","Present"],
            "Scan_Count": [5, 2, 6, 7, 3, 5, 4, 1, 6],
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 9
        })

# Load + persist editable student state
raw_data = load_data()
if st.session_state.students is None:
    st.session_state.students = raw_data.copy()

data = st.session_state.students
student_list = ["Atharva","Shravani","Janhavi","Vaishnavi",
                "Anushka","Aditi","Raj","Om","Jaydip"]
df_monitor = data[data["Name"].isin(student_list)].copy()

# ----------------------------------------
# AUTO REFRESH
# ----------------------------------------
st_autorefresh(interval=30000, key="autorefresh")

# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0;'>
        <div style='font-family:Orbitron,sans-serif;font-size:1.1rem;font-weight:900;
                    background:linear-gradient(135deg,#06b6d4,#8b5cf6);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    letter-spacing:2px;'>⬡ SMART ATTEND</div>
        <div style='color:#334155;font-size:0.72rem;letter-spacing:2px;margin-top:4px;'>
            JSPM NTC · CE DEPT
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:8px;background:rgba(6,182,212,0.08);
                border:1px solid rgba(6,182,212,0.2);border-radius:12px;padding:8px 12px;
                margin-bottom:1rem;'>
        <div style='width:8px;height:8px;background:#10b981;border-radius:50%;'></div>
        <span style='font-size:0.8rem;color:#06b6d4;letter-spacing:1px;'>ADMIN: RAJ</span>
    </div>
    <div style='color:#334155;font-size:0.72rem;letter-spacing:1px;margin-bottom:1.5rem;text-align:center;'>
        {datetime.now().strftime("%d %b %Y · %H:%M")}
    </div>
    """, unsafe_allow_html=True)

    view = st.radio(
        "NAVIGATION",
        ["📊 Overview", "👥 Records", "📈 Analytics", "🤖 AI Assistant", "📍 Location"],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("🔁 Reload Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.students = None
        st.rerun()

    if st.button("📤 Export CSV", use_container_width=True):
        csv = df_monitor.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv,
            file_name=f"attendance_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.students = None
        st.rerun()

# ----------------------------------------
# PAGE TITLE
# ----------------------------------------
st.markdown("""
<div class='page-title'>⬡ COMPUTER ENGINEERING COMMAND CENTER</div>
<div class='page-sub'>SMART ATTENDANCE · JSPM NTC · NARHE, PUNE</div>
""", unsafe_allow_html=True)

# ----------------------------------------
# COMPUTED STATS
# ----------------------------------------
present_count = df_monitor[df_monitor["Status"] == "Present"].shape[0]
absent_count  = df_monitor[df_monitor["Status"] == "Absent"].shape[0]
total_count   = len(df_monitor)
rate          = round((present_count / total_count) * 100) if total_count else 0
total_scans   = int(df_monitor["Scan_Count"].sum()) if "Scan_Count" in df_monitor else 0

# ----------------------------------------
# OVERVIEW TAB
# ----------------------------------------
if view == "📊 Overview":

    # KPI Cards
    st.markdown(f"""
    <div class='kpi-grid'>
        <div class='kpi-card kpi-cyan'>
            <div class='kpi-val'>{total_count}</div>
            <div class='kpi-label'>Total Students</div>
        </div>
        <div class='kpi-card kpi-green'>
            <div class='kpi-val'>{present_count}</div>
            <div class='kpi-label'>Present</div>
        </div>
        <div class='kpi-card kpi-amber'>
            <div class='kpi-val'>{absent_count}</div>
            <div class='kpi-label'>Absent</div>
        </div>
        <div class='kpi-card kpi-purple'>
            <div class='kpi-val'>{rate}%</div>
            <div class='kpi-label'>Attendance Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Attendance rings + absent alerts
    circ = 201
    ring_present_offset = round(circ * (1 - present_count / total_count)) if total_count else circ
    ring_absent_offset  = round(circ * (1 - absent_count  / total_count)) if total_count else circ

    absent_alerts = "".join([
        f"<span class='alert-warn'>⚠ {row['Name']} is Absent</span>"
        for _, row in df_monitor[df_monitor["Status"] == "Absent"].iterrows()
    ])

    st.markdown(f"""
    <div class='glass-card'>
        <div class='card-title'>Today's Attendance Overview</div>
        <div style='display:flex;justify-content:center;gap:3rem;flex-wrap:wrap;'>

            <div style='display:flex;flex-direction:column;align-items:center;gap:8px;'>
                <svg width="90" height="90" viewBox="0 0 90 90" style="transform:rotate(-90deg)">
                    <circle cx="45" cy="45" r="36" fill="none" stroke="rgba(6,182,212,0.12)" stroke-width="9"/>
                    <circle cx="45" cy="45" r="36" fill="none" stroke="#06b6d4" stroke-width="9"
                            stroke-linecap="round" stroke-dasharray="{circ}"
                            stroke-dashoffset="{ring_present_offset}" class="ring-circle"/>
                </svg>
                <div style='font-family:Orbitron,sans-serif;font-size:1.6rem;color:#06b6d4;font-weight:700;'>{present_count}</div>
                <div style='font-size:0.7rem;letter-spacing:2px;color:#475569;text-transform:uppercase;'>Present</div>
            </div>

            <div style='display:flex;flex-direction:column;align-items:center;gap:8px;'>
                <svg width="90" height="90" viewBox="0 0 90 90" style="transform:rotate(-90deg)">
                    <circle cx="45" cy="45" r="36" fill="none" stroke="rgba(248,113,113,0.12)" stroke-width="9"/>
                    <circle cx="45" cy="45" r="36" fill="none" stroke="#f87171" stroke-width="9"
                            stroke-linecap="round" stroke-dasharray="{circ}"
                            stroke-dashoffset="{ring_absent_offset}" class="ring-circle"/>
                </svg>
                <div style='font-family:Orbitron,sans-serif;font-size:1.6rem;color:#f87171;font-weight:700;'>{absent_count}</div>
                <div style='font-size:0.7rem;letter-spacing:2px;color:#475569;text-transform:uppercase;'>Absent</div>
            </div>

            <div style='display:flex;flex-direction:column;align-items:center;gap:8px;'>
                <svg width="90" height="90" viewBox="0 0 90 90" style="transform:rotate(-90deg)">
                    <circle cx="45" cy="45" r="36" fill="none" stroke="rgba(16,185,129,0.12)" stroke-width="9"/>
                    <circle cx="45" cy="45" r="36" fill="none" stroke="#10b981" stroke-width="9"
                            stroke-linecap="round" stroke-dasharray="{circ}"
                            stroke-dashoffset="{round(circ*(1-rate/100))}" class="ring-circle"/>
                </svg>
                <div style='font-family:Orbitron,sans-serif;font-size:1.6rem;color:#10b981;font-weight:700;'>{rate}%</div>
                <div style='font-size:0.7rem;letter-spacing:2px;color:#475569;text-transform:uppercase;'>Rate</div>
            </div>

        </div>
        <div style='margin-top:1.5rem;display:flex;flex-wrap:wrap;gap:4px;'>{absent_alerts}</div>
    </div>
    """, unsafe_allow_html=True)

    # Scan activity chart
    st.markdown("<div class='glass-card'><div class='card-title'>Scan Activity · Today</div>", unsafe_allow_html=True)
    bar_colors = ["#06b6d4" if s == "Present" else "#f87171"
                  for s in df_monitor["Status"]]
    fig_bar = go.Figure(go.Bar(
        x=df_monitor["Name"],
        y=df_monitor["Scan_Count"],
        marker_color=bar_colors,
        marker_line_width=0,
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748b", family="Rajdhani"),
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
        height=220,
        bargap=0.35,
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# RECORDS TAB
# ----------------------------------------
elif view == "👥 Records":

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Student Monitoring Hub</div>", unsafe_allow_html=True)

    search = st.text_input("Search student...", placeholder="Type a name...", label_visibility="collapsed")
    filtered = df_monitor[df_monitor["Name"].str.contains(search, case=False)] if search else df_monitor

    max_scans = df_monitor["Scan_Count"].max() if not df_monitor.empty else 1

    avatar_colors = [
        ("rgba(6,182,212,0.2)","#06b6d4"),
        ("rgba(139,92,246,0.2)","#8b5cf6"),
        ("rgba(16,185,129,0.2)","#10b981"),
        ("rgba(245,158,11,0.2)","#f59e0b"),
        ("rgba(248,113,113,0.2)","#f87171"),
    ]

    rows_html = ""
    for i, (_, row) in enumerate(filtered.iterrows()):
        bg, col = avatar_colors[i % len(avatar_colors)]
        initials = row["Name"][:2].upper()
        pct = int((row["Scan_Count"] / max_scans) * 100) if max_scans else 0
        pill = (f"<span class='pill-present'><span class='dot-present'></span>PRESENT</span>"
                if row["Status"] == "Present"
                else f"<span class='pill-absent'><span class='dot-absent'></span>ABSENT</span>")
        rows_html += f"""
        <tr>
            <td>
                <div style='display:flex;align-items:center;gap:10px;'>
                    <div class='avatar' style='background:{bg};color:{col};'>{initials}</div>
                    <span>{row['Name']}</span>
                </div>
            </td>
            <td>{pill}</td>
            <td>
                <div class='scan-wrap'>
                    <div class='scan-bar'><div class='scan-fill' style='width:{pct}%'></div></div>
                    <span style='font-family:Orbitron,sans-serif;font-size:0.72rem;color:#475569;min-width:16px;text-align:right;'>{int(row['Scan_Count'])}</span>
                </div>
            </td>
            <td style='color:#475569;font-size:0.8rem;'>{row.get('Timestamp','—')}</td>
        </tr>"""

    st.markdown(f"""
    <table class='stu-table'>
        <thead><tr>
            <th>Student</th><th>Status</th><th>Scan Count</th><th>Last Seen</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Live toggle attendance
    st.markdown("<div class='glass-card'><div class='card-title'>Mark Attendance</div>", unsafe_allow_html=True)
    cols = st.columns(len(student_list))
    for i, name in enumerate(student_list):
        with cols[i]:
            match = st.session_state.students["Name"] == name
            current = st.session_state.students.loc[match, "Status"].values
            if len(current):
                status = current[0]
                label = "✓ Present" if status == "Present" else "✗ Absent"
                if st.button(f"{name}\n{label}", key=f"tog_{name}", use_container_width=True):
                    new_status = "Absent" if status == "Present" else "Present"
                    st.session_state.students.loc[match, "Status"] = new_status
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# ANALYTICS TAB
# ----------------------------------------
elif view == "📈 Analytics":

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'><div class='card-title'>Weekly Attendance Trend</div>", unsafe_allow_html=True)
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Today"]
        present_trend = [8,7,9,6,8,7,present_count]
        absent_trend  = [1,2,0,3,1,2,absent_count]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=days, y=present_trend, name="Present",
            line=dict(color="#06b6d4", width=2),
            fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
            mode="lines+markers", marker=dict(size=6)
        ))
        fig_trend.add_trace(go.Scatter(
            x=days, y=absent_trend, name="Absent",
            line=dict(color="#f87171", width=2, dash="dot"),
            fill="tozeroy", fillcolor="rgba(248,113,113,0.06)",
            mode="lines+markers", marker=dict(size=6)
        ))
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748b", family="Rajdhani"),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color="#94a3b8")),
            margin=dict(t=30,b=10,l=10,r=10), height=220,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.07)", range=[0,10])
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'><div class='card-title'>Attendance Distribution</div>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["Present","Absent"],
            values=[present_count, absent_count],
            hole=0.72,
            marker=dict(
                colors=["rgba(6,182,212,0.75)","rgba(248,113,113,0.75)"],
                line=dict(color=["#06b6d4","#f87171"], width=2)
            ),
            textinfo="label+percent",
            textfont=dict(color="#94a3b8", family="Rajdhani")
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748b", family="Rajdhani"),
            legend=dict(font=dict(color="#94a3b8")),
            margin=dict(t=10,b=10,l=10,r=10), height=220,
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Top performers
    st.markdown("<div class='glass-card'><div class='card-title'>Scan Leaderboard</div>", unsafe_allow_html=True)
    top_df = df_monitor.sort_values("Scan_Count", ascending=False).head(5)
    fig_top = go.Figure(go.Bar(
        x=top_df["Scan_Count"], y=top_df["Name"],
        orientation="h",
        marker=dict(
            color=top_df["Scan_Count"],
            colorscale=[[0,"rgba(139,92,246,0.5)"],[1,"rgba(6,182,212,0.9)"]],
            line_width=0
        )
    ))
    fig_top.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748b", family="Rajdhani"),
        margin=dict(t=10,b=10,l=10,r=10), height=220,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_top, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# AI ASSISTANT TAB
# ----------------------------------------
elif view == "🤖 AI Assistant":

    def get_ai_response(q, df):
        ql = q.lower()
        if "location" in ql or "college" in ql or "campus" in ql:
            return "📍 JSPM NTC is in Narhe, Pune at 18.4485°N, 73.8275°E — a premier Computer Engineering institute."
        if "absent" in ql and "who" in ql:
            names = df[df["Status"]=="Absent"]["Name"].tolist()
            return f"Currently absent: {', '.join(names)}." if names else "No one is absent right now!"
        if "present" in ql and "who" in ql:
            names = df[df["Status"]=="Present"]["Name"].tolist()
            return f"Currently present: {', '.join(names)}."
        if "rate" in ql or "percentage" in ql:
            p = df[df["Status"]=="Present"].shape[0]
            pct = round(p / len(df) * 100)
            return f"Today's attendance rate is {pct}%."
        if "scan" in ql and ("top" in ql or "most" in ql or "highest" in ql):
            top = df.sort_values("Scan_Count", ascending=False).iloc[0]
            return f"Highest scans: {top['Name']} with {int(top['Scan_Count'])} scans."
        if "total" in ql and "scan" in ql:
            return f"Total scans recorded today: {int(df['Scan_Count'].sum())}."
        if "summary" in ql or "report" in ql:
            p = df[df["Status"]=="Present"].shape[0]
            a = df[df["Status"]=="Absent"].shape[0]
            return f"Today's summary — Present: {p}, Absent: {a}, Rate: {round(p/len(df)*100)}%."
        for name in df["Name"].tolist():
            if name.lower() in ql:
                row = df[df["Name"].str.lower()==name.lower()].iloc[0]
                return f"{row['Name']} is currently **{row['Status']}** with {int(row['Scan_Count'])} scans today."
        return "I can answer about student status, scan counts, absence alerts, rate, or campus location. Try: 'Who is absent?' or 'What is the attendance rate?'"

    st.markdown("<div class='glass-card'><div class='card-title'>AI Attendance Assistant</div>", unsafe_allow_html=True)

    # Chat history
    chat_html = ""
    for msg in st.session_state.chat_history:
        if msg["role"] == "ai":
            chat_html += f"<div class='ai-tag'>AI ASSISTANT</div><div class='chat-bubble-ai'>{msg['text']}</div>"
        else:
            chat_html += f"<div class='chat-bubble-user'>{msg['text']}</div>"

    if not chat_html:
        chat_html = "<div class='ai-tag'>AI ASSISTANT</div><div class='chat-bubble-ai'>Hello! Ask me about any student's status, scan count, absence alerts, or campus location.</div>"

    st.markdown(f"<div style='max-height:300px;overflow-y:auto;padding-right:6px;'>{chat_html}</div>", unsafe_allow_html=True)

    query = st.text_input("Ask your assistant...", placeholder="e.g. Who is absent? / What is the rate?", label_visibility="collapsed")
    if st.button("SEND →", use_container_width=True) and query:
        st.session_state.chat_history.append({"role":"user","text":query})
        response = get_ai_response(query, df_monitor)
        st.session_state.chat_history.append({"role":"ai","text":response})
        st.rerun()

    if st.button("Clear Chat", use_container_width=False):
        st.session_state.chat_history = []
        st.rerun()

    # Quick prompts
    st.markdown("<div style='margin-top:0.8rem;display:flex;flex-wrap:wrap;gap:6px;'>", unsafe_allow_html=True)
    quick_prompts = ["Who is absent?","Attendance rate?","Top scanner?","Give me a summary"]
    qcols = st.columns(len(quick_prompts))
    for i, qp in enumerate(quick_prompts):
        with qcols[i]:
            if st.button(qp, key=f"qp_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","text":qp})
                st.session_state.chat_history.append({"role":"ai","text":get_ai_response(qp, df_monitor)})
                st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# ----------------------------------------
# LOCATION TAB
# ----------------------------------------
elif view == "📍 Location":

    st.markdown("""
    <div class='glass-card'>
        <div class='card-title'>College Location · JSPM NTC</div>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;'>
            <div class='kpi-card kpi-cyan' style='text-align:center;'>
                <div style='font-family:Orbitron,sans-serif;font-size:0.75rem;color:#06b6d4;margin-bottom:4px;'>LATITUDE</div>
                <div style='font-size:1.1rem;font-weight:600;'>18.4485° N</div>
            </div>
            <div class='kpi-card kpi-purple' style='text-align:center;'>
                <div style='font-family:Orbitron,sans-serif;font-size:0.75rem;color:#8b5cf6;margin-bottom:4px;'>LONGITUDE</div>
                <div style='font-size:1.1rem;font-weight:600;'>73.8275° E</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.map(pd.DataFrame({"lat": [18.4485], "lon": [73.8275]}), zoom=15)
