"""Everything the page says, served as JSON."""

from __future__ import annotations

from .meta import META

CODE = '''# One call per message: a yes/no probability, and what kind of problem it is
response = client.system_one(
    state={"message": text},
    questions={"harmful": Noul(...), "kind": Choice(abuse, spam, scam, none)},
)
p = response.answers["harmful"].noul          # 0.94

# The threshold is YOUR decision, in plain code. Move it, and the trade-off moves.
flag = p >= 0.5'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "Jev gives every chat message a probability of being harmful. Where you draw the line is up to you, and every line "
                 "costs something. This lab lets you see the cost, and checks whether the probabilities can be trusted.",
        "roles": [
            {"name": "Jev", "role": "The scorer", "jev": True, "line": "Gives each message a probability of being abuse, spam or a scam, and says which kind."},
            {"name": "The threshold", "role": "Your decision", "line": "A number in plain code. Lower it and you catch more but flag innocent messages. Raise it and the reverse."},
        ],
        "terms": [
            {"name": "False alarm", "line": "A fine message that got flagged. Someone is annoyed, and a moderator wastes time."},
            {"name": "Miss", "line": "A harmful message that got through. The thing you set out to stop."},
            {"name": "Precision", "line": "Of everything flagged, how much was really harmful."},
            {"name": "Recall", "line": "Of everything harmful, how much was caught."},
        ],
        "calibration": {
            "what": "A calibrated model's \"80% sure\" should be right about 80% of the time. Messages are grouped by the probability Jev gave them, "
                    "and each group's real rate of harm is compared with what Jev said. Points on the diagonal mean the confidence is honest.",
            "ece": "ECE is the average gap between what Jev said and what happened, weighted by group size. Brier is the average squared "
                   "error of the probabilities. Lower is better for both.",
            "context": "TypeSafe says Jev is calibrated. Outside research on LLM-based moderation models finds many are overconfident, with calibration "
                       "errors above 0.10 common. That is the reason to measure it on your own data instead of trusting a claim.",
        },
        "code": CODE,
        "read_first": {
            "title": "How to read this",
            "body": [
                "The 76 messages were written for this page, and the labels are our opinion. Sixteen are marked \"contested\": reasonable people could "
                "label them differently, such as friendly banter that sounds rude, or a plausible account notice with no context.",
                "76 messages is a demonstration, not a benchmark. With so few in each group, the calibration chart can move a lot from small changes. "
                "To trust a threshold, run this on hundreds of your own messages with labels from your own moderators.",
                "The scores are cached after the first run, so moving the slider is instant and free.",
            ],
        },
    }
