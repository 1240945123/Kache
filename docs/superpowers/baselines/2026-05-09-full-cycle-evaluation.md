# 2026-05-09 Full Cycle Evaluation Baseline

## Scope

- Command: `cd demo/server && python main.py`
- Scoring: `cd demo && python calc_monthly_income.py`
- Config file: `demo/server/config/config.json`
- `simulation_duration_days`: `30`
- `simulation_max_steps`: `20000`

## Summary

- Completed steps: `1761`
- Simulate time seconds: `149.7`
- Failed driver count: `0`
- Total net income: `131389.65`
- Total preference penalty: `170630.0`
- Total token usage: `0`

## Driver Income

| Driver | Net income | Preference penalty | Tokens | Calculation aborted |
| --- | ---: | ---: | ---: | --- |
| D001 | 21863.37 | 8000.0 | 0 | False |
| D002 | 16397.52 | 13550.0 | 0 | False |
| D003 | 14877.02 | 15000.0 | 0 | False |
| D004 | 25849.24 | 4000.0 | 0 | False |
| D005 | 19829.25 | 10000.0 | 0 | False |
| D006 | 21228.03 | 12000.0 | 0 | False |
| D007 | 13200.15 | 16580.0 | 0 | False |
| D008 | 17019.74 | 12800.0 | 0 | False |
| D009 | -9194.79 | 39100.0 | 0 | False |
| D010 | -9679.88 | 39600.0 | 0 | False |

## Action Log Signals

| Driver | Steps | Accepted false | Income eligible false |
| --- | ---: | ---: | ---: |
| D001 | 187 | 108 | 0 |
| D002 | 187 | 108 | 0 |
| D003 | 187 | 108 | 0 |
| D004 | 187 | 108 | 0 |
| D005 | 187 | 108 | 0 |
| D006 | 78 | 6 | 0 |
| D007 | 187 | 108 | 0 |
| D008 | 187 | 108 | 0 |
| D009 | 187 | 108 | 0 |
| D010 | 187 | 108 | 0 |

## Notes

- The 30-day full-cycle local evaluation and scoring flow ran successfully with `failed_driver_count=0`.
- Model calls still return HTTP 403 in this environment, so the agent uses deterministic filtered-candidate fallback after the first model error.
- `accepted=false` counts are high, especially after cargo supply thins out; this is the next systematic-debugging target.
- `income_eligible=false` is `0` for all drivers, so horizon filtering is working.
- Preference penalties remain large; future strategy should handle runtime `status["preferences"]` generically without driver-ID hardcoding.
