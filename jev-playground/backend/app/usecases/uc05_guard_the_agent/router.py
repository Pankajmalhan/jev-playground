"""Controller for use case 5. Thin on purpose: logic lives in agent.py and guard.py."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ... import jev, openai_client
from .. import base
from . import guide, service
from .meta import META
from .schemas import RunRequest, StressRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.get("/scenarios")
def scenarios() -> dict:
    return {"scenarios": service.SCENARIOS}


@router.post("/run/{lane}")
def run(lane: str, body: RunRequest) -> dict:
    """lane is 'naive' or 'guarded'. The page calls both at once."""
    if lane not in service.LANES:
        raise HTTPException(404, f"Unknown lane '{lane}'. Use naive or guarded.")
    jev.get_client()
    openai_client.get_client()
    return service.run(lane, body.text, body.hard_rule)


@router.post("/stress")
def stress(body: StressRequest):
    """Run every scenario several times through both agents. Streams progress, then a tally."""
    jev.get_client()
    openai_client.get_client()
    return StreamingResponse(service.stress_stream(body.runs, body.hard_rule), media_type="application/x-ndjson")
