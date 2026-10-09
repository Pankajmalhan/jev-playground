from ..base import UseCase

META = UseCase(
    "structured-decisions", 8, "Decisions from data",
    "Jev applies a written policy to structured data, so the rules live in plain English.",
    ready=True,
    summary="Expense claims go in as JSON, with the policy in plain English. Jev decides approve, refer or reject. "
            "Change a rule in the policy, run again, and watch the decisions move with no code change.",
    highlights=(
        "State that is JSON, not just text",
        "Edit the policy and see what changes",
        "Compared with the same rules written in code",
    ),
    diagram=(
        {"label": None, "nodes": (
            {"text": "Claim + policy", "kind": "data", "note": "JSON and plain English"},
            {"text": "Jev", "kind": "jev", "note": "approve, refer, reject"},
            {"text": "Auto, or a manager", "kind": "out", "note": "only if sure"},
        )},
    ),
)
