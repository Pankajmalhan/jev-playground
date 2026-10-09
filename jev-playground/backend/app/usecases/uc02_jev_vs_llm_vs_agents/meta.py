from ..base import UseCase

META = UseCase(
    "jev-vs-llm-vs-agents", 2, "Jev vs LLM vs agent",
    "The same job given to a decision model, a language model and an agent, side by side.",
    ready=True,
    summary="One message goes to Jev, a language model and an agent at the same moment. "
            "See which is fastest, which is cheapest, and which one checks the facts.",
    highlights=(
        "A live race with time, calls and cost",
        "An answer key: who got it right",
        "A picker for which one to use",
    ),
    diagram=(
        {"label": "Jev", "nodes": (
            {"text": "Message", "kind": "data"},
            {"text": "Jev", "kind": "jev", "note": "1 call"},
            {"text": "Numbers", "kind": "out"},
        )},
        {"label": "Language model", "nodes": (
            {"text": "Message", "kind": "data"},
            {"text": "Model", "kind": "llm", "note": "1 call"},
            {"text": "JSON + words", "kind": "out"},
        )},
        {"label": "Agent", "nodes": (
            {"text": "Message", "kind": "data"},
            {"text": "Model + tool", "kind": "tool", "note": "loops until done"},
            {"text": "Answers + steps", "kind": "out"},
        )},
    ),
)
