"""
Chat Store — SQLite-backed persistent conversation storage.
Zero external dependencies (sqlite3 is built into Python).
"""

import sqlite3
import uuid
import os
from datetime import datetime
from typing import Optional


# Database lives alongside app.py
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chat_history.db")


def _ensure_db_dir():
    """Create the data/ directory if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    """Get a database connection, creating tables if needed."""
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Create tables if they don't exist
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            file_name   TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role            TEXT NOT NULL,
            content         TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conv
            ON messages(conversation_id, id);
    """)
    conn.commit()
    return conn


# ═══════════════════════════════════════════════════════════════════════════════
# Conversation CRUD
# ═══════════════════════════════════════════════════════════════════════════════

def create_conversation(title: str = "New Chat", file_name: str = "") -> str:
    """Create a new conversation and return its ID."""
    conn = _get_conn()
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO conversations (id, title, file_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (conv_id, title, file_name, now, now),
    )
    conn.commit()
    conn.close()
    return conv_id


def list_conversations(limit: int = 50) -> list[dict]:
    """Return recent conversations, newest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, title, file_name, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversation(conv_id: str) -> Optional[dict]:
    """Get a single conversation by ID."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT id, title, file_name, created_at, updated_at FROM conversations WHERE id = ?",
        (conv_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_conversation_title(conv_id: str, title: str):
    """Update a conversation's title."""
    conn = _get_conn()
    conn.execute(
        "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
        (title, datetime.now().isoformat(), conv_id),
    )
    conn.commit()
    conn.close()


def delete_conversation(conv_id: str):
    """Delete a conversation and all its messages."""
    conn = _get_conn()
    conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Message CRUD
# ═══════════════════════════════════════════════════════════════════════════════

def add_message(conv_id: str, role: str, content: str):
    """Add a message to a conversation and update its timestamp."""
    conn = _get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (conv_id, role, content, now),
    )
    conn.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (now, conv_id),
    )
    conn.commit()
    conn.close()


def get_messages(conv_id: str) -> list[dict]:
    """Return all messages for a conversation, oldest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conv_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversation_message_count(conv_id: str) -> int:
    """Return the number of messages in a conversation."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM messages WHERE conversation_id = ?",
        (conv_id,),
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def auto_title_from_first_message(content: str) -> str:
    """Generate a short title from the first user message."""
    title = content.strip()[:60]
    if len(content.strip()) > 60:
        title += "…"
    return title
