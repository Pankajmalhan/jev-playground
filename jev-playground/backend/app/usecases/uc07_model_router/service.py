"""Use case 7: for every prompt, Jev rates the difficulty, both models answer, and Jev judges both answers.

Every prompt is answered by BOTH models, so the page can replay any routing rule afterwards without
more calls. That is what makes the slider free to move.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ... import jev, openai_client
from . import questions

PROMPTS = json.loads((Path(__file__).parent / "data" / "prompts.json").read_text())
SYSTEM = "Answer the user's request clearly and concisely."


def line(event: dict) -> str:
    return json.dumps(event) + "\n"


def rate(prompt: dict) -> dict:
    started = time.perf_counter()
    r = jev.get_client().system_one(state={"prompt": prompt["text"]}, questions=questions.ROUTER_QUESTIONS)
    ms = round((time.perf_counter() - started) * 1000)
    probs = {int(k): v for k, v in (r.answers["difficulty"].probabilities or {}).items()}
    level = max(probs, key=probs.get) if probs else round(r.answers["difficulty"].score)
    return {"difficulty": level, "difficulty_p": round(probs.get(level, 0), 3), "task": r.answers["task"].choice, "ms": ms,
            "cost": jev.cost(r.usage.input_tokens)}


def answer(model: str, prompt: dict) -> dict:
    started = time.perf_counter()
    resp = openai_client.get_client().chat.completions.create(
        model=model, messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt["text"]}], max_completion_tokens=350,
    )
    seconds = time.perf_counter() - started
    u = resp.usage
    return {"model": model, "text": (resp.choices[0].message.content or "").strip(), "seconds": round(seconds, 2),
            "cost": openai_client.cost(u.prompt_tokens, u.completion_tokens, model)}


def judge(prompt: dict, text: str) -> dict:
    state = {"prompt": prompt["text"], "answer": text}
    if prompt.get("reference"):
        state["reference_answer"] = prompt["reference"]
    r = jev.get_client().system_one(state=state, questions=questions.JUDGE_QUESTIONS)
    return {"good": round(r.answers["good_answer"].noul, 3), "cost": jev.cost(r.usage.input_tokens)}


def process(prompt: dict) -> dict:
    """Everything for one prompt. The router call and both answers run at once; then both are judged."""
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_rate = pool.submit(rate, prompt)
        f_small = pool.submit(answer, questions.SMALL, prompt)
        f_big = pool.submit(answer, questions.BIG, prompt)
        route, small, big = f_rate.result(), f_small.result(), f_big.result()
    with ThreadPoolExecutor(max_workers=2) as pool:
        js, jb = pool.submit(judge, prompt, small["text"]), pool.submit(judge, prompt, big["text"])
        small["judge"], big["judge"] = js.result(), jb.result()
    return {"id": prompt["id"], "text": prompt["text"], "has_reference": bool(prompt.get("reference")),
            "route": route, "small": small, "big": big}


def run_stream():
    started = time.perf_counter()
    yield line({"type": "start", "total": len(PROMPTS), "small": questions.SMALL, "big": questions.BIG})
    try:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(process, p) for p in PROMPTS]
            for fut in as_completed(futures):
                try:
                    yield line({"type": "prompt", **fut.result()})
                except Exception as exc:
                    yield line({"type": "prompt_error", "message": f"{type(exc).__name__}: {exc}"})
        yield line({"type": "done", "seconds": round(time.perf_counter() - started, 1)})
    except Exception as exc:
        yield line({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
