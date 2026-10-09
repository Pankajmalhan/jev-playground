"""The two pipelines. Both read the same help centre and use the same answering model.

Plain:     keyword search, take the top 2 passages, ask the model.
With Jev:  keyword search for 5 candidates, Jev scores each, drop the weak ones, Jev decides whether
           the rest can answer the question at all, and only then ask the model.
Then in both cases Jev checks the answer is supported by the passages it was given.
"""

from __future__ import annotations

import time

from ... import jev, openai_client
from ...parallel import map_parallel
from . import questions, retrieval

# The strict prompt tells the model to refuse when the passages do not answer. The loose one is what a
# first draft often looks like. Both are shown, because forgetting that line is a common mistake.
STRICT = ("You answer customer questions using only the passages provided. Cite the passage titles you used in square brackets. "
          "If the passages do not contain the answer, reply with exactly: I don't know.")
LOOSE = "You are a helpful customer support assistant. Answer the customer's question using the passages provided."


def _jev(state: dict, qs: dict):
    r = jev.get_client().system_one(state=state, questions=qs)
    return r, jev.cost(r.usage.input_tokens)


def _answer(question: str, passages: list[dict], strict: bool) -> dict:
    context = "\n\n".join(f"[{p['title']}]\n{p['text']}" for p in passages)
    started = time.perf_counter()
    resp = openai_client.get_client().chat.completions.create(
        model=openai_client.MODEL, max_completion_tokens=250,
        messages=[{"role": "system", "content": STRICT if strict else LOOSE}, {"role": "user", "content": f"PASSAGES:\n{context}\n\nQUESTION: {question}"}],
    )
    u = resp.usage
    return {"text": (resp.choices[0].message.content or "").strip(), "seconds": round(time.perf_counter() - started, 2),
            "cost": openai_client.cost(u.prompt_tokens, u.completion_tokens)}


def _check(question: str, passages: list[dict], answer: str) -> dict:
    state = {"question": question, "passages": [{"title": p["title"], "text": p["text"]} for p in passages], "answer": answer}
    r, cost = _jev(state, questions.GROUNDED)
    p = r.answers["supported"].noul
    return {"supported": round(p, 3), "flagged": p < questions.SUPPORTED_AT, "cost": cost}


def plain(question: str, strict: bool = True) -> dict:
    started = time.perf_counter()
    passages = retrieval.search(question, 2)
    ans = _answer(question, passages, strict) if passages else {"text": "I don't know.", "seconds": 0, "cost": 0}
    refused = ans["text"].lower().startswith("i don't know")
    check = None if refused else _check(question, passages, ans["text"])
    return {
        "lane": "plain", "passages": [{"id": p["id"], "title": p["title"], "kept": True} for p in passages],
        "answer": ans["text"], "refused": refused, "check": check, "gate": None,
        "calls": {"jev": 0 if refused else 1, "model": 1 if passages else 0},
        "seconds": round(time.perf_counter() - started, 2),
        "cost": ans["cost"] + (check["cost"] if check else 0),
    }


def with_jev(question: str, strict: bool = True) -> dict:
    started = time.perf_counter()
    candidates = retrieval.search(question, 5)

    def rate(p: dict) -> dict:
        r, cost = _jev({"question": question, "passage": {"title": p["title"], "text": p["text"]}}, questions.RELEVANCE)
        probs = {int(k): v for k, v in (r.answers["relevance"].probabilities or {}).items()}
        level = max(probs, key=probs.get) if probs else round(r.answers["relevance"].score)
        return {"id": p["id"], "title": p["title"], "level": level, "level_p": round(probs.get(level, 0), 3), "cost": cost,
                "kept": level >= questions.KEEP_AT}

    rated = map_parallel(rate, candidates, workers=5)
    kept_ids = {r["id"] for r in rated if r["kept"]}
    kept = [p for p in candidates if p["id"] in kept_ids]
    cost = sum(r["cost"] for r in rated)
    jev_calls = len(rated)

    gate = None
    answer, refused, check = "I don't know.", True, None
    model_calls, model_cost = 0, 0.0
    if kept:
        r, c = _jev({"question": question, "passages": [{"title": p["title"], "text": p["text"]} for p in kept]}, questions.ANSWERABLE)
        cost += c
        jev_calls += 1
        p = r.answers["answerable"].noul
        gate = {"answerable": round(p, 3), "threshold": questions.ANSWER_AT, "open": p >= questions.ANSWER_AT}
        if gate["open"]:
            ans = _answer(question, kept, strict)
            model_calls, model_cost = 1, ans["cost"]
            answer = ans["text"]
            refused = answer.lower().startswith("i don't know")
            if not refused:
                check = _check(question, kept, answer)
                cost += check["cost"]
                jev_calls += 1
    return {
        "lane": "jev", "passages": [{"id": r["id"], "title": r["title"], "kept": r["kept"], "level": r["level"], "level_p": r["level_p"]} for r in rated],
        "answer": answer, "refused": refused, "check": check, "gate": gate,
        "calls": {"jev": jev_calls, "model": model_calls},
        "seconds": round(time.perf_counter() - started, 2), "cost": cost + model_cost,
    }
