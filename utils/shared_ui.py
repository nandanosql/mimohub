"""
Shared UI — Common sidebar, CSS loading, and data management across pages.
"""

import os
import streamlit as st
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

from utils.excel_processor import get_sheet_names
from utils.user_store import get_user, update_name

load_dotenv()

# ─── Constants ──────────────────────────────────────────────────────────────────
MAX_INPUT_LENGTH = 2000
RATE_LIMIT_MESSAGES = 20
RATE_LIMIT_WINDOW_SEC = 60


def load_css():
    """Load external CSS from assets/styles.css."""
    _css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "styles.css")
    if os.path.exists(_css_path):
        with open(_css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar():
    """
    Render the shared sidebar with user greeting, file upload, API key input.
    Stores everything in st.session_state so it persists across pages.
    Returns api_key_input string.
    """
    with st.sidebar:
        # ─── User Greeting ──────────────────────────────────────────────
        user = get_user()
        if user and user.get("name"):
            st.markdown(
                f"<div style='text-align:center;padding:0.5rem 0 0.2rem;'>"
                f"<span style='font-size:1.4rem;'>👋</span><br>"
                f"<span style='font-size:0.95rem;font-weight:600;color:#F1F5F9;'>Hi, {user['name']}!</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            with st.expander("⚙️ Settings", expanded=False):
                new_name = st.text_input("Update name", value=user["name"], key="setting_name")
                if new_name.strip() and new_name.strip() != user["name"]:
                    if st.button("Save", key="save_name"):
                        update_name(new_name)
                        st.rerun()
            st.divider()

        st.markdown("### 🔑 MiMo AI API Key")
        api_key_input = st.text_input(
            "Enter your Xiaomi MiMo API key",
            type="password",
            value=st.session_state.get("api_key_input", ""),
            placeholder="sk-xxxxxxxxxx",
            help="Get a key at platform.xiaomimimo.com",
            key="sidebar_api_key",
        )
        if api_key_input:
            st.session_state["api_key_input"] = api_key_input

        st.divider()
        st.markdown("### 📁 Upload Data File")
        uploaded_file = st.file_uploader(
            "Drop your .xlsx / .xls / .csv file here",
            type=["xlsx", "xls", "csv"],
            help="Maximum file size: 200 MB",
            key="sidebar_uploader",
        )

        # Handle new file upload → store in session_state
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            uploaded_file.seek(0)
            is_csv = uploaded_file.name.lower().endswith(".csv")
            sheet_names = [] if is_csv else get_sheet_names(uploaded_file)

            # Store file metadata
            st.session_state["file_bytes"] = file_bytes
            st.session_state["file_name"] = uploaded_file.name
            st.session_state["file_size"] = uploaded_file.size
            st.session_state["is_csv"] = is_csv
            st.session_state["sheet_names"] = sheet_names

        # Show file info if data is stored
        if "file_bytes" in st.session_state:
            is_csv = st.session_state.get("is_csv", False)
            sheet_names = st.session_state.get("sheet_names", [])

            # Sheet selector for multi-sheet Excel
            selected_sheet = None
            if not is_csv and len(sheet_names) > 1:
                selected_sheet = st.selectbox(
                    "📄 Select Sheet", sheet_names,
                    index=sheet_names.index(st.session_state.get("selected_sheet", sheet_names[0]))
                    if st.session_state.get("selected_sheet") in sheet_names else 0,
                    key="sidebar_sheet",
                )
            elif sheet_names:
                selected_sheet = sheet_names[0]
                st.info(f"📄 Sheet: **{selected_sheet}**")

            st.session_state["selected_sheet"] = selected_sheet

            st.divider()
            st.markdown("### ℹ️ File Info")
            st.markdown(f"**Name:** {st.session_state['file_name']}")
            size_kb = st.session_state["file_size"] / 1024
            size_display = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
            st.markdown(f"**Size:** {size_display}")
            if sheet_names:
                st.markdown(f"**Sheets:** {len(sheet_names)}")

        st.divider()
        st.markdown(
            "<p style='color:#64748B;font-size:0.75rem;text-align:center;'>"
            "Powered by Xiaomi MiMo AI<br>Built with Streamlit & LiteLLM</p>",
            unsafe_allow_html=True,
        )

    return api_key_input


@st.cache_data(show_spinner=False)
def load_dataframe(file_bytes, sheet, csv_mode=False):
    """Load and cache a DataFrame from uploaded file bytes."""
    if csv_mode:
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet, engine="openpyxl")
    return df


def get_current_df():
    """
    Get the current DataFrame from session_state.
    Returns (df, error_msg) — df may be None.
    """
    if "file_bytes" not in st.session_state:
        return None, "no_file"

    try:
        df = load_dataframe(
            st.session_state["file_bytes"],
            st.session_state.get("selected_sheet") or 0,
            csv_mode=st.session_state.get("is_csv", False),
        )
        return df, None
    except Exception as e:
        return None, str(e)


def show_no_data_message():
    """Display a friendly message when no data is loaded."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#64748B;">
        <p style="font-size:2.5rem;margin-bottom:0.5rem;">📁</p>
        <p style="font-size:1.2rem;font-weight:600;color:#94A3B8;">No data loaded</p>
        <p style="font-size:0.95rem;">Upload an Excel or CSV file from the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)
