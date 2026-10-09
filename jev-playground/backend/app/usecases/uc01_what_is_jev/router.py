"""Controller for use case 1. Thin on purpose: logic lives in service.py."""

from .. import base
from . import guide, service
from .meta import META
from .schemas import AnalyzeRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.get("/examples")
def examples() -> dict:
    return {"examples": service.EXAMPLES}


@router.post("/analyze")
def analyze(body: AnalyzeRequest) -> dict:
    return service.analyze(body.text)


@router.post("/batch")
def batch() -> dict:
    return service.batch()


@router.get("/history")
def history() -> dict:
    return {"runs": service.history()}
