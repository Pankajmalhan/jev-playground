"""Run the workflow and stream what happens, one JSON line per step."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from langgraph.types import Command

from . import graph, tools

EXAMPLES = json.loads((Path(__file__).parent / "data" / "examples.json").read_text())

_runs: dict[str, dict] = {}   # thread_id -> {"events": [...], "started": float}


def _line(event: dict) -> str:
    return json.dumps(event) + "\n"


def _totals(events: list[dict]) -> dict:
    t = {"jev_calls": 0, "model_calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
    for e in events:
        for k in t:
            t[k] += e.get("usage", {}).get(k, 0)
    return t


def _stream(graph_input, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    run = _runs[thread_id]
    try:
        for update in graph.GRAPH.stream(graph_input, config, stream_mode="updates"):
            for node, payload in update.items():
                if node == "__interrupt__":
                    yield _line({"type": "paused", "thread_id": thread_id, **payload[0].value})
                    return
                event = payload["event"]
                run["events"].append(event)
                yield _line({"type": "node", **event})
        final = graph.GRAPH.get_state(config).values.get("final", "")
        yield _line({"type": "done", "final": final, "seconds": round(time.perf_counter() - run["started"], 2),
                     **_totals(run["events"])})
    except Exception as exc:  # the response has started, so the error has to travel as an event
        yield _line({"type": "error", "message": f"{type(exc).__name__}: {exc}"})


def run_stream(text: str):
    thread_id = uuid.uuid4().hex[:8]
    _runs[thread_id] = {"events": [], "started": time.perf_counter()}
    tools.reset_orders()   # every run starts from the same orders
    yield _line({"type": "start", "thread_id": thread_id, "message": text})
    yield from _stream({"message": text, "handled": []}, thread_id)


def is_waiting(thread_id: str) -> bool:
    if thread_id not in _runs:
        return False
    next_node = graph.GRAPH.get_state({"configurable": {"thread_id": thread_id}}).next
    return next_node


def resume_stream(thread_id: str, choice: str):
    yield from _stream(Command(resume=choice), thread_id)
