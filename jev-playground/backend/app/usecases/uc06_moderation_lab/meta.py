from ..base import UseCase

META = UseCase(
    "moderation-lab", 6, "Moderation and calibration",
    "Flag harmful chat messages, tune the threshold, and test whether Jev's confidence can be trusted.",
    ready=True,
    summary="Seventy-six labelled chat messages, including tricky ones that should not be flagged. Drag the threshold and watch "
            "misses and false alarms trade off, then check whether 90% sure really means 90% right.",
    highlights=(
        "A threshold slider with a live confusion matrix",
        "Tricky cases that look bad but are fine",
        "A reliability chart: is the confidence honest?",
    ),
    diagram=(
        {"label": None, "nodes": (
            {"text": "Chat message", "kind": "data"},
            {"text": "Jev", "kind": "jev", "note": "harmful? how sure?"},
            {"text": "Threshold", "kind": "out", "note": "flag, or let through"},
        )},
    ),
)
