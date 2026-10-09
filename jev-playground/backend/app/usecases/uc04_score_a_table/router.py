"""Controller for use case 4. Thin on purpose: logic lives in service.py."""

from fastapi.responses import StreamingResponse

from ... import jev
from .. import base
from . import guide, service
from .meta import META
from .schemas import RunRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.post("/run")
def run(body: RunRequest):
    """Score a sample of the reviews table. The response is a stream: one JSON line per update."""
    jev.get_client()   # fail fast with a clear 503 if the key is missing
    return StreamingResponse(service.run_stream(body.size), media_type="application/x-ndjson")
