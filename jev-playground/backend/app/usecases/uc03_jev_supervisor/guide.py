"""Everything the page says, served as JSON. Written to be read quickly."""

from __future__ import annotations

from . import questions
from .meta import META

CODE_GRAPH = '''g = StateGraph(State)
g.add_node("supervisor", supervisor)              # Jev decides who acts next
for name in ("billing", "shipping", "technical"):
    g.add_node(name, specialist_node(name))       # each one ends with goto="supervisor"
g.add_node("human_review", human_review)          # pauses with interrupt()
g.add_node("finalize", finalize)                  # Jev checks the final reply
g.add_edge(START, "supervisor")
g.add_edge("finalize", END)
graph = g.compile(checkpointer=MemorySaver())     # the checkpointer is what lets a run pause'''

CODE_SUPERVISOR = '''response = client.system_one(
    state={"message": message, "already_handled": handled},   # what Jev reads
    questions={"next_agent": Choice(...), "needs_person": Noul(...)},
)
pick = response.answers["next_agent"]
confidence = pick.probabilities[pick.choice]

# Jev supplied the numbers. These rules are ordinary code.
if needs_person >= 0.5:      return Command(goto="human_review")
if confidence < 0.6:         return Command(goto="human_review")
if pick.choice == "done":    return Command(goto="finalize")
return Command(goto=pick.choice)                              # billing, shipping or technical'''

CODE_HUMAN = '''def human_review(state):
    # interrupt() saves the whole run and stops. The page shows the question to a person.
    choice = interrupt({"why": "unsure", "options": ["billing", "shipping", "technical", "close"]})
    # When the person answers, this node runs again from the top, and interrupt() returns their answer.
    return Command(goto=choice)'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "A team of agents answers a customer message, and Jev is the supervisor. It reads the message, decides which specialist "
                 "acts, reads what came back, decides again, and hands the decision to a person when it is not sure.",
        "cast": [
            {"id": "jev", "name": "Jev", "role": "The supervisor",
             "line": "Reads the message and what has been done so far, then decides who acts next. It never writes a reply.",
             "facts": ["Answers in about half a second", "Gives a probability with every pick"]},
            {"id": "agents", "name": "Three specialists", "role": "The workers",
             "line": "Billing, shipping and technical. Each is a small agent with its own narrow prompt and its own tool.",
             "facts": ["Billing can issue a refund", "Shipping tracks an order", "Technical searches help articles"]},
            {"id": "human", "name": "A person", "role": "The safety net",
             "line": "The workflow pauses and asks when Jev is under 60% sure, or the message needs a person.",
             "facts": ["Picks the team", "Or finishes with what is done so far"]},
        ],
        "read_first": {
            "title": "Before you run it",
            "body": [
                "A run makes a few small Jev calls and a few gpt-4o-mini calls. The cost appears when it finishes, and it is a fraction of a cent.",
                "The orders are demo data. A refund changes an in-memory table, and the orders reset at the start of every run.",
                "Jev has no \"other\" team to pick, so a vague message gets pushed toward the nearest one. That is why the confidence rule matters.",
                "A paused run waits in the server's memory. Restart the server and it is gone. A real deployment would keep it in a database.",
            ],
        },
        "decisions": [
            {"n": 1, "title": "Who acts first?",
             "asks": "Pick one: billing, shipping, technical, or done.",
             "rule": "At least 60% sure: go to that specialist. Less: ask a person."},
            {"n": 2, "title": "Does a person need to handle this?",
             "asks": "Yes or no. Asked in the same call, on the first pass only.",
             "rule": "50% or more: pause before any specialist acts."},
            {"n": 3, "title": "Who acts next, or are we done?",
             "asks": "The same question again after every specialist, now with what they said in front of it.",
             "rule": "Done, or someone who already acted: finish. Someone new: go there. At most three specialists."},
            {"n": 4, "title": "Does the reply answer everything?",
             "asks": "Yes or no about the combined reply.",
             "rule": "Under 60%: flag the reply for a person to check."},
        ],
        "why_jev": (
            "A supervisor's job is a classification with a confidence: pick one option, and say how sure you are. It runs on every "
            "step of every request, so it needs to be quick and cheap, and the confidence has to arrive as data, because a rule "
            "acts on it. That is the shape Jev is built for. A language model can do the same with a JSON schema, but the number it "
            "reports about itself is its own guess."
        ),
        "shapes": {
            "headers": ["", "How it flows", "When it fits"],
            "rows": [
                ["Router", "The supervisor picks one specialist, the specialist answers, done.",
                 "Each request fits one specialist. The common case."],
                ["Supervisor loop (this build)", "A specialist reports back to the supervisor, which may call another, then wraps up.",
                 "One message needs several specialists, like a double charge and a late order."],
                ["Handoff or swarm", "Agents pass control to each other directly, with no central node.",
                 "The agent that just acted is best placed to pick the next step. Less control, harder to debug."],
            ],
            "wiring": [
                {"title": "A node that returns Command(goto=...) (this build)",
                 "body": "The supervisor is plain code around one model call. Routing is explicit, and the label and the confidence are data you can test and put a threshold on."},
                {"title": "Specialists as tools of a supervisor agent",
                 "body": "Less code, and it handles multi-specialist questions naturally. But the choice happens inside the model's tool calling, so there is less to unit-test and nowhere obvious to put a confidence rule."},
            ],
        },
        "code": [
            {"id": "graph", "title": "The graph", "body": CODE_GRAPH},
            {"id": "supervisor", "title": "The supervisor", "body": CODE_SUPERVISOR},
            {"id": "human", "title": "The pause", "body": CODE_HUMAN},
        ],
        "thresholds": {"route": questions.ROUTE_CONFIDENCE, "person": questions.PERSON_AT, "verify": questions.VERIFY_AT},
    }
