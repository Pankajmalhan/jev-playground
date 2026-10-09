"""Plain keyword retrieval: the cheap first step both pipelines share. It finds passages that share
words with the question. That is exactly why it can be fooled: sharing words is not answering."""

from __future__ import annotations

import json
import re
from pathlib import Path

KB = json.loads((Path(__file__).parent / "data" / "kb.json").read_text())
STOP = set("a an and are as at be by can do does for from how i in is it me my of on or our so that the to we what when where which who will with you your".split())


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if w not in STOP and len(w) > 1}


def search(question: str, k: int) -> list[dict]:
    q = words(question)
    scored = [(len(q & words(p["title"] + " " + p["text"])), p) for p in KB]
    ranked = sorted(scored, key=lambda s: -s[0])
    return [{**p, "keyword_score": score} for score, p in ranked[:k] if score > 0]
