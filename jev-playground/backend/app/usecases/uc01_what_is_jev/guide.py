"""Everything the page says, served as JSON.

The page is interactive, so this is data for components, not prose to scroll:
  about    background from TypeSafe AI's launch article
  demo     how this particular page works, built from the real code

The questions and their code snippets are generated from service.QUESTIONS,
so this text cannot drift from what the code actually asks.
"""

from __future__ import annotations

from . import service
from .meta import META

ARTICLE = {
    "label": "Introducing System One Models & Jev (TypeSafe AI)",
    "url": "https://typesafe.ai/blog/introducing-system-one-models-and-jev",
}

KINDS = {
    "noul": ("Yes or no", "One probability that the answer is yes."),
    "choice": ("Pick one", "A probability for every option; the highest wins."),
    "score": ("Score", "A probability for every level, plus a score between them."),
}


def about() -> dict:
    return {
        "source": ARTICLE,
        "intro": "Jev is a model you call like a function: text goes in, typed decisions come out.",
        "definition": (
            "TypeSafe AI, the company behind Jev, calls it \"a frontier-intelligence function call: unstructured "
            "state in, typed probabilistic decisions out.\""
        ),
        "facts": [
            {"head": "It decides, it doesn't write", "body": "Every answer is yes/no, one option from a list, or a score. Never a sentence."},
            {"head": "Every answer has a probability", "body": "So your code can tell a sure answer from a guess."},
            {"head": "One call, many questions", "body": "All the questions are answered together, in parallel."},
        ],
        "name": [
            "The name comes from Daniel Kahneman's Thinking, Fast and Slow. System 1 is fast and intuitive; System 2 is "
            "slow and deliberate. Most of what software needs from AI is the fast kind: is this urgent, which team owns "
            "it, is this safe. TypeSafe's founder, Diogo Almeida, asks: models have been superhuman at chat for years, "
            "so where is all the automation?",
            "Jev itself is named after William Stanley Jevons, who noticed that coal use grew, not shrank, once steam "
            "engines got more efficient. TypeSafe expects machine intelligence to follow a similar adoption curve.",
        ],
        "compare": {
            "headers": ["", "A language model", "Jev"],
            "rows": [
                ["What comes out", "Text. Flexible, but you have to parse and validate it.",
                 "Typed values from the options you define. No parsing step."],
                ["How the answer is produced", "One token at a time, in sequence.",
                 "Every output in parallel, in a single query."],
                ["What it is trained for", "Human preference (RLHF, RLVR).",
                 "Calibrated decisions (RLCD): answers with honest probabilities."],
                ["Hallucination", "Can invent facts and break the format you asked for.",
                 "TypeSafe says it cannot hallucinate and never makes type errors. Its answers are always values you defined."],
                ["Confidence", "Often overconfident, and inconsistent between runs.",
                 "Every answer carries a calibrated probability."],
            ],
        },
        "contrast": {
            "note": "An illustration of the two shapes. The language-model reply is typical, not a live call.",
            "llm": {
                "label": "A language model",
                "output": (
                    "\"Thanks for flagging this! This customer sounds pretty frustrated, so I'd say it's fairly urgent, "
                    "maybe a 4 out of 5. It's mostly a billing matter, though it could be an account issue. "
                    "They might churn if nobody replies soon.\""
                ),
                "code": (
                    '# hope it phrases the score this way...\n'
                    'm = re.search(r"(\\d) out of 5", reply)\n'
                    'urgency = int(m.group(1)) if m else None\n\n'
                    '# "billing, or maybe an account issue"?\n'
                    'team = "billing" if "billing" in reply.lower() else "other"\n\n'
                    '# at risk of leaving? search for "churn", "cancel"...'
                ),
                "points": [
                    "A paragraph your code has to parse before it can act.",
                    "Different wording on another day breaks the parsing.",
                    "\"Mostly billing, could be account\" has no number: how sure is it?",
                ],
            },
            "jev": {
                "label": "Jev",
                "output": (
                    '{\n  "department": { "billing": 0.99, "access": 0.01, ... },\n'
                    '  "urgency":    { "2": 0.89, "3": 0.11, ... },\n'
                    '  "at_risk":    { "yes": 0.17, "no": 0.83 }\n}'
                ),
                "code": (
                    '# always one of your options\n'
                    'team = answers["department"].choice\n\n'
                    '# a number for every level\n'
                    'urgency = answers["urgency"].probabilities\n\n'
                    '# 0.17\n'
                    'at_risk = answers["at_risk"].noul'
                ),
                "points": [
                    "Values your code can branch on straight away.",
                    "The shape is the same every time, so there is nothing to parse.",
                    "Every answer says how sure it is.",
                ],
            },
        },
        "calibration": {
            "quote": "If a model can do a task 95% of the time but doesn't say when it's in the 5%, it can't automate that task.",
            "body": (
                "A calibrated probability is how Jev says when it is in the 5%. Higher confidence should mean higher "
                "accuracy, so your code can act on the sure answers and hand the unsure ones to a person. "
                "Below, every sample message is answered once. Drag the threshold to decide how sure is sure enough."
            ),
        },
        "speed": {
            "llm_seconds": [3, 329],
            "jev_seconds": [0.07, 0.5],
            "llm_input_per_mtok": [0.20, 10],
            "jev_input_per_mtok": 0.042,
            "default_tokens": 700,
            "llm_label": "Frontier models, TypeSafe's cited benchmark",
            "read_first": {
                "title": "Read this before comparing the bars",
                "body": [
                    "TypeSafe quotes 3 to 329 seconds for \"frontier models\" and links an outside benchmark site for it. "
                    "The article does not say which models, which settings (reasoning on or off) or which tasks produced the range, "
                    "and we could not open that source to check it.",
                    "A range this wide most likely includes reasoning models that think for a long time before they answer. "
                    "A small, fast language model on a short classification like this one can typically answer in about a second "
                    "(not measured here), so for this kind of task the real gap may be much smaller than 40x to 200x.",
                    "Treat the long bar as TypeSafe's claim about a different kind of model. The fair test is the language model "
                    "you would actually use, on your own messages. If you have timed one, enter it below.",
                ],
            },
            "claims": [
                "TypeSafe's claim: 40x to 200x faster than those frontier models, for the same level of intelligence on queries shaped like this.",
                "Jev's output tokens are free. TypeSafe says language-model output costs about 5x the input price.",
            ],
            "price_note": (
                "The $0.20 to $10 range runs from small models to flagships. Against the cheapest end, Jev's input price is about "
                "5x lower, not hundreds of times; against the most expensive end it is about 240x lower."
            ),
            "caveat": (
                "These are TypeSafe's own figures. They say their evals run from West Coast laptops close to the service, "
                "and that they cannot prove the pricing is unsubsidised. The time and cost on every run above are measured "
                "on your own calls."
            ),
        },
        "use": [
            {"name": "Smart if-statements", "note": "AI-powered workflows where a rule needs judgement."},
            {"name": "Map-reducing over big data",
             "note": "Ask the same question about every row of a big table, then add up the answers. "
                     "For example, tag 1,000 reviews by topic, then count how many are about bugs."},
            {"name": "Real-time applications", "note": "Anything that needs an answer in around 100 ms."},
            {"name": "Verifying everything", "note": "Score, judge, verify, guardrail and detect jailbreaks."},
        ],
        "avoid": [
            {"name": "Anything that has to write", "note": "Jev gives up string generation."},
            {"name": "Chatbots, copilots and coding agents", "note": "Human-in-the-loop work where freedom matters."},
            {"name": "Verifiable problems", "note": "Math proofs, kernel optimisation."},
        ],
    }


def _snippet(key: str, q) -> str:
    kind = type(q).__name__
    lines = [f'"{key}": {kind}(', f'    instructions="{q.instructions}",']
    criteria = getattr(q, "criteria", None)
    if isinstance(criteria, dict):
        lines.append("    criteria={")
        lines += [f'        "{k}": "{v}",' for k, v in criteria.items()]
        lines.append("    },")
    elif criteria:
        lines.append("    criteria=[")
        lines += [f'        "{v}",' for v in criteria]
        lines.append("    ],")
    lines.append("),")
    return "\n".join(lines)


def _questions() -> list[dict]:
    out = []
    for key, q in service.QUESTIONS.items():
        kind = type(q).__name__.lower()
        label, returns = KINDS[kind]
        criteria = getattr(q, "criteria", None)
        names = service.DISPLAY.get(key, {})
        if isinstance(criteria, dict):
            options = [{"name": names.get(k, k), "meaning": v} for k, v in criteria.items()]
        elif criteria:
            options = [{"name": f"Level {i}", "meaning": v} for i, v in enumerate(criteria)]
        else:
            options = [{"name": "yes", "meaning": "The answer is yes."}, {"name": "no", "meaning": "The answer is no."}]
        out.append({
            "key": key, "tab": service.LABELS[key], "kind": label, "returns": returns,
            "question": q.instructions, "options": options, "code": _snippet(key, q),
        })
    return out


CODE_BUILD = '''state = {"message": text}
questions = {
    "department": Choice(instructions="Which team should handle this message?", criteria={...}),
    "urgency":    Score(instructions="How soon does this need attention?", criteria=[...]),
    "needs_reply": Noul(instructions="Does this message need a reply from a person?"),
    ...  # help_type, at_risk
}'''

CODE_JEV = '''# One call. The message is the "state"; the questions say what to decide about it.
response = client.system_one(state=state, questions=questions)

response.answers["department"].choice          # "billing"
response.answers["department"].probabilities   # {"billing": 0.99, "technical": 0.0, ...}
response.answers["urgency"].probabilities      # {0: 0.0, 1: 0.0, 2: 0.89, 3: 0.11}
response.answers["needs_reply"].noul           # 0.91  (probability of "yes")
response.usage.input_tokens                    # the only thing you pay for'''

CODE_RULES = '''if department_confidence < 0.6:   queue = "Triage: a person decides"
else:                             queue = QUEUES[department]

if at_risk >= 0.5 and level < 3:  level += 1     # may leave: bump the priority'''


def demo() -> dict:
    n = len(service.QUESTIONS)
    return {
        "summary": (
            f"You write a customer message. This page sends it to Jev with {n} fixed questions and gets back {n} answers "
            "in a single call. A few ordinary if-statements then turn those answers into a queue and a priority. "
            "Jev decides; your code acts."
        ),
        "questions": _questions(),
        "steps": [
            {"id": "request", "label": "You", "layer": "Browser", "file": "WhatIsJev.jsx",
             "title": "You send a message",
             "detail": "The page posts your text to the API. Nothing else is sent.",
             "data_note": "The request body."},
            {"id": "controller", "label": "Controller", "layer": "Controller", "file": "router.py",
             "title": "The API receives it",
             "detail": "Checks the text is 1 to 5,000 characters and hands it to the service. No logic lives here, so there is one place to look when something is wrong.",
             "data_note": "What the controller checked."},
            {"id": "build", "label": "Build request", "layer": "Service", "file": "service.py",
             "title": "Build one request",
             "detail": f'Wraps the text as state = {{"message": text}} and attaches all {n} questions. Each question is a type '
                       "(yes/no, pick one or score), an instruction, and the meaning of each option.",
             "data_note": "Exactly what is handed to Jev.", "code": CODE_BUILD},
            {"id": "jev", "label": "Jev", "layer": "Jev", "file": "typesafe_sdk", "highlight": True,
             "title": f"One call, {n} answers",
             "detail": "Jev reads the message once and works out every answer in parallel, each as a probability. It writes no "
                       "sentences, so there is nothing to parse and nothing that can come back in the wrong shape.",
             "data_note": "The raw answers, as Jev returned them.", "code": CODE_JEV},
            {"id": "flatten", "label": "Flatten", "layer": "Service", "file": "jev.py",
             "title": "Flatten the answers",
             "detail": "Turns each answer into a winning value and a confidence, and keeps the full spread of options for the bars. "
                       "Cost is worked out from input tokens only; output is free.",
             "data_note": "One winning value and confidence per question."},
            {"id": "rules", "label": "Rules", "layer": "Service", "file": "service.py", "tag": "no model",
             "title": "Plain code decides what to do",
             "detail": "Ordinary if-statements read the numbers. The queue comes from the team; the priority comes from the urgency, "
                       "one level higher if the writer may leave; and if Jev is under 60% sure of the team, the message goes to a "
                       "person to triage instead.",
             "data_note": "The numbers the rules read, and what they decided.", "code": CODE_RULES},
            {"id": "log", "label": "Log", "layer": "Database", "file": "db.py",
             "title": "Log the run",
             "detail": "Saves the input, the answers and the time to the in-memory runs table, which feeds the history at the bottom of "
                       "the page. Restarting the server clears it.",
             "data_note": "The row that was written."},
        ],
    }


def build() -> dict:
    return {"title": META.title, "about": about(), "demo": demo()}
