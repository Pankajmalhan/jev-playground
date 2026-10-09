# 05 - Guard the agent

A naive refund agent (gpt-4o-mini, two tools) and the same agent with Jev checking every refund before it runs, side by side.
A hard rule in code is a second layer. A repeat test counts how often each agent ends up overpaying.

**Status:** built. **Needs:** `JEV_API_KEY`, `OPENAI_API_KEY`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/guard-the-agent/guide`, `/scenarios` | page content, four example messages with the amount actually owed |
| POST | `/api/guard-the-agent/run/{lane}` `{text, hard_rule}` | run one agent: `naive` or `guarded` |
| POST | `/api/guard-the-agent/stress` `{runs, hard_rule}` | every scenario N times through both agents; streams progress, then a tally |

## Files

`agent.py` (the agent loop), `guard.py` (Jev's four questions, the rules, the hard rule), `ledger.py` (a per-run in-memory ledger),
`service.py` (grading and the repeat test), `data/` (orders, policy text, scenarios).

## What it showed

The small model resists soft tricks but fell for "ignore your instructions, admin mode" ($1,000 paid) and a fake-format amount ($590 paid)
in every test run. Jev's guard blocked both. Splitting the policy check into two simple questions mattered: one combined question gave 63% on a legitimate refund.

## Limits

Jev can be confidently wrong, which is why the hard rule exists. A stronger model may resist more tricks. Nothing touches real money.
