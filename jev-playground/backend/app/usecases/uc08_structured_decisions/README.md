# 08 - Decisions from structured data

Expense claims as JSON plus a written policy in plain English. Jev decides approve, refer or reject and rates fraud risk; a short rule in code
acts automatically only when Jev is sure. The policy is editable, and the same rules written as if-statements are shown for comparison.

**Status:** built. **Needs:** `JEV_API_KEY`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/structured-decisions/guide`, `/examples` | page content, the default policy and eight claims |
| POST | `/api/structured-decisions/batch` `{policy, calculate}` | decide all claims under a policy |
| POST | `/api/structured-decisions/decide` `{expense, policy, calculate}` | decide one claim given as JSON |

## Files

`questions.py` (three questions and the thresholds), `service.py` (the decision and the action rule), `code_rules.py` (the quick code version),
`data/` (policy, claims with expected decisions).

## What it showed

Letting plain code do the arithmetic first (amount per person, per night) raised agreement with our reading from 7 of 8 to 8 of 8, and a team lunch's
"complies" confidence from 33% to 78%. Sums belong in code; judging is Jev's job. Each of the four policy experiments flips exactly one claim.

## Limits

The claims are invented and the expected decisions are our reading of the policy. Jev can be confidently wrong, hence the manager fallback.
