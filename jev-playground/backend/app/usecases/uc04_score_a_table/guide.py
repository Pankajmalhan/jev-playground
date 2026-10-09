"""Everything the page says, served as JSON."""

from __future__ import annotations

from . import questions, service
from .meta import META

CODE = '''# MAP: the same four questions, once per row, many at a time
def score_row(row):
    return client.system_one(state={"review": row["text"]}, questions=questions)

with ThreadPoolExecutor(max_workers=16) as pool:
    results = list(pool.map(score_row, rows))

# REDUCE: plain code adds up the answers
bugs_by_topic = Counter(r.topic for r in results if r.is_bug >= 0.5)
at_risk = sorted(results, key=lambda r: r.churn, reverse=True)[:6]'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "A table of reviews goes in. Jev tags every row, and ordinary code adds up the tags into a dashboard. "
                 "This is the pattern for any big pile of text: support tickets, survey answers, logs.",
        "roles": [
            {"name": "Jev", "role": "The tagger", "jev": True,
             "line": "Answers the same four questions about every row. One fast call each, run many at a time."},
            {"name": "Your code", "role": "The adder",
             "line": "Counts, groups and ranks the answers. No model involved, so it is instant and exact."},
        ],
        "sizes": service.SIZES,
        "questions": [{"key": k, "kind": type(q).__name__.lower(), "text": q.instructions} for k, q in questions.QUESTIONS.items()],
        "typical_cost_per_row": 0.00003,
        "claim": {
            "rows": 50_000_000, "cost": 20,
            "text": "TypeSafe's launch material gives scoring 50 million product reviews as roughly $20, against thousands of dollars with a token-billed LLM.",
        },
        "code": CODE,
        "read_first": {
            "title": "How to read the numbers",
            "body": [
                "The reviews are real app-store reviews, a thousand of them. The star rating is used as a rough answer key for sentiment. "
                "It is not perfect: a 3-star review can be positive, and a 5-star review can be sarcastic.",
                "Speed depends on how many calls are in flight (16 here) and on your distance from the service. "
                "The cost is the real input-token price applied to the tokens this run actually used.",
                "The scale table at the bottom is a straight multiplication of this run's numbers. A real job at that size would "
                "run into rate limits and need a bigger pool of workers.",
            ],
        },
    }
