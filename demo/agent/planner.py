from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

if __package__:
    from .preference_rules import PlannedIntent, PreferenceRule, RuleStrength, RuleType
    from .strategy_helpers import haversine_km
else:
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


def _minute_from_wall_time(value: Any) -> int | None:
    return _minute_from_simulation_end_time(value)


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


def _record_day(record: dict[str, Any], fallback_minute: int) -> int:
    end_minute = _minute_from_simulation_end_time(record.get("simulation_end_time"))
    if end_minute is None:
        end_minute = fallback_minute
    return end_minute // MINUTES_PER_DAY + 1


def _action_name(record: dict[str, Any]) -> str:
    action = record.get("action")
    if not isinstance(action, dict):
        return ""
    return str(action.get("action", ""))


def _is_accepted_order(record: dict[str, Any]) -> bool:
    if _action_name(record) != "take_order":
        return False
    result = record.get("result")
    return not isinstance(result, dict) or result.get("accepted") is not False


def _current_day_order_count(state: PlannerState) -> int:
    return sum(
        1
        for record in state.history_records
        if _record_day(record, state.current_minute) == state.current_day and _is_accepted_order(record)
    )


def _current_day_has_non_wait(state: PlannerState) -> bool:
    for record in state.history_records:
        if _record_day(record, state.current_minute) != state.current_day:
            continue
        if _action_name(record) and _action_name(record) != "wait":
            return True
    return False


def _completed_no_order_days(state: PlannerState) -> int:
    order_days = {
        _record_day(record, state.current_minute)
        for record in state.history_records
        if _is_accepted_order(record)
    }
    return sum(1 for day in range(1, state.current_day) if day not in order_days)


def _completed_off_days(state: PlannerState) -> int:
    active_days = {
        _record_day(record, state.current_minute)
        for record in state.history_records
        if _action_name(record) and _action_name(record) != "wait"
    }
    return sum(1 for day in range(1, state.current_day) if day not in active_days)


def _wait_until_next_day(state: PlannerState) -> dict[str, Any]:
    return {"duration_minutes": max(1, MINUTES_PER_DAY - state.minute_of_day)}


def _visited_target(state: PlannerState, latitude: float, longitude: float, radius_km: float, before_minute: int | None = None) -> bool:
    for record in state.history_records:
        end_minute = _minute_from_simulation_end_time(record.get("simulation_end_time"))
        if before_minute is not None and end_minute is not None and end_minute > before_minute:
            continue
        position = record.get("position_after")
        if not isinstance(position, dict):
            continue
        try:
            position_lat = float(position["lat"])
            position_lng = float(position["lng"])
        except (KeyError, TypeError, ValueError):
            continue
        if haversine_km(position_lat, position_lng, latitude, longitude) <= radius_km:
            return True
    return False


def _sequence_task_intent(state: PlannerState, rule: PreferenceRule) -> PlannedIntent | None:
    try:
        steps = rule.value["steps"]
        pickup_step = steps[0]
        home_step = steps[1]
        pickup_lat = float(pickup_step["lat"])
        pickup_lng = float(pickup_step["lng"])
        pickup_wait = int(pickup_step.get("wait_minutes", 10))
        home_lat = float(home_step["lat"])
        home_lng = float(home_step["lng"])
        deadline_minute = _minute_from_wall_time(rule.value["deadline"])
        stay_until_minute = _minute_from_wall_time(rule.value["stay_until"])
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    if deadline_minute is None or stay_until_minute is None or state.current_minute >= stay_until_minute:
        return None

    home_distance = haversine_km(state.current_lat, state.current_lng, home_lat, home_lng)
    if state.current_minute >= deadline_minute:
        if home_distance > 1.0:
            return PlannedIntent(
                intent_type="sequence_return_home",
                action="reposition",
                params={"latitude": home_lat, "longitude": home_lng},
                reason=rule.source_text,
                priority=120,
                metadata={"rule_type": rule.rule_type.value},
            )
        return PlannedIntent(
            intent_type="sequence_stay_home",
            action="wait",
            params={"duration_minutes": max(1, stay_until_minute - state.current_minute)},
            reason=rule.source_text,
            priority=120,
            metadata={"rule_type": rule.rule_type.value},
        )

    if not _visited_target(state, pickup_lat, pickup_lng, 1.0, before_minute=deadline_minute):
        if haversine_km(state.current_lat, state.current_lng, pickup_lat, pickup_lng) <= 1.0:
            return PlannedIntent(
                intent_type="sequence_pickup_wait",
                action="wait",
                params={"duration_minutes": max(1, pickup_wait)},
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

    if home_distance > 1.0:
        return PlannedIntent(
            intent_type="sequence_return_home",
            action="reposition",
            params={"latitude": home_lat, "longitude": home_lng},
            reason=rule.source_text,
            priority=120,
            metadata={"rule_type": rule.rule_type.value},
        )
    return PlannedIntent(
        intent_type="sequence_wait_deadline",
        action="wait",
        params={"duration_minutes": max(1, deadline_minute - state.current_minute)},
        reason=rule.source_text,
        priority=120,
        metadata={"rule_type": rule.rule_type.value},
    )


def choose_required_intent(state: PlannerState, rules: list[PreferenceRule]) -> PlannedIntent | None:
    for rule in rules:
        if _is_hard(rule) and rule.rule_type == RuleType.SEQUENCE_TASK:
            intent = _sequence_task_intent(state, rule)
            if intent is not None:
                return intent

    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.MONTHLY_VISIT_DAYS:
            continue
        try:
            required_days = int(rule.value["required_days"])
            latitude = float(rule.value["lat"])
            longitude = float(rule.value["lng"])
            radius_km = float(rule.value.get("radius_km", 1.0))
        except (KeyError, TypeError, ValueError):
            continue
        visited_days = _visited_days_near_target(state, latitude, longitude, radius_km)
        if required_days <= 0 or len(visited_days) >= required_days:
            continue
        if state.current_day in visited_days:
            continue
        if haversine_km(state.current_lat, state.current_lng, latitude, longitude) <= radius_km:
            return PlannedIntent(
                intent_type="visit_target_wait",
                action="wait",
                params={"duration_minutes": 30},
                reason=rule.source_text,
                priority=100,
                metadata={"rule_type": rule.rule_type.value},
            )
        else:
            return PlannedIntent(
                intent_type="visit_target",
                action="reposition",
                params={"latitude": latitude, "longitude": longitude},
                reason=rule.source_text,
                priority=100,
                metadata={"rule_type": rule.rule_type.value},
            )

    for rule in rules:
        if not _is_hard(rule) or rule.rule_type not in {RuleType.MONTHLY_NO_ORDER_DAYS, RuleType.MONTHLY_OFF_DAYS}:
            continue
        try:
            required_days = int(rule.value["required_days"])
        except (KeyError, TypeError, ValueError):
            continue
        completed_days = (
            _completed_off_days(state)
            if rule.rule_type == RuleType.MONTHLY_OFF_DAYS
            else _completed_no_order_days(state)
        )
        if completed_days >= required_days:
            continue
        current_day_usable = _current_day_order_count(state) == 0
        if rule.rule_type == RuleType.MONTHLY_OFF_DAYS:
            current_day_usable = not _current_day_has_non_wait(state)
        if current_day_usable:
            return PlannedIntent(
                intent_type="monthly_off_day" if rule.rule_type == RuleType.MONTHLY_OFF_DAYS else "monthly_no_order_day",
                action="wait",
                params=_wait_until_next_day(state),
                reason=rule.source_text,
                priority=98,
                metadata={"rule_type": rule.rule_type.value},
            )

    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.HOME_DEADLINE:
            continue
        try:
            deadline_minute = int(rule.value["deadline_minute"])
            latitude = float(rule.value["lat"])
            longitude = float(rule.value["lng"])
            radius_km = float(rule.value.get("radius_km", 1.0))
        except (KeyError, TypeError, ValueError):
            continue
        distance_km = haversine_km(state.current_lat, state.current_lng, latitude, longitude)
        if state.minute_of_day >= deadline_minute or deadline_minute - state.minute_of_day <= 60:
            if distance_km > radius_km:
                return PlannedIntent(
                    intent_type="home_deadline",
                    action="reposition",
                    params={"latitude": latitude, "longitude": longitude},
                    reason=rule.source_text,
                    priority=97,
                    metadata={"rule_type": rule.rule_type.value},
                )
            if state.minute_of_day >= deadline_minute:
                return PlannedIntent(
                    intent_type="home_deadline_wait",
                    action="wait",
                    params=_wait_until_next_day(state),
                    reason=rule.source_text,
                    priority=97,
                    metadata={"rule_type": rule.rule_type.value},
                )

    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.DAILY_ORDER_LIMIT:
            continue
        try:
            max_orders = int(rule.value["max_orders"])
        except (KeyError, TypeError, ValueError):
            continue
        if max_orders >= 0 and _current_day_order_count(state) >= max_orders:
            return PlannedIntent(
                intent_type="daily_order_limit",
                action="wait",
                params=_wait_until_next_day(state),
                reason=rule.source_text,
                priority=96,
                metadata={"rule_type": rule.rule_type.value},
            )

    for rule in rules:
        if not _is_hard(rule) or rule.rule_type != RuleType.FIRST_ORDER_DEADLINE:
            continue
        try:
            deadline_minute = int(rule.value["deadline_minute"])
        except (KeyError, TypeError, ValueError):
            continue
        if _current_day_order_count(state) == 0 and state.minute_of_day >= deadline_minute:
            return PlannedIntent(
                intent_type="first_order_deadline",
                action="wait",
                params=_wait_until_next_day(state),
                reason=rule.source_text,
                priority=95,
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
