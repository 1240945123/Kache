from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from preference_rules import PlannedIntent, PreferenceRule, RuleStrength, RuleType
from strategy_helpers import haversine_km

MINUTES_PER_DAY = 24 * 60
SIMULATION_EPOCH = datetime(2026, 3, 1, 0, 0)


@dataclass(frozen=True)
class PlannerState:
    current_minute: int
    current_day: int
    minute_of_day: int
    current_lat: float
    current_lng: float
    recent_continuous_wait_minutes: int
    completed_order_count: int
    history_records: tuple[dict[str, Any], ...] = ()


def _non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _wait_minutes_from_record(record: dict[str, Any]) -> int:
    action = record.get("action")
    params = action.get("params") if isinstance(action, dict) else None
    if isinstance(params, dict) and "duration_minutes" in params:
        return _non_negative_int(params["duration_minutes"])
    return _non_negative_int(record.get("step_elapsed_minutes", 0))


def _minute_from_simulation_end_time(value: Any) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
        return int((dt - SIMULATION_EPOCH).total_seconds() // 60)
    return None


def _recent_continuous_wait_minutes(records: list[dict[str, Any]], current_minute: int) -> int:
    total = 0
    day_start = (current_minute // MINUTES_PER_DAY) * MINUTES_PER_DAY
    cursor_end = current_minute
    for record in reversed(records):
        if not isinstance(record, dict):
            break
        action = record.get("action")
        if not isinstance(action, dict) or action.get("action") != "wait":
            break
        duration = _wait_minutes_from_record(record)
        end_minute = _minute_from_simulation_end_time(record.get("simulation_end_time"))
        if end_minute is None:
            end_minute = cursor_end
        start_minute = end_minute - duration
        overlap_start = max(start_minute, day_start)
        overlap_end = min(end_minute, current_minute)
        total += max(0, overlap_end - overlap_start)
        cursor_end = start_minute
    return total


def build_planner_state(status: dict[str, Any], history: dict[str, Any]) -> PlannerState:
    current_minute = int(status.get("simulation_progress_minutes", 0) or 0)
    records = history.get("records", []) if isinstance(history, dict) else []
    if not isinstance(records, list):
        records = []

    return PlannerState(
        current_minute=current_minute,
        current_day=current_minute // MINUTES_PER_DAY + 1,
        minute_of_day=current_minute % MINUTES_PER_DAY,
        current_lat=float(status.get("current_lat", 0.0) or 0.0),
        current_lng=float(status.get("current_lng", 0.0) or 0.0),
        recent_continuous_wait_minutes=_recent_continuous_wait_minutes(records, current_minute),
        completed_order_count=int(status.get("completed_order_count", 0) or 0),
        history_records=tuple(record for record in records if isinstance(record, dict)),
    )


def _is_hard(rule: PreferenceRule) -> bool:
    return rule.strength == RuleStrength.HARD


def _visited_days_near_target(state: PlannerState, latitude: float, longitude: float, radius_km: float) -> set[int]:
    visited_days: set[int] = set()
    for record in state.history_records:
        position = record.get("position_after")
        if not isinstance(position, dict):
            continue
        try:
            position_lat = float(position["lat"])
            position_lng = float(position["lng"])
        except (KeyError, TypeError, ValueError):
            continue
        if haversine_km(position_lat, position_lng, latitude, longitude) > radius_km:
            continue
        end_minute = _minute_from_simulation_end_time(record.get("simulation_end_time"))
        if end_minute is None:
            end_minute = state.current_minute
        visited_days.add(end_minute // MINUTES_PER_DAY + 1)
    return visited_days


def choose_required_intent(state: PlannerState, rules: list[PreferenceRule]) -> PlannedIntent | None:
    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.MONTHLY_VISIT_DAYS:
            continue
        try:
            required_days = int(rule.value["required_days"])
            latitude = float(rule.value["lat"])
            longitude = float(rule.value["lng"])
            radius_km = float(rule.value.get("radius_km", 0.0))
        except (KeyError, TypeError, ValueError):
            continue
        if required_days > 0 and len(_visited_days_near_target(state, latitude, longitude, radius_km)) < required_days:
            return PlannedIntent(
                intent_type="visit_target",
                action="reposition",
                params={"latitude": latitude, "longitude": longitude},
                reason=rule.source_text,
                priority=100,
                metadata={"rule_type": rule.rule_type.value},
            )

    remaining_day = MINUTES_PER_DAY - state.minute_of_day
    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.DAILY_REST:
            continue
        try:
            required_minutes = int(rule.value["minutes"])
        except (KeyError, TypeError, ValueError):
            continue
        if state.recent_continuous_wait_minutes < required_minutes and remaining_day <= required_minutes:
            return PlannedIntent(
                intent_type="daily_rest",
                action="wait",
                params={"duration_minutes": required_minutes - state.recent_continuous_wait_minutes},
                reason=rule.source_text,
                priority=90,
                metadata={"rule_type": rule.rule_type.value},
            )

    return None
