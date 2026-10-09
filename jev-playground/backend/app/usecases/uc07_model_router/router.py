"""Controller for use case 7. Thin on purpose: logic lives in service.py."""

from fastapi.responses import StreamingResponse

from ... import jev, openai_client
from .. import base
from . import guide, service
from .meta import META

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.post("/run")
def run():
    """Answer every prompt with both models and rate it with Jev. Streams one line per finished prompt."""
    jev.get_client()
    openai_client.get_client()
    return StreamingResponse(service.run_stream(), media_type="application/x-ndjson")
