"""What Jev is asked at each of the three points, and the thresholds the plain rules use."""

from __future__ import annotations

from typesafe_sdk import Noul, Score

RELEVANCE = {
    "relevance": Score(
        instructions="How useful is this passage for answering the question?",
        criteria=[
            "Unrelated: it does not help",
            "Related topic only: same subject, but it does not contain the answer",
            "Partly useful: contains some of what is needed",
            "Directly answers the question",
        ],
    ),
}
ANSWERABLE = {
    "answerable": Noul(instructions="Do the passages contain what is needed to answer the question? Mentioning the topic is not enough."),
}
GROUNDED = {
    "supported": Noul(instructions="Is every claim in the answer supported by the passages, with nothing added from outside them?"),
}

KEEP_AT = 2          # passages rated at least this useful are kept
ANSWER_AT = 0.5      # below this chance that the passages answer it, refuse
SUPPORTED_AT = 0.6   # below this, the answer is flagged as unsupported
