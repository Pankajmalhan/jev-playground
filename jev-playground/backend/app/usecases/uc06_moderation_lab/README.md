# 06 - Moderation and calibration

76 labelled chat messages (including tricky and contested ones). Jev scores each; the page lets you move the threshold and shows the
confusion matrix, then a reliability chart with ECE and Brier to test whether the confidence is honest.

**Status:** built. **Needs:** `JEV_API_KEY`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/moderation-lab/guide` | page content |
| POST | `/api/moderation-lab/run` | score all messages once (cached for the life of the server) |
| POST | `/api/moderation-lab/try` `{text}` | score one message |

## Files

`data/messages.json` (our labels; `ambiguous` marks contested ones), `questions.py`, `service.py`. The metrics are computed in the browser,
so the slider is instant.

## What it showed

At 50% the run had one false alarm and no misses; at 90%, ten misses. ECE was about 0.09 on this small set, with Jev under-confident in the middle bins.

## Limits

The labels are our opinion, and 76 messages is a demonstration, not a benchmark. Calibrate on hundreds of your own labelled messages.
