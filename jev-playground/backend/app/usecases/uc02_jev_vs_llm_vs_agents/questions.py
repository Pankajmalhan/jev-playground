"""The three questions every lane answers.

Written once here, so Jev, the language model and the agent are provably asked
the same thing. Each lane turns this list into the format it needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typesafe_sdk import Choice, Noul, Score


@dataclass(frozen=True)
class Question:
    key: str
    kind: str                                     # "choice", "score" or "noul"
    text: str
    options: dict[str, str] = field(default_factory=dict)   # choice: key -> meaning
    levels: tuple[str, ...] = ()                            # score: worst to best


QUESTIONS = [
    Question(
        "department", "choice", "Which team should handle this message?",
        options={
            "billing": "Charges, refunds, invoices or payment problems.",
            "shipping": "Where an order is, delivery, or shipping delays.",
            "technical": "The product or app is broken or not working as it should.",
            "other": "Anything that fits none of the teams above.",
        },
    ),
    Question(
        "urgency", "score", "How soon does this need attention?",
        levels=("No rush at all", "Some time this week", "Today", "Right now, someone is blocked"),
    ),
    Question("refund_due", "noul", "Is the customer owed a refund?"),
]

# Friendly names for the option keys.
DISPLAY = {
    "department": {"billing": "Billing", "shipping": "Shipping", "technical": "Technical support", "other": "General inbox"},
}


# ---- Jev's format -----------------------------------------------------------

def for_jev() -> dict:
    out = {}
    for q in QUESTIONS:
        if q.kind == "choice":
            out[q.key] = Choice(instructions=q.text, criteria=q.options)
        elif q.kind == "score":
            out[q.key] = Score(instructions=q.text, criteria=list(q.levels))
        else:
            out[q.key] = Noul(instructions=q.text)
    return out


# ---- OpenAI's format: a strict JSON schema, plus a prompt -------------------

def json_schema() -> dict:
    """The shape the language model must answer in. 'strict' means OpenAI
    refuses to return anything that does not match it."""
    props = {}
    for q in QUESTIONS:
        if q.kind == "choice":
            answer = {"value": {"type": "string", "enum": list(q.options)}}
        elif q.kind == "score":
            answer = {"level": {"type": "integer", "enum": list(range(len(q.levels)))}}
        else:
            answer = {"yes": {"type": "boolean"}}
        answer["confidence"] = {"type": "number"}
        props[q.key] = {
            "type": "object", "description": q.text, "properties": answer,
            "required": list(answer), "additionalProperties": False,
        }
    props["reason"] = {"type": "string", "description": "One short sentence explaining the answers."}
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def prompt(state: dict) -> str:
    lines = ["MESSAGE:", state["message"]]
    if "order" in state:
        lines += ["", "ORDER RECORD (looked up by our system):", str(state["order"])]
    lines += ["", "QUESTIONS:"]
    for q in QUESTIONS:
        lines.append(f"- {q.key}: {q.text}")
        if q.kind == "choice":
            lines += [f"    {k}: {v}" for k, v in q.options.items()]
        elif q.kind == "score":
            lines += [f"    {i}: {v}" for i, v in enumerate(q.levels)]
        else:
            lines.append("    Answer yes (true) or no (false).")
    return "\n".join(lines)


def read_llm_answers(payload: dict) -> list[dict]:
    """Turn the language model's JSON into the same shape Jev's answers get."""
    out = []
    for q in QUESTIONS:
        got = payload[q.key]
        if q.kind == "choice":
            value = DISPLAY[q.key][got["value"]]
        elif q.kind == "score":
            value = q.levels[got["level"]]
        else:
            value = "yes" if got["yes"] else "no"
        out.append({"key": q.key, "question": q.text, "type": q.kind, "value": value,
                    "confidence": float(got["confidence"]), "options": None})
    return out
