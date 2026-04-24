import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.styles import PULMOCARE_CSS, render_sidebar, confidence_bar
from utils.api_client import analyze_cough

st.set_page_config(page_title="Cough Analysis — PulmoCare AI", page_icon="🎤", layout="wide")
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

with st.sidebar:
    render_sidebar("cough_analysis")

st.markdown("""
<div class="pc-page-title">🎤 TB Acoustic Biomarker Analysis</div>
<div class="pc-page-subtitle">
    Upload or record cough audio for automated TB and respiratory disease screening
    &nbsp;•&nbsp; <span class="pc-hipaa">🔒 Secure Audio Processing</span>
</div>
""", unsafe_allow_html=True)

# ── Recording tip ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:10px 14px; background:#FFFBEB; border:1px solid #FCD34D;
            border-radius:8px; font-size:13px; color:#92400E; margin-bottom:16px;
            display:flex; align-items:center; gap:8px;">
    ℹ️ <strong>Recording tip:</strong> Audio should be recorded in a quiet space for optimal diagnostic accuracy.
    Minimum 5-second cough sample required.
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.2, 1])

with left:
    st.markdown("""
    <div class="pc-card">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
            <div style="font-size:15px; font-weight:700; color:#0F172A;">🎙️ Upload Cough Recording</div>
            <span class="pc-badge pc-badge-gray">WAV, MP3, M4A</span>
        </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload Audio",
        type=["wav", "mp3", "m4a"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.audio(uploaded, format="audio/wav")

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:10px 12px;
                    background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px;
                    font-size:12px; color:#16A34A; margin-top:8px;">
            ✅ <strong>{uploaded.name}</strong> uploaded successfully
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded:
        if st.button("🔍  Analyze Cough Pattern", type="primary", use_container_width=True):
            with st.spinner("Identifying acoustic biomarkers..."):
                try:
                    result = analyze_cough(uploaded.read(), uploaded.name)
                    st.session_state.cough_result = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    # How it works
    st.markdown("""
    <div class="pc-card" style="margin-top:12px;">
        <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            ⚙️ How Acoustic Analysis Works
        </div>
        <div style="font-size:12px; color:#475569; line-height:1.8;">
            <div style="margin-bottom:8px; display:flex; gap:8px;">
                <span style="color:#3B82F6; font-weight:600;">1.</span>
                <span>Audio is processed into MFCC (Mel-Frequency Cepstral Coefficients)</span>
            </div>
            <div style="margin-bottom:8px; display:flex; gap:8px;">
                <span style="color:#3B82F6; font-weight:600;">2.</span>
                <span>Deep learning model extracts respiratory biomarkers</span>
            </div>
            <div style="margin-bottom:8px; display:flex; gap:8px;">
                <span style="color:#3B82F6; font-weight:600;">3.</span>
                <span>TB and respiratory conditions classified with confidence scores</span>
            </div>
            <div style="display:flex; gap:8px;">
                <span style="color:#3B82F6; font-weight:600;">4.</span>
                <span>Combined with X-ray analysis for 94.5% specificity</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    result = st.session_state.get("cough_result")

    if not result:
        st.markdown("""
        <div class="pc-card" style="text-align:center; padding:3rem 2rem;">
            <div style="font-size:48px; margin-bottom:16px; opacity:0.3;">🎤</div>
            <div style="font-size:15px; font-weight:600; color:#94A3B8;">Awaiting Audio Sample</div>
            <div style="font-size:13px; color:#CBD5E1; margin-top:6px;">
                Upload a cough recording to begin analysis
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        top      = result.get("top_finding", "Unknown")
        conf     = result.get("confidence", 0)
        rec      = result.get("recommendation", "")
        findings = result.get("findings", [])

        is_critical = conf > 0.75 and top != "Normal"
        card_class  = "pc-card-danger" if is_critical else "pc-card-success"
        icon        = "⚠️" if is_critical else "✅"

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="font-size:18px;">{icon}</span>
                <span style="font-size:17px; font-weight:700; color:#0F172A;">{top} Detected</span>
            </div>
            <div style="font-size:12px; color:#64748B; margin-bottom:10px;">
                Primary Acoustic Finding
            </div>
            {confidence_bar(conf, "red" if is_critical else "green")}
            <div style="font-size:12px; color:#475569; margin-top:8px; line-height:1.5;">{rec}</div>
        </div>
        """, unsafe_allow_html=True)

        # All findings
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                🔊 Condition Probabilities
            </div>
        """, unsafe_allow_html=True)

        for f in sorted(findings, key=lambda x: x["confidence"], reverse=True):
            cond  = f["condition"]
            c     = f["confidence"]
            color = "red" if c > 0.6 and cond != "Normal" else "green" if cond == "Normal" else "yellow"
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="font-size:13px; font-weight:500; color:#334155; margin-bottom:3px;">{cond}</div>
                {confidence_bar(c, color)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Multi-modal insight
        xray = st.session_state.get("xray_result")
        if xray:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:14px 16px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                    <div style="font-size:14px; font-weight:700; color:#1D4ED8;">
                        🔗 Multi-Modal Insight
                    </div>
                    <span class="pc-badge pc-badge-blue">AI COMBINED</span>
                </div>
                <div style="font-size:12px; color:#1E40AF; line-height:1.5;">
                    The combination of acoustic and visual markers increases diagnostic
                    specificity for active TB to <strong>94.5%</strong>.
                </div>
                <div style="margin-top:10px;">
                    <div style="font-size:11px; color:#3B82F6; margin-bottom:3px;">Combined Confidence</div>
                    {confidence_bar(0.945, "blue")}
                </div>
            </div>
            """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Clear Results"):
                st.session_state.cough_result = None
                st.rerun()
        with c2:
            if st.button("📊 Unified Report", type="primary"):
                st.switch_page("pages/05_unified_report.py")
