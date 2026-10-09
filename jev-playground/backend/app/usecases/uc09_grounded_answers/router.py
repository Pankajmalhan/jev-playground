"""Controller for use case 9. Thin on purpose: logic lives in pipelines.py."""

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ... import jev, openai_client
from .. import base
from . import guide, service
from .meta import META
from .schemas import AskRequest, RunAllRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.get("/questions")
def questions() -> dict:
    return {"questions": service.QUESTIONS, "knowledge_base": service.knowledge_base()}


@router.post("/ask/{lane}")
def ask(lane: str, body: AskRequest) -> dict:
    """lane is 'plain' or 'jev'. The page calls both at once."""
    if lane not in service.LANES:
        raise HTTPException(404, "Unknown lane. Use plain or jev.")
    jev.get_client()
    openai_client.get_client()
    return service.ask(lane, body.question, body.strict)


@router.post("/run-all")
def run_all(body: RunAllRequest):
    """Every example question through both pipelines. Streams progress, then all results."""
    jev.get_client()
    openai_client.get_client()
    return StreamingResponse(service.run_all_stream(body.strict), media_type="application/x-ndjson")
