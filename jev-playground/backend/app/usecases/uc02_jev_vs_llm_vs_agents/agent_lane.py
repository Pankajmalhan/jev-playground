"""Lane 3: an agent. A language model that can call a tool, in a loop.

Each trip round the loop is one model call. If the model asks for the tool, we
run it, hand back the result, and ask again. When it stops asking and answers,
the loop ends. The model decides for itself whether to look anything up.
"""

from __future__ import annotations

import json
import time

from ... import openai_client
from . import questions, tools

MAX_STEPS = 4  # a safety stop, so a confused agent cannot loop forever

SYSTEM = (
    "You triage customer messages for an online shop. Answer every question. "
    "If the message mentions an order number, call lookup_order to check the facts before answering. "
    "If it does not mention an order, do not call the tool. "
    "'confidence' is your honest probability, from 0 to 1, that your own answer is correct. "
    "'reason' is one short sentence."
)


def run(state: dict) -> dict:
    client = openai_client.get_client()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": questions.prompt(state)}]
    steps, calls, tokens_in, tokens_out = [], 0, 0, 0
    started = time.perf_counter()

    for _ in range(MAX_STEPS):
        t = time.perf_counter()
        resp = client.chat.completions.create(
            model=openai_client.MODEL,
            messages=messages,
            tools=tools.TOOL_SPEC,
            response_format={"type": "json_schema", "json_schema": {"name": "triage", "strict": True, "schema": questions.json_schema()}},
        )
        calls += 1
        tokens_in += resp.usage.prompt_tokens
        tokens_out += resp.usage.completion_tokens
        message = resp.choices[0].message
        ms = round((time.perf_counter() - t) * 1000)

        if not message.tool_calls:  # no tool wanted: this is the final answer
            steps.append({"type": "model", "note": f"Model call {calls}: wrote the final answer.", "ms": ms})
            payload = json.loads(message.content)
            break

        steps.append({"type": "model", "note": f"Model call {calls}: asked to use a tool before answering.", "ms": ms})
        messages.append(message.model_dump(exclude_none=True))
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            t = time.perf_counter()
            result = tools.lookup_order(**args)
            steps.append({"type": "tool", "note": f"Tool: lookup_order({args['order_id']})", "result": result,
                          "ms": round((time.perf_counter() - t) * 1000, 2)})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    else:
        raise RuntimeError(f"The agent did not answer within {MAX_STEPS} steps.")

    seconds = time.perf_counter() - started
    return {
        "model": openai_client.MODEL,
        "seconds": seconds,
        "calls": calls,
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
        "cost": openai_client.cost(tokens_in, tokens_out),
        "answers": questions.read_llm_answers(payload),
        "reason": payload["reason"],
        "steps": steps,
    }
