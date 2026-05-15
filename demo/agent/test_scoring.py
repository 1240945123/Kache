from __future__ import annotations

import unittest

from preference_rules import PreferenceRule, RuleStrength, RuleType
from market_heatmap import MarketHeatmap
from scoring import score_candidates
from strategy_helpers import Candidate


def _candidate(**overrides):
    base = {
        "cargo_id": "C1",
        "price": 500.0,
        "pickup_distance_km": 10.0,
        "pickup_minutes": 10,
        "wait_minutes": 0,
        "cost_time_minutes": 120,
        "estimated_finish_minute": 200,
        "haul_distance_km": 100.0,
        "rough_net_value": 300.0,
        "value_per_minute": 2.0,
        "start": {"lat": 22.55, "lng": 114.07},
        "end": {"lat": 22.8, "lng": 114.2},
        "load_time": None,
    }
    base.update(overrides)
    return Candidate(**base)


def _rule(rule_type, strength=RuleStrength.SOFT, value=None):
    return PreferenceRule(rule_type, strength, value or {}, "test preference")


class ScoringTest(unittest.TestCase):
    def test_score_candidates_ranks_by_rough_net_value_without_preferences(self):
        low = _candidate(cargo_id="LOW", rough_net_value=260.0, value_per_minute=1.0)
        high = _candidate(cargo_id="HIGH", rough_net_value=300.0, value_per_minute=1.0)

        scored = score_candidates([low, high], [], cargo_by_id={})

        self.assertEqual([item.candidate.cargo_id for item in scored], ["HIGH", "LOW"])

    def test_score_candidates_ties_by_cargo_id_when_numeric_scores_are_equal(self):
        second = _candidate(cargo_id="C2")
        first = _candidate(cargo_id="C1")

        scored = score_candidates([second, first], [], cargo_by_id={})

        self.assertEqual([item.candidate.cargo_id for item in scored], ["C1", "C2"])

    def test_soft_cargo_category_penalty_can_lower_candidate(self):
        avoided = _candidate(cargo_id="A", rough_net_value=300.0, value_per_minute=1.0)
        normal = _candidate(cargo_id="B", rough_net_value=260.0, value_per_minute=1.0)
        rules = [_rule(RuleType.CARGO_CATEGORY, value={"category": "食品饮料"})]

        scored = score_candidates(
            [avoided, normal],
            rules,
            cargo_by_id={"A": {"category": "食品饮料"}, "B": {"category": "钢材"}},
        )

        self.assertEqual([item.candidate.cargo_id for item in scored], ["B", "A"])
        self.assertTrue(any("soft cargo category" in reason for reason in scored[1].reasons))

    def test_future_market_bonus_can_raise_candidate_ending_near_future_cargo(self):
        isolated = _candidate(
            cargo_id="ISOLATED",
            rough_net_value=300.0,
            value_per_minute=1.0,
            end={"lat": 25.0, "lng": 115.0},
            estimated_finish_minute=100,
        )
        connected = _candidate(
            cargo_id="CONNECTED",
            rough_net_value=260.0,
            value_per_minute=1.0,
            end={"lat": 23.0, "lng": 113.0},
            estimated_finish_minute=100,
        )
        heatmap = MarketHeatmap.from_cargo_records(
            [
                {
                    "cargo_id": f"FUTURE{i}",
                    "create_minute": 120 + i,
                    "price": 1000.0,
                    "start": {"lat": 23.01, "lng": 113.01},
                }
                for i in range(12)
            ]
        )

        scored = score_candidates([isolated, connected], [], cargo_by_id={}, market_heatmap=heatmap)

        self.assertEqual([item.candidate.cargo_id for item in scored], ["CONNECTED", "ISOLATED"])
        self.assertTrue(any("future market bonus" in reason for reason in scored[0].reasons))


if __name__ == "__main__":
    unittest.main()
