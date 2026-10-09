"""Everything the page says, served as JSON."""

from __future__ import annotations

from . import questions
from .meta import META

CODE = '''# 1. Cheap keyword search finds candidates. It matches words, not meaning.
candidates = search(question, k=5)

# 2. Jev scores every candidate at once: how useful is this passage for this question?
levels = map_parallel(lambda p: system_one(state={"question": q, "passage": p}, questions={"relevance": Score(...)}), candidates)
kept = [p for p, level in zip(candidates, levels) if level >= 2]

# 3. Jev decides whether the kept passages can answer it at all. If not, stop: no model call.
if system_one(state={"question": q, "passages": kept}, questions={"answerable": Noul(...)}).noul < 0.5:
    return "I don't know."

# 4. The model answers from the kept passages only.
answer = openai.chat.completions.create(model=..., messages=[system, passages, question])

# 5. Jev checks the answer is supported by what the model was given.
supported = system_one(state={"passages": kept, "answer": answer}, questions={"supported": Noul(...)}).noul
flagged = supported < 0.6'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "A question goes to a small help centre. A retrieval pipeline finds passages and a model writes the answer. "
                 "The risk is an answer that sounds right but is not in the sources. Here Jev sits at three points in the pipeline to catch that.",
        "roles": [
            {"name": "Keyword search", "role": "The finder", "line": "Matches words in the question to words in the passages. Quick and cheap, but sharing words is not answering."},
            {"name": "Jev", "role": "The checker", "jev": True, "line": "Scores each passage, decides whether the answer is there at all, then checks the finished answer against its sources."},
            {"name": "gpt-4o-mini", "role": "The writer", "line": "Writes the answer from whatever passages it is given. It only sees what survives the filter."},
        ],
        "steps": [
            {"n": 1, "who": "Search", "title": "Find candidates", "line": "Keyword matching picks the five passages that share the most words with the question."},
            {"n": 2, "who": "Jev", "title": "Score each passage", "line": "Is this passage useful for this question? Rated 0 to 3, for all five at once. Weak ones are dropped."},
            {"n": 3, "who": "Jev", "title": "Can it be answered at all?", "line": "A yes/no on the passages that are left. If not, the pipeline stops and says it does not know. No model call."},
            {"n": 4, "who": "Model", "title": "Write the answer", "line": "Only from the passages that survived."},
            {"n": 5, "who": "Jev", "title": "Check the answer", "line": "Is every claim supported by those passages? Under 60%, the answer is flagged."},
        ],
        "thresholds": {"keep": questions.KEEP_AT, "answer": questions.ANSWER_AT, "supported": questions.SUPPORTED_AT},
        "code": CODE,
        "read_first": {
            "title": "How to read the results",
            "body": [
                "The help centre is twelve short invented articles, and the eight questions come with a note on whether the sources answer them. "
                "Four do. Four do not, and are there to tempt a pipeline into making something up.",
                "The model is told to say \"I don't know\" when the passages do not answer. That instruction is on by default so the plain pipeline gets a fair "
                "chance. Turn it off to see what happens when that line is forgotten, which is a common first draft.",
                "gpt-4o-mini is cautious. With the instruction on, it rarely invents anything, but it sometimes refuses a question the sources do answer. "
                "Count both kinds of mistake, not only the invented answers.",
                "Jev's support check is an opinion, not proof. It can flag a fine answer or pass a loose one. It is a cheap second look, not a replacement for reading the sources.",
            ],
        },
    }
