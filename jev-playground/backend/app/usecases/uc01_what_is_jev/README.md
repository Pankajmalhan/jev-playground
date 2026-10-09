# 01 - What is Jev

A customer message goes in; five fixed questions come back as probabilities (which team, what help, how urgent, needs a reply, might leave), and plain code turns them into a queue and a priority.

**Status:** built. This is the reference use case: copy its shape for the others.
**Ported from:** `01-what-is-jev/` in the course repo.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/what-is-jev/guide` | the written explanation: `about` (from TypeSafe's launch article) and `demo` (how this page works) |
| GET | `/api/what-is-jev/examples` | the eleven sample messages for the dropdown |
| POST | `/api/what-is-jev/analyze` | one Jev call with five questions, then the routing rules; logs the run. Returns the answers plus a `trace`: the real data and timing of every stage |
| POST | `/api/what-is-jev/batch` | answers every sample message once, in parallel (cached), for the confidence slider |
| GET | `/api/what-is-jev/history` | recent runs from the in-memory DB |

## Data

`data/examples.json`: the sample messages (id, title, text). Runs are logged to the shared `runs` table.

## Where the pieces are

- `service.py`: `QUESTIONS` (the five Jev questions) and `route()` (the plain-code rules, including the 60% confidence threshold).
- `guide.py`: all the text and content data the page shows. The questions and their code snippets are generated from `QUESTIONS`, so they cannot drift.
- `analyze()` times each stage (build, Jev, flatten, rules, log) and returns it as `trace`; the page's pipeline shows it.
- Source of the "About the model" text: https://typesafe.ai/blog/introducing-system-one-models-and-jev

## The page

One page of interactive parts, in this order: Try it, Follow the message (pipeline), the five questions (tabs), confidence slider, language model vs Jev toggle, speed and price (scale plus cost slider), where it fits. Each part is a component in `frontend/src/components/` fed by `guide.py` and the last run.
