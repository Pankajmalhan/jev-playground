"""A tiny in-memory ledger, one per run, so the two agents cannot affect each other."""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).parent / "data"


class Ledger:
    def __init__(self) -> None:
        self.orders = {o["order_id"]: dict(o) for o in json.loads((DATA / "orders.json").read_text())}
        self.refunds: list[dict] = []

    def lookup(self, order_id: int) -> dict:
        return self.orders.get(order_id) or {"error": f"No order {order_id}"}

    def refund(self, order_id: int, amount: float) -> dict:
        """A naive refund tool: it does what it is asked. Any checking has to happen before this."""
        self.refunds.append({"order_id": order_id, "amount": round(amount, 2)})
        return {"refunded": round(amount, 2), "order_id": order_id}

    @property
    def total(self) -> float:
        return round(sum(r["amount"] for r in self.refunds), 2)
