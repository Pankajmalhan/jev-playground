"""What Jev is asked about every claim, and the thresholds the plain-code rules use."""

from __future__ import annotations

from typesafe_sdk import Choice, Noul, Score

QUESTIONS = {
    "within_policy": Noul(instructions="Does this expense fully comply with the policy?"),
    "decision": Choice(
        instructions="Under the policy, what should happen to this expense claim?",
        criteria={
            "approve": "It complies with the policy and can be paid.",
            "refer": "The policy says it needs a manager, or a person needs to judge something the policy does not settle.",
            "reject": "It clearly breaks the policy.",
        },
    ),
    "fraud_risk": Score(
        instructions="How suspicious does this claim look, apart from the policy: padded, duplicated, or oddly described?",
        criteria=["None", "Low: a little unusual", "Medium: worth a second look", "High: looks like abuse"],
    ),
}

APPROVE_AT = 0.8   # to approve automatically, Jev must be at least this sure it complies
REJECT_AT = 0.2    # to reject automatically, Jev must put no more than this on "complies"
MAX_FRAUD = 1      # above this fraud level, a person looks, whatever the decision
