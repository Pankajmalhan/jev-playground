from ..base import UseCase

META = UseCase(
    "score-a-table", 4, "Score a whole table",
    "Ask the same questions about every row of a big table, then add up the answers.",
    ready=True,
    summary="Jev tags every review in a table with sentiment, topic, bug and churn risk, in parallel. "
            "Watch the run, read the dashboard, and see what 50 million rows would cost.",
    highlights=(
        "A live run with rows per second and cost",
        "A dashboard built from the answers",
        "The real cost per row, and where it goes",
    ),
    diagram=(
        {"label": None, "nodes": (
            {"text": "1,000 reviews", "kind": "data", "note": "one row each"},
            {"text": "Jev", "kind": "jev", "note": "4 questions per row, in parallel"},
            {"text": "Dashboard", "kind": "out", "note": "counts, risk, cost"},
        )},
    ),
)
