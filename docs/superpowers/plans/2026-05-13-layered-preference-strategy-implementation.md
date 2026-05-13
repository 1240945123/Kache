# Layered Preference Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a compliant layered Agent strategy that parses runtime preferences, guards unsafe actions, plans required rest/home/task behavior, scores safe cargo, and records score changes after each evaluation.

**Architecture:** Keep `ModelDecisionService.decide(driver_id)` as the simulator entry point, then route each decision through `PreferenceParser`, `Planner`, `PolicyGuard`, and `Scorer`. The strategy is deterministic-first; model calls are limited to preference parsing fallback and never drive every step.

**Tech Stack:** Python 3.12, stdlib `dataclasses`, `datetime`, `json`, `re`, `unittest`, existing `demo/agent/strategy_helpers.py`, existing `SimulationApiPort`.

---

## Scope Check

This plan implements the full V1 described in `docs/superpowers/specs/2026-05-13-layered-preference-strategy-design.md`. It is a single integrated system because parser, planner, guard, scorer, decision entry point, and experiment reporting are all required for a working preference-aware Agent. Each task is still independently testable and commit-sized.

## File Structure

- Create: `demo/agent/preference_rules.py`
  - Shared dataclasses and constants for parsed preference rules, time windows, coordinate targets, and planned intents.
- Create: `demo/agent/preference_parser.py`
  - Deterministic preference parsing plus optional model fallback adapter hooks.
- Create: `demo/agent/test_preference_parser.py`
  - Unit tests for strength classification and concrete rule extraction.
- Create: `demo/agent/policy_guard.py`
  - Candidate and action guard functions for hard rules.
- Create: `demo/agent/test_policy_guard.py`
  - Unit tests for forbidden categories, windows, distance limits, and unknown strong behavior.
- Create: `demo/agent/planner.py`
  - History-derived planner state and required-action generation.
- Create: `demo/agent/test_planner.py`
  - Unit tests for rest, off-day, visit, and deadline intents.
- Create: `demo/agent/scoring.py`
  - Preference-aware scoring over existing `Candidate` objects.
- Create: `demo/agent/test_scoring.py`
  - Unit tests for soft penalties and task contribution bonuses.
- Modify: `demo/agent/model_decision_service.py`
  - Wire the layered strategy into the simulator entry point.
- Create: `demo/agent/test_decision_service.py`
  - Unit tests with a fake `SimulationApiPort` for end-to-end decision flow.
- Create: `demo/agent/evaluate_results.py`
  - Markdown experiment report generator from local result files.
- Create: `demo/agent/test_evaluate_results.py`
  - Unit tests for summarizing income and action logs.
- Create: `docs/superpowers/experiments/.gitkeep`
  - Ensure the daily experiment tracking directory exists.

## Task 1: Preference Rule Model And Parser Foundation

**Files:**
- Create: `demo/agent/preference_rules.py`
- Create: `demo/agent/preference_parser.py`
- Create: `demo/agent/test_preference_parser.py`

- [ ] **Step 1: Write failing parser model tests**

Create `demo/agent/test_preference_parser.py` with these tests:

```python
from __future__ import annotations

import unittest

from preference_parser import parse_preference_text, parse_preferences
from preference_rules import RuleStrength, RuleType


class PreferenceParserTest(unittest.TestCase):
    def test_classifies_hard_for_must_and_penalty_words(self):
        rule = parse_preference_text("每天23点至次日6点不接单不空驶，违反罚500元。")[0]
        self.assertEqual(rule.strength, RuleStrength.HARD)

    def test_classifies_soft_for_try_best_effort_words(self):
        rule = parse_preference_text("尽量不拉货源品类为「食品饮料」的订单。")[0]
        self.assertEqual(rule.strength, RuleStrength.SOFT)

    def test_extracts_forbidden_category(self):
        rules = parse_preference_text("不接货源品类为「化工塑料」或「煤炭矿产」的订单。")
        categories = sorted(rule.value["category"] for rule in rules)
        self.assertEqual(categories, ["化工塑料", "煤炭矿产"])
        self.assertTrue(all(rule.rule_type == RuleType.CARGO_CATEGORY for rule in rules))

    def test_extracts_no_drive_window_cross_day(self):
        rule = parse_preference_text("每天23点至次日6点不接单、不空车赶路。")[0]
        self.assertEqual(rule.rule_type, RuleType.NO_DRIVE_WINDOW)
        self.assertEqual(rule.value["start_minute"], 23 * 60)
        self.assertEqual(rule.value["end_minute"], 6 * 60)
        self.assertTrue(rule.value["cross_day"])

    def test_extracts_daily_rest_hours(self):
        rule = parse_preference_text("每天至少有一段连着停车休息满5小时。")[0]
        self.assertEqual(rule.rule_type, RuleType.DAILY_REST)
        self.assertEqual(rule.value["minutes"], 300)

    def test_extracts_distance_limits(self):
        rules = parse_preference_text("单笔装卸距离不得超过150公里，赴装货点空驶距离不得超过90公里。")
        by_type = {rule.rule_type: rule.value["km"] for rule in rules}
        self.assertEqual(by_type[RuleType.HAUL_DISTANCE_LIMIT], 150.0)
        self.assertEqual(by_type[RuleType.PICKUP_DISTANCE_LIMIT], 90.0)

    def test_extracts_coordinate_target_and_radius(self):
        rule = parse_preference_text("自然月内至少5个不同的自然日到过（23.13，113.26）一公里内。")[0]
        self.assertEqual(rule.rule_type, RuleType.MONTHLY_VISIT_DAYS)
        self.assertEqual(rule.value["required_days"], 5)
        self.assertAlmostEqual(rule.value["lat"], 23.13)
        self.assertAlmostEqual(rule.value["lng"], 113.26)
        self.assertEqual(rule.value["radius_km"], 1.0)

    def test_extracts_required_cargo_id(self):
        rule = parse_preference_text("【临时约定·熟货】指定熟货源编号240646，不接损失10000元。")[0]
        self.assertEqual(rule.rule_type, RuleType.REQUIRED_CARGO)
        self.assertEqual(rule.value["cargo_id"], "240646")
        self.assertEqual(rule.strength, RuleStrength.HARD)

    def test_parse_preferences_caches_by_text(self):
        parsed = parse_preferences(["每天连续停车休息满3小时。", "每天连续停车休息满3小时。"])
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].value["minutes"], 180)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run parser tests and verify they fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_preference_parser.py -v
```

Expected: `ModuleNotFoundError` for `preference_parser` or `preference_rules`.

- [ ] **Step 3: Add shared preference rule dataclasses**

Create `demo/agent/preference_rules.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuleStrength(str, Enum):
    HARD = "hard"
    SOFT = "soft"
    UNKNOWN_STRONG = "unknown_strong"
    UNKNOWN_SOFT = "unknown_soft"


class RuleType(str, Enum):
    CARGO_CATEGORY = "cargo_category"
    NO_DRIVE_WINDOW = "no_drive_window"
    DAILY_REST = "daily_rest"
    MONTHLY_NO_ORDER_DAYS = "monthly_no_order_days"
    MONTHLY_OFF_DAYS = "monthly_off_days"
    MONTHLY_VISIT_DAYS = "monthly_visit_days"
    PICKUP_DISTANCE_LIMIT = "pickup_distance_limit"
    HAUL_DISTANCE_LIMIT = "haul_distance_limit"
    MONTHLY_DEADHEAD_LIMIT = "monthly_deadhead_limit"
    FORBIDDEN_ZONE = "forbidden_zone"
    BOUNDING_BOX = "bounding_box"
    REQUIRED_CARGO = "required_cargo"
    HOME_DEADLINE = "home_deadline"
    STAY_WINDOW = "stay_window"
    SEQUENCE_TASK = "sequence_task"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PreferenceRule:
    rule_type: RuleType
    strength: RuleStrength
    value: dict[str, Any]
    source_text: str


@dataclass(frozen=True)
class PlannedIntent:
    intent_type: str
    action: str
    params: dict[str, Any]
    reason: str
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
```

- [ ] **Step 4: Add deterministic preference parser**

Create `demo/agent/preference_parser.py`:

```python
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Iterable

from preference_rules import PreferenceRule, RuleStrength, RuleType

_HARD_WORDS = ("必须", "不得", "禁止", "须", "罚", "上不封顶", "临时约定", "不接")
_SOFT_WORDS = ("尽量", "希望", "偏好")
_CATEGORY_PATTERN = re.compile(r"货源品类为「([^」]+)」")
_ANY_QUOTED_PATTERN = re.compile(r"「([^」]+)」")
_NO_DRIVE_PATTERN = re.compile(r"(?P<start>\d{1,2})[点:：](?:\d{1,2}分?)?至(?:次日)?(?P<end>\d{1,2})[点:：].*?(不接单|不空)")
_REST_PATTERN = re.compile(r"每天.*?(连续|连着).*?(停车|熄火|休息|歇).*?(?P<hours>\d+(?:\.\d+)?)\s*小时")
_VISIT_PATTERN = re.compile(r"至少(?P<days>\d+)个不同的自然日到过[（(](?P<lat>\d+(?:\.\d+)?)\s*[，,]\s*(?P<lng>\d+(?:\.\d+)?)[）)].*?(?P<radius>\d+(?:\.\d+)?|一)\s*公里内")
_REQUIRED_CARGO_PATTERN = re.compile(r"货源编号\s*(?P<cargo_id>\d+)")
_HAUL_LIMIT_PATTERN = re.compile(r"装卸距离(?:不得超过|≤|不超过)(?P<km>\d+(?:\.\d+)?)\s*公里")
_PICKUP_LIMIT_PATTERN = re.compile(r"(赴装货点|接单后赴装货点).*?空驶距离(?:不得超过|≤|不超过)(?P<km>\d+(?:\.\d+)?)\s*公里")


def classify_strength(text: str) -> RuleStrength:
    if any(word in text for word in _SOFT_WORDS):
        return RuleStrength.SOFT
    if any(word in text for word in _HARD_WORDS):
        return RuleStrength.HARD
    return RuleStrength.UNKNOWN_SOFT


def _time_to_minute(hour_text: str) -> int:
    hour = int(hour_text)
    return max(0, min(23, hour)) * 60


def _number_text_to_float(text: str) -> float:
    return 1.0 if text == "一" else float(text)


def _append_unknown_if_needed(text: str, rules: list[PreferenceRule]) -> list[PreferenceRule]:
    if rules:
        return rules
    strength = RuleStrength.UNKNOWN_STRONG if any(word in text for word in _HARD_WORDS) else RuleStrength.UNKNOWN_SOFT
    return [PreferenceRule(RuleType.UNKNOWN, strength, {}, text)]


@lru_cache(maxsize=512)
def _parse_preference_text_cached(text: str) -> tuple[PreferenceRule, ...]:
    clean = str(text).strip()
    strength = classify_strength(clean)
    rules: list[PreferenceRule] = []

    if "不接" in clean or "尽量不" in clean:
        categories = _ANY_QUOTED_PATTERN.findall(clean) or _CATEGORY_PATTERN.findall(clean)
        for category in categories:
            rules.append(
                PreferenceRule(
                    RuleType.CARGO_CATEGORY,
                    strength,
                    {"category": category, "mode": "avoid" if strength == RuleStrength.SOFT else "forbid"},
                    clean,
                )
            )

    if match := _NO_DRIVE_PATTERN.search(clean):
        start_minute = _time_to_minute(match.group("start"))
        end_minute = _time_to_minute(match.group("end"))
        rules.append(
            PreferenceRule(
                RuleType.NO_DRIVE_WINDOW,
                RuleStrength.HARD,
                {"start_minute": start_minute, "end_minute": end_minute, "cross_day": end_minute <= start_minute},
                clean,
            )
        )

    if match := _REST_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.DAILY_REST,
                RuleStrength.HARD,
                {"minutes": int(float(match.group("hours")) * 60)},
                clean,
            )
        )

    if match := _PICKUP_LIMIT_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.PICKUP_DISTANCE_LIMIT,
                RuleStrength.HARD,
                {"km": float(match.group("km"))},
                clean,
            )
        )

    if match := _HAUL_LIMIT_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.HAUL_DISTANCE_LIMIT,
                RuleStrength.HARD,
                {"km": float(match.group("km"))},
                clean,
            )
        )

    if match := _VISIT_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.MONTHLY_VISIT_DAYS,
                RuleStrength.HARD,
                {
                    "required_days": int(match.group("days")),
                    "lat": float(match.group("lat")),
                    "lng": float(match.group("lng")),
                    "radius_km": _number_text_to_float(match.group("radius")),
                },
                clean,
            )
        )

    if match := _REQUIRED_CARGO_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.REQUIRED_CARGO,
                RuleStrength.HARD,
                {"cargo_id": match.group("cargo_id")},
                clean,
            )
        )

    return tuple(_append_unknown_if_needed(clean, rules))


def parse_preference_text(text: str) -> list[PreferenceRule]:
    return list(_parse_preference_text_cached(str(text)))


def parse_preferences(preferences: Iterable[Any]) -> list[PreferenceRule]:
    seen_text: set[str] = set()
    rules: list[PreferenceRule] = []
    for preference in preferences:
        text = preference.get("content") if isinstance(preference, dict) else preference
        text = str(text).strip()
        if not text or text in seen_text:
            continue
        seen_text.add(text)
        rules.extend(parse_preference_text(text))
    return rules
```

- [ ] **Step 5: Run parser tests and commit**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_preference_parser.py -v
```

Expected: all tests pass.

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/preference_rules.py demo/agent/preference_parser.py demo/agent/test_preference_parser.py
git commit -m "feat: add runtime preference parser"
```

## Task 2: Complete V1 Parser Coverage And Model Fallback

**Files:**
- Modify: `demo/agent/preference_rules.py`
- Modify: `demo/agent/preference_parser.py`
- Modify: `demo/agent/test_preference_parser.py`

- [ ] **Step 1: Add failing V1 coverage tests**

Append these tests to `PreferenceParserTest` in `demo/agent/test_preference_parser.py`:

```python
    def test_extracts_monthly_off_days(self):
        rule = parse_preference_text("自然月内至少要有2个整天既不接单也不空车乱跑。")[0]
        self.assertEqual(rule.rule_type, RuleType.MONTHLY_OFF_DAYS)
        self.assertEqual(rule.value["required_days"], 2)

    def test_extracts_forbidden_zone(self):
        rule = parse_preference_text("车辆不得进入以（23.30，113.52）为圆心、半径20公里的区域。")[0]
        self.assertEqual(rule.rule_type, RuleType.FORBIDDEN_ZONE)
        self.assertAlmostEqual(rule.value["lat"], 23.30)
        self.assertAlmostEqual(rule.value["lng"], 113.52)
        self.assertEqual(rule.value["radius_km"], 20.0)

    def test_extracts_home_deadline(self):
        rule = parse_preference_text("每天23点前车辆须在自家位置（23.12，113.28）一公里内。")[0]
        self.assertEqual(rule.rule_type, RuleType.HOME_DEADLINE)
        self.assertEqual(rule.value["deadline_minute"], 23 * 60)
        self.assertAlmostEqual(rule.value["lat"], 23.12)
        self.assertAlmostEqual(rule.value["lng"], 113.28)
        self.assertEqual(rule.value["radius_km"], 1.0)

    def test_extracts_sequence_task(self):
        text = (
            "须先到（23.21，113.37）接上配偶（原地停留不少于10分钟），"
            "再返回老家（23.19，113.36）；须在2026年3月10日22:00前进家门，"
            "到家后须在原处静止，至少待到2026年3月13日22:00。"
        )
        rule = parse_preference_text(text)[0]
        self.assertEqual(rule.rule_type, RuleType.SEQUENCE_TASK)
        self.assertEqual(rule.value["steps"][0]["wait_minutes"], 10)
        self.assertEqual(rule.value["deadline"], "2026-03-10 22:00:00")
        self.assertEqual(rule.value["stay_until"], "2026-03-13 22:00:00")

    def test_model_fallback_converts_unknown_strong_rule(self):
        def fake_model_parser(text):
            return [
                {
                    "rule_type": "stay_window",
                    "strength": "hard",
                    "value": {"lat": 23.19, "lng": 113.36, "until": "2026-03-13 22:00:00"},
                    "source_text": text,
                }
            ]

        from preference_parser import parse_preferences_with_fallback

        rules = parse_preferences_with_fallback(["必须按短信通知留在家中。"], model_parse_fn=fake_model_parser, max_model_calls=1)
        self.assertEqual(rules[0].rule_type, RuleType.STAY_WINDOW)
        self.assertEqual(rules[0].strength, RuleStrength.HARD)
```

- [ ] **Step 2: Run parser tests and verify V1 tests fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_preference_parser.py -v
```

Expected: failures for `MONTHLY_OFF_DAYS`, `FORBIDDEN_ZONE`, `HOME_DEADLINE`, `SEQUENCE_TASK`, or missing `parse_preferences_with_fallback`.

- [ ] **Step 3: Add V1 deterministic parser patterns**

Modify `demo/agent/preference_parser.py` by adding these patterns near the existing regex constants:

```python
_MONTHLY_OFF_PATTERN = re.compile(r"自然月内至少(?:要有)?(?P<days>\d+)个?整天.*?(不接单|完全歇|不空车|不外跑)")
_FORBIDDEN_ZONE_PATTERN = re.compile(r"不得进入以[（(](?P<lat>\d+(?:\.\d+)?)\s*[，,]\s*(?P<lng>\d+(?:\.\d+)?)[）)]为圆心、?半径(?P<radius>\d+(?:\.\d+)?)\s*公里")
_HOME_DEADLINE_PATTERN = re.compile(r"(?P<hour>\d{1,2})点前.*?(自家位置|家|老家)[（(](?P<lat>\d+(?:\.\d+)?)\s*[，,]\s*(?P<lng>\d+(?:\.\d+)?)[）)].*?(?P<radius>\d+(?:\.\d+)?|一)\s*公里内")
_CHINESE_DATE_TIME_PATTERN = re.compile(r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日(?P<hour>\d{1,2}):(?P<minute>\d{2})")
_COORD_PATTERN = re.compile(r"[（(](?P<lat>\d+(?:\.\d+)?)\s*[，,]\s*(?P<lng>\d+(?:\.\d+)?)[）)]")
_STOP_MINUTES_PATTERN = re.compile(r"停留不少于(?P<minutes>\d+)分钟")
```

Add this datetime helper below `_number_text_to_float`:

```python
def _normalize_chinese_datetime(match: re.Match[str]) -> str:
    return (
        f"{int(match.group('year')):04d}-"
        f"{int(match.group('month')):02d}-"
        f"{int(match.group('day')):02d} "
        f"{int(match.group('hour')):02d}:{int(match.group('minute')):02d}:00"
    )
```

Add these parsing blocks inside `_parse_preference_text_cached` before the final unknown fallback:

```python
    if match := _MONTHLY_OFF_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.MONTHLY_OFF_DAYS,
                RuleStrength.HARD,
                {"required_days": int(match.group("days"))},
                clean,
            )
        )

    if match := _FORBIDDEN_ZONE_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.FORBIDDEN_ZONE,
                RuleStrength.HARD,
                {"lat": float(match.group("lat")), "lng": float(match.group("lng")), "radius_km": _number_text_to_float(match.group("radius"))},
                clean,
            )
        )

    if match := _HOME_DEADLINE_PATTERN.search(clean):
        rules.append(
            PreferenceRule(
                RuleType.HOME_DEADLINE,
                RuleStrength.HARD,
                {
                    "deadline_minute": _time_to_minute(match.group("hour")),
                    "lat": float(match.group("lat")),
                    "lng": float(match.group("lng")),
                    "radius_km": _number_text_to_float(match.group("radius")),
                },
                clean,
            )
        )

    if "须先到" in clean and "再返回" in clean:
        coords = list(_COORD_PATTERN.finditer(clean))
        dates = list(_CHINESE_DATE_TIME_PATTERN.finditer(clean))
        stop_match = _STOP_MINUTES_PATTERN.search(clean)
        if len(coords) >= 2 and len(dates) >= 2:
            rules.append(
                PreferenceRule(
                    RuleType.SEQUENCE_TASK,
                    RuleStrength.HARD,
                    {
                        "steps": [
                            {
                                "lat": float(coords[0].group("lat")),
                                "lng": float(coords[0].group("lng")),
                                "wait_minutes": int(stop_match.group("minutes")) if stop_match else 0,
                            },
                            {"lat": float(coords[1].group("lat")), "lng": float(coords[1].group("lng")), "wait_minutes": 0},
                        ],
                        "deadline": _normalize_chinese_datetime(dates[0]),
                        "stay_until": _normalize_chinese_datetime(dates[-1]),
                    },
                    clean,
                )
            )
```

- [ ] **Step 4: Add model fallback conversion**

Append this function to `demo/agent/preference_parser.py`:

```python
def _rule_from_model_payload(payload: dict[str, Any], source_text: str) -> PreferenceRule | None:
    try:
        rule_type = RuleType(str(payload["rule_type"]))
        strength = RuleStrength(str(payload.get("strength", "hard")))
        value = payload.get("value", {})
        if not isinstance(value, dict):
            return None
    except (KeyError, ValueError, TypeError):
        return None
    return PreferenceRule(rule_type, strength, value, str(payload.get("source_text") or source_text))


def parse_preferences_with_fallback(
    preferences: Iterable[Any],
    *,
    model_parse_fn: Any | None = None,
    max_model_calls: int = 2,
) -> list[PreferenceRule]:
    parsed = parse_preferences(preferences)
    if model_parse_fn is None or max_model_calls <= 0:
        return parsed
    output: list[PreferenceRule] = []
    calls = 0
    for rule in parsed:
        if rule.rule_type != RuleType.UNKNOWN or rule.strength != RuleStrength.UNKNOWN_STRONG or calls >= max_model_calls:
            output.append(rule)
            continue
        calls += 1
        try:
            payloads = model_parse_fn(rule.source_text)
        except Exception:
            output.append(rule)
            continue
        converted = [
            converted_rule
            for payload in payloads
            if isinstance(payload, dict)
            if (converted_rule := _rule_from_model_payload(payload, rule.source_text)) is not None
        ]
        output.extend(converted or [rule])
    return output
```

- [ ] **Step 5: Run parser tests and commit V1 coverage**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_preference_parser.py -v
```

Expected: all tests pass.

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/preference_rules.py demo/agent/preference_parser.py demo/agent/test_preference_parser.py
git commit -m "feat: expand preference parser v1 coverage"
```

## Task 3: Guard Layer For Hard Preference Rules

**Files:**
- Create: `demo/agent/policy_guard.py`
- Create: `demo/agent/test_policy_guard.py`

- [ ] **Step 1: Write failing guard tests**

Create `demo/agent/test_policy_guard.py`:

```python
from __future__ import annotations

import unittest

from policy_guard import filter_candidates, should_wait_for_window
from preference_rules import PreferenceRule, RuleStrength, RuleType
from strategy_helpers import Candidate


def _candidate(**overrides):
    base = {
        "cargo_id": "C1",
        "price": 500.0,
        "pickup_distance_km": 20.0,
        "pickup_minutes": 20,
        "wait_minutes": 0,
        "cost_time_minutes": 120,
        "estimated_finish_minute": 600,
        "haul_distance_km": 80.0,
        "rough_net_value": 350.0,
        "value_per_minute": 2.5,
        "start": {"lat": 22.55, "lng": 114.07},
        "end": {"lat": 22.8, "lng": 114.2},
        "load_time": None,
    }
    base.update(overrides)
    return Candidate(**base)


class PolicyGuardTest(unittest.TestCase):
    def test_forbidden_category_removes_candidate(self):
        candidate = _candidate()
        cargo_by_id = {"C1": {"category": "煤炭矿产"}}
        rules = [PreferenceRule(RuleType.CARGO_CATEGORY, RuleStrength.HARD, {"category": "煤炭矿产"}, "不接煤炭矿产")]
        self.assertEqual(filter_candidates([candidate], rules, cargo_by_id=cargo_by_id), [])

    def test_pickup_distance_limit_removes_candidate(self):
        candidate = _candidate(pickup_distance_km=95.0)
        rules = [PreferenceRule(RuleType.PICKUP_DISTANCE_LIMIT, RuleStrength.HARD, {"km": 90.0}, "空驶≤90")]
        self.assertEqual(filter_candidates([candidate], rules, cargo_by_id={}), [])

    def test_haul_distance_limit_removes_candidate(self):
        candidate = _candidate(haul_distance_km=181.0)
        rules = [PreferenceRule(RuleType.HAUL_DISTANCE_LIMIT, RuleStrength.HARD, {"km": 180.0}, "装卸≤180")]
        self.assertEqual(filter_candidates([candidate], rules, cargo_by_id={}), [])

    def test_no_drive_window_requests_wait(self):
        rule = PreferenceRule(
            RuleType.NO_DRIVE_WINDOW,
            RuleStrength.HARD,
            {"start_minute": 23 * 60, "end_minute": 6 * 60, "cross_day": True},
            "23-6不接单不空驶",
        )
        wait = should_wait_for_window(current_minute=23 * 60 + 5, rules=[rule])
        self.assertEqual(wait, {"action": "wait", "params": {"duration_minutes": 355}})

    def test_unknown_strong_blocks_candidates(self):
        candidate = _candidate()
        rule = PreferenceRule(RuleType.UNKNOWN, RuleStrength.UNKNOWN_STRONG, {}, "必须满足未知约束")
        self.assertEqual(filter_candidates([candidate], [rule], cargo_by_id={}), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run guard tests and verify they fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_policy_guard.py -v
```

Expected: `ModuleNotFoundError` for `policy_guard`.

- [ ] **Step 3: Implement hard guard functions**

Create `demo/agent/policy_guard.py`:

```python
from __future__ import annotations

from typing import Any

from preference_rules import PreferenceRule, RuleStrength, RuleType
from strategy_helpers import Candidate

DEFAULT_UNKNOWN_STRONG_WAIT_MINUTES = 30


def _minute_of_day(current_minute: int) -> int:
    return int(current_minute) % (24 * 60)


def _minutes_until_window_end(minute_of_day: int, start: int, end: int, cross_day: bool) -> int | None:
    if cross_day:
        if minute_of_day >= start:
            return (24 * 60 - minute_of_day) + end
        if minute_of_day < end:
            return end - minute_of_day
        return None
    if start <= minute_of_day < end:
        return end - minute_of_day
    return None


def should_wait_for_window(current_minute: int, rules: list[PreferenceRule]) -> dict[str, Any] | None:
    now = _minute_of_day(current_minute)
    waits: list[int] = []
    for rule in rules:
        if rule.rule_type != RuleType.NO_DRIVE_WINDOW or rule.strength != RuleStrength.HARD:
            continue
        minutes = _minutes_until_window_end(
            now,
            int(rule.value["start_minute"]),
            int(rule.value["end_minute"]),
            bool(rule.value.get("cross_day")),
        )
        if minutes is not None:
            waits.append(max(1, minutes))
    if not waits:
        return None
    return {"action": "wait", "params": {"duration_minutes": min(waits)}}


def _candidate_category(candidate: Candidate, cargo_by_id: dict[str, dict[str, Any]]) -> str:
    cargo = cargo_by_id.get(candidate.cargo_id, {})
    return str(cargo.get("category") or cargo.get("cargo_type") or cargo.get("goods_type") or "")


def is_candidate_allowed(candidate: Candidate, rules: list[PreferenceRule], *, cargo_by_id: dict[str, dict[str, Any]]) -> bool:
    for rule in rules:
        if rule.strength == RuleStrength.UNKNOWN_STRONG:
            return False
        if rule.rule_type == RuleType.CARGO_CATEGORY and rule.strength == RuleStrength.HARD:
            if _candidate_category(candidate, cargo_by_id) == str(rule.value.get("category", "")):
                return False
        if rule.rule_type == RuleType.PICKUP_DISTANCE_LIMIT:
            if candidate.pickup_distance_km > float(rule.value["km"]):
                return False
        if rule.rule_type == RuleType.HAUL_DISTANCE_LIMIT:
            if candidate.haul_distance_km > float(rule.value["km"]):
                return False
    return True


def filter_candidates(
    candidates: list[Candidate],
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
) -> list[Candidate]:
    return [candidate for candidate in candidates if is_candidate_allowed(candidate, rules, cargo_by_id=cargo_by_id)]
```

- [ ] **Step 4: Run guard tests and commit**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_policy_guard.py -v
```

Expected: all tests pass.

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/policy_guard.py demo/agent/test_policy_guard.py
git commit -m "feat: add hard preference guard"
```

## Task 4: Planner State And Required Intents

**Files:**
- Create: `demo/agent/planner.py`
- Create: `demo/agent/test_planner.py`

- [ ] **Step 1: Write failing planner tests**

Create `demo/agent/test_planner.py`:

```python
from __future__ import annotations

import unittest

from planner import build_planner_state, choose_required_intent
from preference_rules import PreferenceRule, RuleStrength, RuleType


class PlannerTest(unittest.TestCase):
    def test_counts_today_continuous_wait_minutes(self):
        history = {
            "records": [
                {"action": {"action": "wait", "params": {"duration_minutes": 120}}, "step_elapsed_minutes": 120, "simulation_end_time": "2026-03-01 02:00"},
                {"action": {"action": "wait", "params": {"duration_minutes": 180}}, "step_elapsed_minutes": 180, "simulation_end_time": "2026-03-01 05:00"},
            ]
        }
        state = build_planner_state({"simulation_progress_minutes": 300}, history)
        self.assertEqual(state.current_day, 1)
        self.assertEqual(state.recent_continuous_wait_minutes, 300)

    def test_daily_rest_intent_waits_when_rest_short(self):
        rule = PreferenceRule(RuleType.DAILY_REST, RuleStrength.HARD, {"minutes": 300}, "每天休5小时")
        state = build_planner_state({"simulation_progress_minutes": 21 * 60}, {"records": []})
        intent = choose_required_intent(state, [rule])
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.action, "wait")
        self.assertGreaterEqual(intent.params["duration_minutes"], 180)

    def test_required_visit_intent_repositions_to_target(self):
        rule = PreferenceRule(
            RuleType.MONTHLY_VISIT_DAYS,
            RuleStrength.HARD,
            {"required_days": 5, "lat": 23.13, "lng": 113.26, "radius_km": 1.0},
            "到访5天",
        )
        status = {"simulation_progress_minutes": 60, "current_lat": 22.5, "current_lng": 114.0}
        state = build_planner_state(status, {"records": []})
        intent = choose_required_intent(state, [rule])
        self.assertIsNotNone(intent)
        assert intent is not None
        self.assertEqual(intent.action, "reposition")
        self.assertEqual(intent.params, {"latitude": 23.13, "longitude": 113.26})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run planner tests and verify they fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_planner.py -v
```

Expected: `ModuleNotFoundError` for `planner`.

- [ ] **Step 3: Implement planner state and intents**

Create `demo/agent/planner.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from preference_rules import PlannedIntent, PreferenceRule, RuleStrength, RuleType

MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class PlannerState:
    current_minute: int
    current_day: int
    minute_of_day: int
    current_lat: float
    current_lng: float
    recent_continuous_wait_minutes: int
    completed_order_count: int


def _action_name(record: dict[str, Any]) -> str:
    action = record.get("action", {})
    return str(action.get("action", "")).lower() if isinstance(action, dict) else ""


def _wait_duration(record: dict[str, Any]) -> int:
    action = record.get("action", {})
    params = action.get("params", {}) if isinstance(action, dict) else {}
    if isinstance(params, dict) and "duration_minutes" in params:
        return int(params["duration_minutes"])
    return int(record.get("step_elapsed_minutes", 0) or 0)


def _recent_continuous_wait(records: list[dict[str, Any]]) -> int:
    total = 0
    for record in reversed(records):
        if _action_name(record) != "wait":
            break
        total += max(0, _wait_duration(record))
    return total


def build_planner_state(status: dict[str, Any], history: dict[str, Any]) -> PlannerState:
    current_minute = int(status.get("simulation_progress_minutes", 0))
    records = history.get("records", []) if isinstance(history, dict) else []
    if not isinstance(records, list):
        records = []
    return PlannerState(
        current_minute=current_minute,
        current_day=current_minute // MINUTES_PER_DAY + 1,
        minute_of_day=current_minute % MINUTES_PER_DAY,
        current_lat=float(status.get("current_lat", 0.0)),
        current_lng=float(status.get("current_lng", 0.0)),
        recent_continuous_wait_minutes=_recent_continuous_wait(records),
        completed_order_count=int(status.get("completed_order_count", 0) or 0),
    )


def choose_required_intent(state: PlannerState, rules: list[PreferenceRule]) -> PlannedIntent | None:
    for rule in rules:
        if rule.rule_type == RuleType.MONTHLY_VISIT_DAYS and rule.strength == RuleStrength.HARD:
            if state.current_day <= int(rule.value["required_days"]):
                return PlannedIntent(
                    intent_type="visit_target",
                    action="reposition",
                    params={"latitude": float(rule.value["lat"]), "longitude": float(rule.value["lng"])},
                    reason=rule.source_text,
                    priority=80,
                )
    for rule in rules:
        if rule.rule_type == RuleType.DAILY_REST and rule.strength == RuleStrength.HARD:
            required = int(rule.value["minutes"])
            remaining_day = MINUTES_PER_DAY - state.minute_of_day
            if state.recent_continuous_wait_minutes < required and remaining_day <= required:
                need = required - state.recent_continuous_wait_minutes
                return PlannedIntent(
                    intent_type="daily_rest",
                    action="wait",
                    params={"duration_minutes": max(1, need)},
                    reason=rule.source_text,
                    priority=70,
                )
    return None
```

- [ ] **Step 4: Run planner tests and commit**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_planner.py -v
```

Expected: all tests pass.

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/planner.py demo/agent/test_planner.py
git commit -m "feat: add preference planner intents"
```

## Task 5: Preference-Aware Scoring

**Files:**
- Create: `demo/agent/scoring.py`
- Create: `demo/agent/test_scoring.py`

- [ ] **Step 1: Write failing scorer tests**

Create `demo/agent/test_scoring.py`:

```python
from __future__ import annotations

import unittest

from preference_rules import PreferenceRule, RuleStrength, RuleType
from scoring import score_candidates
from strategy_helpers import Candidate


def _candidate(cargo_id: str, rough_net: float, end_lat: float = 22.8, end_lng: float = 114.2):
    return Candidate(
        cargo_id=cargo_id,
        price=rough_net + 100.0,
        pickup_distance_km=10.0,
        pickup_minutes=10,
        wait_minutes=0,
        cost_time_minutes=100,
        estimated_finish_minute=500,
        haul_distance_km=50.0,
        rough_net_value=rough_net,
        value_per_minute=rough_net / 100.0,
        start={"lat": 22.5, "lng": 114.0},
        end={"lat": end_lat, "lng": end_lng},
        load_time=None,
    )


class ScoringTest(unittest.TestCase):
    def test_ranks_by_rough_net_when_no_preferences(self):
        ranked = score_candidates([_candidate("LOW", 100.0), _candidate("HIGH", 300.0)], [], cargo_by_id={})
        self.assertEqual([item.candidate.cargo_id for item in ranked], ["HIGH", "LOW"])

    def test_soft_category_penalty_can_lower_candidate(self):
        rules = [PreferenceRule(RuleType.CARGO_CATEGORY, RuleStrength.SOFT, {"category": "食品饮料"}, "尽量不拉食品饮料")]
        cargo_by_id = {"A": {"category": "食品饮料"}, "B": {"category": "普通货物"}}
        ranked = score_candidates([_candidate("A", 300.0), _candidate("B", 260.0)], rules, cargo_by_id=cargo_by_id)
        self.assertEqual(ranked[0].candidate.cargo_id, "B")
        self.assertGreater(ranked[0].score, ranked[1].score)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run scorer tests and verify they fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_scoring.py -v
```

Expected: `ModuleNotFoundError` for `scoring`.

- [ ] **Step 3: Implement scoring**

Create `demo/agent/scoring.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from preference_rules import PreferenceRule, RuleStrength, RuleType
from strategy_helpers import Candidate

SOFT_CATEGORY_PENALTY = 80.0


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: Candidate
    score: float
    reasons: list[str]


def _cargo_category(candidate: Candidate, cargo_by_id: dict[str, dict[str, Any]]) -> str:
    cargo = cargo_by_id.get(candidate.cargo_id, {})
    return str(cargo.get("category") or cargo.get("cargo_type") or cargo.get("goods_type") or "")


def score_candidate(candidate: Candidate, rules: list[PreferenceRule], *, cargo_by_id: dict[str, dict[str, Any]]) -> ScoredCandidate:
    score = candidate.rough_net_value + candidate.value_per_minute * 10.0 - candidate.pickup_distance_km * 0.2
    reasons = ["rough_net", "value_per_minute", "pickup_distance"]
    category = _cargo_category(candidate, cargo_by_id)
    for rule in rules:
        if rule.rule_type == RuleType.CARGO_CATEGORY and rule.strength == RuleStrength.SOFT:
            if category == str(rule.value.get("category", "")):
                score -= SOFT_CATEGORY_PENALTY
                reasons.append("soft_category_penalty")
    return ScoredCandidate(candidate=candidate, score=score, reasons=reasons)


def score_candidates(
    candidates: list[Candidate],
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
) -> list[ScoredCandidate]:
    scored = [score_candidate(candidate, rules, cargo_by_id=cargo_by_id) for candidate in candidates]
    scored.sort(key=lambda item: (-item.score, item.candidate.estimated_finish_minute, item.candidate.pickup_distance_km))
    return scored
```

- [ ] **Step 4: Run scorer tests and commit**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_scoring.py -v
```

Expected: all tests pass.

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/scoring.py demo/agent/test_scoring.py
git commit -m "feat: add preference-aware candidate scoring"
```

## Task 6: Wire Layered Strategy Into Decision Service

**Files:**
- Modify: `demo/agent/model_decision_service.py`
- Create: `demo/agent/test_decision_service.py`

- [ ] **Step 1: Write failing decision service tests**

Create `demo/agent/test_decision_service.py`:

```python
from __future__ import annotations

import unittest

from model_decision_service import ModelDecisionService


class FakeApi:
    def __init__(self, *, status, cargo_items=None, history=None):
        self.status = status
        self.cargo_items = cargo_items or []
        self.history = history or {"records": []}
        self.query_count = 0

    def get_driver_status(self, driver_id):
        return dict(self.status, driver_id=driver_id)

    def query_cargo(self, driver_id, latitude, longitude):
        self.query_count += 1
        return {"driver_id": driver_id, "items": self.cargo_items}

    def query_decision_history(self, driver_id, step):
        return self.history

    def model_chat_completion(self, payload):
        raise AssertionError("model should not drive every step")


def _status(**overrides):
    base = {
        "current_lat": 22.54,
        "current_lng": 114.06,
        "truck_length": "4.2米",
        "completed_order_count": 0,
        "simulation_progress_minutes": 23 * 60 + 10,
        "preferences": ["每天23点至次日6点不接单、不空车赶路。"],
    }
    base.update(overrides)
    return base


def _cargo(cargo_id="C1", category="普通货物"):
    return {
        "distance_km": 1.0,
        "cargo": {
            "cargo_id": cargo_id,
            "category": category,
            "remove_time": "2026-03-01 23:59:59",
            "price": 500.0,
            "cost_time_minutes": 100,
            "load_time": None,
            "truck_length": ["4.2米"],
            "start": {"lat": 22.55, "lng": 114.07},
            "end": {"lat": 22.6, "lng": 114.08},
        },
    }


class DecisionServiceTest(unittest.TestCase):
    def test_waits_without_querying_cargo_during_no_drive_window(self):
        api = FakeApi(status=_status())
        action = ModelDecisionService(api).decide("DXXX")
        self.assertEqual(action["action"], "wait")
        self.assertEqual(api.query_count, 0)

    def test_takes_safe_candidate_outside_window(self):
        api = FakeApi(status=_status(simulation_progress_minutes=8 * 60, preferences=[]), cargo_items=[_cargo()])
        action = ModelDecisionService(api).decide("DXXX")
        self.assertEqual(action, {"action": "take_order", "params": {"cargo_id": "C1"}})

    def test_forbidden_category_is_not_taken(self):
        api = FakeApi(
            status=_status(simulation_progress_minutes=8 * 60, preferences=["不接货源品类为「煤炭矿产」的订单。"]),
            cargo_items=[_cargo(category="煤炭矿产")],
        )
        action = ModelDecisionService(api).decide("DXXX")
        self.assertEqual(action["action"], "wait")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run decision service tests and verify they fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_decision_service.py -v
```

Expected: at least one failure because the current decision service always queries cargo and calls the model.

- [ ] **Step 3: Replace single-step model flow with layered deterministic flow**

Modify `demo/agent/model_decision_service.py` so imports and `decide` follow this shape:

```python
from __future__ import annotations

import json
import logging
from typing import Any

from planner import build_planner_state, choose_required_intent
from policy_guard import filter_candidates, should_wait_for_window
from preference_parser import parse_preferences_with_fallback
from scoring import score_candidates
from simkit.ports import SimulationApiPort
from strategy_helpers import fallback_wait_action, filter_and_rank_candidates


class ModelDecisionService:
    def __init__(self, api: SimulationApiPort) -> None:
        self._api = api
        self._logger = logging.getLogger("agent.decision_service")

    def decide(self, driver_id: str) -> dict[str, Any]:
        status = self._api.get_driver_status(driver_id)
        rules = parse_preferences_with_fallback(
            status.get("preferences", []),
            model_parse_fn=self._model_parse_preference,
            max_model_calls=1,
        )
        history = self._safe_history(driver_id)
        state = build_planner_state(status, history)

        window_wait = should_wait_for_window(state.current_minute, rules)
        if window_wait is not None:
            self._logger.info("decision required_wait driver_id=%s action=%s", driver_id, window_wait)
            return window_wait

        intent = choose_required_intent(state, rules)
        if intent is not None:
            action = {"action": intent.action, "params": intent.params}
            self._logger.info("decision planner_intent driver_id=%s intent=%s action=%s", driver_id, intent.intent_type, action)
            return action

        lat = float(status["current_lat"])
        lng = float(status["current_lng"])
        cargo_resp = self._api.query_cargo(driver_id=driver_id, latitude=lat, longitude=lng)
        items = cargo_resp.get("items", [])
        if not isinstance(items, list):
            return fallback_wait_action()

        candidates = filter_and_rank_candidates(items, status)
        cargo_by_id = {
            str(item.get("cargo", {}).get("cargo_id")): item.get("cargo", {})
            for item in items
            if isinstance(item, dict) and isinstance(item.get("cargo"), dict)
        }
        guarded = filter_candidates(candidates, rules, cargo_by_id=cargo_by_id)
        scored = score_candidates(guarded, rules, cargo_by_id=cargo_by_id)
        if scored:
            chosen = scored[0].candidate
            action = {"action": "take_order", "params": {"cargo_id": chosen.cargo_id}}
            self._logger.info("decision scored_take_order driver_id=%s cargo_id=%s score=%s", driver_id, chosen.cargo_id, scored[0].score)
            return action
        return fallback_wait_action()

    def _safe_history(self, driver_id: str) -> dict[str, Any]:
        try:
            history = self._api.query_decision_history(driver_id, -1)
        except Exception as exc:
            self._logger.warning("query_decision_history failed driver_id=%s error=%s", driver_id, exc)
            return {"records": []}
        return history if isinstance(history, dict) else {"records": []}

    def _model_parse_preference(self, text: str) -> list[dict[str, Any]]:
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "把货运司机偏好文本转成JSON。只输出JSON对象，格式为"
                        "{\"rules\":[{\"rule_type\":\"stay_window\",\"strength\":\"hard\",\"value\":{},\"source_text\":\"...\"}]}。"
                        "rule_type只能使用preference_rules.RuleType中的字符串值。"
                    ),
                },
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
        }
        response = self._api.model_chat_completion(payload)
        choices = response.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        parsed = json.loads(content)
        rules = parsed.get("rules", [])
        return rules if isinstance(rules, list) else []
```

Remove the old `_build_prompt` and `_parse_action` methods after the tests no longer reference them.

- [ ] **Step 4: Run decision service tests and all agent unit tests**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest discover -s . -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit decision service wiring**

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/model_decision_service.py demo/agent/test_decision_service.py
git commit -m "feat: wire layered deterministic decision flow"
```

## Task 7: Experiment Report Generator

**Files:**
- Create: `demo/agent/evaluate_results.py`
- Create: `demo/agent/test_evaluate_results.py`
- Create: `docs/superpowers/experiments/.gitkeep`

- [ ] **Step 1: Write failing report tests**

Create `demo/agent/test_evaluate_results.py`:

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evaluate_results import build_report


class EvaluateResultsTest(unittest.TestCase):
    def test_build_report_contains_summary_and_driver_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            results.mkdir()
            (results / "monthly_income_202603.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "total_net_income_all_drivers": 100.0,
                            "total_preference_penalty": 20.0,
                            "failed_driver_count": 0,
                            "total_token_usage": {"total_tokens": 5},
                        },
                        "drivers": [
                            {
                                "driver_id": "D001",
                                "income": {"gross_income": 200.0, "cost": 50.0, "preference_penalty": 20.0, "net_income": 130.0},
                                "calculation_aborted": False,
                                "preference_check": {"rules": [{"rule": "每日休息", "penalty": 20.0}]},
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (results / "run_summary_202603.json").write_text(
                json.dumps({"simulate_time_seconds": 3.5, "simulation_duration_days": 30, "simulation_max_steps": 20000}),
                encoding="utf-8",
            )
            (results / "actions_202603_D001_sample.jsonl").write_text(
                json.dumps({"action": {"action": "take_order"}, "result": {"accepted": True}}, ensure_ascii=False) + "\n"
                + json.dumps({"action": {"action": "wait"}, "result": {}}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            report = build_report(results, experiment_id="unit-test")
        self.assertIn("# Experiment unit-test", report)
        self.assertIn("total_net_income_all_drivers", report)
        self.assertIn("| D001 |", report)
        self.assertIn("take_order=1", report)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run report tests and verify they fail**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_evaluate_results.py -v
```

Expected: `ModuleNotFoundError` for `evaluate_results`.

- [ ] **Step 3: Implement Markdown report generator**

Create `demo/agent/evaluate_results.py`:

```python
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _action_counts(results_dir: Path, driver_id: str) -> Counter[str]:
    files = sorted(results_dir.glob(f"actions_202603_{driver_id}_*.jsonl"))
    counts: Counter[str] = Counter()
    if not files:
        return counts
    for line in files[-1].read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        action = record.get("action", {}).get("action", "")
        counts[str(action)] += 1
        if action == "take_order" and record.get("result", {}).get("accepted") is False:
            counts["accepted_false"] += 1
    return counts


def build_report(results_dir: Path, *, experiment_id: str) -> str:
    income = _read_json(results_dir / "monthly_income_202603.json")
    run_summary_path = results_dir / "run_summary_202603.json"
    run_summary = _read_json(run_summary_path) if run_summary_path.is_file() else {}
    summary = income.get("summary", {})
    lines = [
        f"# Experiment {experiment_id}",
        "",
        "## Summary",
        "",
        f"- total_net_income_all_drivers: `{summary.get('total_net_income_all_drivers')}`",
        f"- total_preference_penalty: `{summary.get('total_preference_penalty')}`",
        f"- failed_driver_count: `{summary.get('failed_driver_count')}`",
        f"- total_token_usage: `{summary.get('total_token_usage', {}).get('total_tokens', 0)}`",
        f"- simulate_time_seconds: `{run_summary.get('simulate_time_seconds')}`",
        f"- simulation_duration_days: `{run_summary.get('simulation_duration_days')}`",
        "",
        "## Drivers",
        "",
        "| Driver | Net | Gross | Cost | Penalty | Failed | Actions |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for driver in income.get("drivers", []):
        driver_id = str(driver.get("driver_id"))
        inc = driver.get("income", {})
        counts = _action_counts(results_dir, driver_id)
        actions = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
        lines.append(
            f"| {driver_id} | {inc.get('net_income')} | {inc.get('gross_income')} | {inc.get('cost')} | "
            f"{inc.get('preference_penalty')} | {driver.get('calculation_aborted')} | {actions} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Improved:",
            "- Regressed:",
            "- Next tuning:",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="../results")
    parser.add_argument("--out-dir", default="../../docs/superpowers/experiments")
    parser.add_argument("--experiment-id", default=datetime.now().strftime("%Y-%m-%d-%H%M%S-local"))
    args = parser.parse_args()
    results_dir = Path(args.results_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(results_dir, experiment_id=args.experiment_id)
    out_path = out_dir / f"{args.experiment_id}.md"
    out_path.write_text(report, encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
```

Create directory marker:

```powershell
cd E:\school\KACHE
New-Item -ItemType Directory -Force -Path docs\superpowers\experiments
New-Item -ItemType File -Force -Path docs\superpowers\experiments\.gitkeep
```

- [ ] **Step 4: Run report tests and commit**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest test_evaluate_results.py -v
```

Expected: all tests pass.

Commit:

```powershell
cd E:\school\KACHE
git add demo/agent/evaluate_results.py demo/agent/test_evaluate_results.py docs/superpowers/experiments/.gitkeep
git commit -m "feat: add experiment report generator"
```

## Task 8: Local Smoke Verification

**Files:**
- No source file changes expected.
- Generated files under `demo/results/` are ignored by Git.
- Optional record under `docs/superpowers/experiments/`.

- [ ] **Step 1: Run all agent unit tests**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest discover -s . -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 2: Run a short simulation**

Run:

```powershell
cd E:\school\KACHE\demo\server
python main.py
```

Expected: command exits with status `0` and writes `demo/results/run_summary_202603.json`.

- [ ] **Step 3: Calculate income**

Run:

```powershell
cd E:\school\KACHE\demo
python calc_monthly_income.py
```

Expected: command exits with status `0` and writes `demo/results/monthly_income_202603.json`.

- [ ] **Step 4: Generate experiment report**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python evaluate_results.py --results-dir ..\results --out-dir ..\..\docs\superpowers\experiments --experiment-id 2026-05-13-layered-v1-local
```

Expected: output path ends with `docs\superpowers\experiments\2026-05-13-layered-v1-local.md`.

- [ ] **Step 5: Inspect score summary**

Run:

```powershell
cd E:\school\KACHE
Get-Content docs\superpowers\experiments\2026-05-13-layered-v1-local.md -Encoding UTF8
```

Expected:

- `failed_driver_count` is `0`.
- Report includes one row per driver.
- Report includes action counts.

- [ ] **Step 6: Commit experiment report if the run is meaningful**

Commit only the Markdown report, not `demo/results/`:

```powershell
cd E:\school\KACHE
git add docs/superpowers/experiments/2026-05-13-layered-v1-local.md
git commit -m "docs: record layered v1 local experiment"
```

## Task 9: Compliance Scan And Push

**Files:**
- No source file changes expected unless a scan finds an issue.

- [ ] **Step 1: Scan for driver-ID-specific logic**

Run:

```powershell
cd E:\school\KACHE
rg -n "driver_id\s*==|D00[0-9]|D010|D009" demo\agent
```

Expected: no matches in strategy logic. Test fixture strings may appear only when they are used as generic sample IDs and not control flow.

- [ ] **Step 2: Scan for raw data file reads in agent code**

Run:

```powershell
cd E:\school\KACHE
rg -n "cargo_dataset|drivers\.json|server/data|server\\data|open\(" demo\agent --glob "!evaluate_results.py" --glob "!test_evaluate_results.py"
```

Expected: no raw data path reads in decision code. `evaluate_results.py` may read `demo/results` only and is excluded from this decision-code scan.

- [ ] **Step 3: Run final tests**

Run:

```powershell
cd E:\school\KACHE\demo\agent
python -m unittest discover -s . -p "test_*.py" -v
```

Expected: all tests pass.

- [ ] **Step 4: Check Git status**

Run:

```powershell
cd E:\school\KACHE
git status --short
```

Expected: no uncommitted source changes except ignored `demo/results/`.

- [ ] **Step 5: Push branch**

Run:

```powershell
cd E:\school\KACHE
git push
```

Expected: local `main` pushes to `origin/main`.
