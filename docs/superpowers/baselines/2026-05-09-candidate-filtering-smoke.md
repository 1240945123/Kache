# 2026-05-09 Candidate Filtering Smoke

## Commands

- `cd demo/server && python main.py --max-steps 5`
- `cd demo && python calc_monthly_income.py`

## Results

- Completed steps: `5`
- Simulate time seconds: `14.8`
- Failed driver count: `0`
- Total net income: `-1537.12`
- Total preference penalty: `2300.0`
- Total token usage: `0`

## Comparison To Smoke Baseline

- Previous total net income: `-8592.13`
- Previous total preference penalty: `8500.0`
- Previous total token usage: `36199`
- Previous failed driver count: `0`

## Notes

- No driver-specific preference hardcoding was added.
- Decision code still uses runtime `status["preferences"]` only.
- Decision code does not read `demo/server/data/cargo_dataset.jsonl` or `demo/server/data/drivers.json`.
- Model calls currently receive HTTP 403 in this environment; the agent logs the error once, disables model calls for the process, and uses the top-ranked filtered candidate fallback.
