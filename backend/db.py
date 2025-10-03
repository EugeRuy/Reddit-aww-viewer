# funciones para manejar la base SQLite.

import os
import sqlite3
from typing import Dict, Iterable, Optional, List, Any


def get_db_path() -> str:
    """Resolve absolute path to the posts.db at project root."""
    backend_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(backend_dir)
    return os.path.join(project_root, "posts.db")


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection to the project's posts.db."""
    conn = sqlite3.connect(get_db_path())
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Create the posts table if it does not exist.

    Matches expected schema:
    - id (primary key, comes from Reddit)
    - title (text)
    - text (text, optional)
    - thumbnail (text, optional)
    - link (text)
    - created_utc (integer, Unix timestamp)
    - inserted_at (timestamp, defaults to current time)
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            "text" TEXT,
            thumbnail TEXT,
            link TEXT NOT NULL,
            created_utc INTEGER NOT NULL,
            inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def insert_posts(posts: Iterable[Dict[str, Optional[object]]]) -> int:
    """Insert posts using INSERT OR IGNORE to avoid duplicates by id.

    Returns the number of rows actually inserted (duplicates are ignored).
    Expected keys in each post dict: id, title, text, thumbnail, link, created_utc
    """
    conn = get_connection()
    try:
        ensure_schema(conn)
        before = conn.total_changes
        conn.executemany(
            """
            INSERT OR IGNORE INTO posts (id, title, "text", thumbnail, link, created_utc)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                (
                    p.get("id"),
                    p.get("title"),
                    p.get("text"),
                    p.get("thumbnail"),
                    p.get("link"),
                    p.get("created_utc"),
                )
                for p in posts
            ),
        )
        conn.commit()
        after = conn.total_changes
        return max(0, after - before)
    finally:
        conn.close()


def count_posts() -> int:
    conn = get_connection()
    try:
        ensure_schema(conn)
        cur = conn.execute("SELECT COUNT(*) FROM posts")
        row = cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0
    finally:
        conn.close()


def list_posts(limit: int, offset: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        ensure_schema(conn)
        cur = conn.execute(
            'SELECT id, title, "text", thumbnail, link, created_utc FROM posts ORDER BY created_utc DESC LIMIT ? OFFSET ?',
            (int(limit), int(offset)),
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def get_post(post_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        ensure_schema(conn)
        cur = conn.execute(
            'SELECT id, title, "text", thumbnail, link, created_utc FROM posts WHERE id = ?',
            (post_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))
    finally:
        conn.close()
