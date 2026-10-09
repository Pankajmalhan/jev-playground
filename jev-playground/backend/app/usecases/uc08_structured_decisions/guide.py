"""Everything the page says, served as JSON."""

from __future__ import annotations

from . import questions
from .meta import META

CODE = '''# The state is JSON plus the policy in plain English. Code adds the arithmetic.
state = {"policy": POLICY_TEXT,
         "expense": {"category": "meals", "amount": 190, "people": 5, "receipt": True,
                     "calculated_by_code": {"amount_per_person": 38.0}}}

response = client.system_one(state=state, questions={
    "within_policy": Noul(...), "decision": Choice(approve, refer, reject), "fraud_risk": Score(...)})

# Jev supplies the numbers. This rule decides whether a person is needed.
if fraud > 1:                                  action = "manager"
elif decision == "approve" and within >= 0.8:  action = "approve"     # automatic
elif decision == "reject" and within <= 0.2:   action = "reject"      # automatic
else:                                          action = "manager"'''


def build() -> dict:
    return {
        "title": META.title,
        "intro": "Business rules usually live in code, written by a developer, changed by a developer. Here the rules are a paragraph of plain English "
                 "that Jev reads alongside the data. Edit the paragraph, and the decisions change.",
        "roles": [
            {"name": "The policy", "role": "The rules, in English", "line": "A paragraph anyone can read and edit. No deploy to change it."},
            {"name": "Jev", "role": "The decider", "jev": True, "line": "Reads the claim as JSON together with the policy, then decides, says how sure it is, and rates how suspicious it looks."},
            {"name": "Your code", "role": "The gate", "line": "Acts automatically only when Jev is sure. Anything less goes to a manager."},
        ],
        "questions": [{"key": k, "kind": type(q).__name__.lower(), "text": q.instructions} for k, q in questions.QUESTIONS.items()],
        "thresholds": {"approve": questions.APPROVE_AT, "reject": questions.REJECT_AT, "fraud": questions.MAX_FRAUD},
        "experiments": [
            {"label": "Allow business class flights",
             "find": "Flights: economy class only.", "replace": "Flights: any class."},
            {"label": "Require a receipt for everything over $5",
             "find": "Every expense over $25 needs a receipt.", "replace": "Every expense over $5 needs a receipt."},
            {"label": "Raise the hotel limit to $350 a night",
             "find": "Hotels: up to $200 per night.", "replace": "Hotels: up to $350 per night."},
            {"label": "Give 60 days to submit",
             "find": "Expenses must be submitted within 30 days.", "replace": "Expenses must be submitted within 60 days."},
        ],
        "code": CODE,
        "read_first": {
            "title": "How to read the results",
            "body": [
                "The eight claims are invented. The expected decision beside each is our reading of the default policy, and it is only shown while the policy is unchanged.",
                "\"Let code do the arithmetic first\" is on by default. Without it, Jev has to divide a total by the number of people, and in testing it "
                "wrongly rejected a $38-a-head team lunch. Judging is what Jev is for; sums belong in code. Turn it off to see the difference.",
                "The code version is the quick one a developer would write first. It is exact and instant, but a policy change means a code change, "
                "and it misses the exception for client meals. A careful developer could add it. The point is who has to.",
                "Jev can be confidently wrong, which is why it only acts on its own when it is clearly sure, and sends everything else to a manager.",
            ],
        },
    }
