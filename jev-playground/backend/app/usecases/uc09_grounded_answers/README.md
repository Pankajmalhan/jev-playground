# 09 - Grounded answers

A small help centre (12 articles) and eight questions, four answerable and four not. A plain retrieval pipeline and one gated by Jev answer
side by side. Jev scores each passage, decides whether the answer is there at all, and checks the finished answer is supported.

**Status:** built. **Needs:** `JEV_API_KEY`, `OPENAI_API_KEY`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/grounded-answers/guide`, `/questions` | page content, the questions and the help centre |
| POST | `/api/grounded-answers/ask/{lane}` `{question, strict}` | one question through `plain` or `jev` |
| POST | `/api/grounded-answers/run-all` `{strict}` | all questions through both; streams progress, then results |

## Files

`retrieval.py` (keyword search), `pipelines.py` (both pipelines), `questions.py` (Jev's three question sets and thresholds), `data/`.

## What it showed

With a strict "say I don't know" prompt, gpt-4o-mini never invented an answer but did over-refuse. With a loose prompt it answered all four
unanswerable questions, and Jev flagged three as not fully supported. Refusals in the Jev pipeline skip the model call, so they are faster.
The Jev pipeline costs more per question overall, because of its extra Jev calls.

## Limits

Keyword retrieval, not embeddings. Twelve invented articles. Jev's support check is an opinion, not proof.
