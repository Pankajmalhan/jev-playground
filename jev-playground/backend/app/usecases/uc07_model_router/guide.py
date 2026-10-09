"""Everything the page says, served as JSON."""

from __future__ import annotations

from . import questions
from .meta import META

CODE = '''# Before answering, Jev rates the prompt: one fast call
rating = client.system_one(state={"prompt": prompt}, questions={"difficulty": Score(...), "task": Choice(...)})
level = rating.answers["difficulty"]            # 0 trivial ... 3 hard

# The routing rule is plain code. You pick where the line goes.
model = "gpt-4o" if level >= 2 else "gpt-4o-mini"
answer = openai.chat.completions.create(model=model, messages=[...])'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "Most prompts do not need your most expensive model. A router decides, per prompt, which one to use. Jev is a good router "
                 "because the decision is a quick rating, and it has to be cheap enough that routing does not eat the savings.",
        "roles": [
            {"name": "Jev", "role": "The router", "jev": True, "line": "Rates how hard each prompt is, in one fast call, before any model answers."},
            {"name": questions.SMALL, "role": "The cheap model", "line": "Fast and about 16 times cheaper, per token, than the big one."},
            {"name": questions.BIG, "role": "The strong model", "line": "Slower to pay for, better at hard prompts. Worth it only when needed."},
        ],
        "scale": [
            {"level": 0, "name": "Trivial", "line": "A lookup, a conversion, a fix."},
            {"level": 1, "name": "Easy", "line": "A short, clear task."},
            {"level": 2, "name": "Moderate", "line": "Needs an explanation or a few steps."},
            {"level": 3, "name": "Hard", "line": "Reasoning, planning or working code."},
        ],
        "rules": [
            {"at": 0, "label": "Always the big model", "hint": "Nothing is routed. The most expensive option."},
            {"at": 1, "label": "Big from \"easy\" up", "hint": ""},
            {"at": 2, "label": "Big from \"moderate\" up", "hint": ""},
            {"at": 3, "label": "Big for \"hard\" only", "hint": ""},
            {"at": 4, "label": "Always the small model", "hint": "Nothing is routed. The cheapest option."},
        ],
        "code": CODE,
        "read_first": {
            "title": "How to read the results",
            "body": [
                "Every prompt is answered by both models, so you can move the slider and replay any routing rule without more calls. "
                "In real use you would only call the model Jev picked.",
                "Quality here is Jev's judgement. For the prompts with a known right answer, Jev compares against it; for open-ended ones, "
                "it is an opinion, not ground truth. Read the answers yourself with the arrow beside each prompt.",
                "Twelve prompts is a demonstration. In our runs the small model did as well as the big one on nearly all of them, so most of the "
                "saving comes from simply using it. The method is the point: measure this on your own prompts before you trust a rule.",
                "Routing is not free. Jev's rating adds a call (about half a second and a fraction of a cent) before every answer. "
                "Judging every answer, as this page does, is only for the demonstration and would not run in production.",
                "Prices are list prices for the two OpenAI models, set in the backend. Check them before you quote a saving.",
            ],
        },
    }
