from ..base import UseCase

META = UseCase(
    "grounded-answers", 9, "Grounded answers",
    "Jev filters what a retrieval pipeline reads, refuses when the answer is not there, and checks the answer.",
    ready=True,
    summary="Ask a question of a small help centre. A plain retrieval pipeline and one gated by Jev answer side by side. "
            "See which one admits when it does not know.",
    highlights=(
        "Each passage scored for relevance by Jev",
        "A refusal when the sources do not say",
        "A check that the answer is supported",
    ),
    diagram=(
        {"label": "Plain retrieval", "nodes": (
            {"text": "Keyword search", "kind": "data"},
            {"text": "Model", "kind": "llm", "note": "answers from the top passages"},
            {"text": "Answer", "kind": "out"},
        )},
        {"label": "With Jev", "nodes": (
            {"text": "Jev", "kind": "jev", "note": "scores, gates, checks"},
            {"text": "Model", "kind": "llm", "note": "only if answerable"},
            {"text": "Supported answer, or no", "kind": "out"},
        )},
    ),
)
