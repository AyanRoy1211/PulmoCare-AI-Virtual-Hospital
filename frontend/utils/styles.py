PULMOCARE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Global Reset ───────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #F0F4F8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1200px !important; }

/* ── Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    min-width: 240px !important;
    max-width: 240px !important;
}

[data-testid="stSidebar"] .stMarkdown p { margin: 0; }

/* ── Cards ──────────────────────────────────────────────── */
.pc-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.pc-card-danger {
    background: #FFFFFF;
    border: 1.5px solid #FCA5A5;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.pc-card-success {
    background: #F0FDF4;
    border: 1.5px solid #86EFAC;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.pc-card-warning {
    background: #FFFBEB;
    border: 1.5px solid #FCD34D;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── Badge ──────────────────────────────────────────────── */
.pc-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.pc-badge-blue   { background: #EFF6FF; color: #1D4ED8; }
.pc-badge-red    { background: #FEF2F2; color: #DC2626; }
.pc-badge-green  { background: #F0FDF4; color: #16A34A; }
.pc-badge-yellow { background: #FFFBEB; color: #D97706; }
.pc-badge-gray   { background: #F8FAFC; color: #64748B; border: 1px solid #E2E8F0; }

/* ── Page Header ────────────────────────────────────────── */
.pc-page-title {
    font-size: 26px;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
}

.pc-page-subtitle {
    font-size: 14px;
    color: #64748B;
    margin: 0 0 1.5rem 0;
}

/* ── Section Header ─────────────────────────────────────── */
.pc-section-title {
    font-size: 15px;
    font-weight: 600;
    color: #0F172A;
    margin: 0 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Metric Pill ────────────────────────────────────────── */
.pc-metric {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
}

.pc-metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
    font-family: 'DM Mono', monospace;
}

.pc-metric-label {
    font-size: 11px;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 2px;
}

/* ── Confidence Bar ─────────────────────────────────────── */
.pc-conf-bar {
    background: #E2E8F0;
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    margin: 6px 0;
}

.pc-conf-fill-red    { height: 100%; background: #EF4444; border-radius: 4px; }
.pc-conf-fill-yellow { height: 100%; background: #F59E0B; border-radius: 4px; }
.pc-conf-fill-green  { height: 100%; background: #22C55E; border-radius: 4px; }
.pc-conf-fill-blue   { height: 100%; background: #3B82F6; border-radius: 4px; }

/* ── HIPAA Banner ───────────────────────────────────────── */
.pc-hipaa {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 600;
    color: #16A34A;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 20px;
    padding: 3px 10px;
    letter-spacing: 0.04em;
}

/* ── Urgency Tag ────────────────────────────────────────── */
.pc-urgent {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 700;
    color: #DC2626;
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 6px;
    padding: 4px 10px;
}

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(37, 99, 235, 0.35) !important;
}

.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%) !important;
    border: 1px solid #CBD5E1 !important;
    color: #0F172A !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%) !important;
    border-color: #94A3B8 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05) !important;
}

/* ── File Uploader ──────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #FAFBFF !important;
    border: 2px dashed #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #3B82F6 !important;
}

/* ── Chat Input ─────────────────────────────────────────── */
[data-testid="stChatInput"] {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
}

/* ── Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F8FAFC !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border-bottom: none !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: #64748B !important;
}

.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #0F172A !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
}

/* ── Divider ────────────────────────────────────────────── */
hr { border-color: #E2E8F0 !important; margin: 1rem 0 !important; }

/* ── Spinner / Status ───────────────────────────────────── */
.pc-status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.pc-dot-green  { background: #22C55E; box-shadow: 0 0 6px #22C55E; }
.pc-dot-red    { background: #EF4444; box-shadow: 0 0 6px #EF4444; }
.pc-dot-yellow { background: #F59E0B; box-shadow: 0 0 6px #F59E0B; }

/* ── Patient Row ────────────────────────────────────────── */
.pc-patient-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #F1F5F9;
}

.pc-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700;
    background: #EFF6FF; color: #1D4ED8;
    flex-shrink: 0;
}

/* ── Logo ───────────────────────────────────────────────── */
.pc-logo {
    font-size: 20px;
    font-weight: 800;
    color: #1D4ED8;
    letter-spacing: -0.03em;
}

.pc-logo span { color: #0F172A; }

/* ── Streamlit Native Page Link Styling ───────────────── */
[data-testid="stPageLink-NavLink"] {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    margin: 0 8px 2px 8px !important;
    transition: all 0.2s ease !important;
    color: #475569 !important;
    text-decoration: none !important;
}

[data-testid="stPageLink-NavLink"]:hover {
    background: #F1F5F9 !important;
    color: #0F172A !important;
}

[data-testid="stPageLink-NavLink"][data-active="true"] {
    background: #EFF6FF !important;
    color: #1D4ED8 !important;
    font-weight: 600 !important;
}

/* ── Sidebar Nav Item (Fallback) ────────────────────────── */
.pc-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #475569;
    cursor: pointer;
    margin-bottom: 2px;
    text-decoration: none;
}

.pc-nav-item:hover { background: #F1F5F9; color: #0F172A; }
.pc-nav-item.active { background: #EFF6FF; color: #1D4ED8; font-weight: 600; }

/* ── Analysis Progress ──────────────────────────────────── */
.pc-analyzing {
    text-align: center;
    padding: 2.5rem;
    background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
    border-radius: 12px;
    border: 1px solid #BFDBFE;
}

/* ── SOAP Note ──────────────────────────────────────────── */
.pc-soap-section {
    background: #F8FAFC;
    border-left: 3px solid #3B82F6;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 12px;
}

.pc-soap-label {
    font-size: 10px;
    font-weight: 700;
    color: #3B82F6;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}

.pc-soap-content {
    font-size: 13px;
    color: #334155;
    line-height: 1.6;
}
</style>
"""


def render_sidebar(active_page: str = "overview"):
    """Render the PulmoCare sidebar navigation."""
    import streamlit as st

    nav_items = [
        ("overview",        "🏠", "Overview",        "app.py"),
        ("chest_xray",      "🫁", "Chest X-Ray",     "pages/01_chest_xray.py"),
        ("cough_analysis",  "🎤", "Cough Analysis",  "pages/02_cough_analysis.py"),
        ("medical_scribe",  "💬", "Medical Scribe",  "pages/03_medical_scribe.py"),
        ("prescription",    "📋", "Prescription",    "pages/04_prescription.py"),
        ("unified_report",  "📊", "Unified Report",  "pages/05_unified_report.py"),
        ("schedule",        "📅", "Schedule",        "pages/06_schedule.py"),
    ]

    st.markdown("""
    <div style="padding: 20px 16px 12px 16px;">
        <div class="pc-logo">Pulmo<span>Care</span> <span style="color:#3B82F6;font-size:13px;font-weight:600;">AI</span></div>
        <div style="margin-top:6px;">
            <span class="pc-hipaa">🔒 HIPAA Compliant</span>
        </div>
    </div>
    <hr style="margin: 0 16px 12px 16px; border-color: #E2E8F0;">
    """, unsafe_allow_html=True)

    for key, icon, label, page in nav_items:
        # Use Streamlit's native interactive page link
        st.page_link(page, label=label, icon=icon)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin: 8px; padding: 12px 14px; background: #FEF2F2;
                border: 1px solid #FECACA; border-radius: 10px; cursor: pointer;">
        <div style="display:flex; align-items:center; gap:8px;
                    color:#DC2626; font-weight:700; font-size:13px;">
            ✳️ Emergency AI Chat
        </div>
    </div>
    """, unsafe_allow_html=True)


def confidence_bar(value: float, color: str = "blue") -> str:
    """Return an HTML confidence bar string."""
    pct = int(value * 100)
    colors = {
        "red":    "#EF4444",
        "yellow": "#F59E0B",
        "green":  "#22C55E",
        "blue":   "#3B82F6",
    }
    fill = colors.get(color, "#3B82F6")
    return f"""
    <div style="display:flex; align-items:center; gap:10px; margin: 6px 0;">
        <div style="flex:1; background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
            <div style="width:{pct}%; height:100%; background:{fill}; border-radius:4px;"></div>
        </div>
        <span style="font-size:13px; font-weight:600; color:#0F172A;
                     font-family:'DM Mono',monospace; min-width:36px;">{pct}%</span>
    </div>
    """
