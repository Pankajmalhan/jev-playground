"""The workflow, as a LangGraph graph.

    START -> supervisor (Jev) --+--> billing   --+
                                +--> shipping  --+--> back to supervisor
                                +--> technical --+
                                +--> human_review --> the specialist the person picks
                                +--> finalize (Jev checks the reply) -> END

Every node returns Command(goto=...), so the routing is visible in the code, not hidden in edges.
Each node also puts an `event` in the state: a description of what just happened, which the
page shows as one step in the timeline.
"""

from __future__ import annotations

import time
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from ... import jev
from . import questions, specialists


class State(TypedDict, total=False):
    message: str
    handled: list      # [{"agent": "billing", "reply": "..."}]: what the specialists have done so far
    pending: dict      # why the workflow is waiting for a person
    final: str
    event: dict        # what just happened (for the timeline)


def _jev_usage(response) -> dict:
    tokens = response.usage.input_tokens
    return {"jev_calls": 1, "model_calls": 0, "input_tokens": tokens,
            "output_tokens": response.usage.output_tokens, "cost": jev.cost(tokens)}


# ---- the supervisor: Jev decides, plain code applies the rules ---------------------

def supervisor(state: State) -> Command[Literal["billing", "shipping", "technical", "human_review", "finalize"]]:
    handled = state.get("handled", [])
    first_pass = not handled
    seen = {"message": state["message"], "already_handled": [{"agent": h["agent"], "reply": h["reply"]} for h in handled]}
    asked = questions.supervisor_questions(first_pass)

    started = time.perf_counter()
    response = jev.get_client().system_one(state=seen, questions=asked)
    ms = round((time.perf_counter() - started) * 1000)

    pick = response.answers["next_agent"]
    choice = pick.choice
    confidence = pick.probabilities.get(choice, pick.confidence)
    needs_person = response.answers["needs_person"].noul if first_pass else None

    # The rules. Jev supplied the numbers; this decides what to do with them.
    pending = None
    if needs_person is not None and needs_person >= questions.PERSON_AT:
        goto, reason = "human_review", f"Jev put {needs_person:.0%} on 'a person should handle this', at or above {questions.PERSON_AT:.0%}."
        pending = {"why": "sensitive", "detail": reason}
    elif confidence < questions.ROUTE_CONFIDENCE:   # applies to any pick, including "done"
        goto, reason = "human_review", f"Jev is only {confidence:.0%} sure ({choice}), below {questions.ROUTE_CONFIDENCE:.0%}."
        pending = {"why": "unsure", "detail": reason}
    elif choice == "done":
        goto, reason = "finalize", f"Jev is {confidence:.0%} sure every part of the message has been answered."
    elif choice in {h["agent"] for h in handled}:
        goto, reason = "finalize", f"{choice} has already acted, so the loop stops here."
    elif len(handled) >= questions.MAX_SPECIALISTS:
        goto, reason = "finalize", "The limit on specialists was reached, so the loop stops here."
    else:
        goto, reason = choice, f"Jev is {confidence:.0%} sure, at or above {questions.ROUTE_CONFIDENCE:.0%}."

    event = {
        "node": "supervisor", "ms": ms, "round": len(handled) + 1,
        "jev": {
            "state_sent": seen,
            "questions": [{"key": k, "type": type(q).__name__.lower(), "instructions": q.instructions} for k, q in asked.items()],
            "answers": {k: jev.raw_answer(response.answers[k]) for k in asked},
        },
        "decision": {"goto": goto, "pick": choice, "confidence": round(confidence, 3), "reason": reason},
        "usage": _jev_usage(response),
    }
    update = {"event": event}
    if pending:
        update["pending"] = {**pending, "jev_pick": choice, "jev_confidence": round(confidence, 3)}
    return Command(goto=goto, update=update)


# ---- the human: the graph stops here until someone answers -------------------------

def human_review(state: State) -> Command[Literal["billing", "shipping", "technical", "finalize"]]:
    pending = state["pending"]
    # interrupt() saves the state and pauses the whole graph. When the page sends an answer,
    # this node runs again from the top and interrupt() returns that answer.
    choice = interrupt({"why": pending["why"], "detail": pending["detail"],
                        "jev_pick": pending["jev_pick"], "jev_confidence": pending["jev_confidence"],
                        "options": [*questions.AGENTS, "close"]})
    goto = choice if choice in questions.AGENTS else "finalize"
    return Command(goto=goto, update={"event": {"node": "human_review", "choice": choice}})


# ---- the specialists: one node each, all return to the supervisor ------------------

def _specialist_node(name: str):
    def node(state: State) -> Command[Literal["supervisor"]]:
        result = specialists.run(name, state["message"])
        handled = state.get("handled", []) + [{"agent": name, "reply": result["reply"]}]
        return Command(goto="supervisor", update={"handled": handled, "event": {
            "node": name, "title": specialists.SPECIALISTS[name].title, **result}})
    return node


# ---- the finish: Jev checks the combined reply -------------------------------------

def finalize(state: State) -> dict:
    handled = state.get("handled", [])
    if not handled:
        text = "No automated reply was sent: this message needs a person."
        return {"final": text, "event": {"node": "finalize", "final": text, "verify": None, "flagged": False,
                                         "usage": {"jev_calls": 0, "model_calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0}}}
    text = "\n\n".join(h["reply"] for h in handled)
    seen = {"message": state["message"], "reply": text}
    started = time.perf_counter()
    response = jev.get_client().system_one(state=seen, questions=questions.VERIFY_QUESTIONS)
    ms = round((time.perf_counter() - started) * 1000)
    p = response.answers["answers_everything"].noul
    return {"final": text, "event": {
        "node": "finalize", "ms": ms, "final": text, "flagged": p < questions.VERIFY_AT,
        "verify": {"state_sent": seen, "answers": {"answers_everything": jev.raw_answer(response.answers["answers_everything"])},
                   "probability": round(p, 3), "threshold": questions.VERIFY_AT},
        "usage": _jev_usage(response)}}


def build():
    g = StateGraph(State)
    g.add_node("supervisor", supervisor)
    g.add_node("human_review", human_review)
    for name in questions.AGENTS:
        g.add_node(name, _specialist_node(name))
    g.add_node("finalize", finalize)
    g.add_edge(START, "supervisor")
    g.add_edge("finalize", END)
    # MemorySaver keeps a paused run in memory. A real deployment would use a database.
    return g.compile(checkpointer=MemorySaver())


GRAPH = build()
