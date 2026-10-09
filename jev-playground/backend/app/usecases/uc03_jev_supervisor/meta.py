from ..base import UseCase

META = UseCase(
    "jev-supervisor", 3, "Jev as supervisor",
    "A multi-agent workflow where Jev decides who acts next, and when to ask a person.",
    ready=True,
    summary="A customer message goes to a team of agents. Jev reads it, decides which specialist acts, reads what "
            "came back, decides again, and pauses for a person when it is not sure.",
    highlights=(
        "Watch the graph light up as the workflow runs",
        "See exactly what Jev was given and how sure it was",
        "Answer when Jev hands the decision to you",
    ),
    diagram=(
        {"label": "Jev decides who acts next", "nodes": (
            {"text": "Message", "kind": "data"},
            {"text": "Jev", "kind": "jev", "note": "supervisor"},
            {"text": "Specialist", "kind": "tool", "note": "billing, shipping, technical"},
        )},
        {"label": "Then checks the work", "nodes": (
            {"text": "Specialist reply", "kind": "data"},
            {"text": "Jev", "kind": "jev", "note": "next, or done?"},
            {"text": "Reply, or a person", "kind": "out"},
        )},
    ),
)
