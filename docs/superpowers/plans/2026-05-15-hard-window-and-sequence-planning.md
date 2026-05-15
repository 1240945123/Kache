# Hard Window And Sequence Planning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce hard-window penalties by requiring sequence pickup dwell completion and filtering cargo candidates that would make future hard windows impossible.

**Architecture:** Keep sequence state inside `planner.py`, because it already owns required intents from parsed rules and history. Add a small hard-window feasibility layer in `model_decision_service.py` before scoring, using parsed rules, current status, candidate estimates, and the existing distance helper.

**Tech Stack:** Python standard library, `unittest`, existing deterministic agent modules.

---

## File Structure

- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/planner.py`
  - Add sequence dwell-history detection and use it in `_sequence_task_intent`.
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_planner.py`
  - Add TDD coverage for pickup dwell wait, partial dwell, and completed dwell.
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/model_decision_service.py`
  - Add generic hard-window candidate feasibility filtering before scoring.
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_decision_service.py`
  - Add TDD coverage for rejecting candidates that make a home deadline impossible.
- Generated: `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/2026-05-15-hard-window-sequence-local.*`
  - Full-run report and JSON sidecar with baseline delta.

## Task 1: Sequence Pickup Dwell Completion

**Files:**
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/planner.py`
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_planner.py`

- [ ] **Step 1: Add failing planner tests**

Add these tests to `PlannerTest`:

```python
def _sequence_rule(self):
    return _rule(
        RuleType.SEQUENCE_TASK,
        {
            "steps": [
                {"action": "pickup", "lat": 23.21, "lng": 113.37, "wait_minutes": 10},
                {"action": "return_home", "lat": 23.19, "lng": 113.36},
            ],
            "deadline": "2026-03-10 22:00:00",
            "stay_until": "2026-03-13 22:00:00",
        },
    )


def test_sequence_task_waits_remaining_pickup_dwell_when_at_pickup(self):
    state = build_planner_state(
        {
            "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60,
            "current_lat": 23.21,
            "current_lng": 113.37,
            "completed_order_count": 0,
        },
        {"records": []},
    )

    intent = choose_required_intent(state, [self._sequence_rule()])

    self.assertIsNotNone(intent)
    self.assertEqual(intent.intent_type, "sequence_pickup_wait")
    self.assertEqual(intent.action, "wait")
    self.assertEqual(intent.params, {"duration_minutes": 10})


def test_sequence_task_waits_only_remaining_pickup_dwell(self):
    state = build_planner_state(
        {
            "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60 + 4,
            "current_lat": 23.21,
            "current_lng": 113.37,
            "completed_order_count": 0,
        },
        {
            "records": [
                {
                    "action": {"action": "wait", "params": {"duration_minutes": 4}},
                    "position_after": {"lat": 23.21, "lng": 113.37},
                    "simulation_end_time": "2026-03-10 16:04",
                    "step_elapsed_minutes": 4,
                }
            ]
        },
    )

    intent = choose_required_intent(state, [self._sequence_rule()])

    self.assertIsNotNone(intent)
    self.assertEqual(intent.intent_type, "sequence_pickup_wait")
    self.assertEqual(intent.params, {"duration_minutes": 6})


def test_sequence_task_returns_home_after_pickup_dwell_satisfied(self):
    state = build_planner_state(
        {
            "simulation_progress_minutes": 9 * 24 * 60 + 16 * 60 + 10,
            "current_lat": 23.21,
            "current_lng": 113.37,
            "completed_order_count": 0,
        },
        {
            "records": [
                {
                    "action": {"action": "wait", "params": {"duration_minutes": 10}},
                    "position_after": {"lat": 23.21, "lng": 113.37},
                    "simulation_end_time": "2026-03-10 16:10",
                    "step_elapsed_minutes": 10,
                }
            ]
        },
    )

    intent = choose_required_intent(state, [self._sequence_rule()])

    self.assertIsNotNone(intent)
    self.assertEqual(intent.intent_type, "sequence_return_home")
    self.assertEqual(intent.action, "reposition")
    self.assertEqual(intent.params, {"latitude": 23.19, "longitude": 113.36})
```

- [ ] **Step 2: Verify tests fail**

Run:

```powershell
python -m unittest demo\agent\test_planner.py -v
```

Expected: at least one new sequence dwell test fails because visiting the pickup point currently counts as completion before dwell is satisfied.

- [ ] **Step 3: Add dwell-credit helper**

In `planner.py`, add:

```python
def _wait_credit_near_target_before(
    state: PlannerState,
    latitude: float,
    longitude: float,
    radius_km: float,
    before_minute: int,
) -> int:
    credit = 0
    for record in reversed(state.history_records):
        if _action_name(record) != "wait":
            break
        end_minute = _minute_from_simulation_end_time(record.get("simulation_end_time"))
        if end_minute is None:
            end_minute = state.current_minute
        if end_minute > before_minute:
            continue
        position = record.get("position_after")
        if not isinstance(position, dict):
            break
        try:
            position_lat = float(position["lat"])
            position_lng = float(position["lng"])
        except (KeyError, TypeError, ValueError):
            break
        if haversine_km(position_lat, position_lng, latitude, longitude) > radius_km:
            break
        credit += _wait_minutes_from_record(record)
    return credit
```

- [ ] **Step 4: Update `_sequence_task_intent`**

Replace the pickup-completion branch with logic equivalent to:

```python
pickup_radius_km = float(pickup_step.get("radius_km", 1.0))
pickup_dwell_credit = _wait_credit_near_target_before(
    state,
    pickup_lat,
    pickup_lng,
    pickup_radius_km,
    deadline_minute,
)
pickup_dwell_satisfied = pickup_dwell_credit >= pickup_wait
at_pickup = haversine_km(state.current_lat, state.current_lng, pickup_lat, pickup_lng) <= pickup_radius_km

if not pickup_dwell_satisfied:
    if at_pickup:
        return PlannedIntent(
            intent_type="sequence_pickup_wait",
            action="wait",
            params={"duration_minutes": max(1, pickup_wait - pickup_dwell_credit)},
            reason=rule.source_text,
            priority=120,
            metadata={"rule_type": rule.rule_type.value},
        )
    return PlannedIntent(
        intent_type="sequence_pickup",
        action="reposition",
        params={"latitude": pickup_lat, "longitude": pickup_lng},
        reason=rule.source_text,
        priority=120,
        metadata={"rule_type": rule.rule_type.value},
    )
```

Do not use `_visited_target` to mark the pickup complete.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
python -m unittest demo\agent\test_planner.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add demo/agent/planner.py demo/agent/test_planner.py
git commit -m "fix: require sequence pickup dwell"
```

## Task 2: Hard Future Window Candidate Feasibility

**Files:**
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/model_decision_service.py`
- Modify: `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent/test_decision_service.py`

- [ ] **Step 1: Add failing decision-service test**

Add a test with a fake API status near a home deadline and two candidates:

```python
def test_candidate_that_makes_home_deadline_impossible_is_filtered(self):
    api = FakeApi()
    api.status = {
        "simulation_progress_minutes": 22 * 60,
        "current_lat": 23.12,
        "current_lng": 113.28,
        "completed_order_count": 0,
        "preferences": [
            {
                "content": "每天23点前车辆须在自家位置（23.12，113.28）一公里内；当天23点至次日8点不接单、不空跑。"
            }
        ],
    }
    api.cargo_items = [
        {
            "cargo": {
                "cargo_id": "late",
                "load_lat": 23.12,
                "load_lng": 113.28,
                "unload_lat": 24.50,
                "unload_lng": 115.00,
                "freight_price": 10000,
                "distance_km": 260,
                "truck_length_required": "4.2米",
                "cargo_name": "普通货物",
                "load_window_start": "2026-03-01 22:00:00",
                "load_window_end": "2026-03-01 22:30:00",
            }
        }
    ]

    action = ModelDecisionService(api).decide("DXXX")

    self.assertEqual(action["action"], "wait")
```

Adjust fixture field names to match existing `FakeApi` and candidate helper patterns in `test_decision_service.py`.

- [ ] **Step 2: Verify test fails**

Run:

```powershell
python -m unittest demo\agent\test_decision_service.py -v
```

Expected: new test fails because the high-value late candidate is currently selected.

- [ ] **Step 3: Implement helper methods in `ModelDecisionService`**

Add methods:

```python
def _candidate_finish_minute(self, status: dict[str, Any], candidate: Candidate) -> int:
    current_minute = int(status.get("simulation_progress_minutes", 0) or 0)
    return current_minute + max(0, int(round(candidate.pickup_eta_minutes + candidate.haul_eta_minutes)))


def _travel_minutes(self, from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> int:
    distance_km = haversine_km(from_lat, from_lng, to_lat, to_lng)
    return int(distance_km / 60.0 * 60) + 1
```

Import `haversine_km` from `strategy_helpers`.

- [ ] **Step 4: Implement home-deadline feasibility**

Add:

```python
def _apply_hard_future_window_feasibility(
    self,
    candidates: list[Candidate],
    rules: list[PreferenceRule],
    status: dict[str, Any],
) -> list[Candidate]:
    filtered: list[Candidate] = []
    for candidate in candidates:
        if self._candidate_preserves_home_deadline(candidate, rules, status):
            filtered.append(candidate)
    return filtered


def _candidate_preserves_home_deadline(
    self,
    candidate: Candidate,
    rules: list[PreferenceRule],
    status: dict[str, Any],
) -> bool:
    finish_minute = self._candidate_finish_minute(status, candidate)
    finish_day_start = (finish_minute // 1440) * 1440
    for rule in rules:
        if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.HOME_DEADLINE:
            continue
        try:
            deadline_minute = int(rule.value["deadline_minute"])
            home_lat = float(rule.value["lat"])
            home_lng = float(rule.value["lng"])
        except (KeyError, TypeError, ValueError):
            continue
        deadline_abs = finish_day_start + deadline_minute
        if finish_minute > deadline_abs:
            return False
        return_home_minutes = self._travel_minutes(candidate.unload_lat, candidate.unload_lng, home_lat, home_lng)
        if finish_minute + return_home_minutes > deadline_abs:
            return False
    return True
```

- [ ] **Step 5: Wire feasibility before scoring**

After required cargo and monthly-deadhead filtering, before `score_candidates`, add:

```python
allowed_candidates = self._apply_hard_future_window_feasibility(allowed_candidates, rules, status)
```

If all candidates are filtered, existing fallback wait behavior should apply.

- [ ] **Step 6: Run focused tests**

Run:

```powershell
python -m unittest demo\agent\test_decision_service.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```powershell
git add demo/agent/model_decision_service.py demo/agent/test_decision_service.py
git commit -m "feat: filter impossible home deadline candidates"
```

## Task 3: Verification And Experiment Report

**Files:**
- Generated:
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/2026-05-15-hard-window-sequence-local.md`
  - `E:/school/KACHE/.worktrees/layered-preference-strategy/docs/superpowers/experiments/2026-05-15-hard-window-sequence-local.json`

- [ ] **Step 1: Run full unit tests**

Run:

```powershell
python -m unittest discover -s demo\agent -p "test_*.py" -v
```

Expected: PASS.

- [ ] **Step 2: Run full local simulation**

Run from `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/server`:

```powershell
python main.py
```

Expected: simulation completes and writes `demo/results`.

- [ ] **Step 3: Calculate monthly income**

Run from `E:/school/KACHE/.worktrees/layered-preference-strategy/demo`:

```powershell
python calc_monthly_income.py
```

Expected: monthly income JSON is updated.

- [ ] **Step 4: Generate diff report**

Run from `E:/school/KACHE/.worktrees/layered-preference-strategy/demo/agent`:

```powershell
python evaluate_results.py --results-dir ..\results --out-dir ..\..\docs\superpowers\experiments --experiment-id 2026-05-15-hard-window-sequence-local --baseline ..\..\docs\superpowers\experiments\2026-05-14-diff-diagnostics-local.json --timeline-driver D009 --timeline-driver D010
```

Expected: report and JSON paths are printed.

- [ ] **Step 5: Inspect deltas**

Run:

```powershell
rg -n "## Summary|## Delta|\| D009 \||\| D010 \||total_token_usage.total_tokens" E:\school\KACHE\.worktrees\layered-preference-strategy\docs\superpowers\experiments\2026-05-15-hard-window-sequence-local.md
```

Expected: summary, delta, token usage, and D009/D010 rows are visible.

- [ ] **Step 6: Hardcoding scan**

Run:

```powershell
rg -n "driver_id\s*==|D009|D010|240646" E:\school\KACHE\.worktrees\layered-preference-strategy\demo\agent --glob "!test_*.py"
```

Expected: no production decision-code matches.

- [ ] **Step 7: Commit experiment report**

Run:

```powershell
git add docs/superpowers/experiments/2026-05-15-hard-window-sequence-local.md docs/superpowers/experiments/2026-05-15-hard-window-sequence-local.json
git commit -m "docs: record hard window sequence experiment"
```

## Final Verification

- [ ] Run:

```powershell
python -m unittest discover -s demo\agent -p "test_*.py" -v
```

- [ ] Run:

```powershell
git status --short --branch
```

- [ ] Push:

```powershell
git push origin layered-preference-strategy
```

