import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.styles import PULMOCARE_CSS, render_sidebar

st.set_page_config(page_title="Schedule — PulmoCare AI", page_icon="📅", layout="wide")
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

with st.sidebar:
    render_sidebar("schedule")

st.markdown("""
<div class="pc-page-title">📅 Schedule Appointments</div>
<div class="pc-page-subtitle">
    Manage your upcoming consultations and patient visits.
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.5, 1])

with left:
    st.markdown("""
    <div class="pc-card">
        <div style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            ➕ Book New Appointment
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("schedule_form"):
        st.text_input("Patient Name", placeholder="e.g. John Doe")
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Date")
        with col2:
            st.time_input("Time")
            
        st.selectbox("Consultation Type", ["In-Clinic", "Telehealth", "Follow-up", "Emergency"])
        st.text_area("Notes", placeholder="Reason for visit...")
        
        submitted = st.form_submit_button("Schedule Appointment", type="primary", use_container_width=True)
        if submitted:
            st.success("Appointment scheduled successfully! (UI Only)")
            
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="pc-card">
        <div style="font-size:16px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            📆 Upcoming Schedule
        </div>
    """, unsafe_allow_html=True)
    
    schedule = [
        ("Today, 09:00 AM", "Sarah Jenkins", "Follow-up: Asthma", True),
        ("Today, 10:30 AM", "David Chen", "New Patient Consult", True),
        ("Tomorrow, 11:15 AM", "Robert King", "Spirometry PFT", False),
    ]

    for time, name, note, online in schedule:
        dot_color = "#22C55E" if online else "#CBD5E1"
        st.markdown(f"""
        <div style="display:flex; gap:12px; padding:10px 0;
                    border-bottom:1px solid #F1F5F9; align-items:flex-start;">
            <div style="font-size:11px; color:#94A3B8; min-width:80px;
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
        
    st.markdown("</div>", unsafe_allow_html=True)
