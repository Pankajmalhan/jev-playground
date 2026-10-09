"""Controller for use case 2. Thin on purpose: logic lives in service.py."""

from fastapi import APIRouter, HTTPException

from .. import base
from . import guide, service, tools
from .meta import META
from .schemas import AskRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.get("/examples")
def examples() -> dict:
    return {"examples": service.EXAMPLES}


@router.get("/orders")
def orders() -> dict:
    """The table the agent's tool reads, shown so you can check its work."""
    return {"orders": tools.all_orders()}


@router.post("/ask/{lane}")
def ask(lane: str, body: AskRequest) -> dict:
    """lane is jev, llm or agent. The page calls all three at once."""
    if lane not in service.LANES:
        raise HTTPException(404, f"Unknown lane '{lane}'. Use one of: {', '.join(service.LANES)}.")
    return service.ask(lane, body.text, body.with_order)
