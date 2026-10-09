"""Two questions per message. The yes/no probability is what the threshold slider works on."""

from __future__ import annotations

from typesafe_sdk import Choice, Noul

QUESTIONS = {
    "harmful": Noul(
        instructions=(
            "Should this message be removed from a community chat because it is abuse, spam or a scam? "
            "Criticism, anger, swearing for emphasis, jokes, sarcasm, and warnings about scams are not harmful."
        )
    ),
    "kind": Choice(
        instructions="If the message is a problem, what kind?",
        criteria={
            "abuse": "Insults, threats or harassment aimed at a person or group.",
            "spam": "Unwanted advertising, link dropping or engagement farming.",
            "scam": "An attempt to trick someone out of money, passwords or personal details.",
            "none": "None of these: an ordinary message.",
        },
    ),
}
