from __future__ import annotations

from typing import Any

if __package__:
    from .preference_rules import PreferenceRule, RuleStrength, RuleType
    from .strategy_helpers import Candidate, haversine_km
else:
    from preference_rules import PreferenceRule, RuleStrength, RuleType
    from strategy_helpers import Candidate, haversine_km

DEFAULT_UNKNOWN_STRONG_WAIT_MINUTES = 30
MINUTES_PER_DAY = 24 * 60
CARGO_CATEGORY_KEYS = ("category", "cargo_name", "cargo_type", "goods_type")


def _wait_action(duration_minutes: int) -> dict[str, Any]:
    return {"action": "wait", "params": {"duration_minutes": int(duration_minutes)}}


def _is_hard(rule: PreferenceRule) -> bool:
    return rule.strength == RuleStrength.HARD


def _is_unknown_strong(rule: PreferenceRule) -> bool:
    return rule.strength == RuleStrength.UNKNOWN_STRONG


def _current_day_minute(current_minute: int) -> int:
    return int(current_minute) % MINUTES_PER_DAY


def _point_in_box(point: dict[str, Any], value: dict[str, Any]) -> bool:
    try:
        lat = float(point["lat"])
        lng = float(point["lng"])
        return (
            float(value["min_lat"]) <= lat <= float(value["max_lat"])
            and float(value["min_lng"]) <= lng <= float(value["max_lng"])
        )
    except (KeyError, TypeError, ValueError):
        return True


def _point_in_zone(point: dict[str, Any], value: dict[str, Any]) -> bool:
    try:
        return (
            haversine_km(float(point["lat"]), float(point["lng"]), float(value["lat"]), float(value["lng"]))
            <= float(value["radius_km"])
        )
    except (KeyError, TypeError, ValueError):
        return False


def _remaining_window_minutes(current_minute: int, rule: PreferenceRule) -> int | None:
    value = rule.value
    try:
        start_minute = int(value["start_minute"])
        end_minute = int(value["end_minute"])
        cross_day = bool(value.get("cross_day", False))
    except (KeyError, TypeError, ValueError):
        return None

    minute = _current_day_minute(current_minute)
    if cross_day:
        if minute >= start_minute:
            return (MINUTES_PER_DAY - minute) + end_minute
        if minute < end_minute:
            return end_minute - minute
        return None
    if start_minute <= minute < end_minute:
        return end_minute - minute
    return None


def should_wait_for_window(current_minute: int, rules: list[PreferenceRule]) -> dict[str, Any] | None:
    for rule in rules:
        if _is_unknown_strong(rule):
            return _wait_action(DEFAULT_UNKNOWN_STRONG_WAIT_MINUTES)
        if not _is_hard(rule) or rule.rule_type != RuleType.NO_DRIVE_WINDOW:
            continue
        duration = _remaining_window_minutes(current_minute, rule)
        if duration is not None:
            return _wait_action(duration)
    return None


def is_candidate_allowed(
    candidate: Candidate,
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
) -> bool:
    for rule in rules:
        if _is_unknown_strong(rule):
            return False
        if not _is_hard(rule):
            continue
        if rule.rule_type == RuleType.CARGO_CATEGORY:
            cargo = cargo_by_id.get(candidate.cargo_id, {})
            blocked_category = rule.value.get("category")
            if blocked_category in {cargo.get(key) for key in CARGO_CATEGORY_KEYS}:
                return False
        elif rule.rule_type == RuleType.PICKUP_DISTANCE_LIMIT:
            try:
                if candidate.pickup_distance_km > float(rule.value["km"]):
                    return False
            except (KeyError, TypeError, ValueError):
                continue
        elif rule.rule_type == RuleType.HAUL_DISTANCE_LIMIT:
            try:
                if candidate.haul_distance_km > float(rule.value["km"]):
                    return False
            except (KeyError, TypeError, ValueError):
                continue
        elif rule.rule_type == RuleType.BOUNDING_BOX:
            if not _point_in_box(candidate.start, rule.value) or not _point_in_box(candidate.end, rule.value):
                return False
        elif rule.rule_type == RuleType.FORBIDDEN_ZONE:
            if _point_in_zone(candidate.start, rule.value) or _point_in_zone(candidate.end, rule.value):
                return False
    return True


def filter_candidates(
    candidates: list[Candidate],
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
) -> list[Candidate]:
    return [
        candidate
        for candidate in candidates
        if is_candidate_allowed(candidate, rules, cargo_by_id=cargo_by_id)
    ]
