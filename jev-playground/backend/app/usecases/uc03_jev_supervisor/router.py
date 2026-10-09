"""Controller for use case 3. Thin on purpose: logic lives in graph.py and service.py."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ... import jev, openai_client
from .. import base
from . import guide, questions, service, tools
from .meta import META
from .schemas import ResumeRequest, RunRequest

router = base.make_router(META)
NDJSON = "application/x-ndjson"


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.get("/examples")
def examples() -> dict:
    return {"examples": service.EXAMPLES}


@router.get("/orders")
def orders() -> dict:
    return {"orders": tools.all_orders()}


@router.post("/run")
def run(body: RunRequest):
    """Start the workflow. The response is a stream: one JSON line per step."""
    jev.get_client()            # fail fast with a clear 503 if a key is missing,
    openai_client.get_client()  # before the stream starts
    return StreamingResponse(service.run_stream(body.text), media_type=NDJSON)


@router.post("/resume")
def resume(body: ResumeRequest):
    """Answer a paused workflow. Streams the rest of the run."""
    if not service.is_waiting(body.thread_id):
        raise HTTPException(409, "That run is not waiting for an answer.")
    if body.choice not in (*questions.AGENTS, "close"):
        raise HTTPException(422, f"Choose one of: {', '.join((*questions.AGENTS, 'close'))}.")
    return StreamingResponse(service.resume_stream(body.thread_id, body.choice), media_type=NDJSON)
