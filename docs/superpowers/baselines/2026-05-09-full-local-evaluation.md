# 2026-05-09 Full Local Evaluation Baseline

## Scope

- Command: `cd demo/server && python main.py`
- Scoring: `cd demo && python calc_monthly_income.py`
- Config file: `demo/server/config/config.json`
- `simulation_duration_days`: `1`
- `simulation_max_steps`: `20000`

## Summary

- Completed steps: `89`
- Simulate time seconds: `139.57`
- Failed driver count: `0`
- Total net income: `-30611.48`
- Total preference penalty: `38150.0`
- Total token usage: `0`

## Driver Income

| Driver | Net income | Preference penalty | Tokens | Calculation aborted |
| --- | ---: | ---: | ---: | --- |
| D001 | -1537.12 | 2300.0 | 0 | False |
| D002 | -5352.97 | 6200.0 | 0 | False |
| D003 | 576.53 | 200.0 | 0 | False |
| D004 | 548.75 | 200.0 | 0 | False |
| D005 | 528.75 | 200.0 | 0 | False |
| D006 | -2548.65 | 3200.0 | 0 | False |
| D007 | -120.34 | 800.0 | 0 | False |
| D008 | -1080.76 | 1800.0 | 0 | False |
| D009 | -10445.29 | 11250.0 | 0 | False |
| D010 | -11180.38 | 12000.0 | 0 | False |

## Action Log Signals

| Driver | Steps | Accepted false | Income eligible false |
| --- | ---: | ---: | ---: |
| D001 | 9 | 0 | 0 |
| D002 | 9 | 0 | 0 |
| D003 | 9 | 0 | 0 |
| D004 | 9 | 0 | 0 |
| D005 | 9 | 0 | 0 |
| D006 | 8 | 1 | 0 |
| D007 | 9 | 0 | 0 |
| D008 | 9 | 0 | 0 |
| D009 | 9 | 0 | 0 |
| D010 | 9 | 0 | 0 |

## Notes

- The complete local evaluation and scoring flow ran successfully with `failed_driver_count=0`.
- Model calls still return HTTP 403 in this environment, so the agent uses deterministic filtered-candidate fallback after the first model error.
- D006 had one `accepted=false` action due to an expired/invalid cargo at execution time; scoring still completed, but this is a good next debugging target.
- Most negative score comes from preference penalties, so the next strategic improvement should be generic runtime preference handling without driver-ID hardcoding.
