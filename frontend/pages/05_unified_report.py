import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.styles import PULMOCARE_CSS, render_sidebar, confidence_bar
from utils.api_client import get_unified_report

st.set_page_config(page_title="Unified Report — PulmoCare AI", page_icon="📊", layout="wide")
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

if "unified_report_text" not in st.session_state:
    st.session_state.unified_report_text = None

with st.sidebar:
    render_sidebar("unified_report")

st.markdown("""
<div class="pc-page-title">📊 Unified Clinical Report</div>
<div class="pc-page-subtitle">
    Multi-modal AI synthesis — combining X-ray, cough, and symptom analysis
    &nbsp;•&nbsp; <span class="pc-hipaa">🔒 Physician Review Recommended</span>
</div>
""", unsafe_allow_html=True)

# ── Session Summary ───────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:12px;">
    📋 Current Session Data
</div>
""", unsafe_allow_html=True)

xray  = st.session_state.get("xray_result")
cough = st.session_state.get("cough_result")
scribe = st.session_state.get("scribe_context")

c1, c2, c3, c4 = st.columns(4)
modules = [
    (c1, "🫁", "X-Ray Analysis",   xray,   xray.get("top_finding")  if xray  else None, xray.get("confidence")  if xray  else None),
    (c2, "🎤", "Cough Analysis",   cough,  cough.get("top_finding") if cough else None, cough.get("confidence") if cough else None),
    (c3, "💬", "Symptom Context",  scribe, "Collected" if scribe else None, None),
    (c4, "📋", "Prescription",     st.session_state.get("prescription_data"),
     "Parsed" if st.session_state.get("prescription_data") else None, None),
]

for col, icon, label, data, finding, conf in modules:
    with col:
        done   = data is not None
        bg     = "#F0FDF4" if done else "#F8FAFC"
        border = "#BBF7D0" if done else "#E2E8F0"
        color  = "#16A34A" if done else "#94A3B8"
        status = "✓ Complete" if done else "○ Pending"
        st.markdown(f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:10px;
                    padding:14px; text-align:center; margin-bottom:8px;">
            <div style="font-size:22px; margin-bottom:6px;">{icon}</div>
            <div style="font-size:12px; font-weight:600; color:#0F172A;">{label}</div>
            <div style="font-size:11px; color:{color}; font-weight:600; margin-top:4px;">{status}</div>
            {f'<div style="font-size:11px; color:#64748B; margin-top:3px;">{finding}</div>' if finding else ''}
        </div>
        """, unsafe_allow_html=True)

# ── Generate Button ───────────────────────────────────────────────────────────
any_data = any([xray, cough, scribe])

if not any_data:
    st.markdown("""
    <div style="background:#FFF7ED; border:1.5px solid #FCD34D; border-radius:12px;
                padding:2rem; text-align:center; margin:1rem 0;">
        <div style="font-size:32px; margin-bottom:12px;">⚠️</div>
        <div style="font-size:15px; font-weight:700; color:#92400E; margin-bottom:6px;">
            No Diagnostic Data Available
        </div>
        <div style="font-size:13px; color:#B45309; line-height:1.6;">
            Complete at least one diagnostic module first:<br>
            Chest X-Ray, Cough Analysis, or Medical Scribe
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_nav1, c_nav2, c_nav3 = st.columns(3)
    with c_nav1:
        if st.button("🫁 Chest X-Ray", use_container_width=True):
            st.switch_page("pages/01_chest_xray.py")
    with c_nav2:
        if st.button("🎤 Cough Analysis", use_container_width=True):
            st.switch_page("pages/02_cough_analysis.py")
    with c_nav3:
        if st.button("💬 Medical Scribe", use_container_width=True):
            st.switch_page("pages/03_medical_scribe.py")

else:
    gen_col, _ = st.columns([1, 2])
    with gen_col:
        if st.button("🔬  Generate Unified Clinical Report", type="primary", use_container_width=True):
            with st.spinner("Synthesizing multi-modal diagnostic data..."):
                try:
                    result = get_unified_report(
                        xray_result=xray,
                        cough_result=cough,
                        scribe_context=scribe
                    )
                    st.session_state.unified_report_text = result.get("report", "")
                    st.rerun()
                except Exception as e:
                    st.error(f"Report generation failed: {e}")

    # ── Report Output ─────────────────────────────────────────────────────────
    if st.session_state.unified_report_text:
        report = st.session_state.unified_report_text

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
            <div style="font-size:16px; font-weight:700; color:#0F172A;">
                📄 Clinical Report
            </div>
            <span class="pc-hipaa">🔒 AI-Generated — Physician Review Required</span>
        </div>
        """, unsafe_allow_html=True)

        left, right = st.columns([1.8, 1])

        with left:
            # Parse and render report sections
            section_config = {
                "FINDINGS SUMMARY":    ("#3B82F6", "🔍", "#EFF6FF", "#BFDBFE"),
                "CLINICAL CORRELATION": ("#8B5CF6", "🩺", "#F5F3FF", "#DDD6FE"),
                "PROBABLE CONDITIONS": ("#F59E0B", "📊", "#FFFBEB", "#FDE68A"),
                "URGENCY LEVEL":       ("#EF4444", "⚡", "#FEF2F2", "#FECACA"),
                "RECOMMENDED NEXT STEPS": ("#22C55E", "📋", "#F0FDF4", "#BBF7D0"),
                "DISCLAIMER":          ("#94A3B8", "⚠️", "#F8FAFC", "#E2E8F0"),
            }

            for section, (color, icon, bg, border) in section_config.items():
                marker = f"## {icon} {section}"
                alt_marker = f"## {section}"
                content = ""

                for m in [marker, alt_marker]:
                    if m in report:
                        parts = report.split(m)
                        if len(parts) > 1:
                            content = parts[1]
                            # Cut at next section
                            for other in section_config.keys():
                                for prefix in [f"## 🔍", f"## 🩺", f"## 📊", f"## ⚡",
                                               f"## 📋", f"## ⚠️", f"## {other}"]:
                                    if prefix in content and prefix != m:
                                        content = content[:content.index(prefix)]
                            content = content.strip()
                            break

                if content:
                    # Special urgency styling
                    urgency_bg = bg
                    if section == "URGENCY LEVEL":
                        if "EMERGENCY" in content.upper():
                            urgency_bg = "#FEF2F2"
                            color = "#DC2626"
                        elif "URGENT" in content.upper():
                            urgency_bg = "#FFF7ED"
                            color = "#D97706"
                        else:
                            urgency_bg = "#F0FDF4"
                            color = "#16A34A"

                    st.markdown(f"""
                    <div style="background:{urgency_bg}; border:1px solid {border};
                                border-radius:10px; padding:16px 18px; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                            <span style="font-size:15px;">{icon}</span>
                            <span style="font-size:13px; font-weight:700; color:{color};
                                         text-transform:uppercase; letter-spacing:0.06em;">
                                {section}
                            </span>
                        </div>
                        <div style="font-size:13px; color:#334155; line-height:1.7;">
                            {content.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # If report doesn't match expected format, render raw
            has_sections = any(s in report for s in section_config.keys())
            if not has_sections:
                st.markdown(f"""
                <div class="pc-card">
                    <div style="font-size:13px; color:#334155; line-height:1.8; white-space:pre-wrap;">{report}</div>
                </div>
                """, unsafe_allow_html=True)

        with right:
            # Module confidence summary
            st.markdown("""
            <div class="pc-card">
                <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                    🎯 Diagnostic Confidence
                </div>
            """, unsafe_allow_html=True)

            if xray:
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="font-size:12px; font-weight:600; color:#475569; margin-bottom:4px;">
                        🫁 X-Ray: {xray.get('top_finding', 'Unknown')}
                    </div>
                    {confidence_bar(xray.get('confidence', 0), 'red' if xray.get('confidence', 0) > 0.7 and xray.get('top_finding') != 'Normal' else 'green')}
                </div>
                """, unsafe_allow_html=True)

            if cough:
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="font-size:12px; font-weight:600; color:#475569; margin-bottom:4px;">
                        🎤 Cough: {cough.get('top_finding', 'Unknown')}
                    </div>
                    {confidence_bar(cough.get('confidence', 0), 'red' if cough.get('confidence', 0) > 0.7 and cough.get('top_finding') != 'Normal' else 'green')}
                </div>
                """, unsafe_allow_html=True)

            if xray and cough:
                combined = min((xray.get("confidence", 0) + cough.get("confidence", 0)) / 2 * 1.1, 0.99)
                st.markdown(f"""
                <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px;
                            padding:12px; margin-top:4px;">
                    <div style="font-size:12px; font-weight:700; color:#1D4ED8; margin-bottom:6px;">
                        🔗 Combined Multi-Modal
                    </div>
                    {confidence_bar(combined, 'blue')}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Action buttons
            st.markdown("""
            <div class="pc-card" style="margin-top:12px;">
                <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                    ⚡ Actions
                </div>
            """, unsafe_allow_html=True)

            st.download_button(
                "📥 Download Report",
                st.session_state.unified_report_text,
                file_name="pulmocare_clinical_report.txt",
                mime="text/plain",
                use_container_width=True
            )
            if st.button("🔄 Regenerate Report", use_container_width=True):
                st.session_state.unified_report_text = None
                st.rerun()
            if st.button("🗑️ Clear All Session Data", use_container_width=True):
                for k in ["xray_result", "cough_result", "scribe_context",
                           "prescription_data", "unified_report_text"]:
                    st.session_state[k] = None
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Disclaimer box
            st.markdown("""
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px;
                        padding:12px 14px; margin-top:8px;">
                <div style="font-size:11px; font-weight:700; color:#DC2626;
                            text-transform:uppercase; letter-spacing:0.05em; margin-bottom:5px;">
                    ⚠️ Medical Disclaimer
                </div>
                <div style="font-size:11px; color:#7F1D1D; line-height:1.6;">
                    This AI-generated report is for preliminary screening only.
                    All findings must be reviewed and confirmed by a licensed physician
                    before any clinical decisions are made.
                </div>
            </div>
            """, unsafe_allow_html=True)
