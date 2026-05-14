# D009/D010 Diagnostic Notes

## Current Evidence

- Baseline report: `2026-05-14-diff-diagnostics-local.md`
- Total net income: `155022.58`
- Total preference penalty: `99510.0`
- Token usage: `0`

## D009

- Penalty: `36100.0`
- Net income: `-3660.33`
- Action counts: `accepted_false=4, reposition=9, take_order=75, wait=74`
- Penalty split from monthly income:
  - Required familiar cargo `240646` was not satisfied: `10000.0`
  - Must be home before 23:00 and avoid orders/reposition from 23:00 to next 08:00: `29` violations, `26100.0`
  - Forbidden category rule: `0.0`
- Timeline evidence:
  - The driver waits near home for a long block from `2026-03-02 01:05` through `2026-03-03 16:00`, then resumes work.
  - The required cargo window starts around `2026-03-03 14:43`, but the final timeline never shows `cargo=240646`.
  - After the early waiting block, the driver often accepts orders that end late or require later return-home reposition, which still leaves many night/home-window violations.

## D010

- Penalty: `16910.0`
- Net income: `13369.83`
- Action counts: `accepted_false=1, reposition=7, take_order=64, wait=10`
- Penalty split from monthly income:
  - Family sequence task failed: `10910.0`
  - Daily continuous parking rest at least 3 hours: `26` violations, `6000.0`
  - Monthly visit rule satisfied: `0.0`
  - Soft forbidden cargo category: `0.0`
- Sequence details from monthly income:
  - `pickup_done_minute` is `null`
  - `first_home_minute` is `13942`
  - `minutes_not_home_in_window` is `382`
  - `triggers_spouse_incomplete` is `true`
  - `left_after_arrival` is `false`
- Timeline evidence:
  - On `2026-03-10`, the driver repositions to `(23.21,113.37)` at minute `13939`, then to `(23.19,113.36)` at minute `13942`, then waits until `2026-03-13 22:00`.
  - This reaches home and stays, but the pickup step is not recognized because the stay at pickup is only `3` minutes, while the preference requires at least `10` minutes.

## First Generic Fix Candidate

- Target rule type: hard time-window planning for `HOME_DEADLINE`, `NO_DRIVE_WINDOW`, and `SEQUENCE_TASK`.
- Current behavior:
  - The planner can issue required reposition/wait intents, but the scorer still takes profitable orders that consume time too close to hard future windows.
  - Sequence pickup can immediately proceed to the next step without reserving the required dwell time at the pickup location.
- Proposed generic behavior:
  - Add a generic candidate feasibility check against upcoming hard windows before taking an order.
  - Reject or strongly deprioritize candidates whose estimated finish time leaves insufficient time to reposition to the required hard target before the deadline.
  - For sequence tasks, when already at a step with `wait_minutes`, wait long enough to satisfy the step before moving to the next step.
- Why this is not driver-ID hardcoding:
  - The behavior is driven by parsed `PreferenceRule` values: target coordinates, deadline minutes, no-drive windows, and sequence step dwell times.
  - It does not check `driver_id`, named drivers, or raw dataset files.
  - D009 and D010 are only diagnostic examples for measuring impact.

## Test Plan

- Unit test:
  - Add planner test where a sequence task reaches a pickup target before deadline and must wait the required dwell minutes before returning home.
  - Add decision-service or scoring test where a candidate is rejected when its finish time would make a parsed home deadline/no-drive window impossible.
- Full smoke comparison:
  - Run the full simulation.
  - Generate a new experiment report with `--baseline docs/superpowers/experiments/2026-05-14-diff-diagnostics-local.json`.
  - Compare D009/D010 penalty deltas and verify other drivers do not regress sharply.

