"""Everything the page says, served as JSON. Written to be read quickly."""

from __future__ import annotations

from . import questions
from .meta import META

CODE_JEV = '''response = client.system_one(
    state={"message": text},
    questions={"department": Choice(...), "urgency": Score(...), "refund_due": Noul(...)},
)
response.answers["refund_due"].noul     # 0.51 : about a coin flip, and it says so'''

CODE_LLM = '''resp = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[system, user],                       # the message and the questions, as text
    response_format={"type": "json_schema",        # force the answer into our shape
                     "json_schema": {"strict": True, "schema": schema}},
)
json.loads(resp.choices[0].message.content)
# {"refund_due": {"yes": false, "confidence": 0.7}, "reason": "Charged once."}'''

CODE_AGENT = '''for step in range(4):                              # a safety stop
    resp = openai.chat.completions.create(model=..., messages=messages, tools=[lookup_order])
    message = resp.choices[0].message
    if not message.tool_calls:                     # no tool wanted: this is the answer
        break
    for call in message.tool_calls:                # the model asked us to run a tool
        result = lookup_order(**json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    # ...and loop: the model now sees the result and decides again'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "Three ways to get a decision out of a model. Each gets the same three questions about the same customer message, at the same moment.",
        "questions": [{"key": q.key, "text": q.text} for q in questions.QUESTIONS],
        "roles": [
            {"id": "jev", "name": "Jev", "role": "The judge",
             "line": "You give it fixed questions. It answers each one as numbers: a probability for every option.",
             "facts": ["One call", "Writes no text", "Cannot look anything up"]},
            {"id": "llm", "name": "A language model", "role": "The writer",
             "line": "Reads the message and answers in its own words. Here it is forced into the same fixed shape, plus a one-line reason.",
             "facts": ["One call", "Can explain itself", "Cannot look anything up"]},
            {"id": "agent", "name": "An agent", "role": "The worker",
             "line": "A language model that is allowed to use tools and loop: look something up, read the result, then decide.",
             "facts": ["Two or more calls", "Can explain itself", "Can fetch facts it was not given"]},
        ],
        "read_first": {
            "title": "How to read the results",
            "body": [
                "One run is not a benchmark. Times change from run to run, and they include the distance from your machine to each service.",
                "The language model and the agent here use gpt-4o-mini, a small, fast model. Larger or reasoning models are slower and may "
                "decide differently. The agent has a single tool, so this shows the idea, not the limits.",
                "The example messages come with a known right answer, so you can see a tick or a cross. Your own messages have none.",
            ],
        },
        "toggle": {
            "label": "Let plain code look up the order first",
            "help": "Code finds the order number in the text, reads the orders table, and hands the record to Jev and the language model. "
                    "The agent always has to fetch it itself.",
        },
        "compare": {
            "headers": ["", "Jev", "Language model", "Agent"],
            "rows": [
                ["What it is", "A model trained to decide", "A model trained to write", "A language model plus a loop and tools"],
                ["Model calls", "1", "1", "1 to several (this demo stops at 4)"],
                ["Shape of the answer", "Always one of your options", "Forced into your shape by a JSON schema", "Forced into your shape by a JSON schema"],
                ["How sure it is", "A probability for every option. TypeSafe says they are calibrated.", "A number it reports about itself", "A number it reports about itself"],
                ["Explains itself", "No, it writes no text", "Yes, in a sentence", "Yes, in a sentence"],
                ["Can look things up", "No, only what you hand it", "No, only what you hand it", "Yes, with the tools you give it"],
                ["Time and cost are predictable", "Yes: one call each time", "Mostly: one call, but the length varies", "No: it depends on how many steps it takes"],
            ],
        },
        "picker": {
            "questions": [
                {"id": "facts", "text": "Does the answer depend on facts that are not in the message?",
                 "example": "Was this customer really charged twice?"},
                {"id": "known", "text": "Do you know in advance which facts to fetch?",
                 "example": "Always: find the order number, read that order.", "only_if": "facts"},
                {"id": "words", "text": "Do you need the answer written out in words, not just chosen?",
                 "example": "A short explanation for a person to read."},
            ],
            "results": {
                "jev": {"title": "Jev",
                        "why": "Everything needed is in the text, and you only need a choice. One fast call gives a decision and how sure it is."},
                "llm": {"title": "A language model",
                        "why": "Everything needed is in the text, but you need words. Better still: let Jev decide, then have a model write the sentence."},
                "code": {"title": "Plain code fetches the facts, then Jev decides",
                         "why": "You know which facts to fetch, so you do not need an agent to find them. Your code looks them up and passes them in with the message. One decision call, predictable cost."},
                "agent": {"title": "An agent",
                          "why": "The answer needs facts from outside the message, and which ones depends on the message. That is the job an agent is for, and the extra calls are the price."},
            },
            "words_note": "You also need words: add a language model to write the explanation after the decision is made.",
        },
        "code": [
            {"id": "jev", "title": "Jev", "body": CODE_JEV},
            {"id": "llm", "title": "A language model", "body": CODE_LLM},
            {"id": "agent", "title": "An agent", "body": CODE_AGENT},
        ],
    }
