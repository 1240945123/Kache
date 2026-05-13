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


def _wait_minutes_from_record(record: dict[str, Any]) -> int:
    action = record.get("action")
    params = action.get("params") if isinstance(action, dict) else None
    if isinstance(params, dict) and "duration_minutes" in params:
        return int(params["duration_minutes"])
    return int(record.get("step_elapsed_minutes", 0) or 0)


def _recent_continuous_wait_minutes(records: list[dict[str, Any]]) -> int:
    total = 0
    for record in reversed(records):
        if not isinstance(record, dict):
            break
        action = record.get("action")
        if not isinstance(action, dict) or action.get("action") != "wait":
            break
        total += _wait_minutes_from_record(record)
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
        recent_continuous_wait_minutes=_recent_continuous_wait_minutes(records),
        completed_order_count=int(status.get("completed_order_count", 0) or 0),
    )


def _is_hard(rule: PreferenceRule) -> bool:
    return rule.strength == RuleStrength.HARD


def choose_required_intent(state: PlannerState, rules: list[PreferenceRule]) -> PlannedIntent | None:
    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.MONTHLY_VISIT_DAYS:
            continue
        try:
            required_days = int(rule.value["required_days"])
            latitude = float(rule.value["lat"])
            longitude = float(rule.value["lng"])
        except (KeyError, TypeError, ValueError):
            continue
        if state.current_day <= required_days:
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
