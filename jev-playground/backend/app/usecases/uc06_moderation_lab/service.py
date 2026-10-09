"""Use case 6: score a labelled set of chat messages, then let the page do the arithmetic."""

from __future__ import annotations

import json
import time
from pathlib import Path

from ... import jev
from ...parallel import map_parallel
from . import questions

MESSAGES = json.loads((Path(__file__).parent / "data" / "messages.json").read_text())
_cache: dict | None = None   # the scores cost a little, so keep them for the life of the server


def ask(text: str) -> dict:
    response = jev.get_client().system_one(state={"message": text}, questions=questions.QUESTIONS)
    kind = response.answers["kind"]
    return {
        "p_harmful": round(response.answers["harmful"].noul, 4),
        "kind_pred": kind.choice,                      # Jev's guess; "kind" is our own label
        "kind_pred_p": round(kind.probabilities[kind.choice], 3),
        "tokens": response.usage.input_tokens,
    }


def run(force: bool = False) -> dict:
    global _cache
    if _cache and not force:
        return {**_cache, "cached": True}
    started = time.perf_counter()
    scored = map_parallel(lambda m: {**m, **ask(m["text"])}, MESSAGES, workers=12)
    _cache = {
        "items": scored, "count": len(scored), "seconds": round(time.perf_counter() - started, 2),
        "cost": sum(jev.cost(s["tokens"]) for s in scored),
    }
    return {**_cache, "cached": False}
