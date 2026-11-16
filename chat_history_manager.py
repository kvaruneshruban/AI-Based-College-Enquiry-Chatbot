"""
Database & Chat History Manager for VR College of Engineering AI Chatbot.

Provides SQLite persistence for:
1. Conversations (ID, Title, Timestamps, Search, Delete).
2. Messages (Role, Content, Meta JSON with image/status data).
3. Recent Searches (User queries and pre-seeded quick college topics).

100% local, lightweight, thread-safe, and survives application restarts.
"""

import os
import sqlite3
import json
import datetime
import re
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.db")

DEFAULT_RECENT_SEARCHES = [
    "Available Engineering Courses",
    "College Fee Structure",
    "Hostel Facilities",
    "Placement Details",
    "Admission Process",
    "Scholarship Information",
    "Library Facilities",
    "Transportation Details"
]


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns an active SQLite database connection with row factory."""
    path = db_path or DB_FILE
    conn = sqlite3.connect(path, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None):
    """Initializes the database schema and pre-seeds default recent searches."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    meta_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS recent_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

            # Create search performance indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv_id ON messages(conversation_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at DESC);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_recent_searches_date ON recent_searches(created_at DESC);")

            # Pre-seed default searches if table is empty
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM recent_searches;")
            count = cur.fetchone()[0]
            if count == 0:
                now = datetime.datetime.now()
                for idx, item in enumerate(DEFAULT_RECENT_SEARCHES):
                    # Stagger timestamps in the past so user additions are strictly newer
                    t_str = (now - datetime.timedelta(minutes=(idx + 1) * 5)).strftime("%Y-%m-%d %H:%M:%S")
                    cur.execute(
                        "INSERT OR IGNORE INTO recent_searches (query_text, created_at) VALUES (?, ?);",
                        (item, t_str)
                    )
    finally:
        conn.close()


def generate_conversation_title(query: str) -> str:
    """
    Intelligently generates a clean, concise ChatGPT-style conversation title
    from the user's first query.
    """
    clean = query.strip()
    # Strip typical query starters for concise title
    clean = re.sub(
        r"^(what\s+is\s+the|what\s+are\s+the|tell\s+me\s+about|can\s+you\s+explain|give\s+me\s+details\s+about|how\s+to\s+apply\s+for|what\s+about)\s+",
        "",
        clean,
        flags=re.IGNORECASE
    )
    clean = clean.rstrip("?.,! ")
    
    # Capitalize words
    words = clean.split()
    if not words:
        return "New Chat"

    # Limit to first 4-5 words or 35 characters
    title = " ".join(words[:5])
    if len(title) > 35:
        title = title[:32].rstrip() + "..."
    
    return title.title()


def create_conversation(conv_id: str, title: str = "New Chat", db_path: Optional[str] = None) -> str:
    """Creates a new conversation record in the database."""
    conn = get_connection(db_path)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    try:
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?);",
                (conv_id, title, now_str, now_str)
            )
        return conv_id
    finally:
        conn.close()


def get_conversation(conv_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves metadata for a specific conversation."""
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?;", (conv_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def update_conversation_title(conv_id: str, title: str, db_path: Optional[str] = None):
    """Updates the title of an existing conversation."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "UPDATE conversations SET title = ? WHERE id = ?;",
                (title.strip(), conv_id)
            )
    finally:
        conn.close()


def save_message(
    conv_id: str,
    role: str,
    content: str,
    meta: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> int:
    """
    Saves a message in a conversation.
    If it is the first user query, updates the conversation title automatically.
    """
    conn = get_connection(db_path)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    meta_str = json.dumps(meta) if meta else None

    try:
        with conn:
            # Ensure conversation exists
            cur = conn.cursor()
            cur.execute("SELECT id, title FROM conversations WHERE id = ?;", (conv_id,))
            conv_row = cur.fetchone()

            if not conv_row:
                initial_title = generate_conversation_title(content) if role == "user" else "New Chat"
                conn.execute(
                    "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?);",
                    (conv_id, initial_title, now_str, now_str)
                )
            else:
                # If current title is default "New Chat" and this is a user message, generate title
                if role == "user" and (conv_row["title"] in ["New Chat", "Conversation"]):
                    new_title = generate_conversation_title(content)
                    conn.execute(
                        "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?;",
                        (new_title, now_str, conv_id)
                    )
                else:
                    conn.execute(
                        "UPDATE conversations SET updated_at = ? WHERE id = ?;",
                        (now_str, conv_id)
                    )

            # Insert message
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content, meta_json, created_at) VALUES (?, ?, ?, ?, ?);",
                (conv_id, role, content, meta_str, now_str)
            )
            return cur.lastrowid
    finally:
        conn.close()


def get_conversation_messages(conv_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all messages for a given conversation ordered by ID/created_at."""
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content, meta_json, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC;",
            (conv_id,)
        )
        rows = cur.fetchall()
        messages = []
        for r in rows:
            meta = None
            if r["meta_json"]:
                try:
                    meta = json.loads(r["meta_json"])
                except Exception:
                    meta = None
            messages.append({
                "role": r["role"],
                "content": r["content"],
                "meta": meta,
                "created_at": r["created_at"]
            })
        return messages
    finally:
        conn.close()


def list_conversations(
    search_query: str = "",
    limit: int = 30,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Returns list of saved conversations sorted newest first.
    If search_query is supplied, filters by title or message content.
    """
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        clean_q = search_query.strip()

        if clean_q:
            like_term = f"%{clean_q}%"
            # Find matching conversations by title OR by message text
            cur.execute("""
                SELECT DISTINCT c.id, c.title, c.created_at, c.updated_at,
                       (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.title LIKE ? OR m.content LIKE ?
                ORDER BY c.updated_at DESC
                LIMIT ?;
            """, (like_term, like_term, limit))
        else:
            cur.execute("""
                SELECT c.id, c.title, c.created_at, c.updated_at,
                       (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count
                FROM conversations c
                ORDER BY c.updated_at DESC
                LIMIT ?;
            """, (limit,))

        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_conversation(conv_id: str, db_path: Optional[str] = None) -> bool:
    """Deletes a conversation and its messages."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?;", (conv_id,))
            cur = conn.execute("DELETE FROM conversations WHERE id = ?;", (conv_id,))
            return cur.rowcount > 0
    finally:
        conn.close()


def add_recent_search(query_text: str, db_path: Optional[str] = None):
    """
    Records or bumps a user's enquiry search term into the recent_searches table.
    """
    clean = query_text.strip()
    if not clean or len(clean) < 3:
        return

    # Normalize: strip ending question mark
    clean = clean.rstrip("?.,! ")
    # Format nicely
    if len(clean) > 50:
        clean = clean[:47] + "..."

    conn = get_connection(db_path)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    try:
        with conn:
            conn.execute("""
                INSERT INTO recent_searches (query_text, created_at)
                VALUES (?, ?)
                ON CONFLICT(query_text) DO UPDATE SET created_at = excluded.created_at;
            """, (clean, now_str))
    finally:
        conn.close()


def get_recent_searches(limit: int = 8, db_path: Optional[str] = None) -> List[str]:
    """Retrieves top recent search queries, newest first."""
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT query_text FROM recent_searches ORDER BY created_at DESC, id DESC LIMIT ?;",
            (limit,)
        )
        rows = cur.fetchall()
        return [r["query_text"] for r in rows]
    finally:
        conn.close()


def delete_recent_search(query_text: str, db_path: Optional[str] = None) -> bool:
    """Removes a specific query from recent searches."""
    conn = get_connection(db_path)
    try:
        with conn:
            cur = conn.execute("DELETE FROM recent_searches WHERE query_text = ?;", (query_text.strip(),))
            return cur.rowcount > 0
    finally:
        conn.close()


# Initialize database automatically on module import
init_db()
