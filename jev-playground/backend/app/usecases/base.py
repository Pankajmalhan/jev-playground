"""What every use-case folder shares: its metadata and a pre-tagged router."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter


@dataclass(frozen=True)
class UseCase:
    slug: str       # URL segment: /what-is-jev in the UI, /api/what-is-jev/... in the API
    number: int     # matches the 01-11 course projects
    title: str
    tagline: str
    ready: bool = False   # flip to True when the use case is built: the tab goes live
    # Shown on the home page card
    summary: str = ""                  # two short sentences: what you will do here
    highlights: tuple = ()             # three short "you will see" lines
    diagram: tuple = ()                # rows of {"label", "nodes": [{"text", "kind", "note"}]}; kind: data, jev, llm, tool, out


def make_router(meta: UseCase) -> APIRouter:
    """A router mounted at /api/<slug>, grouped under its own heading in /docs."""
    return APIRouter(prefix=f"/{meta.slug}", tags=[f"{meta.number:02d} {meta.title}"])
