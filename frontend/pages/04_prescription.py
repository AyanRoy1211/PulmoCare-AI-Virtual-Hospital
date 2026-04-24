import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.styles import PULMOCARE_CSS, render_sidebar
from utils.api_client import parse_prescription, check_interactions

st.set_page_config(page_title="Prescription — PulmoCare AI", page_icon="📋", layout="wide")
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

if "parsed_prescription" not in st.session_state:
    st.session_state.parsed_prescription = None
if "interaction_result" not in st.session_state:
    st.session_state.interaction_result = None

with st.sidebar:
    render_sidebar("prescription")

st.markdown("""
<div class="pc-page-title">📋 Prescription Parser & Drug Safety</div>
<div class="pc-page-subtitle">
    OCR-powered prescription parsing + AI drug-drug interaction detection
    &nbsp;•&nbsp; <span class="pc-hipaa">🔒 Powered by Groq Vision</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📷 Parse Prescription", "💊 Drug Interaction Checker"])

# ── Tab 1: Parse ──────────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([1.2, 1.4])

    with left:
        st.markdown('<div class="pc-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:14px;">
            📸 Upload Prescription Image
        </div>
        """, unsafe_allow_html=True)

        img_file = st.file_uploader("Prescription", type=["jpg", "jpeg", "png"],
                                    label_visibility="collapsed", key="presc_img")
        if img_file:
            st.image(img_file, caption="Prescription Preview", use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if img_file:
            if st.button("🔍  Parse Prescription", type="primary", use_container_width=True):
                with st.spinner("Reading prescription with AI Vision..."):
                    try:
                        result = parse_prescription(img_file.read(), img_file.name)
                        st.session_state.parsed_prescription = result
                        st.session_state.prescription_data   = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"Parsing failed: {e}")

    with right:
        parsed = st.session_state.parsed_prescription

        if not parsed:
            st.markdown("""
            <div class="pc-card" style="text-align:center; padding:3rem 2rem;">
                <div style="font-size:40px; margin-bottom:12px; opacity:0.3;">📋</div>
                <div style="font-size:14px; font-weight:600; color:#94A3B8;">Parsed Data Appears Here</div>
                <div style="font-size:12px; color:#CBD5E1; margin-top:6px;">
                    Upload a prescription image to extract medication data
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Patient Info
            st.markdown("""
            <div class="pc-card">
                <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                    👤 Patient Information
                </div>
            """, unsafe_allow_html=True)

            info_rows = [
                ("Patient",   parsed.get("patient_name", "—")),
                ("Age",       parsed.get("patient_age", "—")),
                ("Date",      parsed.get("date", "—")),
                ("Doctor",    parsed.get("doctor_name", "—")),
                ("Diagnosis", parsed.get("diagnosis", "—")),
            ]
            for label, val in info_rows:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:7px 0;
                            border-bottom:1px solid #F1F5F9; font-size:13px;">
                    <span style="color:#94A3B8; font-weight:500;">{label}</span>
                    <span style="color:#0F172A; font-weight:500; text-align:right; max-width:60%;">{val or '—'}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Medications
            meds = parsed.get("medications", [])
            if meds:
                st.markdown("""
                <div class="pc-card">
                    <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                        💊 Medications Extracted
                    </div>
                """, unsafe_allow_html=True)

                for i, med in enumerate(meds):
                    drug = med.get("drug_name") or "—"
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0;
                                border-radius:8px; padding:12px 14px; margin-bottom:8px;">
                        <div style="display:flex; align-items:center; justify-content:space-between;">
                            <div style="font-size:14px; font-weight:600; color:#0F172A;">{drug}</div>
                            <span class="pc-badge pc-badge-blue">Drug {i+1}</span>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">
                            <span class="pc-badge pc-badge-gray">💉 {med.get('dosage') or '—'}</span>
                            <span class="pc-badge pc-badge-gray">⏱ {med.get('frequency') or '—'}</span>
                            <span class="pc-badge pc-badge-gray">📅 {med.get('duration') or '—'}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Auto-check interactions
                drug_names = [m.get("drug_name") for m in meds if m.get("drug_name")]
                if len(drug_names) >= 2:
                    st.markdown(f"""
                    <div style="padding:10px 14px; background:#FFFBEB; border:1px solid #FCD34D;
                                border-radius:8px; font-size:12px; color:#92400E; margin-bottom:8px;">
                        ⚠️ {len(drug_names)} medications detected.
                        Check for drug interactions in the next tab.
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state["drugs_to_check"] = drug_names
                    if st.button("💊  Check Interactions Now", type="primary", use_container_width=True):
                        with st.spinner("Analyzing drug interactions..."):
                            try:
                                r = check_interactions(drug_names)
                                st.session_state.interaction_result = r.get("analysis", "")
                            except Exception as e:
                                st.error(f"Interaction check failed: {e}")

            if parsed.get("instructions"):
                st.markdown(f"""
                <div class="pc-card" style="background:#F0FDF4; border-color:#BBF7D0;">
                    <div style="font-size:12px; font-weight:700; color:#16A34A;
                                text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
                        Doctor's Instructions
                    </div>
                    <div style="font-size:13px; color:#14532D; line-height:1.6;">
                        {parsed.get("instructions")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── Tab 2: Drug Interactions ──────────────────────────────────────────────────
with tab2:
    left2, right2 = st.columns([1, 1.4])

    with left2:
        st.markdown('<div class="pc-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:12px;">
            💊 Enter Medications
        </div>
        <div style="font-size:12px; color:#64748B; margin-bottom:12px;">
            Enter one medication per line. Minimum 2 required.
        </div>
        """, unsafe_allow_html=True)

        # Pre-populate from parsed prescription
        prefill = ""
        if st.session_state.get("drugs_to_check"):
            prefill = "\n".join(st.session_state["drugs_to_check"])

        drugs_input = st.text_area("Medications", value=prefill, height=180,
                                   placeholder="Metformin\nRifampicin\nIsoniazid\nPyrazinamide",
                                   label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🔍  Check Interactions", type="primary", use_container_width=True):
            drug_list = [d.strip() for d in drugs_input.strip().splitlines() if d.strip()]
            if len(drug_list) < 2:
                st.warning("Enter at least 2 medications.")
            else:
                with st.spinner("Analyzing drug interactions..."):
                    try:
                        r = check_interactions(drug_list)
                        st.session_state.interaction_result = r.get("analysis", "")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Interaction check failed: {e}")

        # Common dangerous combos
        st.markdown("""
        <div class="pc-card" style="margin-top:12px;">
            <div style="font-size:12px; font-weight:700; color:#EF4444; margin-bottom:8px;">
                🔴 Known High-Risk Combos
            </div>
            <div style="font-size:11px; color:#475569; line-height:1.8;">
                • Warfarin + Aspirin<br>
                • Metformin + Contrast dye<br>
                • Rifampicin + oral contraceptives<br>
                • MAOIs + SSRIs
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right2:
        result_text = st.session_state.interaction_result

        if not result_text:
            st.markdown("""
            <div class="pc-card" style="text-align:center; padding:3rem 2rem;">
                <div style="font-size:40px; margin-bottom:12px; opacity:0.3;">💊</div>
                <div style="font-size:14px; font-weight:600; color:#94A3B8;">Interaction Analysis Appears Here</div>
                <div style="font-size:12px; color:#CBD5E1; margin-top:6px;">
                    Enter medications and click Check Interactions
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="pc-card">
                <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:14px;">
                    🧪 Drug Interaction Analysis
                </div>
            """, unsafe_allow_html=True)

            # Color severe/moderate/mild sections
            for line in result_text.split("\n"):
                if "SEVERE" in line or "🔴" in line:
                    st.markdown(f"""
                    <div style="background:#FEF2F2; border:1px solid #FECACA;
                                border-radius:6px; padding:8px 12px; margin-bottom:6px;
                                font-size:13px; color:#991B1B; font-weight:600;">{line}</div>
                    """, unsafe_allow_html=True)
                elif "MODERATE" in line or "🟡" in line:
                    st.markdown(f"""
                    <div style="background:#FFFBEB; border:1px solid #FDE68A;
                                border-radius:6px; padding:8px 12px; margin-bottom:6px;
                                font-size:13px; color:#92400E; font-weight:600;">{line}</div>
                    """, unsafe_allow_html=True)
                elif "MILD" in line or "🟢" in line:
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1px solid #BBF7D0;
                                border-radius:6px; padding:8px 12px; margin-bottom:6px;
                                font-size:13px; color:#14532D; font-weight:600;">{line}</div>
                    """, unsafe_allow_html=True)
                elif line.strip():
                    st.markdown(f"<div style='font-size:13px; color:#475569; line-height:1.6; padding:2px 0;'>{line}</div>",
                                unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("🔄 Clear Analysis"):
                st.session_state.interaction_result = None
                st.rerun()
