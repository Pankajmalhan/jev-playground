# 03 - Jev as supervisor

A multi-agent workflow in LangGraph where Jev is the supervisor. A customer message goes to a team of
specialist agents. Jev decides who acts next, reads what came back, decides again, and hands the
decision to a person when it is not sure.

**Status:** built.
**Idea from:** the course's supervisor-pattern notes (router, supervisor loop, handoff). This build is the
supervisor loop, with the supervisor written as a node that returns `Command(goto=...)`.

## The graph

```
START -> supervisor (Jev) --+--> billing   --+
                            +--> shipping  --+--> back to supervisor
                            +--> technical --+
                            +--> human_review --> the specialist the person picks
                            +--> finalize (Jev checks the reply) -> END
```

## The four Jev decisions (all in `questions.py` and `graph.py`)

| # | Question | Plain-code rule |
|---|---|---|
| 1 | Who acts first? (pick one: billing, shipping, technical, done) | Under 60% sure: ask a person. |
| 2 | Should a person handle this? (yes/no, first pass only, same call as 1) | 50% or more: pause before any specialist acts. |
| 3 | Who acts next, or are we done? (asked after every specialist) | Done or already-acted: finish. Else go there. Max 3 specialists. |
| 4 | Does the reply answer everything? (yes/no, the verifier) | Under 60%: flag the reply. |

The thresholds are constants at the top of `questions.py`.

## Files

| File | What it holds |
|---|---|
| `graph.py` | The LangGraph graph: supervisor, human_review, specialist nodes, finalize. |
| `questions.py` | Jev's questions and the thresholds. |
| `specialists.py` | The three agents: a narrow prompt and tools each, one shared runner (gpt-4o-mini). |
| `tools.py` | The tools: look up / refund an order, track an order, search help articles. |
| `service.py` | Runs the graph and streams one JSON line per step. |
| `router.py` | `POST /run` and `POST /resume` (both stream), plus `/guide`, `/examples`, `/orders`. |
| `data/` | Orders, help articles, example messages. |

## How the pause works

`human_review` calls `interrupt()`. LangGraph saves the run (here in memory, with `MemorySaver`) and the
stream ends with a `paused` event. The page shows the question; the answer is sent to `POST /resume`,
which streams the rest. The node runs again from the top on resume, so it does nothing before `interrupt()`.

## Needs

`JEV_API_KEY` and `OPENAI_API_KEY`, plus `langgraph` (in `requirements.txt`). Orders reset at the start of
every run, so a refund does not leak into the next one.

## Limits

One small model and one tool per specialist. A paused run lives in server memory and is lost on restart.
Jev has no "other" team, so vague messages lean toward the nearest team, which is what the confidence rule is for.
