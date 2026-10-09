"""Use-case discovery.

Every folder named uc<NN>_<name>/ in this package is one use case (one tab in
the UI). Each folder is self-contained and exposes two things from its
__init__.py:

    META     its slug, number, title, tagline and `ready` flag   (meta.py)
    router   its controller                                      (router.py)

Nothing here needs editing when a use case is added: create the folder and it
is found. The React app reads the result from GET /api/usecases.

Folder layout:
    meta.py       identity of the use case
    router.py     the controller: HTTP in, HTTP out, nothing else
    service.py    the Jev call, the in-memory DB, the logic
    schemas.py    request bodies
    data/         files only this use case needs
    README.md     what it shows, where it came from, the endpoints
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import asdict

from fastapi import APIRouter

from .base import UseCase


def _discover() -> list:
    packages = [
        importlib.import_module(f"{__name__}.{m.name}")
        for m in pkgutil.iter_modules(__path__)
        if m.ispkg and m.name.startswith("uc")
    ]
    return sorted(packages, key=lambda p: p.META.number)


_PACKAGES = _discover()

CATALOG: list[UseCase] = [p.META for p in _PACKAGES]

# Only built use cases are mounted; the rest stay "planned" in the UI.
ROUTERS: dict[str, APIRouter] = {p.META.slug: p.router for p in _PACKAGES if p.META.ready}


def catalog_json() -> list[dict]:
    out = []
    for u in CATALOG:
        d = asdict(u)
        d["status"] = "ready" if d.pop("ready") else "planned"
        out.append(d)
    return out
