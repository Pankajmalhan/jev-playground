"""Use case 4: score every row of a table with Jev, in parallel, and summarise.

The same call is made once per review. A pool of workers keeps many calls in flight, so
the run takes seconds, not minutes. Progress streams out as it happens.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from ... import db, jev
from . import questions

WORKERS = 16
SIZES = [50, 200, 500, 1000]


def pick_rows(size: int) -> list[dict]:
    """Spread the sample across the whole table instead of taking the first rows."""
    everything = db.query("SELECT id, app, text, stars FROM reviews ORDER BY id")
    step = max(1, len(everything) // size)
    return everything[::step][:size]


def score_row(row: dict) -> dict:
    response = jev.get_client().system_one(state={"review": row["text"]}, questions=questions.QUESTIONS)
    a = response.answers
    sentiment, topic, churn = a["sentiment"], a["topic"], a["churn_risk"]
    probs = {int(k): v for k, v in (churn.probabilities or {}).items()}
    level = max(probs, key=probs.get) if probs else round(churn.score)
    return {
        "id": row["id"], "app": row["app"], "stars": row["stars"], "text": row["text"],
        "sentiment": sentiment.choice, "sentiment_p": round(sentiment.probabilities[sentiment.choice], 3),
        "topic": topic.choice, "topic_p": round(topic.probabilities[topic.choice], 3),
        "is_bug": round(a["is_bug"].noul, 3),
        "churn": level, "churn_score": round(churn.score, 2),
        "tokens": response.usage.input_tokens,
    }


def star_label(stars: int) -> str:
    return "positive" if stars >= 4 else "negative" if stars <= 2 else "neutral"


def summarise(rows: list[dict], seconds: float, errors: int) -> dict:
    n = len(rows)
    tokens = sum(r["tokens"] for r in rows)
    cost = jev.cost(tokens)
    review_tokens = sum(len(r["text"]) for r in rows) / 4 / max(n, 1)   # about 4 characters a token

    matrix = {t: Counter() for t in questions.TOPICS}
    bugs_by_topic = {t: [0, 0] for t in questions.TOPICS}   # [bug reviews, all reviews]
    for r in rows:
        matrix[r["topic"]][r["sentiment"]] += 1
        bugs_by_topic[r["topic"]][1] += 1
        bugs_by_topic[r["topic"]][0] += r["is_bug"] >= 0.5

    agree = sum(r["sentiment"] == star_label(r["stars"]) for r in rows)
    at_risk = sorted(rows, key=lambda r: (-r["churn"], -r["churn_score"]))[:6]
    return {
        "rows": n, "errors": errors, "seconds": round(seconds, 2), "rows_per_second": round(n / seconds, 1) if seconds else 0,
        "cost": cost, "cost_per_row": cost / n if n else 0,
        "avg_tokens": round(tokens / n) if n else 0, "avg_review_tokens": round(review_tokens),
        "sentiment": {s: sum(r["sentiment"] == s for r in rows) for s in questions.SENTIMENTS},
        "matrix": {t: {s: matrix[t][s] for s in questions.SENTIMENTS} for t in questions.TOPICS},
        "bugs_by_topic": {t: {"bugs": b, "all": total} for t, (b, total) in bugs_by_topic.items()},
        "bug_reviews": sum(r["is_bug"] >= 0.5 for r in rows),
        "churn": {questions.CHURN_LEVELS[i]: sum(r["churn"] == i for r in rows) for i in range(4)},
        "star_agreement": round(agree / n, 3) if n else 0,
        "at_risk": [{k: r[k] for k in ("id", "app", "stars", "churn", "text")} | {"text": r["text"][:200]} for r in at_risk],
    }


def line(event: dict) -> str:
    return json.dumps(event) + "\n"


def run_stream(size: int):
    rows = pick_rows(size)
    started = time.perf_counter()
    results, errors, tokens, last = [], 0, 0, 0.0
    yield line({"type": "start", "total": len(rows), "workers": WORKERS})
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = [pool.submit(score_row, r) for r in rows]
            for i, fut in enumerate(as_completed(futures), 1):
                try:
                    res = fut.result()
                    results.append(res)
                    tokens += res["tokens"]
                except Exception:
                    errors += 1
                now = time.perf_counter()
                if now - last > 0.35 or i == len(rows):
                    last = now
                    elapsed = now - started
                    yield line({"type": "progress", "done": i, "total": len(rows), "elapsed": round(elapsed, 2),
                                "rows_per_second": round(i / elapsed, 1), "cost": jev.cost(tokens)})
        seconds = time.perf_counter() - started
        results.sort(key=lambda r: r["id"])
        yield line({"type": "done", "summary": summarise(results, seconds, errors)})
    except Exception as exc:
        yield line({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
