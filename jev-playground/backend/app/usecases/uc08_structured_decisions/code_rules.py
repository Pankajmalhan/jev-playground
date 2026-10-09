"""The quick version of the policy written as ordinary if-statements.

This is what a developer would write on the first pass. It is here for comparison: it is exact
and instant, but every change to the policy means changing and shipping code, and the exceptions
(like client meals) are easy to miss.
"""

from __future__ import annotations


def decide(e: dict) -> str:
    if e.get("days_since_expense", 0) > 30:
        return "reject"
    if e["amount"] > 25 and not e.get("receipt"):
        return "reject"
    if e["category"] == "meals" and e["amount"] / max(e.get("people", 1), 1) > 50:
        return "reject"
    if e["category"] == "lodging" and e["amount"] / max(e.get("nights", 1), 1) > 200:
        return "reject"
    if e["category"] == "flight" and e.get("class") != "economy":
        return "reject"
    if e["category"] == "equipment" and e["amount"] > 100 and not e.get("manager_approved_beforehand"):
        return "refer"
    if e.get("alcohol"):
        return "reject"
    return "approve"
