"""The three specialists. Each is a small agent: its own narrow prompt, its own tools,
and a short loop (ask the model, run a tool if it wants one, repeat).

They all share one runner, so what differs between them is only the prompt and
the tools. That is the point of splitting a big agent up.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

from ... import openai_client
from . import tools

MAX_STEPS = 4


@dataclass(frozen=True)
class Specialist:
    name: str
    title: str
    prompt: str
    tool_specs: list
    tool_impls: dict
    actions: tuple = ()   # tools that change data (shown as actions in the log)


SPECIALISTS = {
    "billing": Specialist(
        "billing", "Billing agent",
        "You are the billing specialist for an online shop. Handle only the billing part of the customer's message; "
        "other specialists handle the rest. Look up the order, and if the card was charged more than once, issue the refund. "
        "Never refund otherwise. Reply to the customer in 2 or 3 sentences, using only what the tools returned.",
        [
            tools.spec("lookup_order", "Look up an order: item, amount, how many times the card was charged, refunded amount.", tools.ORDER_ID),
            tools.spec("issue_refund", "Refund the extra charges on an order. Fails if the order was charged only once.", tools.ORDER_ID),
        ],
        {"lookup_order": tools.lookup_order, "issue_refund": tools.issue_refund},
        actions=("issue_refund",),
    ),
    "shipping": Specialist(
        "shipping", "Shipping agent",
        "You are the shipping specialist for an online shop. Handle only the shipping part of the customer's message; "
        "other specialists handle the rest. Track the order and tell the customer where it is. "
        "Reply in 1 or 2 sentences, using only what the tool returned.",
        [tools.spec("track_order", "Get an order's shipping status and estimated arrival.", tools.ORDER_ID)],
        {"track_order": tools.track_order},
    ),
    "technical": Specialist(
        "technical", "Technical agent",
        "You are the technical support specialist for an online shop. Handle only the app or product problem in the customer's "
        "message; other specialists handle the rest. Search the help articles and answer from the article only. "
        "If there is no matching article, say you will pass it to the engineering team. Reply in 2 or 3 sentences.",
        [tools.spec("search_help", "Search the help articles for a problem description.", {"query": {"type": "string"}})],
        {"search_help": tools.search_help},
    ),
}


def run(name: str, message: str) -> dict:
    """Run one specialist on the customer's message. Returns its reply, what it did, and what it cost."""
    spec = SPECIALISTS[name]
    client = openai_client.get_client()
    messages = [{"role": "system", "content": spec.prompt}, {"role": "user", "content": message}]
    steps, actions = [], []
    calls = tokens_in = tokens_out = 0
    started = time.perf_counter()
    reply = ""

    for _ in range(MAX_STEPS):
        resp = client.chat.completions.create(
            model=openai_client.MODEL, messages=messages, tools=spec.tool_specs, max_completion_tokens=250,
        )
        calls += 1
        tokens_in += resp.usage.prompt_tokens
        tokens_out += resp.usage.completion_tokens
        msg = resp.choices[0].message
        if not msg.tool_calls:
            reply = (msg.content or "").strip()
            break
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            t = time.perf_counter()
            result = spec.tool_impls[call.function.name](**args)
            step = {"tool": call.function.name, "args": args, "result": result, "ms": round((time.perf_counter() - t) * 1000, 2)}
            steps.append(step)
            if call.function.name in spec.actions and "error" not in result:
                actions.append(step)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    else:
        reply = "I could not finish this request."

    return {
        "reply": reply, "steps": steps, "actions": actions, "ms": round((time.perf_counter() - started) * 1000),
        "usage": {"jev_calls": 0, "model_calls": calls, "input_tokens": tokens_in, "output_tokens": tokens_out,
                  "cost": openai_client.cost(tokens_in, tokens_out)},
    }
