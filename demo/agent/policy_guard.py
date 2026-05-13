from __future__ import annotations

from typing import Any

from preference_rules import PreferenceRule, RuleStrength, RuleType
from strategy_helpers import Candidate

DEFAULT_UNKNOWN_STRONG_WAIT_MINUTES = 30
MINUTES_PER_DAY = 24 * 60


def _wait_action(duration_minutes: int) -> dict[str, Any]:
    return {"action": "wait", "params": {"duration_minutes": int(duration_minutes)}}


def _is_hard(rule: PreferenceRule) -> bool:
    return rule.strength == RuleStrength.HARD


def _is_unknown_strong(rule: PreferenceRule) -> bool:
    return rule.strength == RuleStrength.UNKNOWN_STRONG


def _current_day_minute(current_minute: int) -> int:
    return int(current_minute) % MINUTES_PER_DAY


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
            elapsed_since_start = minute - start_minute
            remaining = end_minute - elapsed_since_start
            return remaining if remaining > 0 else None
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
            if cargo.get("category") == rule.value.get("category"):
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
