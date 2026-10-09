"""The four questions asked about every review, in one call per row."""

from __future__ import annotations

from typesafe_sdk import Choice, Noul, Score

QUESTIONS = {
    "sentiment": Choice(
        instructions="What is the reviewer's overall feeling about the app?",
        criteria={
            "positive": "Pleased, thankful, or recommending it.",
            "neutral": "Mixed, factual, or no strong feeling either way.",
            "negative": "Annoyed, disappointed, or complaining.",
        },
    ),
    "topic": Choice(
        instructions="What is the review mainly about?",
        criteria={
            "performance": "Speed, battery use, crashes on start, lag, or memory.",
            "ui": "Layout, design, colours, readability or ease of use.",
            "features": "What the app can or cannot do, or features the reviewer wants.",
            "pricing": "Cost, ads, subscriptions, or paid versions.",
            "bugs": "Something that is broken or does not work as it should.",
            "other": "Anything that fits none of the above.",
        },
    ),
    "is_bug": Noul(instructions="Does the review report a concrete defect, something that is broken?"),
    "churn_risk": Score(
        instructions="How likely is this reviewer to stop using the app?",
        criteria=[
            "Committed: happy and staying",
            "Leaning: some annoyance, probably staying",
            "Wavering: serious frustration, may leave",
            "Gone: has stopped or is about to stop using it",
        ],
    ),
}

TOPICS = ["performance", "ui", "features", "pricing", "bugs", "other"]
SENTIMENTS = ["positive", "neutral", "negative"]
CHURN_LEVELS = ["Committed", "Leaning", "Wavering", "Gone"]
