# Hard Window Risk Weight Tuning Design

## Context

The current hard-window risk scoring experiment improved total net income from 178521.2 to 182696.6 and reduced total preference penalty from 81770.0 to 81570.0. The remaining largest avoidable penalties include hard no-drive windows for D005 and D007, plus related rest-window pressure for several drivers.

## Goal

Tune the generic `NO_DRIVE_WINDOW` risk penalty so candidate ranking internalizes more of the downstream penalty cost, without hardcoding driver IDs, cargo IDs, or literal preference cases.

## Options Considered

1. Raise the generic no-drive risk penalty and run full replay.
   - Pros: smallest change, applies to all no-drive rules, easy to roll back.
   - Cons: may reject profitable overnight jobs too aggressively.

2. Convert no-drive risk into a hard filter.
   - Pros: strongest penalty reduction.
   - Cons: likely sacrifices too much gross income and can strand drivers.

3. Add driver-specific window behavior.
   - Pros: high local score potential.
   - Cons: violates the competition constraint against hardcoding driver preferences.

## Chosen Design

Use option 1. Increase only `HARD_NO_DRIVE_WINDOW_RISK_PENALTY`, leave sequence-deadline scoring unchanged, and accept the change only if a fresh full simulation improves total net income versus `2026-05-15-hard-window-risk-scoring-local`.

## Test And Evaluation

- Existing scoring tests must continue to pass.
- Full unit test discovery must pass.
- Full monthly simulation plus income calculation must be run.
- A new experiment report must compare against `2026-05-15-hard-window-risk-scoring-local`.
- If total net income regresses, restore the previous constant and do not commit the tuning.

## Self-Review

- No driver IDs or cargo IDs are used by the scoring logic.
- Scope is limited to a single generic constant.
- Success criterion is objective: full-replay total net income must improve.
