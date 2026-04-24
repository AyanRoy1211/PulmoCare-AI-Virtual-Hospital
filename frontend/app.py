import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.styles import PULMOCARE_CSS, render_sidebar, confidence_bar
from utils.api_client import login, register, get_me, get_patient_sessions

st.set_page_config(
    page_title="PulmoCare AI",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)


# ── Session Init ──────────────────────────────────────────────────────────────
for key in ["access_token", "user", "session_id", "xray_result",
            "cough_result", "scribe_context", "prescription_data"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ── Auth Gate ─────────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 0 2rem 0;">
            <div style="font-size:42px; font-weight:900; color:#1D4ED8;
                        letter-spacing:-0.04em; margin-bottom:6px;">
                Pulmo<span style="color:#0F172A;">Care</span>
                <span style="color:#3B82F6; font-size:22px;">AI</span>
            </div>
            <div style="font-size:14px; color:#64748B; margin-bottom:2rem;">
                AI-Powered Virtual Hospital Platform
            </div>
            <span class="pc-hipaa">🔒 HIPAA Compliant &nbsp;•&nbsp; Secure Session</span>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["Sign In", "Register"])

        with tab_login:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            email    = st.text_input("Email", placeholder="doctor@hospital.com", key="li_email")
            password = st.text_input("Password", type="password", key="li_pass")
            if st.button("Sign In", type="primary", use_container_width=True):
                try:
                    data = login(email, password)
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user = {
                        "id": data["user_id"],
                        "full_name": data["full_name"],
                        "role": data["role"]
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

            st.markdown("""
            <div style="text-align:center; margin-top:12px; font-size:12px; color:#94A3B8;">
                Demo credentials: demo@pulmocare.ai / demo1234
            </div>
            """, unsafe_allow_html=True)

        with tab_reg:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: r_name  = st.text_input("Full Name",  key="rg_name")
            with c2: r_role  = st.selectbox("Role", ["patient", "doctor"], key="rg_role")
            r_email = st.text_input("Email", key="rg_email")
            r_pass  = st.text_input("Password", type="password", key="rg_pass")
            c3, c4  = st.columns(2)
            with c3: r_age   = st.number_input("Age", min_value=1, max_value=120, key="rg_age")
            with c4: r_gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], key="rg_gender")
            r_phone = st.text_input("Phone", key="rg_phone")

            if st.button("Create Account", type="primary", use_container_width=True):
                try:
                    register(r_name, r_email, r_pass, r_role, r_phone, int(r_age), r_gender)
                    st.success("Account created! Please sign in.")
                except Exception as e:
                    st.error(f"Registration failed: {e}")


# ── Dashboard ─────────────────────────────────────────────────────────────────
def show_dashboard():
    user = st.session_state.user or {"full_name": "Doctor", "role": "doctor", "id": 1}

    with st.sidebar:
        render_sidebar("overview")
        st.markdown("<hr style='border-color:#E2E8F0; margin:8px 16px;'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="padding: 8px 16px 12px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div class="pc-avatar">
                    {user['full_name'][:2].upper()}
                </div>
                <div>
                    <div style="font-size:13px; font-weight:600; color:#0F172A;">{user['full_name']}</div>
                    <div style="font-size:11px; color:#94A3B8; text-transform:capitalize;">{user['role']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── Top Bar ────────────────────────────────────────────────────────────────
    top_left, top_right = st.columns([3, 1])
    with top_left:
        import datetime
        hour = datetime.datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        st.markdown(f"""
        <div class="pc-page-title">{greeting}, {user['full_name'].split()[0]} 👋</div>
        <div class="pc-page-subtitle">
            AI diagnostic suite ready &nbsp;•&nbsp;
            <span class="pc-hipaa" style="font-size:10px;">🔒 HIPAA Compliant</span>
        </div>
        """, unsafe_allow_html=True)
    with top_right:
        if st.button("➕  New Patient Session", type="primary"):
            st.switch_page("pages/01_chest_xray.py")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Quick Stats ────────────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("3", "Urgent Reviews", "#EF4444"),
        ("8", "Today's Sessions", "#3B82F6"),
        ("94.5%", "AI Accuracy", "#22C55E"),
        ("2 min", "Avg. Report Time", "#8B5CF6"),
    ]
    for col, (val, label, color) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f"""
            <div class="pc-card" style="text-align:center; padding:1.2rem;">
                <div style="font-size:28px; font-weight:800; color:{color};
                            font-family:'DM Mono',monospace;">{val}</div>
                <div style="font-size:11px; color:#94A3B8; text-transform:uppercase;
                            letter-spacing:0.05em; margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Main Content ───────────────────────────────────────────────────────────
    left_col, right_col = st.columns([1.6, 1])

    with left_col:
        # Urgent Reviews
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:#EF4444; font-size:16px;">⚠️</span>
                <span style="font-size:16px; font-weight:700; color:#0F172A;">Urgent AI Reviews</span>
            </div>
            <span class="pc-urgent">3 Pending</span>
        </div>
        """, unsafe_allow_html=True)

        urgent_cases = [
            ("EV", "Eleanor Vance",   "Chest X-Ray (AP/PA)",          "85% Pneumonia probability", "#FEF2F2", "#EF4444"),
            ("MR", "Marcus Reed",     "TB Acoustic Analysis",          "92% TB pattern detected",   "#FFF7ED", "#F59E0B"),
            ("PK", "Priya Kumar",     "Cough Sound + X-Ray (combined)", "94.5% TB confidence",      "#FEF2F2", "#DC2626"),
        ]
        for init, name, test, flag, bg, fc in urgent_cases:
            st.markdown(f"""
            <div style="background:{bg}; border:1px solid {fc}30;
                        border-left: 3px solid {fc};
                        border-radius:10px; padding:14px 16px; margin-bottom:10px;">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div class="pc-avatar" style="background:{fc}15; color:{fc};">{init}</div>
                        <div>
                            <div style="font-size:14px; font-weight:600; color:#0F172A;">{name}</div>
                            <div style="font-size:12px; color:#64748B; margin-top:1px;">🔬 {test}</div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:{fc}15; color:{fc}; font-size:11px;
                                     font-weight:700; padding:4px 10px; border-radius:20px;">{flag}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Module Navigation Cards
        st.markdown("""
        <div style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            🚀 Diagnostic Modules
        </div>
        """, unsafe_allow_html=True)

        modules = [
            ("🫁", "Chest X-Ray Analysis",    "Pneumonia & TB lesion detection", "pages/01_chest_xray"),
            ("🎤", "Cough Sound Analysis",     "TB acoustic biomarker screening", "pages/02_cough_analysis"),
            ("💬", "Medical Scribe",           "RAG-powered clinical Q&A",        "pages/03_medical_scribe"),
            ("📋", "Prescription Parser",      "OCR + drug interaction checker",  "pages/04_prescription"),
            ("📊", "Unified Report",           "Multi-modal clinical synthesis",   "pages/05_unified_report"),
        ]

        m1, m2 = st.columns(2)
        cols = [m1, m2, m1, m2, m1]
        for col, (icon, title, desc, page) in zip(cols, modules):
            with col:
                st.markdown(f"""
                <div class="pc-card" style="padding:1.2rem; cursor:pointer;
                            transition: all 0.15s; margin-bottom:10px;"
                     onmouseover="this.style.borderColor='#3B82F6';this.style.transform='translateY(-2px)'"
                     onmouseout="this.style.borderColor='#E2E8F0';this.style.transform='none'">
                    <div style="font-size:24px; margin-bottom:8px;">{icon}</div>
                    <div style="font-size:14px; font-weight:600; color:#0F172A;">{title}</div>
                    <div style="font-size:12px; color:#94A3B8; margin-top:3px;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    with right_col:
        # Today's Schedule
        st.markdown("""
        <div style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            📅 Today's Schedule
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Schedule Appointment", type="primary", use_container_width=True):
            st.switch_page("pages/06_schedule.py")
            
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        schedule = [
            ("09:00 AM", "Sarah Jenkins",  "Follow-up: Asthma",       True),
            ("10:30 AM", "David Chen",     "New Patient Consult",      True),
            ("11:15 AM", "Robert King",    "Room 4 — Spirometry PFT",  False),
            ("02:00 PM", "Anita Sharma",   "TB Screening Review",      False),
            ("03:30 PM", "Liu Wei",        "Post-treatment Follow-up", False),
        ]

        for time, name, note, online in schedule:
            dot_color = "#22C55E" if online else "#CBD5E1"
            st.markdown(f"""
            <div style="display:flex; gap:12px; padding:10px 0;
                        border-bottom:1px solid #F1F5F9; align-items:flex-start;">
                <div style="font-size:11px; color:#94A3B8; min-width:58px;
                            font-family:'DM Mono',monospace; padding-top:2px;">{time}</div>
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:6px; margin-bottom:2px;">
                        <span style="width:7px; height:7px; border-radius:50%;
                                     background:{dot_color}; display:inline-block;
                                     box-shadow:0 0 5px {dot_color};"></span>
                        <span style="font-size:13px; font-weight:600; color:#0F172A;">{name}</span>
                    </div>
                    <div style="font-size:12px; color:#94A3B8;">{note}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Session Status
        st.markdown("""
        <div style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            🔬 Current Session Status
        </div>
        """, unsafe_allow_html=True)

        modules_status = [
            ("🫁", "X-Ray Analysis",    st.session_state.xray_result),
            ("🎤", "Cough Analysis",    st.session_state.cough_result),
            ("💬", "Medical Scribe",    st.session_state.scribe_context),
            ("📋", "Prescription",      st.session_state.prescription_data),
        ]

        for icon, label, result in modules_status:
            done   = result is not None
            color  = "#22C55E" if done else "#CBD5E1"
            status = "Complete" if done else "Pending"
            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between;
                        padding:8px 12px; background:#F8FAFC; border-radius:8px; margin-bottom:6px;">
                <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:#334155;">
                    {icon} {label}
                </div>
                <span style="font-size:11px; font-weight:600; color:{color};">
                    {"✓" if done else "○"} {status}
                </span>
            </div>
            """, unsafe_allow_html=True)

        any_done = any([st.session_state.xray_result,
                        st.session_state.cough_result,
                        st.session_state.scribe_context])
        if any_done:
            if st.button("📊 Generate Unified Report", type="primary", use_container_width=True):
                st.switch_page("pages/05_unified_report.py")

    # ── Recent Consultations ───────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
        <div style="font-size:16px; font-weight:700; color:#0F172A;">📁 Recent Consultations Log</div>
        <a style="font-size:13px; color:#3B82F6; text-decoration:none; font-weight:500;">View All →</a>
    </div>
    """, unsafe_allow_html=True)

    consultations = [
        ("AM", "Alice Morgan",   "Oct 24, 2023 • 2:30 PM",  "Telehealth",   "COPD Exacerbation — Rx updated"),
        ("JT", "James Thompson", "Oct 24, 2023 • 1:15 PM",  "In-Clinic",    "Routine Spirometry Review"),
        ("PS", "Priya Sharma",   "Oct 23, 2023 • 11:00 AM", "Telehealth",   "TB Screening — Sputum ordered"),
        ("DL", "David Liu",      "Oct 23, 2023 • 9:45 AM",  "In-Clinic",    "Asthma Follow-up — Stable"),
    ]

    header_cols = st.columns([2, 2, 1.5, 3, 0.5])
    headers = ["Patient", "Date & Time", "Consult Type", "Primary Diagnosis", ""]
    for col, h in zip(header_cols, headers):
        with col:
            st.markdown(f"<div style='font-size:11px; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em; padding:6px 0;'>{h}</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:0 0 4px 0; border-color:#E2E8F0;'>", unsafe_allow_html=True)

    for init, name, dt, ctype, diag in consultations:
        row_cols = st.columns([2, 2, 1.5, 3, 0.5])
        with row_cols[0]:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; padding:10px 0;">
                <div class="pc-avatar">{init}</div>
                <span style="font-size:13px; font-weight:500; color:#0F172A;">{name}</span>
            </div>
            """, unsafe_allow_html=True)
        with row_cols[1]:
            st.markdown(f"<div style='font-size:12px; color:#64748B; padding:14px 0 0;'>{dt}</div>", unsafe_allow_html=True)
        with row_cols[2]:
            color = "#1D4ED8" if ctype == "Telehealth" else "#7C3AED"
            bg    = "#EFF6FF" if ctype == "Telehealth" else "#F5F3FF"
            icon  = "📹" if ctype == "Telehealth" else "🏥"
            st.markdown(f"""
            <div style="padding:12px 0 0;">
                <span style="background:{bg}; color:{color}; font-size:11px; font-weight:600;
                             padding:3px 10px; border-radius:20px;">{icon} {ctype}</span>
            </div>
            """, unsafe_allow_html=True)
        with row_cols[3]:
            st.markdown(f"<div style='font-size:13px; color:#334155; padding:14px 0 0;'>{diag}</div>", unsafe_allow_html=True)
        with row_cols[4]:
            st.markdown(f"<div style='font-size:18px; padding:10px 0 0; cursor:pointer;'>📄</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:0; border-color:#F1F5F9;'>", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
if not st.session_state.access_token:
    show_login()
else:
    show_dashboard()
