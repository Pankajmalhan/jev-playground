"""Use case 9: answer one question through one pipeline."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import pipelines, retrieval

QUESTIONS = json.loads((Path(__file__).parent / "data" / "questions.json").read_text())
LANES = {"plain": pipelines.plain, "jev": pipelines.with_jev}


def ask(lane: str, question: str, strict: bool = True) -> dict:
    return LANES[lane](question, strict)


def knowledge_base() -> list[dict]:
    return [{"id": p["id"], "title": p["title"], "text": p["text"]} for p in retrieval.KB]


def line(event: dict) -> str:
    return json.dumps(event) + "\n"


def run_all_stream(strict: bool):
    """Every example question through both pipelines. Streams progress, then every result."""
    jobs = [(q, lane) for q in QUESTIONS for lane in LANES]
    results = {q["id"]: {} for q in QUESTIONS}
    started = time.perf_counter()
    yield line({"type": "start", "total": len(jobs)})
    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(ask, lane, q["text"], strict): (q, lane) for q, lane in jobs}
            for i, fut in enumerate(as_completed(futures), 1):
                q, lane = futures[fut]
                try:
                    results[q["id"]][lane] = fut.result()
                except Exception as exc:
                    results[q["id"]][lane] = {"error": f"{type(exc).__name__}: {exc}"}
                yield line({"type": "progress", "done": i, "total": len(jobs)})
        yield line({"type": "done", "seconds": round(time.perf_counter() - started, 1), "results": results, "strict": strict})
    except Exception as exc:
        yield line({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
