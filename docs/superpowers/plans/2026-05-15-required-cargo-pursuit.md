# Required Cargo Pursuit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make hard required-cargo rules actively pursue visible pickup metadata and accept the required cargo without the ordinary order-duration cap.

**Architecture:** `preference_parser.py` extracts optional pickup/time metadata into the existing `REQUIRED_CARGO` rule. `planner.py` turns that metadata into required reposition/wait intents before cargo query. `strategy_helpers.py` exposes a required-cargo mode that bypasses only `MAX_TOTAL_ORDER_MINUTES`, and `model_decision_service.py` uses it only when required cargo IDs exist.

**Tech Stack:** Python standard library, existing unittest suite, local simulation scripts.

---

### Task 1: Parse Required Cargo Metadata

**Files:**
- Modify: `demo/agent/preference_parser.py`
- Test: `demo/agent/test_preference_parser.py`

- [ ] Add a failing parser test using a generic cargo ID and Chinese preference text containing pickup coordinates and create time.
- [ ] Extend `_parse_required_cargo` to keep `cargo_id` and add `pickup_lat`, `pickup_lng`, and `available_minute` when present.
- [ ] Run `python -m unittest test_preference_parser.py -v` from `demo/agent`.
- [ ] Commit parser changes.

### Task 2: Plan Required Cargo Pursuit

**Files:**
- Modify: `demo/agent/planner.py`
- Modify: `demo/agent/model_decision_service.py`
- Test: `demo/agent/test_planner.py`

- [ ] Add failing planner tests for required-cargo reposition and near-pickup bounded wait.
- [ ] Add `REQUIRED_CARGO` to the decision-service history/planner path.
- [ ] Implement a generic required-cargo planner intent driven by rule metadata.
- [ ] Run `python -m unittest test_planner.py test_decision_service.py -v` from `demo/agent`.
- [ ] Commit planner changes.

### Task 3: Required Cargo Duration Bypass

**Files:**
- Modify: `demo/agent/strategy_helpers.py`
- Modify: `demo/agent/model_decision_service.py`
- Test: `demo/agent/test_decision_service.py`
- Test: `demo/agent/test_strategy_helpers.py`

- [ ] Add failing tests showing ordinary cargo over the duration cap is filtered, but required cargo can be selected when otherwise feasible.
- [ ] Add a `max_total_order_minutes` parameter to candidate building/ranking.
- [ ] Call ranking with no total-duration cap only when hard required cargo IDs exist.
- [ ] Run `python -m unittest test_strategy_helpers.py test_decision_service.py -v` from `demo/agent`.
- [ ] Commit duration-bypass changes.

### Task 4: Full Verification And Experiment Record

**Files:**
- Create: `docs/superpowers/experiments/2026-05-15-required-cargo-pursuit-local.md`
- Create: `docs/superpowers/experiments/2026-05-15-required-cargo-pursuit-local.json`

- [ ] Run full agent tests.
- [ ] Run hardcoding scan against production `demo/agent` files.
- [ ] Run `python main.py` from `demo/server`.
- [ ] Run `python calc_monthly_income.py` from `demo`.
- [ ] Generate an experiment report against `2026-05-15-hard-window-sequence-local.json`.
- [ ] Commit the experiment report and push the branch.
