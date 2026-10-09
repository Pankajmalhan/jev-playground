"""The specialists' tools. All of them read or change small in-memory data.

Orders live in a table that is reset at the start of every run, so a refund
issued in one run does not leak into the next.
"""

from __future__ import annotations

import json
from pathlib import Path

from ... import db

DATA = Path(__file__).parent / "data"
ARTICLES = json.loads((DATA / "help.json").read_text())


@db.on_init
def seed_orders() -> None:
    db.execute(
        "CREATE TABLE support_orders (order_id INTEGER PRIMARY KEY, customer TEXT, item TEXT, amount REAL, "
        "times_charged INTEGER, status TEXT, days_since_order INTEGER, refunded REAL DEFAULT 0)"
    )
    for o in json.loads((DATA / "orders.json").read_text()):
        db.execute(
            "INSERT INTO support_orders (order_id, customer, item, amount, times_charged, status, days_since_order) "
            "VALUES (:order_id, :customer, :item, :amount, :times_charged, :status, :days_since_order)", o
        )


def reset_orders() -> None:
    db.execute("UPDATE support_orders SET refunded = 0")


def all_orders() -> list[dict]:
    return db.query("SELECT * FROM support_orders ORDER BY order_id")


def _order(order_id: int) -> dict | None:
    rows = db.query("SELECT * FROM support_orders WHERE order_id = ?", (order_id,))
    return rows[0] if rows else None


# ---- billing ----------------------------------------------------------------

def lookup_order(order_id: int) -> dict:
    return _order(order_id) or {"error": f"No order {order_id}"}


def issue_refund(order_id: int) -> dict:
    """The one tool that changes data. Policy lives here, not in the prompt: only
    extra charges are refunded, and only once."""
    order = _order(order_id)
    if not order:
        return {"error": f"No order {order_id}"}
    if order["refunded"] > 0:
        return {"error": "Already refunded"}
    extra = order["times_charged"] - 1
    if extra < 1:
        return {"error": "Not eligible: the card was charged only once"}
    amount = round(extra * order["amount"], 2)
    db.execute("UPDATE support_orders SET refunded = ? WHERE order_id = ?", (amount, order_id))
    return {"refunded": amount, "order_id": order_id}


# ---- shipping ---------------------------------------------------------------

def track_order(order_id: int) -> dict:
    order = _order(order_id)
    if not order:
        return {"error": f"No order {order_id}"}
    status, days = order["status"], order["days_since_order"]
    if status == "processing":
        eta = "Ships within 1 to 2 days."
    elif status == "shipped" and days <= 7:
        eta = "Arrives in 1 to 3 days."
    elif status == "shipped":
        eta = "Late. The carrier has been asked to trace the parcel."
    else:
        eta = "Delivered."
    return {"order_id": order_id, "status": status, "days_since_order": days, "eta": eta}


# ---- technical --------------------------------------------------------------

def search_help(query: str) -> dict:
    words = {w.strip(".,?!").lower() for w in query.split()}
    scored = sorted(((len(words & set(a["keywords"])), a) for a in ARTICLES), key=lambda s: -s[0])
    score, best = scored[0]
    if score == 0:
        return {"error": "No matching help article"}
    return {"id": best["id"], "title": best["title"], "body": best["body"]}


def spec(name: str, description: str, params: dict) -> dict:
    """How a tool is described to the model (OpenAI's tool format)."""
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": params, "required": list(params), "additionalProperties": False}}}


ORDER_ID = {"order_id": {"type": "integer"}}
