"""One shared OpenAI client, built on first use so the app boots without a key."""

from __future__ import annotations

import os
import threading

from .config import load_env

MODEL = "gpt-4o-mini"
# List prices per million tokens. OpenAI changes these, so check before quoting.
INPUT_PER_MTOK = 0.15
OUTPUT_PER_MTOK = 0.60
# (input, output) per million tokens, by model
PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00)}


class OpenAINotConfigured(RuntimeError):
    """Raised when OPENAI_API_KEY is missing. The API turns this into a 503."""


_client = None
_lock = threading.Lock()


def is_configured() -> bool:
    load_env()
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def get_client():
    global _client
    with _lock:
        if _client is None:
            load_env()
            key = os.environ.get("OPENAI_API_KEY", "").strip()
            if not key:
                raise OpenAINotConfigured("OPENAI_API_KEY is not set. Add it to .env to run the language-model and agent lanes.")
            from openai import OpenAI

            _client = OpenAI(api_key=key, timeout=60.0)
        return _client


def cost(input_tokens: int, output_tokens: int, model: str = MODEL) -> float:
    price_in, price_out = PRICES.get(model, (INPUT_PER_MTOK, OUTPUT_PER_MTOK))
    return input_tokens / 1_000_000 * price_in + output_tokens / 1_000_000 * price_out
