"""
MiMo Hub — Home Page
First-time users see an onboarding walkthrough, returning users see the dashboard.
"""

import streamlit as st
from utils.shared_ui import load_css, render_sidebar
from utils.user_store import get_user, create_user, complete_onboarding

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MiMo Hub — Talk to Your Excel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# ─── Check User State ───────────────────────────────────────────────────────────
user = get_user()

# ═══════════════════════════════════════════════════════════════════════════════
# ONBOARDING: New user — name entry
# ═══════════════════════════════════════════════════════════════════════════════
if user is None:
    # Full-screen welcome — no sidebar
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        section[data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div style="text-align:center;">
            <p style="font-size:3.5rem;margin-bottom:0;">🧠</p>
            <h1 style="font-size:2.2rem;font-weight:800;
                background:linear-gradient(135deg,#FF6900,#FF8C38,#FFB347);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:0.3rem;">Welcome to MiMo Hub</h1>
            <p style="color:#64748B;font-size:1.05rem;margin-bottom:2rem;">
                Your AI-powered Excel analysis companion
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF7ED,#FEF3C7);
            border:1px solid #FDBA74; border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
            <p style="color:#92400E;font-size:0.95rem;font-weight:600;margin-bottom:0.5rem;">
                👋 Let's get to know you
            </p>
            <p style="color:#78716C;font-size:0.88rem;">
                Enter your name below to personalize your experience. Your name is stored
                locally on this device — no account needed.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("welcome_form"):
            name = st.text_input(
                "Your Name",
                placeholder="e.g. Nandan, Sarah, Alex...",
                max_chars=50,
            )
            submitted = st.form_submit_button(
                "🚀 Get Started",
                use_container_width=True,
                type="primary",
            )
            if submitted:
                if name.strip():
                    create_user(name.strip())
                    st.rerun()
                else:
                    st.error("Please enter your name to continue.")

    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ONBOARDING: Name set but walkthrough not completed
# ═══════════════════════════════════════════════════════════════════════════════
if not user.get("onboarded"):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        section[data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    # Track onboarding step
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 0

    step = st.session_state.onboarding_step

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 3, 1])
    with col_center:

        # Progress indicator
        total_steps = 4
        progress_pct = (step + 1) / total_steps
        st.progress(progress_pct, text=f"Step {step + 1} of {total_steps}")
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Step 0: Welcome ─────────────────────────────────────────
        if step == 0:
            st.markdown(f"""
            <div style="text-align:center;">
                <p style="font-size:3rem;">🎉</p>
                <h1 style="font-size:2rem;font-weight:800;color:#1E293B;">
                    Welcome, {user['name']}!
                </h1>
                <p style="color:#64748B;font-size:1.05rem;max-width:500px;margin:0.5rem auto 1.5rem;">
                    Let's take a quick tour of what MiMo Hub can do for you.
                    It'll only take a minute.
                </p>
            </div>
            """, unsafe_allow_html=True)

            feat_cols = st.columns(3)
            features = [
                ("📊", "Smart Analysis", "Auto-generated stats, charts, and data quality insights"),
                ("💬", "AI Chat", "Ask questions about your data in plain English"),
                ("📄", "Export Reports", "Download beautiful HTML reports with interactive charts"),
            ]
            for col, (icon, title, desc) in zip(feat_cols, features):
                with col:
                    st.markdown(f"""
                    <div style="text-align:center;padding:1.2rem;background:#F8FAFC;
                        border:1px solid #E2E8F0;border-radius:16px;">
                        <p style="font-size:2rem;margin-bottom:0.3rem;">{icon}</p>
                        <p style="font-weight:700;color:#1E293B;font-size:0.95rem;">{title}</p>
                        <p style="color:#64748B;font-size:0.82rem;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Step 1: Upload ──────────────────────────────────────────
        elif step == 1:
            st.markdown("""
            <div style="text-align:center;">
                <p style="font-size:3rem;">📁</p>
                <h2 style="font-size:1.8rem;font-weight:700;color:#1E293B;">
                    Step 1 — Upload Your Excel File
                </h2>
                <p style="color:#64748B;font-size:1rem;max-width:500px;margin:0.5rem auto 1.5rem;">
                    Upload any <strong>.xlsx</strong>, <strong>.xls</strong>, or <strong>.csv</strong> file.
                    MiMo Hub handles multi-sheet workbooks too.
                </p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="padding:1rem;background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;">
                    <p style="font-weight:600;color:#166534;">✅ Supported formats</p>
                    <p style="color:#15803D;font-size:0.88rem;">Excel (.xlsx, .xls) and CSV files up to 200 MB</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="padding:1rem;background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;">
                    <p style="font-weight:600;color:#1E40AF;">🔒 100% Private</p>
                    <p style="color:#1D4ED8;font-size:0.88rem;">Your files never leave your device — processed locally</p>
                </div>
                """, unsafe_allow_html=True)

        # ── Step 2: Analyze & Chat ──────────────────────────────────
        elif step == 2:
            st.markdown("""
            <div style="text-align:center;">
                <p style="font-size:3rem;">🤖</p>
                <h2 style="font-size:1.8rem;font-weight:700;color:#1E293B;">
                    Step 2 — Analyze & Chat
                </h2>
                <p style="color:#64748B;font-size:1rem;max-width:520px;margin:0.5rem auto 1.5rem;">
                    Once your file is uploaded, MiMo Hub auto-generates a full analysis dashboard.
                    Then ask <strong>any question</strong> about your data in plain English.
                </p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="padding:1.2rem;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;">
                    <p style="font-size:1.5rem;margin-bottom:0.3rem;">📊</p>
                    <p style="font-weight:700;color:#1E293B;">Auto Analysis</p>
                    <ul style="color:#64748B;font-size:0.85rem;padding-left:1rem;margin-top:0.4rem;">
                        <li>Summary statistics</li>
                        <li>Distribution charts</li>
                        <li>Correlation heatmaps</li>
                        <li>Data quality warnings</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="padding:1.2rem;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;">
                    <p style="font-size:1.5rem;margin-bottom:0.3rem;">💬</p>
                    <p style="font-weight:700;color:#1E293B;">AI Chat</p>
                    <ul style="color:#64748B;font-size:0.85rem;padding-left:1rem;margin-top:0.4rem;">
                        <li>"What's the average sales?"</li>
                        <li>"Show trends by region"</li>
                        <li>"Find anomalies in Q4"</li>
                        <li>Chat history saved</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        # ── Step 3: Export & API Key ────────────────────────────────
        elif step == 3:
            st.markdown("""
            <div style="text-align:center;">
                <p style="font-size:3rem;">🔑</p>
                <h2 style="font-size:1.8rem;font-weight:700;color:#1E293B;">
                    Step 3 — API Key & Export
                </h2>
                <p style="color:#64748B;font-size:1rem;max-width:520px;margin:0.5rem auto 1.5rem;">
                    To use AI Chat, you'll need a <strong>free Xiaomi MiMo API key</strong>.
                    You can also export beautiful reports anytime.
                </p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="padding:1.2rem;background:#FFF7ED;border:1px solid #FED7AA;border-radius:12px;">
                    <p style="font-size:1.5rem;margin-bottom:0.3rem;">🔑</p>
                    <p style="font-weight:700;color:#9A3412;">BYOK — Bring Your Own Key</p>
                    <p style="color:#C2410C;font-size:0.85rem;margin-top:0.3rem;">
                        Get a free key at <strong>platform.xiaomimimo.com</strong>.
                        Enter it in the sidebar — it's never stored on any server.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="padding:1.2rem;background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;">
                    <p style="font-size:1.5rem;margin-bottom:0.3rem;">📄</p>
                    <p style="font-weight:700;color:#166534;">Export Reports</p>
                    <p style="color:#15803D;font-size:0.85rem;margin-top:0.3rem;">
                        Download interactive HTML reports with charts,
                        CSV data exports, or print to PDF.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # Navigation buttons
        st.markdown("<br>", unsafe_allow_html=True)
        nav_cols = st.columns([1, 1, 1])
        with nav_cols[0]:
            if step > 0:
                if st.button("← Back", use_container_width=True):
                    st.session_state.onboarding_step -= 1
                    st.rerun()
        with nav_cols[2]:
            if step < total_steps - 1:
                if st.button("Next →", use_container_width=True, type="primary"):
                    st.session_state.onboarding_step += 1
                    st.rerun()
            else:
                if st.button("🚀 Start Using MiMo Hub", use_container_width=True, type="primary"):
                    complete_onboarding()
                    st.session_state.onboarding_step = 0
                    st.rerun()

    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN HOME PAGE — Returning users
# ═══════════════════════════════════════════════════════════════════════════════
render_sidebar()

st.markdown(f"""
<div class="hero-header">
    <h1>🧠 MiMo Hub</h1>
    <p>Welcome back, <strong>{user['name']}</strong>! Upload your Excel • Get instant analysis • Chat with your data</p>
</div>
""", unsafe_allow_html=True)

if "file_bytes" in st.session_state:
    st.success(f"✅ **{st.session_state['file_name']}** loaded! Use the sidebar to navigate to Analysis, Chat, or Export.")
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">📊</div>
        <div class="metric-label">Data Analysis</div>
        <p style="color:#64748B;font-size:0.82rem;margin-top:0.5rem;">
            Auto-generated stats, distributions, correlations, and data quality checks
        </p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">💬</div>
        <div class="metric-label">Chat with Data</div>
        <p style="color:#64748B;font-size:0.82rem;margin-top:0.5rem;">
            Ask questions in natural language and get AI-powered answers
        </p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">📄</div>
        <div class="metric-label">Export Reports</div>
        <p style="color:#64748B;font-size:0.82rem;margin-top:0.5rem;">
            Download beautiful HTML reports with charts, or save as PDF
        </p>
    </div>
    """, unsafe_allow_html=True)

if "file_bytes" not in st.session_state:
    st.markdown("""
    <div style="text-align:center;margin-top:2rem;color:#64748B;">
        <p style="font-size:1.1rem;">👈 Upload an Excel or CSV file from the sidebar to get started</p>
    </div>
    """, unsafe_allow_html=True)
