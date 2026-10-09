# 04 - Score a whole table

Jev tags every review in a table with sentiment, topic, bug and churn risk, in parallel (16 calls at once), and plain code
adds up the tags into a dashboard. The pattern for any big pile of text: map (Jev), then reduce (code).

**Status:** built. **Needs:** `JEV_API_KEY`. **Data:** the shared `reviews` table (1,000 app-store reviews).

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/score-a-table/guide` | page content |
| POST | `/api/score-a-table/run` `{size}` | score a sample of 10 to 1,000 reviews; streams progress, then the summary |

## Files

`questions.py` (the four questions), `service.py` (the parallel run and the summary), `router.py`, `guide.py`.

## What it measured

About 27 rows a second, about $0.000027 a row. Roughly 95% of each call's input tokens are the question definitions, not the review,
so the cost at scale (50M rows is about $1,360 here) is far above the $20 in TypeSafe's launch material. The page shows this.

## Limits

Sentiment is checked against the star rating, which is a rough answer key. Speed depends on concurrency and distance to the service.
