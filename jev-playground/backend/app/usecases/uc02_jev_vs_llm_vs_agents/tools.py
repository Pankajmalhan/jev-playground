"""The agent's one tool: look up an order. It reads a small in-memory table.

The same table is what 'let plain code look it up' reads in the other lanes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ... import db

DATA = Path(__file__).parent / "data"


@db.on_init
def seed_orders() -> None:
    db.execute(
        "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer TEXT, item TEXT, amount REAL, "
        "times_charged INTEGER, status TEXT, days_since_order INTEGER)"
    )
    for o in json.loads((DATA / "orders.json").read_text()):
        db.execute(
            "INSERT INTO orders VALUES (:order_id, :customer, :item, :amount, :times_charged, :status, :days_since_order)", o
        )


def lookup_order(order_id: int) -> dict:
    rows = db.query("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    return rows[0] if rows else {"error": f"No order {order_id}"}


def all_orders() -> list[dict]:
    return db.query("SELECT * FROM orders ORDER BY order_id")


def find_order_id(text: str) -> int | None:
    """Plain code: spot an order number such as '#1042' or 'order 1042'."""
    m = re.search(r"#\s*(\d{3,6})|order\s+(\d{3,6})", text, re.I)
    return int(m.group(1) or m.group(2)) if m else None


# How the agent is told the tool exists (OpenAI's tool format).
TOOL_SPEC = [{
    "type": "function",
    "function": {
        "name": "lookup_order",
        "description": "Look up an order by its number: item, amount, how many times the card was charged, and shipping status.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}]
