# Jev Playground

One project, one server. FastAPI serves the API and the built React app; every
tab is one use case from the 01-11 course projects, with its own page, its own
controller and its own data.

The full guide (use cases, curl examples, API reference, troubleshooting) is in the
[root README](../README.md). This file covers the project layout.

## Run

Needs Python 3.10+, [uv](https://docs.astral.sh/uv/), Node 20.19+ (or 22.12+) and `make`.

```bash
make setup        # backend venv (uv) + frontend npm install + .env
# put JEV_API_KEY (and OPENAI_API_KEY for use cases 02, 03, 05, 07, 09) in .env

make dev          # hot reload: open http://localhost:5173 (API proxied to :8000)
make run          # production shape: build React, serve all from http://localhost:8000
```

Other targets: `make api` (backend only), `make web` (Vite only), `make build`, `make clean`,
`make help`. Check the keys at <http://localhost:8000/api/health>; browse the API at
<http://localhost:8000/docs>.

## The nine use cases

| # | Slug | Needs | Folder |
|---|---|---|---|
| 01 | `what-is-jev` | Jev | [uc01_what_is_jev](backend/app/usecases/uc01_what_is_jev/README.md) |
| 02 | `jev-vs-llm-vs-agents` | Jev + OpenAI | [uc02_jev_vs_llm_vs_agents](backend/app/usecases/uc02_jev_vs_llm_vs_agents/README.md) |
| 03 | `jev-supervisor` | Jev + OpenAI | [uc03_jev_supervisor](backend/app/usecases/uc03_jev_supervisor/README.md) |
| 04 | `score-a-table` | Jev | [uc04_score_a_table](backend/app/usecases/uc04_score_a_table/README.md) |
| 05 | `guard-the-agent` | Jev + OpenAI | [uc05_guard_the_agent](backend/app/usecases/uc05_guard_the_agent/README.md) |
| 06 | `moderation-lab` | Jev | [uc06_moderation_lab](backend/app/usecases/uc06_moderation_lab/README.md) |
| 07 | `model-router` | Jev + OpenAI | [uc07_model_router](backend/app/usecases/uc07_model_router/README.md) |
| 08 | `structured-decisions` | Jev | [uc08_structured_decisions](backend/app/usecases/uc08_structured_decisions/README.md) |
| 09 | `grounded-answers` | Jev + OpenAI | [uc09_grounded_answers](backend/app/usecases/uc09_grounded_answers/README.md) |

Page URL is `/<slug>`; API prefix is `/api/<slug>`.

## Architecture

```
browser ──► FastAPI :8000
              ├─ /api/*   use-case controllers
              └─ /*       backend/static  (the React build, index.html fallback)
```

```
backend/
  app/
    main.py              app, /api mount, SPA serving
    config.py            paths + .env loading
    jev.py               shared Jev client, cost, answer -> JSON
    openai_client.py     shared OpenAI client and per-model prices
    parallel.py          map_parallel(): many calls at once, results in order
    db.py                shared in-memory SQLite (reviews seeded, runs logged)
    usecases/
      __init__.py        auto-discovers every uc<NN>_* folder
      base.py            UseCase metadata + make_router()
      uc01_what_is_jev/          one folder per use case, all the same shape:
        meta.py                    slug, number, title, tagline, ready flag, and the
                                   home-page card: summary, highlights, diagram
        router.py                  the controller (HTTP only)
        service.py                 Jev calls, DB, logic
        guide.py                   the written explanation the page shows
        schemas.py                 request bodies
        data/                      files only this use case needs
        README.md                  what it shows, source project, endpoints
  data/reviews.jsonl     shared dataset, seeded into the `reviews` table by db.py
  static/                React build output (git-ignored)
frontend/
  vite.config.js         build.outDir -> ../backend/static, dev proxy /api
  src/
    App.jsx              routes: /  (the dashboard, no menu)  and  /:slug  (a playground, with the menu)
    api.js               every backend call
    components/          HomeLayout (dashboard), Layout (menu + playground), MiniFlow (card diagrams), Bars,
                         and the interactive parts of a use case page:
                         ChapterNav, Pipeline, QuestionExplorer, ConfidenceLab, Contrast, SpeedPrice,
                         LaneCard, Picker, AgentGraph, RunTimeline, PageHead, Stats, Callout, BarList
    pages/               Home (the dashboard of cards), and one file per use case
    pages/registry.js    slug -> page component
```

Where things go: anything one use case needs lives in its own folder; only
what two or more use cases share (Jev client, DB, reviews) lives in `app/`.
In `/docs` each use case has its own section.

Request path for any tab: **page -> api.js -> router.py -> service.py -> Jev
(and/or the in-memory DB)**.

## Building the next use case

Use cases are added one at a time, so there is no pre-made stub. Copy
`uc01_what_is_jev/`, rename it `uc<NN>_<name>/`, then:

1. Edit `meta.py`: slug, number, title, tagline, and the home-page card (`summary`,
   `highlights`, and `diagram` rows of nodes). Set `ready=True`. The router is found and
   mounted automatically, and the card appears on the home page by itself.
2. Write `service.py`, `router.py`, `schemas.py`, and put files only this use case
   needs in `data/`.
3. Write `guide.py`: what goes in, what Jev is asked, the steps through the backend,
   what comes out. Serve it from a `GET /guide` route.
4. Frontend: `src/pages/<Name>.jsx` (open with `<Guide>`, then the live demo), one
   line in `pages/registry.js`, its helpers in `api.js`.

## Status

| Use case | State |
|---|---|
| 01 What is Jev | built (reference implementation) |
| 02 Jev vs LLM vs agent | built (needs OPENAI_API_KEY) |
| 03 Jev as supervisor | built (LangGraph, needs OPENAI_API_KEY) |
| 04 Score a whole table | built |
| 05 Guard the agent | built (needs OPENAI_API_KEY) |
| 06 Moderation and calibration | built |
| 07 Model router | built (needs OPENAI_API_KEY) |
| 08 Decisions from data | built |
| 09 Grounded answers | built (needs OPENAI_API_KEY) |
