"""Lane 2: a language model, forced to answer in the same shape.

One call. OpenAI's strict JSON schema makes it return exactly our fields, and
we also ask for a one-line reason, because writing is what a language model does.
"""

from __future__ import annotations

import json
import time

from ... import openai_client
from . import questions

SYSTEM = (
    "You triage customer messages for an online shop. Answer every question. "
    "'confidence' is your honest probability, from 0 to 1, that your own answer is correct. "
    "'reason' is one short sentence."
)


def run(state: dict) -> dict:
    started = time.perf_counter()
    resp = openai_client.get_client().chat.completions.create(
        model=openai_client.MODEL,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": questions.prompt(state)}],
        response_format={"type": "json_schema", "json_schema": {"name": "triage", "strict": True, "schema": questions.json_schema()}},
    )
    seconds = time.perf_counter() - started
    payload = json.loads(resp.choices[0].message.content)

    usage = resp.usage
    return {
        "model": openai_client.MODEL,
        "seconds": seconds,
        "calls": 1,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cost": openai_client.cost(usage.prompt_tokens, usage.completion_tokens),
        "answers": questions.read_llm_answers(payload),
        "reason": payload["reason"],
        "steps": [{"type": "model", "note": "One call: the answers as JSON, plus a one-line reason.",
                   "ms": round(seconds * 1000)}],
    }
