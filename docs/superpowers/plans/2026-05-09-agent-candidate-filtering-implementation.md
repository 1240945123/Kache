# Agent Candidate Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a generic candidate filtering and fallback layer so the Agent avoids obviously invalid or unprofitable cargo before asking the model to choose.

**Architecture:** Keep `ModelDecisionService` as the injected decision entry point, move reusable scoring math to a new `demo/agent/strategy_helpers.py`, and cover those helpers with stdlib `unittest` tests. The Agent will pass only top-ranked allowed candidates to the model and reject model-selected cargo IDs outside that allowed set.

**Tech Stack:** Python 3.12, standard library `dataclasses`/`datetime`/`math`/`unittest`, existing `SimulationApiPort`.

---

## File Structure

- Create: `demo/agent/strategy_helpers.py`
  - Pure helper functions and dataclass for candidate estimation, filtering, ranking, and fallback action creation.
- Create: `demo/agent/test_strategy_helpers.py`
  - Standard-library unit tests for filtering, ranking, truck length checks, fallback, and allowed cargo guards.
- Modify: `demo/agent/model_decision_service.py`
  - Use helper functions, reduce candidate prompt size, include runtime preferences, validate model-selected cargo IDs, and fall back safely.
- Verify: `demo/server/main.py`
  - Run short local smoke simulation.
- Verify: `demo/calc_monthly_income.py`
  - Recompute legality and income for smoke result.

### Task 1: Add Strategy Helper Tests First

**Files:**
- Create: `demo/agent/test_strategy_helpers.py`

- [ ] **Step 1: Write failing tests for candidate filtering and fallback**

Create `demo/agent/test_strategy_helpers.py`:

```python
from __future__ import annotations

import unittest

from strategy_helpers import (
    DEFAULT_FALLBACK_WAIT_MINUTES,
    build_candidate,
    fallback_wait_action,
    filter_and_rank_candidates,
    parse_model_action,
)


def _status(**overrides):
    base = {
        "current_lat": 22.54,
        "current_lng": 114.06,
        "truck_length": "4.2米",
        "simulation_progress_minutes": 60,
    }
    base.update(overrides)
    return base


def _item(**cargo_overrides):
    cargo = {
        "cargo_id": "C1",
        "price": 500.0,
        "cost_time_minutes": 120,
        "load_time": ["2026-03-01 02:00:00", "2026-03-01 06:00:00"],
        "truck_length": ["4.2米"],
        "start": {"lat": 22.55, "lng": 114.07},
        "end": {"lat": 22.8, "lng": 114.2},
    }
    cargo.update(cargo_overrides)
    return {"distance_km": 1.5, "cargo": cargo}


class StrategyHelpersTest(unittest.TestCase):
    def test_build_candidate_accepts_valid_positive_candidate(self):
        candidate = build_candidate(_item(), _status())
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.cargo_id, "C1")
        self.assertGreater(candidate.rough_net_value, 0)
        self.assertGreater(candidate.estimated_finish_minute, 60)

    def test_expired_load_window_is_filtered(self):
        expired = _item(load_time=["2026-03-01 00:00:00", "2026-03-01 00:30:00"])
        ranked = filter_and_rank_candidates([expired], _status(simulation_progress_minutes=120))
        self.assertEqual(ranked, [])

    def test_negative_value_candidate_is_filtered(self):
        bad = _item(price=1.0)
        ranked = filter_and_rank_candidates([bad], _status())
        self.assertEqual(ranked, [])

    def test_missing_coordinates_candidate_is_skipped(self):
        malformed = _item(start={})
        ranked = filter_and_rank_candidates([malformed], _status())
        self.assertEqual(ranked, [])

    def test_unsupported_truck_length_is_filtered(self):
        wrong_truck = _item(truck_length=["13.0米"])
        ranked = filter_and_rank_candidates([wrong_truck], _status(truck_length="4.2米"))
        self.assertEqual(ranked, [])

    def test_candidates_rank_by_rough_value(self):
        low = _item(cargo_id="LOW", price=300.0)
        high = _item(cargo_id="HIGH", price=800.0)
        ranked = filter_and_rank_candidates([low, high], _status())
        self.assertEqual([c.cargo_id for c in ranked], ["HIGH", "LOW"])

    def test_parse_model_action_rejects_unapproved_cargo(self):
        response = {"choices": [{"message": {"content": "{\"action\":\"take_order\",\"params\":{\"cargo_id\":\"BAD\"}}"}}]}
        action = parse_model_action(response, allowed_cargo_ids={"GOOD"})
        self.assertEqual(action, fallback_wait_action())

    def test_fallback_wait_action_is_valid(self):
        self.assertEqual(
            fallback_wait_action(),
            {"action": "wait", "params": {"duration_minutes": DEFAULT_FALLBACK_WAIT_MINUTES}},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail because helpers do not exist**

Run:

```powershell
cd demo\agent
python -m unittest test_strategy_helpers.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'strategy_helpers'`.

### Task 2: Implement Strategy Helpers

**Files:**
- Create: `demo/agent/strategy_helpers.py`
- Test: `demo/agent/test_strategy_helpers.py`

- [ ] **Step 1: Add helper module**

Create `demo/agent/strategy_helpers.py`:

```python
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

SIMULATION_EPOCH = datetime(2026, 3, 1, 0, 0, 0)
DEFAULT_SPEED_KM_PER_HOUR = 60.0
DEFAULT_COST_PER_KM = 1.5
DEFAULT_TOP_CANDIDATE_LIMIT = 10
DEFAULT_FALLBACK_WAIT_MINUTES = 30
MAX_TOTAL_ORDER_MINUTES = 12 * 60


@dataclass(frozen=True)
class Candidate:
    cargo_id: str
    price: float
    pickup_distance_km: float
    pickup_minutes: int
    wait_minutes: int
    cost_time_minutes: int
    estimated_finish_minute: int
    haul_distance_km: float
    rough_net_value: float
    value_per_minute: float
    start: dict[str, Any]
    end: dict[str, Any]
    load_time: Any

    def to_prompt_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["price"] = round(self.price, 2)
        data["pickup_distance_km"] = round(self.pickup_distance_km, 2)
        data["haul_distance_km"] = round(self.haul_distance_km, 2)
        data["rough_net_value"] = round(self.rough_net_value, 2)
        data["value_per_minute"] = round(self.value_per_minute, 4)
        return data


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    p1 = math.radians(lat1)
    l1 = math.radians(lng1)
    p2 = math.radians(lat2)
    l2 = math.radians(lng2)
    dp = p2 - p1
    dl = l2 - l1
    h = math.sin(dp * 0.5) ** 2 + math.cos(p1) * math.cos(p2) * (math.sin(dl * 0.5) ** 2)
    h = min(1.0, max(0.0, h))
    return 2.0 * radius_km * math.asin(math.sqrt(h))


def movement_minutes(distance_km: float, speed_km_per_hour: float = DEFAULT_SPEED_KM_PER_HOUR) -> int:
    if distance_km <= 1e-6:
        return 0
    return max(1, math.ceil((distance_km / speed_km_per_hour) * 60))


def wall_time_to_minutes(text: str) -> int:
    dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S")
    return int((dt - SIMULATION_EPOCH).total_seconds() // 60)


def _load_window_minutes(load_time: Any) -> tuple[int, int] | None:
    if load_time is None:
        return None
    if not isinstance(load_time, list) or len(load_time) != 2:
        return None
    left = str(load_time[0]).strip()
    right = str(load_time[1]).strip()
    if not left or not right:
        return None
    start = wall_time_to_minutes(left)
    end = wall_time_to_minutes(right)
    if end < start:
        return None
    return start, end


def _truck_length_allowed(cargo: dict[str, Any], driver_truck_length: str) -> bool:
    allowed = cargo.get("truck_length")
    if not allowed or not driver_truck_length:
        return True
    if isinstance(allowed, list):
        return str(driver_truck_length) in {str(item) for item in allowed}
    return str(allowed) == str(driver_truck_length)


def build_candidate(
    item: dict[str, Any],
    status: dict[str, Any],
    *,
    speed_km_per_hour: float = DEFAULT_SPEED_KM_PER_HOUR,
    cost_per_km: float = DEFAULT_COST_PER_KM,
) -> Candidate | None:
    try:
        cargo = item.get("cargo")
        if not isinstance(cargo, dict):
            return None
        cargo_id = str(cargo.get("cargo_id", "")).strip()
        if not cargo_id:
            return None
        price = float(cargo.get("price", 0.0))
        if price <= 0:
            return None
        cost_time_minutes = int(cargo.get("cost_time_minutes"))
        if cost_time_minutes < 0:
            return None
        driver_truck_length = str(status.get("truck_length", "")).strip()
        if not _truck_length_allowed(cargo, driver_truck_length):
            return None
        current_lat = float(status["current_lat"])
        current_lng = float(status["current_lng"])
        current_minute = int(status.get("simulation_progress_minutes", 0))
        start = cargo.get("start")
        end = cargo.get("end")
        if not isinstance(start, dict) or not isinstance(end, dict):
            return None
        start_lat = float(start["lat"])
        start_lng = float(start["lng"])
        end_lat = float(end["lat"])
        end_lng = float(end["lng"])
    except (KeyError, TypeError, ValueError):
        return None

    pickup_distance_km = haversine_km(current_lat, current_lng, start_lat, start_lng)
    pickup_minutes = movement_minutes(pickup_distance_km, speed_km_per_hour=speed_km_per_hour)
    arrival_minute = current_minute + pickup_minutes
    window = _load_window_minutes(cargo.get("load_time"))
    wait_minutes = 0
    if window is not None:
        load_start, load_end = window
        if arrival_minute > load_end:
            return None
        wait_minutes = max(0, load_start - arrival_minute)
    estimated_finish_minute = arrival_minute + wait_minutes + cost_time_minutes
    total_order_minutes = estimated_finish_minute - current_minute
    if total_order_minutes > MAX_TOTAL_ORDER_MINUTES:
        return None
    haul_distance_km = haversine_km(start_lat, start_lng, end_lat, end_lng)
    rough_cost = (pickup_distance_km + haul_distance_km) * cost_per_km
    rough_net_value = price - rough_cost
    if rough_net_value <= 0:
        return None
    value_per_minute = rough_net_value / max(1, total_order_minutes)
    return Candidate(
        cargo_id=cargo_id,
        price=price,
        pickup_distance_km=pickup_distance_km,
        pickup_minutes=pickup_minutes,
        wait_minutes=wait_minutes,
        cost_time_minutes=cost_time_minutes,
        estimated_finish_minute=estimated_finish_minute,
        haul_distance_km=haul_distance_km,
        rough_net_value=rough_net_value,
        value_per_minute=value_per_minute,
        start=start,
        end=end,
        load_time=cargo.get("load_time"),
    )


def filter_and_rank_candidates(
    items: list[dict[str, Any]],
    status: dict[str, Any],
    *,
    limit: int = DEFAULT_TOP_CANDIDATE_LIMIT,
) -> list[Candidate]:
    candidates = [candidate for item in items if (candidate := build_candidate(item, status)) is not None]
    candidates.sort(
        key=lambda c: (
            -c.rough_net_value,
            -c.value_per_minute,
            c.pickup_distance_km,
            c.estimated_finish_minute,
        )
    )
    return candidates[:limit]


def fallback_wait_action(duration_minutes: int = DEFAULT_FALLBACK_WAIT_MINUTES) -> dict[str, Any]:
    return {"action": "wait", "params": {"duration_minutes": int(duration_minutes)}}


def parse_model_action(model_resp: dict[str, Any], *, allowed_cargo_ids: set[str]) -> dict[str, Any]:
    try:
        choices = model_resp.get("choices")
        if not isinstance(choices, list) or not choices:
            return fallback_wait_action()
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            return fallback_wait_action()
        action = json.loads(content)
        if not isinstance(action, dict):
            return fallback_wait_action()
        action_name = str(action.get("action", "")).strip().lower()
        params = action.get("params")
        if not isinstance(params, dict):
            return fallback_wait_action()
        if action_name == "take_order":
            cargo_id = str(params.get("cargo_id", "")).strip()
            if cargo_id not in allowed_cargo_ids:
                return fallback_wait_action()
            return {"action": "take_order", "params": {"cargo_id": cargo_id}}
        if action_name == "reposition":
            latitude = float(params["latitude"])
            longitude = float(params["longitude"])
            return {"action": "reposition", "params": {"latitude": latitude, "longitude": longitude}}
        if action_name == "wait":
            duration_minutes = int(params["duration_minutes"])
            if duration_minutes <= 0:
                return fallback_wait_action()
            return {"action": "wait", "params": {"duration_minutes": duration_minutes}}
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return fallback_wait_action()
    return fallback_wait_action()
```

- [ ] **Step 2: Run helper tests and verify they pass**

Run:

```powershell
cd demo\agent
python -m unittest test_strategy_helpers.py -v
```

Expected: `Ran 8 tests` and `OK`.

### Task 3: Wire Helpers Into ModelDecisionService

**Files:**
- Modify: `demo/agent/model_decision_service.py`
- Test: `demo/agent/test_strategy_helpers.py`

- [ ] **Step 1: Update imports**

Replace the imports at the top of `demo/agent/model_decision_service.py`:

```python
from __future__ import annotations

import json
import logging
from typing import Any

from simkit.ports import SimulationApiPort
from strategy_helpers import (
    Candidate,
    fallback_wait_action,
    filter_and_rank_candidates,
    parse_model_action,
)
```

- [ ] **Step 2: Replace `decide` body with filtered candidate flow**

Replace `ModelDecisionService.decide` with:

```python
    def decide(self, driver_id: str) -> dict[str, Any]:
        status = self._api.get_driver_status(driver_id)
        lat = float(status["current_lat"])
        lng = float(status["current_lng"])
        cargo_resp = self._api.query_cargo(driver_id=driver_id, latitude=lat, longitude=lng)
        items = cargo_resp.get("items", [])
        if not isinstance(items, list):
            items = []
        candidates = filter_and_rank_candidates(items, status)
        self._logger.info(
            "decision input driver_id=%s time_min=%s loc=(%.5f,%.5f) cargo_items=%s filtered_candidates=%s",
            driver_id,
            status.get("simulation_progress_minutes"),
            lat,
            lng,
            len(items),
            len(candidates),
        )
        if not candidates:
            action = fallback_wait_action()
            self._logger.info("decision fallback driver_id=%s reason=no_filtered_candidates action=%s", driver_id, action)
            return action

        prompt = self._build_prompt(driver_id=driver_id, status=status, candidates=candidates)
        model_resp = self._api.model_chat_completion(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "你是货运调度决策器。"
                            "只允许输出一个JSON对象，格式必须是"
                            '{"action":"take_order|reposition|wait","params":{...}}。'
                            "禁止输出markdown、解释或额外文本。"
                            "当action是take_order时，params必须包含cargo_id字符串，且cargo_id必须来自用户消息allowed_cargo_ids。"
                            "当action是reposition时，params必须包含latitude和longitude数值。"
                            "当action是wait时，params必须包含duration_minutes正整数。"
                            "必须遵守driver_status.preferences中的运行时偏好文本；不要假设隐藏司机规则。"
                            "优先选择可完成、粗略净值高、空驶距离低、时间效率高的候选。"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
            }
        )
        allowed_cargo_ids = {candidate.cargo_id for candidate in candidates}
        action = parse_model_action(model_resp, allowed_cargo_ids=allowed_cargo_ids)
        self._logger.info(
            "decision output driver_id=%s action=%s params=%s",
            driver_id,
            action.get("action"),
            action.get("params"),
        )
        return action
```

- [ ] **Step 3: Replace `_build_prompt` to accept ranked candidates**

Replace `_build_prompt` with:

```python
    def _build_prompt(self, driver_id: str, status: dict[str, Any], candidates: list[Candidate]) -> str:
        cargo_candidates = [candidate.to_prompt_dict() for candidate in candidates]
        decision_context = {
            "driver_id": driver_id,
            "simulation_progress_minutes": status.get("simulation_progress_minutes"),
            "driver_status": {
                "current_lat": status.get("current_lat"),
                "current_lng": status.get("current_lng"),
                "truck_length": status.get("truck_length"),
                "completed_order_count": status.get("completed_order_count"),
                "preferences": status.get("preferences", []),
            },
            "allowed_cargo_ids": [candidate.cargo_id for candidate in candidates],
            "cargo_candidates": cargo_candidates,
            "decision_rules": [
                "take_order只能选择allowed_cargo_ids中的cargo_id",
                "如果候选与司机运行时偏好明显冲突，选择wait",
                "如果没有足够把握，选择wait 30分钟",
            ],
        }
        return json.dumps(decision_context, ensure_ascii=False)
```

- [ ] **Step 4: Remove old `_parse_action` method**

Delete the existing `_parse_action` method from `model_decision_service.py`, because `strategy_helpers.parse_model_action` now handles model-output validation and allowed cargo enforcement.

- [ ] **Step 5: Run helper tests after integration**

Run:

```powershell
cd demo\agent
python -m unittest test_strategy_helpers.py -v
```

Expected: `Ran 8 tests` and `OK`.

### Task 4: Run Smoke Simulation And Score

**Files:**
- Verify: `demo/server/main.py`
- Verify: `demo/calc_monthly_income.py`
- Read: `demo/results/run_summary_202603.json`
- Read: `demo/results/monthly_income_202603.json`

- [ ] **Step 1: Run 5-step smoke simulation**

Run:

```powershell
cd demo\server
python main.py --max-steps 5
```

Expected: exit code `0`, `completed_steps` equals `5`, and no Python traceback.

- [ ] **Step 2: Run scoring and validation**

Run:

```powershell
cd demo
python calc_monthly_income.py
```

Expected: exit code `0`, JSON output contains:

```json
"failed_driver_count": 0
```

- [ ] **Step 3: Inspect smoke output for first-order regression signals**

Open `demo/results/monthly_income_202603.json` and check:

```text
summary.failed_driver_count == 0
summary.total_token_usage.total_tokens <= 36199 or the increase is explained by more accepted useful work
```

Open the newest `demo/results/actions_202603_D001_*.jsonl` and check:

```text
No accepted D001 action has result.income_eligible set to false in the first 5-step smoke run.
```

### Task 5: Record The New Baseline

**Files:**
- Create: `docs/superpowers/baselines/2026-05-09-candidate-filtering-smoke.md`

- [ ] **Step 1: Write updated baseline report from result JSON**

Run this from the repository root after scoring succeeds:

```powershell
$summary = Get-Content -Encoding UTF8 demo\results\run_summary_202603.json | ConvertFrom-Json
$income = Get-Content -Encoding UTF8 demo\results\monthly_income_202603.json | ConvertFrom-Json
$tokens = $income.summary.total_token_usage.total_tokens
$content = @"
# 2026-05-09 Candidate Filtering Smoke

## Commands

- ``cd demo/server && python main.py --max-steps 5``
- ``cd demo && python calc_monthly_income.py``

## Results

- Completed steps: ``$($summary.completed_steps)``
- Simulate time seconds: ``$($summary.simulate_time_seconds)``
- Failed driver count: ``$($income.summary.failed_driver_count)``
- Total net income: ``$($income.summary.total_net_income_all_drivers)``
- Total preference penalty: ``$($income.summary.total_preference_penalty)``
- Total token usage: ``$tokens``

## Comparison To Smoke Baseline

- Previous total net income: ``-8592.13``
- Previous total preference penalty: ``8500.0``
- Previous total token usage: ``36199``
- Previous failed driver count: ``0``

## Notes

- No driver-specific preference hardcoding was added.
- Decision code still uses runtime ``status["preferences"]`` only.
- Decision code does not read ``demo/server/data/cargo_dataset.jsonl`` or ``demo/server/data/drivers.json``.
"@
Set-Content -Encoding UTF8 -Path docs\superpowers\baselines\2026-05-09-candidate-filtering-smoke.md -Value $content
```

Expected: `docs/superpowers/baselines/2026-05-09-candidate-filtering-smoke.md` contains concrete numbers from the latest result JSON.

## Self-Review Checklist

- Spec coverage: implements generic candidate filtering, allowed cargo enforcement, runtime preferences in prompt, and safe fallback.
- Official preference rule: no `driver_id`-specific preference logic is added.
- Data boundary: no decision-code reads of raw cargo or driver data files.
- Test coverage: helper-level filtering and fallback behavior are covered before integration.
- Verification: smoke simulation and scoring must pass before reporting completion.
