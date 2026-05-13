# 2026-05-09 Smoke Baseline

## Scope

- Command: `python main.py --max-steps 5`
- Working directory: `demo/server`
- Config: `demo/server/config/config.json`
- Local-only config change: `model_timeout_seconds` increased from `60` to `180` after the first run timed out.
- Follow-up scoring command: `python calc_monthly_income.py` from `demo`

## Root Cause From First Attempt

The first `--max-steps 20` run failed during the second model call with:

```text
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='dashscope.aliyuncs.com', port=443): Read timed out. (read timeout=60.0)
```

The environment had Python dependencies and `DASHSCOPE_API_KEY`, but `demo/server/config/config.json` was initially missing. After copying `config.example.json`, the 60 second model timeout still failed under the current prompt/model behavior.

## Smoke Run Result

- Completed steps: `5`
- Simulate wall time: `270.86` seconds
- Result files: `10`
- Failed drivers: `0`
- Total net income: `-8592.13`
- Total preference penalty: `8500.0`
- Total token usage: `36199`

Driver details from the scoring output:

| Driver | Steps | Net income | Preference penalty | Total tokens | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| D001 | 4 | -2392.13 | 2300.0 | 35366 | Took 3 orders; one was outside the 1-day income horizon; violated rest and Shenzhen-bound preference checks. |
| D002 | 1 | -6200.0 | 6200.0 | 833 | Only waited 30 minutes; failed month/day preference checks under the 1-day smoke horizon. |
| D003-D010 | 0 | 0.0 | 0.0 | 0 | Not reached by the 5-step cap. |

## Evidence

D001 step sequence:

1. `wait` 30 minutes at 2026-03-01 00:00.
2. `take_order` cargo `220575`, accepted, finished at minute 430.
3. `take_order` cargo `306511`, accepted, finished at minute 709.
4. `take_order` cargo `221203`, accepted, finished at minute 1509, `income_eligible=false`.

D002 step sequence:

1. `wait` 30 minutes at 2026-03-01 00:00.

## Conclusions

- The current baseline is valid enough to score on a tiny smoke run; no action-log validation failures occurred.
- Model latency and reasoning-token usage are the biggest immediate bottlenecks.
- The current prompt does not sufficiently protect against horizon-ineligible orders or location/preference violations.
- Future preference handling must stay generic: use the runtime `preferences` content from `get_driver_status`, not `driver_id` hardcoding.

## Recommended Next Design Target

Design a deterministic pre-model candidate scoring and fallback layer in `demo/agent/model_decision_service.py`:

- Filter clearly infeasible cargo before asking the model.
- Include runtime preference text in the model context without writing driver-specific rules.
- Prefer short, valid, income-eligible decisions under the configured horizon.
- Fall back to bounded `wait` when model output is invalid, slow, or no cargo is visible.
