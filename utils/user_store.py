"""
User Store — Local device-based user profiles.
Persists user name and onboarding status to SQLite.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chat_history.db")


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY CHECK (id = 1),
            name            TEXT NOT NULL,
            onboarded       INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


def get_user() -> dict | None:
    """Get the local user profile, or None if not set up yet."""
    conn = _get_conn()
    row = conn.execute("SELECT name, onboarded, created_at FROM users WHERE id = 1").fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(name: str) -> dict:
    """Create the local user profile."""
    conn = _get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO users (id, name, onboarded, created_at, updated_at) VALUES (1, ?, 0, ?, ?)",
        (name.strip(), now, now),
    )
    conn.commit()
    conn.close()
    return {"name": name.strip(), "onboarded": 0, "created_at": now}


def complete_onboarding():
    """Mark onboarding as complete."""
    conn = _get_conn()
    conn.execute(
        "UPDATE users SET onboarded = 1, updated_at = ? WHERE id = 1",
        (datetime.now().isoformat(),),
    )
    conn.commit()
    conn.close()


def update_name(name: str):
    """Update the user's display name."""
    conn = _get_conn()
    conn.execute(
        "UPDATE users SET name = ?, updated_at = ? WHERE id = 1",
        (name.strip(), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
