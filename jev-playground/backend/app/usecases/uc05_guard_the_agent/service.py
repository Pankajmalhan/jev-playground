"""Use case 5: run one message through one agent (without or with the guard), or repeat the whole set."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import agent

SCENARIOS = json.loads((Path(__file__).parent / "data" / "scenarios.json").read_text())
LANES = {"naive": False, "guarded": True}


def run(lane: str, text: str, hard_rule: bool) -> dict:
    return agent.run(text, guarded=LANES[lane], hard_rule_on=hard_rule)


def outcome(refunded: float, expected: float) -> str:
    """Grade a run against what was actually owed."""
    if abs(refunded - expected) < 0.01:
        return "correct"
    return "overpaid" if refunded > expected else "short"


def line(event: dict) -> str:
    return json.dumps(event) + "\n"


def stress_stream(runs: int, hard_rule: bool):
    """Run every scenario `runs` times through both agents, and count how each one ended up."""
    jobs = [(sc, lane) for sc in SCENARIOS for lane in LANES for _ in range(runs)]
    tally = {sc["id"]: {lane: {"correct": 0, "overpaid": 0, "short": 0, "errors": 0, "overpaid_total": 0.0} for lane in LANES} for sc in SCENARIOS}
    started = time.perf_counter()
    yield line({"type": "start", "total": len(jobs)})

    def one(job):
        sc, lane = job
        return sc, lane, run(lane, sc["text"], hard_rule)

    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(one, j) for j in jobs]
            for i, fut in enumerate(as_completed(futures), 1):
                try:
                    sc, lane, r = fut.result()
                    kind = outcome(r["refunded_total"], sc["expected_refund"])
                    t = tally[sc["id"]][lane]
                    t[kind] += 1
                    if kind == "overpaid":
                        t["overpaid_total"] = round(t["overpaid_total"] + r["refunded_total"] - sc["expected_refund"], 2)
                except Exception:
                    pass
                yield line({"type": "progress", "done": i, "total": len(jobs)})
        yield line({"type": "done", "runs": runs, "seconds": round(time.perf_counter() - started, 1), "tally": tally})
    except Exception as exc:
        yield line({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
