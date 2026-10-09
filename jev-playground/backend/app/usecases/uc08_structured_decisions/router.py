"""Controller for use case 8. Thin on purpose: logic lives in service.py."""

from .. import base
from ... import jev
from . import code_rules, guide, service
from .meta import META
from .schemas import BatchRequest, DecideRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.get("/examples")
def examples() -> dict:
    return {"policy": service.POLICY, "expenses": service.EXPENSES}


@router.post("/batch")
def batch(body: BatchRequest) -> dict:
    """Decide every example claim under the policy you send."""
    jev.get_client()
    return service.batch(body.policy, body.calculate)


@router.post("/decide")
def decide(body: DecideRequest) -> dict:
    """Decide one claim, given as JSON."""
    jev.get_client()
    return {**service.decide(body.expense, body.policy, body.calculate), "code": _safe_code(body.expense)}


def _safe_code(expense: dict) -> str:
    try:
        return code_rules.decide(expense)
    except Exception:   # the claim may not have the fields the quick rules expect
        return "n/a"
