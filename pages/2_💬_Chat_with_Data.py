"""
💬 Chat with Data — MiMo Hub
Ask questions about your data using Xiaomi MiMo AI.
Conversations are automatically saved and persist across sessions.
"""

import time
import streamlit as st
from datetime import datetime

from utils.shared_ui import (
    load_css, render_sidebar, get_current_df, show_no_data_message,
    MAX_INPUT_LENGTH, RATE_LIMIT_MESSAGES, RATE_LIMIT_WINDOW_SEC,
)
from utils.excel_processor import generate_summary_text
from utils.mimo_client import chat_with_data, get_api_key, SUGGESTED_QUESTIONS
from utils.chat_store import (
    create_conversation, list_conversations, get_messages,
    add_message, delete_conversation, update_conversation_title,
    auto_title_from_first_message, get_conversation_message_count,
)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat with Data — MiMo Hub",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
api_key_input = render_sidebar()


# ─── Conversation Management (Sidebar) ──────────────────────────────────────────
def _render_conversation_sidebar():
    """Render the conversation list and controls in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💬 Conversations")

        # New chat button
        if st.button("➕ New Chat", use_container_width=True, key="new_chat_btn"):
            file_name = st.session_state.get("file_name", "")
            conv_id = create_conversation(title="New Chat", file_name=file_name)
            st.session_state["active_conv_id"] = conv_id
            st.session_state["messages"] = []
            st.rerun()

        # List previous conversations
        conversations = list_conversations(limit=30)
        active_id = st.session_state.get("active_conv_id")

        if conversations:
            for conv in conversations:
                col_btn, col_del = st.columns([5, 1])
                is_active = conv["id"] == active_id
                label = f"{'▸ ' if is_active else ''}{conv['title']}"

                # Truncate long titles for sidebar
                if len(label) > 40:
                    label = label[:37] + "…"

                with col_btn:
                    if st.button(
                        label,
                        key=f"conv_{conv['id']}",
                        use_container_width=True,
                        disabled=is_active,
                    ):
                        # Load this conversation
                        st.session_state["active_conv_id"] = conv["id"]
                        msgs = get_messages(conv["id"])
                        st.session_state["messages"] = [
                            {"role": m["role"], "content": m["content"]} for m in msgs
                        ]
                        st.rerun()

                with col_del:
                    if st.button("🗑️", key=f"del_{conv['id']}", help="Delete"):
                        delete_conversation(conv["id"])
                        if active_id == conv["id"]:
                            st.session_state["active_conv_id"] = None
                            st.session_state["messages"] = []
                        st.rerun()
        else:
            st.caption("No saved conversations yet.")


_render_conversation_sidebar()

# ─── Page Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header" style="padding:1.2rem 1rem 0.8rem;">
    <h1 style="font-size:1.8rem;">💬 Chat with Data</h1>
    <p>Ask questions about your dataset using Xiaomi MiMo AI</p>
</div>
""", unsafe_allow_html=True)

# ─── Load Data ──────────────────────────────────────────────────────────────────
df, error = get_current_df()

if df is None:
    if error == "no_file":
        show_no_data_message()
    else:
        st.error(f"❌ Failed to load file: {error}")
    st.stop()

# ─── API Key Check ──────────────────────────────────────────────────────────────
api_key = get_api_key(api_key_input)

if not api_key:
    st.warning(
        "🔑 **Enter your Xiaomi MiMo API key** in the sidebar to enable AI chat. "
        "Get one free at [platform.xiaomimimo.com](https://platform.xiaomimimo.com)."
    )

# ─── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "msg_timestamps" not in st.session_state:
    st.session_state.msg_timestamps = []

# ─── Cached Summary ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cached_summary(_hash, df):
    return generate_summary_text(df)

_hash = hash(st.session_state.get("file_bytes", b""))

# ─── Active Conversation Info ───────────────────────────────────────────────────
active_conv_id = st.session_state.get("active_conv_id")
if active_conv_id:
    msg_count = get_conversation_message_count(active_conv_id)
    st.caption(f"💾 Auto-saving to conversation • {msg_count} messages saved")
else:
    st.caption("💡 Messages will be saved automatically when you start chatting.")

# ─── Suggested Questions ────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("#### 💡 Try asking:")
    suggestion_cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with suggestion_cols[i % 3]:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
                # Auto-create conversation if needed
                if not st.session_state.get("active_conv_id"):
                    file_name = st.session_state.get("file_name", "")
                    conv_id = create_conversation(
                        title=auto_title_from_first_message(q),
                        file_name=file_name,
                    )
                    st.session_state["active_conv_id"] = conv_id

                st.session_state.messages.append({"role": "user", "content": q})
                add_message(st.session_state["active_conv_id"], "user", q)
                st.rerun()

# ─── Chat History ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🧠"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ─── Chat Input with Sanitization & Rate Limiting ───────────────────────────────
if user_input := st.chat_input("Ask anything about your data...", key="chat_input"):

    # Sanitize
    clean_input = user_input.strip()
    if not clean_input:
        st.toast("⚠️ Please enter a valid question.", icon="⚠️")
        st.stop()

    # Length limit
    if len(clean_input) > MAX_INPUT_LENGTH:
        st.toast(
            f"⚠️ Message too long ({len(clean_input)} chars). Max is {MAX_INPUT_LENGTH}.",
            icon="⚠️",
        )
        st.stop()

    # Rate limiting
    now = time.time()
    st.session_state.msg_timestamps = [
        t for t in st.session_state.msg_timestamps
        if now - t < RATE_LIMIT_WINDOW_SEC
    ]
    if len(st.session_state.msg_timestamps) >= RATE_LIMIT_MESSAGES:
        st.toast(
            f"⏳ Rate limit reached ({RATE_LIMIT_MESSAGES} msgs / {RATE_LIMIT_WINDOW_SEC}s). Please wait.",
            icon="⏳",
        )
        st.stop()
    st.session_state.msg_timestamps.append(now)

    # Auto-create conversation on first message
    if not st.session_state.get("active_conv_id"):
        file_name = st.session_state.get("file_name", "")
        conv_id = create_conversation(
            title=auto_title_from_first_message(clean_input),
            file_name=file_name,
        )
        st.session_state["active_conv_id"] = conv_id

    # Add user message to history + persist
    st.session_state.messages.append({"role": "user", "content": clean_input})
    add_message(st.session_state["active_conv_id"], "user", clean_input)

    # Auto-title from first user message if still "New Chat"
    if len(st.session_state.messages) == 1:
        update_conversation_title(
            st.session_state["active_conv_id"],
            auto_title_from_first_message(clean_input),
        )

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(clean_input)

    # Generate AI response
    with st.chat_message("assistant", avatar="🧠"):
        if not api_key:
            st.error("🔑 Please enter your MiMo API key in the sidebar first.")
        else:
            data_context = cached_summary(_hash, df)
            try:
                stream = chat_with_data(
                    messages=st.session_state.messages,
                    data_context=data_context,
                    api_key=api_key,
                    stream=True,
                )
                response = st.write_stream(stream)

                # Persist AI response
                st.session_state.messages.append({"role": "assistant", "content": response})
                add_message(st.session_state["active_conv_id"], "assistant", response)

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
