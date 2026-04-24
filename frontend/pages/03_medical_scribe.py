import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.styles import PULMOCARE_CSS, render_sidebar
from utils.api_client import ask_scribe, ingest_document, transcribe

st.set_page_config(page_title="Medical Scribe — PulmoCare AI", page_icon="💬", layout="wide")
st.markdown(PULMOCARE_CSS, unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

# Init session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "soap_note" not in st.session_state:
    st.session_state.soap_note = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None

with st.sidebar:
    render_sidebar("medical_scribe")

st.markdown("""
<div class="pc-page-title">💬 AI Medical Scribe</div>
<div class="pc-page-subtitle">
    RAG-powered clinical Q&A, consultation transcription, and SOAP note generation
    &nbsp;•&nbsp; <span class="pc-hipaa">🔒 Knowledge-Grounded Responses</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬 Medical Q&A", "🎙️ Transcribe Consultation", "📄 Upload Report"])

# ── Tab 1: Chat ───────────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([1.8, 1])

    with left:
        st.markdown("""
        <div style="font-size:14px; font-weight:600; color:#0F172A; margin-bottom:12px;">
            Ask anything — general medicine or about uploaded documents
        </div>
        """, unsafe_allow_html=True)

        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_messages:
                st.markdown("""
                <div style="text-align:center; padding:2.5rem; background:#F8FAFC;
                            border-radius:12px; border:1px solid #E2E8F0; margin-bottom:12px;">
                    <div style="font-size:32px; margin-bottom:10px;">🩺</div>
                    <div style="font-size:14px; font-weight:600; color:#475569;">PulmoCare AI Scribe</div>
                    <div style="font-size:12px; color:#94A3B8; margin-top:6px; line-height:1.6;">
                        Ask about symptoms, treatments, diagnoses, or<br>
                        upload a report and ask specific questions about it.
                    </div>
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px;">
                    <span style="background:#EFF6FF; color:#1D4ED8; font-size:12px; padding:6px 12px;
                                 border-radius:20px; cursor:pointer; border:1px solid #BFDBFE;">
                        What is tuberculosis?
                    </span>
                    <span style="background:#EFF6FF; color:#1D4ED8; font-size:12px; padding:6px 12px;
                                 border-radius:20px; cursor:pointer; border:1px solid #BFDBFE;">
                        TB vs Pneumonia symptoms
                    </span>
                    <span style="background:#EFF6FF; color:#1D4ED8; font-size:12px; padding:6px 12px;
                                 border-radius:20px; cursor:pointer; border:1px solid #BFDBFE;">
                        COPD management guidelines
                    </span>
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask a medical question..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            # Accumulate context for unified report
            ctx = st.session_state.get("scribe_context") or ""
            st.session_state.scribe_context = ctx + f"\nPatient: {prompt}"

            with st.spinner("Searching knowledge base..."):
                try:
                    resp = ask_scribe(prompt)
                    answer = resp.get("answer", "")
                    collection = resp.get("collection_used", "")
                except Exception as e:
                    answer = f"⚠️ Error: {e}"
                    collection = ""

            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            ctx = st.session_state.get("scribe_context") or ""
            st.session_state.scribe_context = ctx + f"\nAssistant: {answer}"
            st.rerun()

    with right:
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:10px;">
                📚 Knowledge Base Coverage
            </div>
        """, unsafe_allow_html=True)

        kb_items = [
            ("🏥", "Medical Conditions",    "MedlinePlus — 30+ conditions"),
            ("💊", "Drug Knowledge",        "OpenFDA — 20+ medications"),
            ("🔬", "Research Evidence",     "PubMed — 200+ abstracts"),
            ("📋", "Clinical Guidelines",   "WHO — TB, Malaria, Child Health"),
            ("📄", "Patient Documents",     "Your uploaded reports"),
        ]
        for icon, title, source in kb_items:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:8px 0;
                        border-bottom:1px solid #F1F5F9;">
                <span style="font-size:16px;">{icon}</span>
                <div>
                    <div style="font-size:13px; font-weight:500; color:#0F172A;">{title}</div>
                    <div style="font-size:11px; color:#94A3B8;">{source}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.chat_messages:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

# ── Tab 2: Transcribe ─────────────────────────────────────────────────────────
with tab2:
    left2, right2 = st.columns([1.2, 1])

    with left2:
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:14px;">
                🎙️ Upload Consultation Recording
            </div>
        """, unsafe_allow_html=True)

        audio_file = st.file_uploader("Consultation audio", type=["mp3", "wav", "m4a"],
                                      label_visibility="collapsed", key="consult_audio")
        if audio_file:
            st.audio(audio_file)
        st.markdown("</div>", unsafe_allow_html=True)

        if audio_file:
            if st.button("📝  Transcribe & Generate SOAP Note", type="primary", use_container_width=True):
                with st.spinner("Transcribing with Groq Whisper..."):
                    try:
                        result = transcribe(audio_file.read(), audio_file.name)
                        st.session_state.transcript = result.get("transcript", "")
                        st.session_state.soap_note  = result.get("soap_note", "")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")

        if st.session_state.transcript:
            st.markdown("""
            <div class="pc-card" style="margin-top:12px;">
                <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:10px;">
                    📝 Transcript
                </div>
            """, unsafe_allow_html=True)
            st.text_area("Transcript", st.session_state.transcript, height=200,
                          label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

    with right2:
        if st.session_state.soap_note:
            st.markdown("""
            <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:14px;">
                📋 Generated SOAP Note
            </div>
            """, unsafe_allow_html=True)

            # Parse SOAP sections
            soap = st.session_state.soap_note
            sections = {
                "SUBJECTIVE":   ("#3B82F6", "S"),
                "OBJECTIVE":    ("#8B5CF6", "O"),
                "ASSESSMENT":   ("#F59E0B", "A"),
                "PLAN":         ("#22C55E", "P"),
                "FLAGS":        ("#EF4444", "⚠"),
            }
            for section, (color, abbr) in sections.items():
                marker = f"## {section}"
                if marker in soap:
                    parts  = soap.split(marker)
                    if len(parts) > 1:
                        next_sections = [f"## {s}" for s in sections.keys() if s != section]
                        content = parts[1]
                        for ns in next_sections:
                            if ns in content:
                                content = content[:content.index(ns)]
                        content = content.strip()
                        st.markdown(f"""
                        <div style="background:#F8FAFC; border-left:3px solid {color};
                                    padding:12px 14px; border-radius:0 8px 8px 0; margin-bottom:10px;">
                            <div style="font-size:10px; font-weight:700; color:{color};
                                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:5px;">
                                {section}
                            </div>
                            <div style="font-size:13px; color:#334155; line-height:1.6;">{content}</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.download_button("📥 Download SOAP Note", st.session_state.soap_note,
                               "soap_note.txt", use_container_width=True)
        else:
            st.markdown("""
            <div class="pc-card" style="text-align:center; padding:3rem 2rem;">
                <div style="font-size:40px; margin-bottom:12px; opacity:0.3;">📋</div>
                <div style="font-size:14px; font-weight:600; color:#94A3B8;">SOAP Note Appears Here</div>
                <div style="font-size:12px; color:#CBD5E1; margin-top:6px;">
                    Upload and transcribe a consultation recording
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 3: Upload Report ──────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div style="font-size:14px; color:#475569; margin-bottom:16px;">
        Upload a medical report or prescription PDF to ask specific questions about it.
        The document will be indexed into the patient knowledge base.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown('<div class="pc-card">', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload medical report PDF", type=["pdf"],
                                    label_visibility="collapsed", key="report_pdf")
        if pdf_file:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:10px 12px;
                        background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; margin-top:8px;">
                📄 <strong style="font-size:13px;">{pdf_file.name}</strong>
                <span style="font-size:11px; color:#16A34A; margin-left:auto;">Ready to index</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📥  Index Document", type="primary", use_container_width=True):
                with st.spinner("Indexing into ChromaDB..."):
                    try:
                        result = ingest_document(pdf_file.read(), pdf_file.name)
                        st.success(f"✅ {result.get('message', 'Document indexed successfully!')}")
                    except Exception as e:
                        st.error(f"Ingestion failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pc-card">
            <div style="font-size:14px; font-weight:700; color:#0F172A; margin-bottom:10px;">
                💡 After Uploading
            </div>
            <div style="font-size:12px; color:#475569; line-height:1.8;">
                Go to the <strong>Medical Q&A</strong> tab and ask:
                <div style="margin-top:8px;">
                    <div style="background:#F1F5F9; border-radius:6px; padding:8px 10px;
                                font-size:12px; color:#334155; margin-bottom:6px;">
                        "What does my HbA1c value mean?"
                    </div>
                    <div style="background:#F1F5F9; border-radius:6px; padding:8px 10px;
                                font-size:12px; color:#334155; margin-bottom:6px;">
                        "Explain the findings in my report"
                    </div>
                    <div style="background:#F1F5F9; border-radius:6px; padding:8px 10px;
                                font-size:12px; color:#334155;">
                        "Is my creatinine level normal?"
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
