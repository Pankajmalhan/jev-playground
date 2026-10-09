"""In-memory SQLite shared by every use case.

Nothing is written to disk: the data is seeded at startup and disappears on
restart, which is exactly what a demo wants. One connection plus a lock keeps
FastAPI's threadpool from stepping on itself.
"""

from __future__ import annotations

import json
import sqlite3
import threading

from .config import DATA_DIR

_conn: sqlite3.Connection | None = None
_lock = threading.RLock()
_seeds: list = []


def on_init(fn):
    """Decorator: run fn() at startup, after the shared tables exist.

    A use case calls this to create and fill the tables only it needs."""
    _seeds.append(fn)
    return fn

SCHEMA = """
CREATE TABLE reviews (
    id    INTEGER PRIMARY KEY,
    app   TEXT,
    text  TEXT NOT NULL,
    stars INTEGER,
    date  TEXT
);
-- every use case logs its runs here, so each tab can show a history
CREATE TABLE runs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    usecase    TEXT NOT NULL,
    input      TEXT NOT NULL,
    output     TEXT NOT NULL,
    seconds    REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db() -> None:
    global _conn
    with _lock:
        _conn = sqlite3.connect(":memory:", check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript(SCHEMA)
        seed = DATA_DIR / "reviews.jsonl"
        if seed.exists():
            rows = [json.loads(line) for line in seed.read_text().splitlines() if line.strip()]
            _conn.executemany(
                "INSERT INTO reviews (id, app, text, stars, date) VALUES (:id, :app, :text, :stars, :date)",
                rows,
            )
        _conn.commit()
        for seed in _seeds:
            seed()


def query(sql: str, params: tuple | dict = ()) -> list[dict]:
    with _lock:
        assert _conn is not None, "init_db() has not run"
        return [dict(r) for r in _conn.execute(sql, params).fetchall()]


def execute(sql: str, params: tuple | dict = ()) -> int:
    with _lock:
        assert _conn is not None, "init_db() has not run"
        cur = _conn.execute(sql, params)
        _conn.commit()
        return cur.lastrowid


def log_run(usecase: str, input_: dict, output: dict, seconds: float) -> int:
    return execute(
        "INSERT INTO runs (usecase, input, output, seconds) VALUES (?, ?, ?, ?)",
        (usecase, json.dumps(input_), json.dumps(output), seconds),
    )


def recent_runs(usecase: str, limit: int = 10) -> list[dict]:
    rows = query(
        "SELECT id, input, output, seconds, created_at FROM runs WHERE usecase = ? ORDER BY id DESC LIMIT ?",
        (usecase, limit),
    )
    for r in rows:
        r["input"] = json.loads(r["input"])
        r["output"] = json.loads(r["output"])
    return rows
