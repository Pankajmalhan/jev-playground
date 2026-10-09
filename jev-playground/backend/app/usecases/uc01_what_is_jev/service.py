"""Use case 1: one message in, five fixed questions out, then plain code routes it.

Jev only decides. It answers every question as a probability and writes no text.
What to do with those numbers (which queue, how soon) is ordinary code, below.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from typesafe_sdk import Choice, Noul, Score

from ... import db, jev
from .meta import META

SLUG = META.slug

# ---- the five questions: two yes/no, two pick-one, one score ---------------

QUESTIONS = {
    "department": Choice(
        instructions="Which team should handle this message?",
        criteria={
            "billing": "Charges, refunds, invoices, payment methods or plan prices already being paid.",
            "technical": "Something is broken, slow or not working as it should.",
            "access": "Logging in, passwords, verification codes, account security or being locked out.",
            "sales": "Buying, pricing for a new purchase, volume deals or comparing plans before paying.",
            "product": "Ideas, requests for new features, or general opinions about the product.",
            "other": "Anything that fits none of the teams above.",
        },
    ),
    "help_type": Choice(
        instructions="What kind of help does the writer need?",
        criteria={
            "payment": "A charge fixed or money returned.",
            "problem": "Something broken put right.",
            "howto": "To be shown how to do something that should already be possible.",
            "change": "A change to their account, plan or access.",
            "idea": "Nothing fixed: they are suggesting something new.",
            "none": "No help needed; they are just sharing feedback or thanks.",
        },
    ),
    "urgency": Score(
        instructions="How soon does this need attention?",
        criteria=[
            "No rush at all",
            "Some time this week",
            "Today",
            "Right now, someone is blocked",
        ],
    ),
    "needs_reply": Noul(instructions="Does this message need a reply from a person?"),
    "at_risk": Noul(instructions="Is the writer considering cancelling or leaving?"),
}

LABELS = {
    "department": "Which team should handle it?",
    "help_type": "What kind of help is needed?",
    "urgency": "How soon does it need attention?",
    "needs_reply": "Does it need a reply?",
    "at_risk": "Might they leave?",
}

# Friendly names for the option keys Jev answers with.
DISPLAY = {
    "department": {
        "billing": "Billing", "technical": "Technical support", "access": "Account access",
        "sales": "Sales", "product": "Product", "other": "General inbox",
    },
    "help_type": {
        "payment": "Fix a charge or refund", "problem": "Fix something broken",
        "howto": "Show me how", "change": "Change my account", "idea": "A suggestion",
        "none": "No help needed",
    },
}

# ---- the plain-code half: what to do with the decisions ---------------------

QUEUES = {
    "billing": "Billing team", "technical": "Technical support", "access": "Account security",
    "sales": "Sales team", "product": "Product team", "other": "General inbox",
}
PRIORITIES = {  # urgency level -> (label, response target)
    3: ("P1", "Reply right now"), 2: ("P2", "Reply today"),
    1: ("P3", "Reply this week"), 0: ("P4", "Reply when there is time"),
}
MIN_CONFIDENCE = 0.6  # below this on the department, a person decides where it goes

EXAMPLES = json.loads((Path(__file__).parent / "data" / "examples.json").read_text())


def _top(answer) -> tuple[str, float]:
    key = answer.choice
    return key, answer.probabilities.get(key, answer.confidence)


def _urgency_level(answer) -> int:
    probs = {int(k): v for k, v in (answer.probabilities or {}).items()}
    return max(probs, key=probs.get) if probs else round(answer.score)


def route(answers: dict) -> dict:
    """Ordinary if-statements. Jev decided; this is what the software does about it."""
    dept, dept_conf = _top(answers["department"])
    level = _urgency_level(answers["urgency"])
    at_risk = answers["at_risk"].noul >= 0.5
    needs_reply = answers["needs_reply"].noul >= 0.5
    help_type, _ = _top(answers["help_type"])

    reasons = []
    triage = dept_conf < MIN_CONFIDENCE
    if triage:
        reasons.append(
            f"Department confidence is only {dept_conf:.0%}, below {MIN_CONFIDENCE:.0%}, so a person decides where it goes."
        )
    if at_risk and level < 3:
        level += 1
        reasons.append("The writer may leave, so the priority goes up one level.")
    if not needs_reply and help_type == "none":
        reasons.append("No reply or help is needed, so it can be logged and closed.")

    priority, target = PRIORITIES[level]
    return {
        "queue": "Triage: a person decides" if triage else QUEUES[dept],
        "priority": priority,
        "target": target,
        "triage": triage,
        "reasons": reasons or ["Confident on the team and no special rules applied."],
    }


def _relabel(item: dict, names: dict) -> dict:
    item["value"] = names.get(item["value"], item["value"])
    item["options"] = {names.get(k, k): v for k, v in item["options"].items()}
    return item


def _ask(state: dict):
    """The one Jev call. Returns the response and how long it took."""
    started = time.perf_counter()
    response = jev.get_client().system_one(state=state, questions=QUESTIONS)
    return response, time.perf_counter() - started


def _ms(since: float) -> float:
    return round((time.perf_counter() - since) * 1000, 2)


def analyze(text: str) -> dict:
    """Run one message and keep a trace of every stage, with real timings."""
    t = time.perf_counter()
    state = {"message": text}
    questions = [
        {"key": k, "type": type(q).__name__.lower(), "instructions": q.instructions}
        for k, q in QUESTIONS.items()
    ]
    build_ms = _ms(t)

    response, seconds = _ask(state)

    t = time.perf_counter()
    answers = []
    for key in QUESTIONS:
        if key not in response.answers:
            continue
        item = jev.answer_to_dict(key, LABELS[key], response.answers[key])
        answers.append(_relabel(item, DISPLAY[key]) if key in DISPLAY else item)
    flatten_ms = _ms(t)

    t = time.perf_counter()
    routing = route(response.answers)
    rules_ms = _ms(t)

    result = {
        "model": jev.MODEL,
        "seconds": seconds,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cost": jev.cost(response.usage.input_tokens),
        "answers": answers,
        "routing": routing,
    }

    t = time.perf_counter()
    run_id = db.log_run(SLUG, {"text": text}, result, seconds)
    log_ms = _ms(t)

    dept = response.answers["department"]
    result["trace"] = [
        {"id": "request", "ms": None, "data": {"message": text}},
        {"id": "controller", "ms": None, "data": {
            "endpoint": "POST /api/what-is-jev/analyze", "characters": len(text), "check": "1 to 5000 characters: ok"}},
        {"id": "build", "ms": build_ms, "data": {"state": state, "questions": questions}},
        {"id": "jev", "ms": round(seconds * 1000, 1), "data": {
            "model": jev.MODEL,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "answers": {k: jev.raw_answer(response.answers[k]) for k in QUESTIONS if k in response.answers}}},
        {"id": "flatten", "ms": flatten_ms, "data": {
            a["key"]: {"value": a["value"], "confidence": round(a["confidence"], 3)} for a in answers}},
        {"id": "rules", "ms": rules_ms, "data": {
            "inputs": {
                "department_confidence": round(_top(dept)[1], 3),
                "urgency_level": _urgency_level(response.answers["urgency"]),
                "at_risk": round(response.answers["at_risk"].noul, 3),
            },
            "result": routing}},
        {"id": "log", "ms": log_ms, "data": {"table": "runs", "run_id": run_id}},
    ]
    return result


_batch_cache: dict | None = None


def batch(force: bool = False) -> dict:
    """Run every sample message once, in parallel, so the page can show how
    confidence varies from message to message. Cached: it costs a little."""
    global _batch_cache
    if _batch_cache and not force:
        return _batch_cache

    def one(ex: dict) -> dict:
        response, seconds = _ask({"message": ex["text"]})
        dept, conf = _top(response.answers["department"])
        names = DISPLAY["department"]
        return {
            "id": ex["id"], "title": ex["title"], "text": ex["text"],
            "department": names[dept], "confidence": conf,
            "options": {names[k]: v for k, v in response.answers["department"].probabilities.items()},
            "tokens": response.usage.input_tokens, "seconds": seconds,
        }

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        items = list(pool.map(one, EXAMPLES))
    _batch_cache = {
        "items": items,
        "calls": len(items),
        "wall_seconds": time.perf_counter() - started,
        "cost": sum(jev.cost(i["tokens"]) for i in items),
        "threshold": MIN_CONFIDENCE,
    }
    return _batch_cache


def history() -> list[dict]:
    return db.recent_runs(SLUG)
