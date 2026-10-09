# 07 - Model router

Twelve prompts, each answered by gpt-4o-mini and gpt-4o. Jev rates each prompt's difficulty, and also judges every answer. The page replays any
routing rule from the stored answers, so the slider is free.

**Status:** built. **Needs:** `JEV_API_KEY`, `OPENAI_API_KEY`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/model-router/guide` | page content |
| POST | `/api/model-router/run` | answer and rate all prompts; streams one line per finished prompt |

## Files

`questions.py` (the router and judge questions, model names), `service.py`, `data/prompts.json` (with reference answers where one exists).
Prices are in `app/openai_client.py`.

## What it showed

The small model matched the big one's judged quality on nearly every prompt at about a sixteenth of the cost. Routing "hard only" to the big
model saved about three quarters of the big-model bill. Jev's routing calls are not free: about half a second and a fraction of a cent each.

## Limits

Quality is Jev's judgement (against a reference where there is one), not ground truth. Judging every answer is for the demo only.
