from ..base import UseCase

META = UseCase(
    "model-router", 7, "Model router",
    "Jev decides how hard each prompt is, so easy ones go to a cheap model and hard ones to a strong one.",
    ready=True,
    summary="Twelve prompts, answered by a small and a big model. Jev rates how hard each is and judges the answers. "
            "Move the routing line and watch cost, speed and quality change.",
    highlights=(
        "A real cost comparison on real model calls",
        "A slider for where the line goes",
        "Jev judging the answers it routed",
    ),
    diagram=(
        {"label": None, "nodes": (
            {"text": "Prompt", "kind": "data"},
            {"text": "Jev", "kind": "jev", "note": "how hard is it?"},
            {"text": "Small or big model", "kind": "llm", "note": "cheap or strong"},
        )},
    ),
)
