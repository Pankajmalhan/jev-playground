"""Paths and environment loading. Everything else imports from here."""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
# The React build lands here (see frontend/vite.config.js) and FastAPI serves it.
STATIC_DIR = BACKEND_DIR / "static"


def load_env() -> None:
    """Read .env from the project root or backend/, without overriding real env vars."""
    for folder in (PROJECT_DIR, BACKEND_DIR):
        env = folder / ".env"
        if not env.exists():
            continue
        for raw in env.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


load_env()
