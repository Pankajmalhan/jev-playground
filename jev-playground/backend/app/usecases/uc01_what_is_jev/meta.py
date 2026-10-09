from ..base import UseCase

META = UseCase(
    "what-is-jev", 1, "What is Jev",
    "A model that decides instead of writes: fixed questions in, probabilities out.",
    ready=True,
    summary="Give Jev a customer message and it answers five fixed questions as probabilities. "
            "See what goes in, what comes out, and what happens in between.",
    highlights=(
        "Five questions answered in one call",
        "Click through the backend, stage by stage",
        "Drag a confidence threshold and watch messages move",
    ),
    diagram=(
        {"label": None, "nodes": (
            {"text": "Message", "kind": "data", "note": "a customer email"},
            {"text": "Jev", "kind": "jev", "note": "5 questions, 1 call"},
            {"text": "Answers", "kind": "out", "note": "team, urgency, refund..."},
        )},
    ),
)
