# Cribbage Math

Cribbage scoring honesty. Nobody at the table counts the same hand the same way twice. Cribbage Math counts it once: fifteens, pairs, runs, flush, nobs - every subset, every time.

## What it computes

- **The hand truth** - the full count of a 4-card hand plus the starter, with the breakdown: eight fifteens (16), six pairs (12), no runs, no flush, and nobs (1) - 29 points.
- **The count truth** - the 31 limit while pegging: 24 plus a 7 is 31 for 2; 24 plus an 8 is 32, and it doesn't go.
- **The win truth** - the last holes to 121: 109 plus 6 is 115, 6 to go.

## Boundary

Rules arithmetic only. Cribbage Math counts the hand you type in; it never calls your pegging or judges the crib you threw.

## Files

- `index.html` - landing page with the honesty pitch and the boundary.
- `app.html` - the interactive scorer.
- `engine.js` - the arithmetic, shared by the app and the tests.
- `oracle.py` - the Python mirror that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (18 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/cribbagemath/
Repo: https://github.com/iLanis-agent/cribbagemath
