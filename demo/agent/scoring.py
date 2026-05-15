from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

if __package__:
    from .market_heatmap import MarketHeatmap
    from .preference_rules import PreferenceRule, RuleStrength, RuleType
    from .strategy_helpers import Candidate
else:
    from market_heatmap import MarketHeatmap
    from preference_rules import PreferenceRule, RuleStrength, RuleType
    from strategy_helpers import Candidate

SOFT_CATEGORY_PENALTY = 80.0
HARD_NO_DRIVE_WINDOW_RISK_PENALTY = 700.0
SEQUENCE_DEADLINE_RISK_PENALTY = 700.0
SEQUENCE_DEADLINE_BUFFER_MINUTES = 8 * 60
VALUE_PER_MINUTE_BONUS_FACTOR = 1.0
PICKUP_DISTANCE_PENALTY_FACTOR = 0.5
FUTURE_MARKET_BONUS_FACTOR = 1.0
CARGO_CATEGORY_KEYS = ("category", "cargo_name", "cargo_type", "goods_type")
MINUTES_PER_DAY = 24 * 60
SIMULATION_EPOCH = datetime(2026, 3, 1, 0, 0, 0)


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: Candidate
    score: float
    reasons: list[str]


def _matches_cargo_category(candidate: Candidate, rule: PreferenceRule, cargo_by_id: dict[str, dict[str, Any]]) -> bool:
    avoided_category = rule.value.get("category")
    if not avoided_category:
        return False
    cargo = cargo_by_id.get(candidate.cargo_id, {})
    return avoided_category in {cargo.get(key) for key in CARGO_CATEGORY_KEYS}


def _candidate_start_minute(candidate: Candidate) -> int:
    duration = candidate.pickup_minutes + candidate.wait_minutes + candidate.cost_time_minutes
    return max(0, candidate.estimated_finish_minute - duration)


def _overlaps_interval(start_minute: int, end_minute: int, window_start: int, window_end: int) -> bool:
    return start_minute < window_end and end_minute > window_start


def _overlaps_daily_window(
    start_minute: int,
    end_minute: int,
    *,
    window_start_minute: int,
    window_end_minute: int,
    cross_day: bool,
) -> bool:
    if end_minute <= start_minute:
        return False
    start_day = max(0, start_minute // MINUTES_PER_DAY - 1)
    end_day = end_minute // MINUTES_PER_DAY + 1
    for day in range(start_day, end_day + 1):
        day_start = day * MINUTES_PER_DAY
        window_start = day_start + window_start_minute
        if cross_day or window_end_minute <= window_start_minute:
            window_end = (day + 1) * MINUTES_PER_DAY + window_end_minute
        else:
            window_end = day_start + window_end_minute
        if _overlaps_interval(start_minute, end_minute, window_start, window_end):
            return True
    return False


def _hard_no_drive_window_risk(candidate: Candidate, rule: PreferenceRule) -> bool:
    if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.NO_DRIVE_WINDOW:
        return False
    try:
        window_start_minute = int(rule.value["start_minute"])
        window_end_minute = int(rule.value["end_minute"])
    except (KeyError, TypeError, ValueError):
        return False
    start_minute = _candidate_start_minute(candidate)
    return _overlaps_daily_window(
        start_minute,
        candidate.estimated_finish_minute,
        window_start_minute=window_start_minute,
        window_end_minute=window_end_minute,
        cross_day=bool(rule.value.get("cross_day")),
    )


def _minute_from_wall_time(value: Any) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
        return int((dt - SIMULATION_EPOCH).total_seconds() // 60)
    return None


def _sequence_deadline_risk(candidate: Candidate, rule: PreferenceRule) -> bool:
    if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.SEQUENCE_TASK:
        return False
    deadline_minute = _minute_from_wall_time(rule.value.get("deadline"))
    if deadline_minute is None:
        return False
    risk_start_minute = deadline_minute - SEQUENCE_DEADLINE_BUFFER_MINUTES
    return candidate.estimated_finish_minute > risk_start_minute and _candidate_start_minute(candidate) < deadline_minute


def score_candidate(
    candidate: Candidate,
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
    market_heatmap: MarketHeatmap | None = None,
) -> ScoredCandidate:
    score = (
        candidate.rough_net_value
        + (candidate.value_per_minute * VALUE_PER_MINUTE_BONUS_FACTOR)
        - (candidate.pickup_distance_km * PICKUP_DISTANCE_PENALTY_FACTOR)
    )
    reasons = [
        f"rough net value {candidate.rough_net_value:.2f}",
        f"value per minute bonus {candidate.value_per_minute * VALUE_PER_MINUTE_BONUS_FACTOR:.2f}",
        f"pickup distance penalty {candidate.pickup_distance_km * PICKUP_DISTANCE_PENALTY_FACTOR:.2f}",
    ]

    if market_heatmap is not None:
        try:
            future_bonus = market_heatmap.future_value(
                float(candidate.end["lat"]),
                float(candidate.end["lng"]),
                current_minute=candidate.estimated_finish_minute,
            ) * FUTURE_MARKET_BONUS_FACTOR
        except (KeyError, TypeError, ValueError):
            future_bonus = 0.0
        if future_bonus > 0:
            score += future_bonus
            reasons.append(f"future market bonus {future_bonus:.2f}")

    for rule in rules:
        if _hard_no_drive_window_risk(candidate, rule):
            score -= HARD_NO_DRIVE_WINDOW_RISK_PENALTY
            reasons.append(f"no-drive window risk penalty {HARD_NO_DRIVE_WINDOW_RISK_PENALTY:.2f}")
        if _sequence_deadline_risk(candidate, rule):
            score -= SEQUENCE_DEADLINE_RISK_PENALTY
            reasons.append(f"sequence deadline risk penalty {SEQUENCE_DEADLINE_RISK_PENALTY:.2f}")

    for rule in rules:
        if rule.strength != RuleStrength.SOFT or rule.rule_type != RuleType.CARGO_CATEGORY:
            continue
        if _matches_cargo_category(candidate, rule, cargo_by_id):
            score -= SOFT_CATEGORY_PENALTY
            reasons.append(f"soft cargo category penalty {SOFT_CATEGORY_PENALTY:.2f}")

    return ScoredCandidate(candidate=candidate, score=score, reasons=reasons)


def score_candidates(
    candidates: list[Candidate],
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
    market_heatmap: MarketHeatmap | None = None,
) -> list[ScoredCandidate]:
    scored = [
        score_candidate(candidate, rules, cargo_by_id=cargo_by_id, market_heatmap=market_heatmap)
        for candidate in candidates
    ]
    scored.sort(
        key=lambda item: (
            -item.score,
            -item.candidate.rough_net_value,
            -item.candidate.value_per_minute,
            item.candidate.pickup_distance_km,
            item.candidate.estimated_finish_minute,
            item.candidate.cargo_id,
        )
    )
    return scored
