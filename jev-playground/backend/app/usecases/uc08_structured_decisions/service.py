"""Use case 8: Jev decides each claim, plain code decides what happens next."""

from __future__ import annotations

import json
import time
from pathlib import Path

from ... import jev
from ...parallel import map_parallel
from . import code_rules, questions

DATA = Path(__file__).parent / "data"
POLICY = (DATA / "policy.txt").read_text()
EXPENSES = json.loads((DATA / "expenses.json").read_text())["expenses"]


def with_calculations(expense: dict) -> dict:
    """Plain code does the arithmetic and hands Jev the result. A decision model is for judging,
    not for dividing, so per-person and per-night amounts are worked out here."""
    calc = {}
    if expense.get("people"):
        calc["amount_per_person"] = round(expense["amount"] / expense["people"], 2)
    if expense.get("nights"):
        calc["amount_per_night"] = round(expense["amount"] / expense["nights"], 2)
    return {**expense, "calculated_by_code": calc} if calc else expense


def decide(expense: dict, policy: str, calculate: bool = True) -> dict:
    state = {"policy": policy, "expense": with_calculations(expense) if calculate else expense}
    started = time.perf_counter()
    r = jev.get_client().system_one(state=state, questions=questions.QUESTIONS)
    ms = round((time.perf_counter() - started) * 1000)
    a = r.answers
    pick = a["decision"]
    probs = {int(k): v for k, v in (a["fraud_risk"].probabilities or {}).items()}
    fraud = max(probs, key=probs.get) if probs else round(a["fraud_risk"].score)
    within = a["within_policy"].noul
    decision = pick.choice

    # Jev supplies the numbers. This is the plain-code rule for what happens next.
    if fraud > questions.MAX_FRAUD:
        action, why = "manager", f"Fraud risk is level {fraud}, above {questions.MAX_FRAUD}, so a person looks."
    elif decision == "approve" and within >= questions.APPROVE_AT:
        action, why = "approve", f"Jev says approve and is {within:.0%} sure it complies, at or above {questions.APPROVE_AT:.0%}."
    elif decision == "reject" and within <= questions.REJECT_AT:
        action, why = "reject", f"Jev says reject and puts only {within:.0%} on it complying, at or below {questions.REJECT_AT:.0%}."
    else:
        action, why = "manager", f"Jev says {decision} but is not sure enough ({within:.0%} complies) to act without a person."

    return {
        "decision": decision, "decision_p": round(pick.probabilities[decision], 3),
        "options": {k: round(v, 3) for k, v in pick.probabilities.items()},
        "within_policy": round(within, 3), "fraud": fraud, "action": action, "why": why,
        "state_sent": state, "ms": ms, "tokens": r.usage.input_tokens, "cost": jev.cost(r.usage.input_tokens),
    }


def batch(policy: str, calculate: bool = True) -> dict:
    started = time.perf_counter()
    rows = map_parallel(lambda e: {"id": e["id"], "title": e["title"], "expected": e["expected"], "data": e["data"],
                                   "code": code_rules.decide(e["data"]), **decide(e["data"], policy, calculate)}, EXPENSES, workers=8)
    return {"rows": rows, "seconds": round(time.perf_counter() - started, 2), "cost": sum(r["cost"] for r in rows),
            "default_policy": policy.strip() == POLICY.strip()}
