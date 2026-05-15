# Hard Window And Sequence Planning Design

## Context

The latest diagnostics show that the remaining high penalties are concentrated in hard time-window behavior:

- D009 has `36100.0` penalty:
  - Required cargo `240646` was not satisfied: `10000.0`
  - Home-before-23:00 and no-drive 23:00-08:00 violations: `26100.0`
- D010 has `16910.0` penalty:
  - Family sequence task failed: `10910.0`
  - Daily rest violations: `6000.0`

The D010 timeline shows the driver reached the pickup coordinate and then home on `2026-03-10`, but the pickup step was not counted. The likely cause is that the planner treats "visited the pickup coordinate" as enough, while the preference requires staying at the pickup point for at least `wait_minutes`.

The next optimization should first fix the low-risk sequence dwell issue, then add a generic hard-window feasibility filter for cargo candidates.

## Goals

1. Ensure sequence-task pickup steps are only treated as complete after the required dwell time is satisfied.
2. Prevent taking orders that make parsed hard future windows obviously impossible.
3. Keep the logic generic and driven by parsed preference rules, never by driver IDs or hidden dataset files.
4. Preserve the existing layered deterministic strategy and keep `qwen3.5-flash` only as unknown strong preference parsing fallback.
5. Produce a new experiment report with baseline delta against `2026-05-14-diff-diagnostics-local.json`.

## Non-Goals

1. Do not make the model choose cargo or actions.
2. Do not special-case D009, D010, cargo `240646`, or any specific driver ID in production decision logic.
3. Do not read `server/data/cargo_dataset.jsonl` or `server/data/drivers.json` from agent decision code.
4. Do not implement a full route optimizer; this is a conservative hard-rule feasibility pass.

## Approach

### Sequence Dwell Completion

Add planner logic that can distinguish these states for a sequence pickup step:

1. Not at pickup target yet: reposition to pickup.
2. At pickup target but required dwell is not satisfied: wait remaining dwell minutes.
3. Dwell satisfied before the deadline: proceed to return-home step.

The dwell check should use action history, not driver ID. It should count continuous waiting at the target location before the sequence deadline. A record can contribute dwell credit when:

- The action is `wait`.
- `position_after` is within the step radius of the pickup target.
- The wait ended before or at the sequence deadline.

The current in-place case should also work: if the current position is within pickup radius and no sufficient wait history exists, return a `sequence_pickup_wait` intent for the remaining dwell.

### Hard Future Window Feasibility

Add a conservative candidate filter before scoring. It should reject a candidate when:

- The candidate's estimated finish minute plus travel time to a required target exceeds a parsed `HOME_DEADLINE`.
- The candidate would finish or require travel inside a parsed `NO_DRIVE_WINDOW` where the action is forbidden.
- A sequence task is active and the candidate would consume time needed to pickup, dwell, return home, and arrive before the sequence deadline.

This filter should use existing candidate estimates and simple reposition travel estimates. It should prefer false negatives over false positives: only block candidates when the violation is obvious.

### Required Cargo Planning

Required cargo planning should remain a follow-up unless the first two changes are insufficient. The current iteration may keep waiting when required cargo is not visible. If the hard-window feasibility work reduces D009 night/home violations but still misses required cargo, the next design should add runtime-only planning around parsed required-cargo metadata.

## Data Flow

1. `ModelDecisionService.decide()` parses deterministic preference rules.
2. Planner checks required sequence/home/window intents before cargo query.
3. Cargo candidates are queried and filtered by policy guard.
4. New feasibility filtering removes candidates that conflict with hard future windows.
5. Scoring chooses among remaining candidates.
6. Experiment report compares the new run to the saved baseline JSON.

## Testing

Add focused tests before implementation:

- Planner test: at pickup target with no dwell history returns `sequence_pickup_wait`.
- Planner test: partial dwell history returns wait for remaining minutes.
- Planner test: enough dwell history allows return-home intent.
- Decision-service test: candidate that would make a home deadline impossible is rejected in favor of wait or a safer candidate.
- Decision-service test: feasibility filtering is generic and rule-driven.

Existing parser, policy guard, planner, scoring, decision service, and report tests must still pass.

## Acceptance Criteria

1. D010 sequence pickup dwell can be satisfied generically without driver-ID checks.
2. Candidate selection avoids clearly impossible hard future windows.
3. No production `demo/agent` code contains `driver_id ==`, `D009`, `D010`, or cargo `240646` hardcoding.
4. Unit tests pass.
5. A full local simulation report is generated with delta against `2026-05-14-diff-diagnostics-local.json`.
6. The report records total score, per-driver score changes, penalties, action changes, and token usage.

