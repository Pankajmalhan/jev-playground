"""One shared Jev client plus the small helpers every use case needs."""

from __future__ import annotations

import os
import threading

from .config import load_env

MODEL = "jev-latest"
# Jev's published price: $0.042 per 1M input tokens, output free.
INPUT_PER_MTOK = 0.042


class JevNotConfigured(RuntimeError):
    """Raised when JEV_API_KEY is missing. The API turns this into a 503."""


_client = None
_lock = threading.Lock()


def get_client():
    """Create the client on first use so the app still boots without a key."""
    global _client
    with _lock:
        if _client is None:
            load_env()
            key = (os.environ.get("JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY") or "").strip()
            if not key:
                raise JevNotConfigured("JEV_API_KEY is not set. Copy .env.example to .env and add your key.")
            from typesafe_sdk import TypeSafeClient

            _client = TypeSafeClient(api_key=key, model=MODEL, timeout=60.0)
        return _client


def is_configured() -> bool:
    load_env()
    return bool((os.environ.get("JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY") or "").strip())


def cost(input_tokens: int) -> float:
    return input_tokens / 1_000_000 * INPUT_PER_MTOK


def answer_to_dict(key: str, label: str, answer) -> dict:
    """Flatten one Jev answer (noul / choice / score) into plain JSON for the page."""
    out = {"key": key, "question": label, "type": answer.type}
    if answer.type == "noul":
        p = answer.noul
        out.update(
            value="yes" if p >= 0.5 else "no",
            confidence=max(p, 1 - p),
            options={"yes": p, "no": 1 - p},
        )
    elif answer.type == "choice":
        out.update(
            value=answer.choice,
            confidence=answer.probabilities.get(answer.choice, answer.confidence),
            options=dict(answer.probabilities),
        )
    else:
        legend = {int(k): v for k, v in (answer.legend or {}).items()}
        probs = {int(k): v for k, v in (answer.probabilities or {}).items()}
        level = max(probs, key=probs.get) if probs else round(answer.score)
        out.update(
            value=legend.get(level, str(level)),
            confidence=probs.get(level, answer.confidence),
            score=answer.score,
            options={legend.get(k, str(k)): v for k, v in probs.items()},
        )
    return out


def raw_answer(answer) -> dict:
    """What Jev actually returned for one question, trimmed for display."""
    if answer.type == "noul":
        return {"noul": round(answer.noul, 3)}
    probs = {str(k): round(v, 3) for k, v in (answer.probabilities or {}).items()}
    if answer.type == "choice":
        return {"choice": answer.choice, "probabilities": probs}
    return {"score": round(answer.score, 2), "probabilities": probs}
