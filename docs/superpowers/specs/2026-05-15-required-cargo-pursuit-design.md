# Required Cargo Pursuit Design

## Context

The current strategy already parses `REQUIRED_CARGO` and prioritizes a required cargo when it appears in `query_cargo` results. The remaining failure mode is visibility and generic candidate filtering:

- A required cargo can be far outside the nearest-cargo query set unless the driver moves near its pickup point.
- A required cargo can exceed the normal `MAX_TOTAL_ORDER_MINUTES` guard, even when accepting it avoids a large hard-rule penalty.

## Goals

1. Pursue any hard `REQUIRED_CARGO` rule that includes pickup coordinates and an availability time.
2. Keep the implementation generic: no production checks for driver IDs, D009, or a fixed cargo ID.
3. Preserve normal candidate limits for ordinary cargo.
4. Record the next experiment score so later tuning has a concrete before/after trace.

## Design

Extend required cargo parsing to capture optional metadata from the preference text:

- `cargo_id`
- `pickup_lat`
- `pickup_lng`
- `available_minute`

Add a planner intent for hard required cargo rules with pickup metadata. Before the cargo is available, the driver should reposition toward the pickup point when there is not enough remaining lead time to stay idle elsewhere. If already near the pickup point, wait in bounded chunks until the cargo can appear. Once available, normal cargo query should see the target because the driver is nearby.

Update candidate building so required-cargo selection can bypass only the generic maximum total order duration. Other guards still apply, including truck length, load window feasibility, removal time, positive value, horizon, and hard policy filters.

## Non-Goals

- Do not implement broader no-drive-window future feasibility in this step.
- Do not special-case any specific driver, cargo ID, coordinate, or date in production code.
- Do not use an LLM for this rule when the structured text parser can extract it deterministically.

## Validation

- Unit tests prove parser metadata extraction, planner reposition/wait behavior, and required-cargo duration bypass.
- Full simulation report compares against `2026-05-15-hard-window-sequence-local.json`.
- Hardcoding scan checks production `demo/agent` code for driver/cargo-specific branches.
