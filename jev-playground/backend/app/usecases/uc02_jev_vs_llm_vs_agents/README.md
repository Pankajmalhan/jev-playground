# 02 - Jev vs LLM vs agent

The same three questions about the same customer message (which team, how urgent, is a
refund owed), answered at the same moment by a decision model, a language model and an agent.

**Status:** built.
**Ported from:** the idea of `04-jev-vs-llm-vs-agents/` in the course repo, simplified. The old
agent had a tool the task did not need; here one question (refund owed?) can only be answered by
looking up an order, so each lane is shown at what it is good at and where it is not.

## The three lanes

| File | Lane | What it does |
|---|---|---|
| `jev_lane.py` | Jev | One call, three answers as probabilities. |
| `llm_lane.py` | Language model (gpt-4o-mini) | One call, strict JSON schema, plus a one-line reason. |
| `agent_lane.py` | Agent (gpt-4o-mini) | A loop of model calls with one tool, `lookup_order`. Stops after 4 steps. |

`questions.py` defines the three questions once and converts them to Jev's format and OpenAI's
JSON schema, so every lane is provably asked the same thing. `tools.py` holds the tool, the
orders table (in-memory SQLite, seeded at startup through `db.on_init`) and a small regex that
finds an order number in text.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/jev-vs-llm-vs-agents/guide` | the written content for the page |
| GET | `/api/jev-vs-llm-vs-agents/examples` | four examples, each with an answer key |
| GET | `/api/jev-vs-llm-vs-agents/orders` | the orders table the agent can check |
| POST | `/api/jev-vs-llm-vs-agents/ask/{lane}` | run one lane (`jev`, `llm` or `agent`). The page calls all three at once |

`ask` takes `{"text": "...", "with_order": false}`. With `with_order: true`, plain code finds the
order number in the text, reads the order, and hands it to the Jev and language-model lanes.

## Data

- `data/orders.json`: four invented orders, one of them charged twice.
- `data/examples.json`: the example messages and their answer keys (team and refund owed).

## Needs

`JEV_API_KEY` and `OPENAI_API_KEY` in `.env`. Prices for gpt-4o-mini are in `app/openai_client.py`;
check them against OpenAI's current list before quoting any cost.

## Honest limits

One small model, one tool, three questions, and one run is not a benchmark. The page says so.
