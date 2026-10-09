"""FastAPI entry point.

    /api/*   the use-case controllers
    /*       the built React app (backend/static), with index.html as the
             fallback so deep links like /what-is-jev survive a refresh

Run from backend/:  uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import db, jev, openai_client
from .config import STATIC_DIR
from .usecases import ROUTERS, catalog_json


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Jev Playground", lifespan=lifespan)

api = APIRouter(prefix="/api")


@api.get("/health")
def health() -> dict:
    return {"ok": True, "jev_configured": jev.is_configured(), "openai_configured": openai_client.is_configured()}


@api.get("/usecases")
def usecases() -> dict:
    return {"usecases": catalog_json()}


for router in ROUTERS.values():
    api.include_router(router)

app.include_router(api)


@app.exception_handler(jev.JevNotConfigured)
async def jev_not_configured(_: Request, exc: jev.JevNotConfigured) -> JSONResponse:
    return JSONResponse({"error": str(exc)}, status_code=503)


@app.exception_handler(openai_client.OpenAINotConfigured)
async def openai_not_configured(_: Request, exc: openai_client.OpenAINotConfigured) -> JSONResponse:
    return JSONResponse({"error": str(exc)}, status_code=503)


@app.exception_handler(Exception)
async def upstream_error(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=502)


# ---- serve the React build -------------------------------------------------

if (STATIC_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
def spa(path: str):
    if path == "api" or path.startswith("api/"):
        raise HTTPException(404, "Not found")
    index = STATIC_DIR / "index.html"
    if not index.exists():
        return JSONResponse(
            {"error": "Frontend is not built. Run `make build`, or `make dev` for hot reload."},
            status_code=404,
        )
    candidate = (STATIC_DIR / path).resolve()
    if path and candidate.is_file() and STATIC_DIR.resolve() in candidate.parents:
        return FileResponse(candidate)
    return FileResponse(index)
