"""Small SQLite persistence layer with no ORM dependency."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = Path(
    os.getenv("SCRIPT_WRITER_DB_PATH", BASE_DIR / "data" / "scripts.db")
)


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    database = _connect()
    try:
        yield database
        database.commit()
    except Exception:
        database.rollback()
        raise
    finally:
        database.close()


def initialize_database() -> None:
    with connection() as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                style TEXT NOT NULL,
                length TEXT NOT NULL,
                hook TEXT NOT NULL,
                introduction TEXT NOT NULL,
                main_content TEXT NOT NULL,
                call_to_action TEXT NOT NULL,
                titles TEXT NOT NULL,
                thumbnail_ideas TEXT NOT NULL,
                full_script TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                estimated_minutes REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_script(script: dict) -> int:
    with connection() as database:
        cursor = database.execute(
            """
            INSERT INTO scripts (
                topic, style, length, hook, introduction, main_content,
                call_to_action, titles, thumbnail_ideas, full_script,
                word_count, estimated_minutes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                script["topic"],
                script["style"],
                script["length"],
                script["hook"],
                script["introduction"],
                script["main_content"],
                script["call_to_action"],
                json.dumps(script["titles"]),
                json.dumps(script["thumbnail_ideas"]),
                script["full_script"],
                script["word_count"],
                script["estimated_minutes"],
            ),
        )
        return int(cursor.lastrowid)


def _deserialize(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    result = dict(row)
    result["titles"] = json.loads(result["titles"])
    result["thumbnail_ideas"] = json.loads(result["thumbnail_ideas"])
    return result


def get_script(script_id: int) -> dict | None:
    with connection() as database:
        row = database.execute(
            "SELECT * FROM scripts WHERE id = ?", (script_id,)
        ).fetchone()
    return _deserialize(row)


def list_scripts(limit: int = 12) -> list[dict]:
    with connection() as database:
        rows = database.execute(
            """
            SELECT id, topic, style, length, word_count, created_at
            FROM scripts ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]

