# Layered Preference Strategy Design

## Goal

Build a competition-oriented Agent strategy that improves monthly net income by combining profitable order selection with runtime preference compliance. The strategy must remain compliant with the official rule: decision code must not hardcode driver-specific behavior by `driver_id`, and must not read raw data files such as `cargo_dataset.jsonl` or `drivers.json`.

The first implementation target is a layered strategy system:

1. Parse visible runtime preferences into structured rules.
2. Use a planner and guard layer to block dangerous actions and schedule required tasks.
3. Score remaining cargo candidates by expected value and preference risk.
4. Record every evaluation result so strategy changes can be compared over time.

## Current Baseline

The latest recorded 30-day full-cycle baseline is `docs/superpowers/baselines/2026-05-09-full-cycle-evaluation.md`.

Key values:

- Total net income: `131389.65`
- Total preference penalty: `170630.0`
- Failed driver count: `0`
- Total token usage: `0`
- D009 net income: `-9194.79`, preference penalty: `39100.0`
- D010 net income: `-9679.88`, preference penalty: `39600.0`

The main strategic bottleneck is preference penalty, especially large penalties from ignored home, temporary appointment, visit, rest, and no-drive constraints. A secondary bottleneck is excessive rejected `take_order` actions after cargo supply thins out.

## Compliance Boundary

Allowed:

- Read driver state and visible preferences from `get_driver_status(driver_id)`.
- Query visible cargo through `query_cargo(driver_id, latitude, longitude)`.
- Read in-session decision history through `query_decision_history(driver_id, step)`.
- Parse preference text generically, using text patterns, numbers, times, coordinates, categories, and cargo IDs found in the visible preference text.
- Cache parsed preference results in memory by preference text, not by driver ID.
- Use a model only as a fallback parser for preference text that deterministic parsing cannot classify.

Forbidden:

- Any logic such as `if driver_id == "D009"` or a table of D001-D010 special cases.
- Reading or scanning `demo/server/data/cargo_dataset.jsonl`, `demo/server/data/drivers.json`, or equivalent raw data paths from agent decision code.
- Precomputing hidden cargo or hidden driver rules outside the official simulation interfaces.
- Treating public sample driver IDs as stable competition semantics.

Every constraint applied by the strategy must be traceable to a visible runtime preference string, current status, visible cargo candidate, or decision history record.

## Architecture

Keep `ModelDecisionService.decide(driver_id)` as the public entry point used by the simulator. Internally, route each decision through four focused units.

### Preference Layer

`PreferenceParser` converts runtime `status["preferences"]` entries into structured `PreferenceRule` objects. It uses a dual-track parser:

1. Deterministic parsing first, using generic patterns.
2. Model fallback only when a preference cannot be parsed and appears important enough to justify token cost.

The parser assigns each rule a `strength`:

- `hard`: contains language such as `必须`, `不得`, `禁止`, `须`, `罚`, `上不封顶`, or `临时约定`.
- `soft`: contains language such as `尽量`, `希望`, or `偏好`.
- `unknown_strong`: deterministic and model parsing both fail, but the source text looks like a hard constraint.
- `unknown_soft`: parsing fails and the source text looks like a soft preference.

Model fallback is not part of per-step action selection. It is only used to convert unfamiliar preference text into a structure that the deterministic strategy can execute.

### Planner Layer

`Planner` maintains lightweight derived state from current status and decision history:

- Current day and clock window.
- Recent waits, orders, and reposition actions.
- Daily continuous rest progress.
- Monthly off-day and no-order-day progress.
- Visit-day completion for coordinate targets.
- Temporary task progress, such as reaching pickup/home coordinates and remaining stationary during a required window.

Planner output is a set of required or preferred intents, such as:

- `must_wait_until`
- `must_reposition_to_target`
- `reserve_rest_window`
- `reserve_off_day`
- `pursue_required_cargo`
- `avoid_action_until_window_ends`

Planner decisions are based on generic rule types, not driver IDs.

### Guard Layer

`PolicyGuard` evaluates a proposed action or cargo candidate against hard rules. It may reject candidates or override normal scoring with a required wait/reposition action.

Hard guards include:

- Forbidden cargo categories.
- No-drive or no-order time windows.
- Required home or stay-at-target windows.
- Required temporary cargo by visible cargo ID.
- Pickup-deadhead distance limit.
- Haul distance limit.
- Monthly deadhead limit.
- Forbidden circular zones.
- Allowed bounding-box area rules.
- Risks that a chosen order will cross a hard deadline or prevent required rest/home/task completion.
- `unknown_strong` rules, which trigger conservative behavior until they are parsed.

Soft preferences do not hard-block candidates by default. They apply scoring penalties unless the text clearly says a violation has high financial consequences.

### Scorer Layer

`Scorer` ranks only candidates that survive base filtering and hard guards. It should reuse or extend the existing `demo/agent/strategy_helpers.py` candidate calculations.

Core scoring factors:

- Rough net value: price minus pickup and haul distance cost estimate.
- Value per estimated minute.
- Pickup distance.
- Load-window feasibility.
- Estimated finish time.
- Rejected-action risk.
- Preference risk.
- Contribution to planned tasks, such as ending near a required home or visit point.
- Schedule pressure, such as nearing a rest or no-drive window.

Action selection priority:

1. If Planner says a hard task is currently required, execute that task.
2. If safe high-value cargo exists, `take_order`.
3. If a spatial task is required and movement is allowed, `reposition`.
4. If no safe useful action exists, `wait`.
5. If an `unknown_strong` preference is active, prefer short waits or clearly low-risk actions.

The Agent should not always query cargo first. If the current state is obviously inside a mandatory wait/home/no-drive window, the decision can return `wait` before paying query scan cost.

## Rule Types For V1

The first complete preference version should cover these generic rule families.

### Cargo Rules

- Hard forbidden category: `不接货源品类为「X」`
- Soft avoided category: `尽量不拉/不接 X`
- Required temporary cargo: visible text containing a cargo ID such as `指定熟货源编号 240646`

### Time Behavior Rules

- Daily continuous rest of `N` hours.
- No-order/no-drive windows such as `23点至次日6点不接单不空驶`.
- Lunch or daytime rest windows such as `12–13点`.
- First order must begin before a daily cutoff.
- Stay still until a stated time or after arriving at a target.

### Monthly Planning Rules

- At least `N` days with no completed orders.
- At least `N` days with no orders and no reposition.
- At least `N` fully idle days.
- At least `N` distinct visit days within a radius of a target coordinate.

### Spatial And Distance Rules

- Pickup-deadhead distance must be at most `N` km.
- Haul distance must be at most `N` km.
- Monthly deadhead distance must be at most `N` km.
- Forbidden circular area: center coordinate plus radius.
- Required city or bounding-box area.
- Required target coordinate or home coordinate.

### Temporary Task Rules

- Go to a target before a deadline.
- Visit one coordinate, wait a minimum duration, then go to another coordinate.
- Be home by a deadline and remain there until a release time.
- Complete a specified cargo ID by a visible appointment requirement.

## Unknown Preference Handling

Unknown preferences are handled by strength:

- `unknown_strong`: avoid risky `take_order` and `reposition` unless the action is clearly needed for an already parsed hard task. Prefer short waits while preserving time for later recovery. Log the source text and parse failure.
- `unknown_soft`: keep normal profit-seeking behavior, but apply a small risk penalty and include the text in experiment notes.

This avoids both extremes: blindly ignoring a high-penalty rule or stopping the driver for every unclear sentence.

## Decision Flow

Each `decide(driver_id)` call should follow this order:

1. Get current status.
2. Parse or retrieve cached rules for visible preferences.
3. Query recent decision history.
4. Reconstruct planner state.
5. Ask Planner whether a required action exists now.
6. If a required action exists and passes Guard, return it.
7. If current rules allow cargo search, call `query_cargo`.
8. Build and rank candidates with base candidate filtering.
9. Apply PolicyGuard hard filters.
10. Score remaining candidates.
11. Return `take_order`, `reposition`, or `wait`.
12. Log compact decision reasoning for later experiment analysis.

## Experiment Tracking

Every full or partial evaluation must produce a durable experiment record. The goal is to make strategy tuning measurable rather than intuition-driven.

Use two locations:

- `docs/superpowers/experiments/`: day-to-day tuning runs, parameter sweeps, partial simulations, and failed experiments worth remembering.
- `docs/superpowers/baselines/`: stable milestone runs that represent a meaningful comparison point.

Each experiment record should include:

- Experiment ID, using timestamp plus strategy name, for example `2026-05-13-preference-v1-full-30d`.
- Code and configuration summary.
- Commands used for simulation and scoring.
- Simulation settings, including `simulation_duration_days` and `simulation_max_steps`.
- Total metrics:
  - `total_net_income_all_drivers`
  - `total_preference_penalty`
  - `failed_driver_count`
  - `total_token_usage`
  - `simulate_time_seconds`
- Per-driver metrics:
  - gross income
  - cost
  - preference penalty
  - net income
  - accepted/rejected/wait/reposition counts
  - important preference-rule penalties
- Deltas from the chosen baseline:
  - net income delta
  - preference penalty delta
  - D009 and D010 deltas
  - accepted-false delta
  - token and runtime delta
- Interpretation:
  - what improved
  - what regressed
  - what to tune next

A small summarizer script should be part of the implementation plan. It should read `demo/results/monthly_income_202603.json`, `demo/results/run_summary_202603.json`, and latest `actions_202603_D*.jsonl` files, then emit a Markdown report in the appropriate tracking directory.

## Testing Strategy

### Unit Tests

Add focused tests for:

- Preference strength classification.
- Cargo category extraction.
- Time window extraction, including cross-day windows.
- Coordinate and radius extraction.
- Distance-limit extraction.
- Temporary cargo ID extraction.
- Home/stay-window extraction.
- Unknown strong and unknown soft fallback classification.
- Guard rejection for forbidden category, time window, distance limit, and forbidden zone.
- Scorer ordering after soft penalties.

### Strategy Tests

Create small scenario tests for:

- Mandatory wait during no-drive windows.
- Reposition to a required coordinate before a deadline.
- Refusing a profitable cargo that would violate a hard preference.
- Choosing a slightly lower-profit cargo that satisfies a planned task.
- Scheduling rest before the day ends.
- Avoiding repeated invalid `take_order` after recent rejected actions.

### Full Evaluation

For milestone runs:

```powershell
cd E:\school\KACHE\demo\server
python main.py
cd E:\school\KACHE\demo
python calc_monthly_income.py
```

Then generate an experiment report and compare with the current 30-day baseline.

## Success Criteria

The design is successful when an implementation can show:

- `failed_driver_count = 0` on local full evaluation.
- No driver-ID-specific preference hardcoding.
- No raw data file reads from decision code.
- Total preference penalty lower than the baseline `170630.0`.
- Total net income higher than the baseline `131389.65`.
- D009 and D010 are no longer negative primarily because of ignored temporary/home obligations.
- Accepted-false counts are lower than the baseline.
- Token use remains controlled because model calls are limited to preference parsing fallback.
- Every meaningful run has an experiment record with total metrics, per-driver metrics, and next tuning notes.

## Non-Goals

- Do not modify official simulator, scoring scripts, or raw data files for competitive advantage.
- Do not build a global optimizer that requires direct access to all cargo data.
- Do not make every step model-driven.
- Do not solve every possible natural-language preference in V1; unknown handling exists for safe degradation.
- Do not package local results for finals unless the submission rules require them.

## Open Implementation Decisions

These decisions should be resolved in the implementation plan:

- Exact module split under `demo/agent/`.
- Whether parsed rules are dataclasses or plain dictionaries.
- Cache key and cache lifetime for parsed preferences.
- Maximum model fallback calls per driver.
- Exact wait duration for conservative unknown-strong handling.
- How aggressively to schedule monthly off-days early versus preserving earning opportunities.
- Scoring weights for soft preferences and task contribution.
- Report filename format for experiments and baselines.

## Git Note

This workspace is not currently a git repository, so the Superpowers brainstorming instruction to commit the written design cannot be completed here. The spec is saved on disk and should be reviewed directly.
