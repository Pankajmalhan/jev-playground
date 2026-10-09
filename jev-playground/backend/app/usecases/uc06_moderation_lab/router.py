"""Controller for use case 6. Thin on purpose: logic lives in service.py."""

from .. import base
from ... import jev
from . import guide, service
from .meta import META
from .schemas import TryRequest

router = base.make_router(META)


@router.get("/guide")
def get_guide() -> dict:
    return guide.build()


@router.post("/run")
def run() -> dict:
    """Score all the labelled messages once (cached afterwards)."""
    jev.get_client()
    return service.run()


@router.post("/try")
def try_one(body: TryRequest) -> dict:
    jev.get_client()
    return service.ask(body.text)
