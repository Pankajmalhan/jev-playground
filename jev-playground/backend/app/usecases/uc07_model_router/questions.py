"""What Jev is asked: how hard is the prompt (the routing decision), and was the answer good (the check)."""

from __future__ import annotations

from typesafe_sdk import Choice, Noul, Score

SMALL = "gpt-4o-mini"
BIG = "gpt-4o"

ROUTER_QUESTIONS = {
    "difficulty": Score(
        instructions="How hard is this prompt for an AI model to answer correctly?",
        criteria=[
            "Trivial: a simple lookup, conversion or fix",
            "Easy: a short, clear task with an obvious answer",
            "Moderate: needs a clear explanation or a few steps of thought",
            "Hard: needs careful reasoning, a trick to spot, planning or working code",
        ],
    ),
    "task": Choice(
        instructions="What kind of task is this?",
        criteria={
            "lookup": "A fact, a conversion or a simple fix.",
            "rewrite": "Rewriting, summarising or rephrasing given text.",
            "explain": "Explaining a concept.",
            "reasoning": "A puzzle, a calculation or a logic problem.",
            "build": "Writing code, or a plan or recommendation.",
        },
    ),
}

JUDGE_QUESTIONS = {
    "good_answer": Noul(instructions="Is the answer correct, complete and a direct response to the prompt? If a reference answer is given, it must agree with it."),
}
