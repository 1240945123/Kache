# Agent Candidate Filtering Design

## Goal

Improve the first-round Agent strategy by adding a generic candidate filtering and ranking layer before model selection. The change should prioritize income legality and basic profitability while preserving the official rule that driver preferences must not be hardcoded by driver ID.

## Scope

In scope:

- Modify `demo/agent/model_decision_service.py`.
- Add small, testable helper functions inside the agent module or a sibling agent helper module.
- Filter visible cargo candidates before sending them to the model.
- Keep runtime driver preferences in the model context without parsing them into driver-specific hardcoded rules.
- Add safe fallback behavior for no candidates, invalid model output, or model choosing an unapproved cargo ID.
- Validate with a short simulation and income calculation.

Out of scope for this first round:

- Modifying `demo/server/`, `demo/simkit/`, or scoring scripts.
- Reading `demo/server/data/cargo_dataset.jsonl` or `demo/server/data/drivers.json` from decision code.
- Writing `if driver_id == "D001"` or equivalent driver-specific preference rules.
- Building a complete long-horizon optimizer.
- Changing model provider, model endpoint, or official evaluation protocol.

## Current Baseline Evidence

The smoke baseline in `docs/superpowers/baselines/2026-05-09-smoke-baseline.md` showed:

- `python main.py --max-steps 5` completed after increasing local model timeout to `180` seconds.
- `python calc_monthly_income.py` produced `failed_driver_count=0`.
- Total net income was `-8592.13`.
- Total preference penalty was `8500.0`.
- Total token usage was `36199` for only five steps.
- D001 accepted an order with `income_eligible=false` under the 1-day smoke horizon.

This indicates the current baseline is syntactically valid but makes obviously poor decisions and spends too much time/tokens asking the model to reason over noisy candidate lists.

## Architecture

Keep `ModelDecisionService.decide(driver_id)` as the public entry point. Internally, split the work into focused helpers:

- `_build_candidate(...)`
  - Converts a `query_cargo` item into a normalized candidate summary.
  - Computes pickup distance, pickup time, load-window feasibility, estimated finish minute, gross price, rough distance cost, and rough net value.
- `_filter_and_rank_candidates(...)`
  - Removes clearly invalid or low-quality cargo.
  - Sorts remaining candidates by rough net value and time efficiency.
  - Returns the top candidates to expose to the model.
- `_build_prompt(...)`
  - Includes the driver state, runtime `preferences`, and only the filtered top candidates.
  - Instructs the model to choose only from allowed `cargo_id` values or return `wait` / `reposition`.
- `_parse_action(...)`
  - Keeps existing JSON structure validation.
  - Adds a guard that `take_order` can only use an allowed filtered `cargo_id`.
- `_fallback_action(...)`
  - Returns a safe action when no candidate is available or model output is invalid.
  - First-round fallback should prefer bounded waiting over expensive movement.

The implementation can use dictionaries or dataclasses. The preference is to keep the first round compact and testable; introduce a dataclass only if it makes the filtering code clearer.

## Candidate Estimation

For each cargo candidate, estimate:

- `cargo_id`
- `price`
- `pickup_distance_km`
- `pickup_minutes`
- `load_start_minutes` and `load_end_minutes`, when `load_time` exists
- `estimated_start_transport_minute`
- `cost_time_minutes`
- `estimated_finish_minute`
- `pickup_cost`
- `haul_distance_km`, computed from cargo `start` and `end` when coordinates exist
- `haul_cost`
- `rough_net_value = price - pickup_cost - haul_cost`

Use the same broad semantics as `simkit.simulation_actions`:

- Haversine distance for coordinate distance.
- `ceil(distance / speed * 60)` for movement minutes.
- Zero pickup distance should cost `0` pickup minutes for taking an order.
- If arrival is before the load window start, include waiting until the window start.
- If arrival is after the load window end, reject the candidate.

Because `SimulationApiPort` does not expose `simulation_duration_days`, the first round should not hardcode a formal horizon in decision code. Instead, it should reject candidates that are clearly bad in the visible context and avoid very long orders during short smoke runs through a configurable or conservative local threshold. The implementation plan should decide whether this threshold belongs as a constant in the agent module or a parameter inside helper functions for tests.

## Filtering Rules

Reject a candidate when:

- Required fields are missing or malformed.
- `cargo_id` is empty.
- `price` is missing or non-positive.
- Start/end coordinates are missing.
- `cost_time_minutes` is missing or negative.
- The truck length field clearly excludes the driver's `truck_length`, when both sides are available.
- The pickup arrival time misses the `load_time` end.
- Rough net value is clearly negative after estimated pickup and haul distance costs.

Do not reject based on driver-specific preference text in code. The filtering layer may pass preference text to the model and may include generic instruction such as “respect the driver's runtime preferences.”

## Ranking Rules

Rank candidates by:

1. Higher `rough_net_value`.
2. Higher value per total estimated minute.
3. Lower pickup distance.
4. Earlier feasible finish time.

Expose at most 8-12 candidates to the model. The implementation plan should choose one fixed number for the first iteration.

## Fallback Behavior

When there are no filtered candidates:

- Query recent history with `query_decision_history(driver_id, step)` if available.
- If recent history shows repeated waiting with no accepted order, first-round behavior may still wait conservatively unless a low-cost reposition target is already available from visible candidates.
- Return `wait` with a bounded duration such as 30 or 60 minutes.

When the model output is invalid:

- Return fallback `wait`.
- Log the reason at `INFO` or `WARNING` level.

When the model returns `take_order` for a cargo ID outside the allowed filtered set:

- Return fallback `wait`, or choose the top-ranked allowed candidate deterministically.
- First-round recommendation: choose top-ranked allowed candidate only if its rough net value is positive; otherwise wait.

## Preference Handling

The design must comply with the official constraint:

- Do not hardcode driver preference rules by `driver_id`.
- Do not read or cache `drivers.json`.
- Do not write rules like `D001 must stay in Shenzhen`.
- Use `status["preferences"]` only as runtime data.
- Include preference text or preference objects in the model prompt.
- Let the model interpret preferences from text in the context of the filtered candidate list.

Future versions may add generic natural-language preference classifiers, but only if they do not depend on specific driver IDs or hidden data files.

## Error Handling

- Catch JSON parsing failures from model output and fall back safely.
- Catch missing candidate fields inside candidate-building helpers and skip only the malformed candidate.
- Keep `decide(driver_id)` returning one valid action dictionary whenever possible.
- Preserve exceptions for unexpected API failures unless a fallback can be produced without hiding a real infrastructure issue.

## Testing Strategy

Add focused tests or a lightweight verification script for helper behavior:

- Candidate with expired load window is filtered.
- Candidate with negative rough net value is filtered.
- Candidate with missing coordinates is skipped.
- Candidate with unsupported truck length is filtered.
- Candidate with valid positive rough value is ranked above weaker alternatives.
- Model output selecting an unapproved `cargo_id` cannot pass through as `take_order`.
- Fallback returns a valid `wait` action.

Then run:

```powershell
cd demo\server
python main.py --max-steps 5
cd ..
python calc_monthly_income.py
```

Compare against the smoke baseline:

- `failed_driver_count` must remain `0`.
- D001 should not accept a clearly horizon-ineligible or grossly negative-value cargo in the first five steps.
- Total token usage should decrease or at least avoid a meaningful increase.
- Simulation wall time should decrease or at least avoid a meaningful increase.

## Success Criteria

- The agent still produces legal action logs under the local smoke run.
- The implementation contains no driver-ID-specific preference hardcoding.
- The model receives fewer and cleaner candidates than the current baseline.
- Invalid model output and unapproved cargo IDs are handled safely.
- The change is isolated to competitor-owned agent logic unless tests require a new local test file.

## Open Decisions For Implementation Plan

- Whether helpers live in `model_decision_service.py` or a new `demo/agent/strategy_helpers.py`.
- Whether to use a dataclass for candidate summaries.
- The exact top candidate count, recommended first value: `10`.
- The exact fallback wait duration, recommended first value: `30` minutes.
- The rough cost model for haul distance when official driver `cost_per_km` is not visible through `get_driver_status`.

## Git Note

This workspace is not currently a git repository, so the Superpowers brainstorming instruction to commit the written design cannot be completed here. The design is saved on disk and verified directly instead.
