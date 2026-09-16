import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "repoquest.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_id TEXT UNIQUE,
                github_login TEXT UNIQUE,
                name TEXT,
                avatar_url TEXT,
                access_token TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                repo_url TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def upsert_user(github_id: str, github_login: str, name: str | None, avatar_url: str | None, access_token: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE github_id = ? OR github_login = ?",
            (github_id, github_login),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE users SET github_id = ?, github_login = ?, name = ?, avatar_url = ?, access_token = ? WHERE id = ?",
                (github_id, github_login, name, avatar_url, access_token, row["id"]),
            )
            user_id = row["id"]
        else:
            cursor = conn.execute(
                "INSERT INTO users (github_id, github_login, name, avatar_url, access_token) VALUES (?, ?, ?, ?, ?)",
                (github_id, github_login, name, avatar_url, access_token),
            )
            user_id = cursor.lastrowid
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(user)
    finally:
        conn.close()


def create_session_for_user(user_id: int) -> str:
    session_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        conn.execute("INSERT INTO sessions (session_id, user_id, created_at) VALUES (?, ?, ?)", (session_id, user_id, utc_now()))
        conn.commit()
    finally:
        conn.close()
    return session_id


def get_user_from_session(session_id: str | None):
    if not session_id:
        return None
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()


def save_repo_history(user_id: int, repo_url: str, repo_name: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO user_history (user_id, repo_url, repo_name, created_at) VALUES (?, ?, ?, ?)",
            (user_id, repo_url, repo_name, utc_now()),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_history(user_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT repo_url, repo_name, created_at FROM user_history WHERE user_id = ? ORDER BY id DESC LIMIT 12",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_user_id_from_session(session_id: str | None):
    user = get_user_from_session(session_id)
    return user["id"] if user else None


init_db()
