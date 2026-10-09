"""Use case 2: run one message through one lane.

The router calls ask() three times at once, once per lane, so the page can show
each lane finishing on its own.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from ... import db
from . import agent_lane, jev_lane, llm_lane, tools
from .meta import META

SLUG = META.slug
EXAMPLES = json.loads((Path(__file__).parent / "data" / "examples.json").read_text())

LANES = {"jev": jev_lane, "llm": llm_lane, "agent": agent_lane}


def ask(lane: str, text: str, with_order: bool) -> dict:
    """Run one lane. The Jev and language-model lanes see only the message,
    unless with_order is set and plain code finds an order number in it."""
    state = {"message": text}
    code_step = None
    if with_order and lane != "agent":  # the agent fetches facts itself
        t = time.perf_counter()
        order_id = tools.find_order_id(text)
        if order_id is not None:
            state["order"] = tools.lookup_order(order_id)
            code_step = {"type": "code", "note": f"Plain code found order #{order_id} in the text and looked it up.",
                         "result": state["order"], "ms": round((time.perf_counter() - t) * 1000, 2)}

    result = LANES[lane].run(state)
    if code_step:
        result["steps"].insert(0, code_step)
    result["lane"] = lane
    db.log_run(SLUG, {"text": text, "lane": lane, "with_order": with_order}, result, result["seconds"])
    return result
