from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from preference_rules import PreferenceRule, RuleStrength, RuleType
from strategy_helpers import Candidate

SOFT_CATEGORY_PENALTY = 80.0
VALUE_PER_MINUTE_BONUS_FACTOR = 1.0
PICKUP_DISTANCE_PENALTY_FACTOR = 0.5
CARGO_CATEGORY_KEYS = ("category", "cargo_name", "cargo_type", "goods_type")


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


def score_candidate(
    candidate: Candidate,
    rules: list[PreferenceRule],
    *,
    cargo_by_id: dict[str, dict[str, Any]],
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
) -> list[ScoredCandidate]:
    scored = [score_candidate(candidate, rules, cargo_by_id=cargo_by_id) for candidate in candidates]
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
