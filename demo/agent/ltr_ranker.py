from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

if __package__:
    from .market_heatmap import MarketHeatmap
    from .preference_rules import PreferenceRule, RuleStrength, RuleType
    from .scoring import ScoredCandidate
else:
    from market_heatmap import MarketHeatmap
    from preference_rules import PreferenceRule, RuleStrength, RuleType
    from scoring import ScoredCandidate

MINUTES_PER_DAY = 24 * 60
SIMULATION_EPOCH = datetime(2026, 3, 1, 0, 0, 0)


@dataclass(frozen=True)
class LearningToRankWeights:
    rough_net_value: float = 0.0
    value_per_minute: float = 0.0
    pickup_distance_km: float = 0.0
    total_order_minutes: float = 0.0
    wait_minutes: float = 0.0
    haul_distance_km: float = 0.0
    future_market_value: float = 0.0
    no_drive_window_risk: float = 0.0
    sequence_deadline_risk: float = 0.0


DEFAULT_LTR_WEIGHTS = LearningToRankWeights(
    value_per_minute=2.5,
    pickup_distance_km=-0.15,
    total_order_minutes=-0.03,
    wait_minutes=-0.02,
    future_market_value=0.0,
    no_drive_window_risk=-250.0,
    sequence_deadline_risk=-180.0,
)


def rerank_scored_candidates(
    scored_candidates: list[ScoredCandidate],
    rules: list[PreferenceRule],
    *,
    market_heatmap: MarketHeatmap | None = None,
    weights: LearningToRankWeights = DEFAULT_LTR_WEIGHTS,
) -> list[ScoredCandidate]:
    reranked = [
        _apply_ltr_adjustment(item, rules, market_heatmap=market_heatmap, weights=weights)
        for item in scored_candidates
    ]
    reranked.sort(
        key=lambda item: (
            -item.score,
            -item.candidate.rough_net_value,
            -item.candidate.value_per_minute,
            item.candidate.pickup_distance_km,
            item.candidate.estimated_finish_minute,
            item.candidate.cargo_id,
        )
    )
    return reranked


def _apply_ltr_adjustment(
    item: ScoredCandidate,
    rules: list[PreferenceRule],
    *,
    market_heatmap: MarketHeatmap | None,
    weights: LearningToRankWeights,
) -> ScoredCandidate:
    features = _candidate_features(item, rules, market_heatmap=market_heatmap, weights=weights)
    adjustment = (
        features["rough_net_value"] * weights.rough_net_value
        + features["value_per_minute"] * weights.value_per_minute
        + features["pickup_distance_km"] * weights.pickup_distance_km
        + features["total_order_minutes"] * weights.total_order_minutes
        + features["wait_minutes"] * weights.wait_minutes
        + features["haul_distance_km"] * weights.haul_distance_km
        + features["future_market_value"] * weights.future_market_value
        + features["no_drive_window_risk"] * weights.no_drive_window_risk
        + features["sequence_deadline_risk"] * weights.sequence_deadline_risk
    )
    if abs(adjustment) < 1e-9:
        return item
    reasons = list(item.reasons)
    reasons.append(f"ltr adjustment {adjustment:.2f}")
    return replace(item, score=item.score + adjustment, reasons=reasons)


def _candidate_features(
    item: ScoredCandidate,
    rules: list[PreferenceRule],
    *,
    market_heatmap: MarketHeatmap | None,
    weights: LearningToRankWeights,
) -> dict[str, float]:
    candidate = item.candidate
    total_order_minutes = max(
        1,
        candidate.pickup_minutes + candidate.wait_minutes + candidate.cost_time_minutes,
    )
    return {
        "rough_net_value": candidate.rough_net_value,
        "value_per_minute": candidate.value_per_minute,
        "pickup_distance_km": candidate.pickup_distance_km,
        "total_order_minutes": float(total_order_minutes),
        "wait_minutes": float(candidate.wait_minutes),
        "haul_distance_km": candidate.haul_distance_km,
        "future_market_value": _future_market_value(candidate_end=candidate.end, current_minute=candidate.estimated_finish_minute, market_heatmap=market_heatmap)
        if abs(weights.future_market_value) > 1e-9
        else 0.0,
        "no_drive_window_risk": 1.0 if _has_hard_no_drive_window_risk(item, rules) else 0.0,
        "sequence_deadline_risk": 1.0 if _has_sequence_deadline_risk(item, rules) else 0.0,
    }


def _future_market_value(
    *,
    candidate_end: dict[str, Any],
    current_minute: int,
    market_heatmap: MarketHeatmap | None,
) -> float:
    if market_heatmap is None:
        return 0.0
    try:
        return market_heatmap.future_value(
            float(candidate_end["lat"]),
            float(candidate_end["lng"]),
            current_minute=current_minute,
        )
    except (KeyError, TypeError, ValueError):
        return 0.0


def _candidate_start_minute(item: ScoredCandidate) -> int:
    candidate = item.candidate
    duration = candidate.pickup_minutes + candidate.wait_minutes + candidate.cost_time_minutes
    return max(0, candidate.estimated_finish_minute - duration)


def _has_hard_no_drive_window_risk(item: ScoredCandidate, rules: list[PreferenceRule]) -> bool:
    start_minute = _candidate_start_minute(item)
    end_minute = item.candidate.estimated_finish_minute
    for rule in rules:
        if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.NO_DRIVE_WINDOW:
            continue
        try:
            window_start = int(rule.value["start_minute"])
            window_end = int(rule.value["end_minute"])
        except (KeyError, TypeError, ValueError):
            continue
        if _overlaps_daily_window(
            start_minute,
            end_minute,
            window_start_minute=window_start,
            window_end_minute=window_end,
            cross_day=bool(rule.value.get("cross_day")),
        ):
            return True
    return False


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
        if start_minute < window_end and end_minute > window_start:
            return True
    return False


def _has_sequence_deadline_risk(item: ScoredCandidate, rules: list[PreferenceRule]) -> bool:
    for rule in rules:
        if rule.strength != RuleStrength.HARD or rule.rule_type != RuleType.SEQUENCE_TASK:
            continue
        deadline_minute = _minute_from_wall_time(rule.value.get("deadline"))
        if deadline_minute is None:
            continue
        if item.candidate.estimated_finish_minute > deadline_minute - 8 * 60 and _candidate_start_minute(item) < deadline_minute:
            return True
    return False


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
