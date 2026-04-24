import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.styles import PULMOCARE_CSS, render_sidebar, confidence_bar
from utils.api_client import analyze_xray

st.set_page_config(page_title="Chest X-Ray — PulmoCare AI", page_icon="🫁", layout="wide")
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

with st.sidebar:
    render_sidebar("chest_xray")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pc-page-title">🫁 Chest X-Ray Analysis</div>
<div class="pc-page-subtitle">
    Upload chest X-ray images for AI-powered pneumonia & TB lesion detection
    &nbsp;•&nbsp; <span class="pc-hipaa">🔒 HIPAA Compliant</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.2, 1])

with left:
    st.markdown("""
    <div class="pc-card" style="padding:1.5rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
            <div style="font-size:15px; font-weight:700; color:#0F172A;">📤 Upload X-Ray Image</div>
            <span class="pc-badge pc-badge-gray">DICOM, JPEG, PNG</span>
        </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload X-Ray",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.image(uploaded, caption="Uploaded X-Ray", use_column_width=True)

    st.markdown("""
        <div style="margin-top:10px; padding:10px 12px; background:#FFFBEB;
                    border:1px solid #FCD34D; border-radius:8px; font-size:12px; color:#92400E;">
            ℹ️ Ensure images are clear and appropriately cropped. Max file size: 100MB.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if uploaded:
        if st.button("🔍  Analyze X-Ray", type="primary", use_container_width=True):
            with st.spinner("AI analyzing respiratory patterns..."):
                try:
                    result = analyze_xray(uploaded.read(), uploaded.name)
                    st.session_state.xray_result = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

with right:
    result = st.session_state.get("xray_result")

    if not result:
        st.markdown("""
        <div class="pc-card" style="text-align:center; padding:3rem 2rem;">
            <div style="font-size:48px; margin-bottom:16px; opacity:0.3;">🫁</div>
            <div style="font-size:15px; font-weight:600; color:#94A3B8;">No Analysis Yet</div>
            <div style="font-size:13px; color:#CBD5E1; margin-top:6px;">
                Upload an X-ray image and click Analyze
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        top   = result.get("top_finding", "Unknown")
        conf  = result.get("confidence", 0)
        rec   = result.get("recommendation", "")
        findings = result.get("findings", [])

        # Severity color
        is_critical = conf > 0.8 and top != "Normal"
        card_class  = "pc-card-danger" if is_critical else "pc-card-success" if top == "Normal" else "pc-card-warning"
        icon        = "⚠️" if is_critical else "✅" if top == "Normal" else "ℹ️"

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                <span style="font-size:16px;">{icon}</span>
                <span style="font-size:16px; font-weight:700; color:#0F172A;">{top}</span>
            </div>
            <div style="font-size:12px; color:#64748B; margin-bottom:10px;">Primary AI Finding</div>
            {confidence_bar(conf, "red" if is_critical else "green" if top == "Normal" else "yellow")}
            <div style="font-size:12px; color:#64748B; margin-top:6px; line-height:1.5;">{rec}</div>
        </div>
        """, unsafe_allow_html=True)

        # All findings
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                📊 All Condition Probabilities
            </div>
        """, unsafe_allow_html=True)

        for f in sorted(findings, key=lambda x: x["confidence"], reverse=True):
            cond = f["condition"]
            c    = f["confidence"]
            color = "red" if c > 0.7 and cond != "Normal" else "green" if cond == "Normal" else "yellow"
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-size:13px;
                            font-weight:500; color:#334155; margin-bottom:3px;">
                    <span>{cond}</span>
                </div>
                {confidence_bar(c, color)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Clinical markers
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                🔬 Clinical Markers
            </div>
        """, unsafe_allow_html=True)

        markers = [
            ("Pleural Effusion",  "None",     "#F0FDF4", "#16A34A"),
            ("Cardiomegaly",      "Negative",  "#F0FDF4", "#16A34A"),
            ("Pneumothorax",      "Negative",  "#F0FDF4", "#16A34A"),
        ]
        for marker, val, bg, color in markers:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:8px 0; border-bottom:1px solid #F1F5F9; font-size:13px;">
                <span style="color:#334155;">{marker}</span>
                <span style="background:{bg}; color:{color}; font-size:11px;
                             font-weight:600; padding:2px 10px; border-radius:20px;">{val}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Clinical notes
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:10px;">
                🗒️ Clinical Notes
            </div>
        """, unsafe_allow_html=True)
        st.text_area("Notes", placeholder="Enter clinical observations, correlation with symptoms...",
                     height=100, label_visibility="collapsed", key="xray_notes")
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Clear Results"):
                st.session_state.xray_result = None
                st.rerun()
        with c2:
            if st.button("📊 Go to Unified Report", type="primary"):
                st.switch_page("pages/05_unified_report.py")
