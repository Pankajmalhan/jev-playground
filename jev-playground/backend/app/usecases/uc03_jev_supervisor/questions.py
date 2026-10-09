"""The questions Jev answers, and the thresholds the plain-code rules use.

Jev is asked in two places: the supervisor (who acts next?) and the verifier
(does the reply answer everything?). Both are here so they are easy to find.
"""

from __future__ import annotations

from typesafe_sdk import Choice, Noul

AGENTS = ("billing", "shipping", "technical")

ROUTE_CONFIDENCE = 0.6   # below this, the supervisor hands the decision to a person
PERSON_AT = 0.5          # at or above this, a person should handle the message
VERIFY_AT = 0.6          # below this, the final reply is flagged for a person to check
MAX_SPECIALISTS = 3      # a safety stop for the loop


def supervisor_questions(first_pass: bool) -> dict:
    """Who acts next? On the first pass we also ask whether a person should handle it."""
    questions = {
        "next_agent": Choice(
            instructions=(
                "Look at the customer's message and what has already been handled. "
                "Who should act next?"
            ),
            criteria={
                "billing": "A charge, refund, invoice or payment problem that has not been answered yet.",
                "shipping": "Where an order is, or a delivery or shipping delay, that has not been answered yet.",
                "technical": "The product or app is broken or not working, and that has not been answered yet.",
                "done": "Every part of the customer's message has already been answered in already_handled.",
            },
        )
    }
    if first_pass:
        questions["needs_person"] = Noul(
            instructions=(
                "Does this message contain a legal threat, abuse, or an account-security problem "
                "that a person should handle instead of an automated agent?"
            )
        )
    return questions


VERIFY_QUESTIONS = {
    "answers_everything": Noul(instructions="Does the reply address everything the customer asked about?"),
}
