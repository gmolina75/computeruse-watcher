from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable
import json

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS event_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    hostname TEXT NOT NULL,
    os TEXT NOT NULL,
    os_version TEXT,
    username TEXT,
    process_name TEXT,
    window_title TEXT,
    start_time TEXT NOT NULL,
    duration_seconds REAL,
    payload TEXT NOT NULL,
    sent_status INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_event_cache_pending ON event_cache(sent_status);
"""

class DB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def insert_event(self, event_type: str, payload: dict) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO event_cache
            (event_type, hostname, os, os_version, username, process_name, window_title,
             start_time, duration_seconds, payload, sent_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                event_type,
                payload.get("hostname"),
                payload.get("os"),
                payload.get("os_version"),
                payload.get("username"),
                payload.get("process_name"),
                payload.get("window_title"),
                payload.get("start_time") or payload.get("timestamp"),
                payload.get("duration_seconds"),
                json.dumps(payload, separators=(",", ":")),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def pending(self, limit: int = 500) -> Iterable[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM event_cache WHERE sent_status = 0 ORDER BY id ASC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        return rows

    def mark_sent(self, ids: list[int]) -> None:
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        self.conn.execute(f"UPDATE event_cache SET sent_status = 1 WHERE id IN ({placeholders})", ids)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
