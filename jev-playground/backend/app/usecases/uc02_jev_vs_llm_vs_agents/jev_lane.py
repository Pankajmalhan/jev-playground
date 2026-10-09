"""Lane 1: Jev. One call, three answers, each a probability."""

from __future__ import annotations

import time

from ... import jev
from . import questions


def run(state: dict) -> dict:
    started = time.perf_counter()
    response = jev.get_client().system_one(state=state, questions=questions.for_jev())
    seconds = time.perf_counter() - started

    answers = []
    for q in questions.QUESTIONS:
        item = jev.answer_to_dict(q.key, q.text, response.answers[q.key])
        names = questions.DISPLAY.get(q.key)
        if names:  # use friendly names for the options
            item["value"] = names.get(item["value"], item["value"])
            item["options"] = {names.get(k, k): v for k, v in item["options"].items()}
        answers.append(item)

    tokens = response.usage.input_tokens
    return {
        "model": jev.MODEL,
        "seconds": seconds,
        "calls": 1,
        "input_tokens": tokens,
        "output_tokens": response.usage.output_tokens,
        "cost": jev.cost(tokens),
        "answers": answers,
        "reason": None,
        "steps": [{"type": "model", "note": "One call: all three questions answered together, each as a probability.",
                   "ms": round(seconds * 1000)}],
    }
