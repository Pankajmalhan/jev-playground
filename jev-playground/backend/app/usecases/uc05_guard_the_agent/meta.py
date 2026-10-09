from ..base import UseCase

META = UseCase(
    "guard-the-agent", 5, "Guard the agent",
    "Jev checks what an agent is about to do, before it does it.",
    ready=True,
    summary="A refund agent can be talked into things. Run the same message past an agent with no guard and one "
            "with Jev checking each refund, and see what actually leaves the account.",
    highlights=(
        "Two agents, one message, side by side",
        "Jev's view of each proposed refund",
        "A hard rule in code as a second layer",
    ),
    diagram=(
        {"label": None, "nodes": (
            {"text": "Agent", "kind": "llm", "note": "proposes a refund"},
            {"text": "Jev guard", "kind": "jev", "note": "allow, hold or block"},
            {"text": "Refund", "kind": "out", "note": "only if allowed"},
        )},
    ),
)
